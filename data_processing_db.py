import json

from util_functions import connect_database


class DataProcessError(RuntimeError):
    def __init__(self, msg: str):
        self.msg = msg


# Check if the database is connected and reconnect if necessary
def reconnect():
    global cursor, connection
    try:
        connection.ping()
    except Exception:
        cursor, connection = connection()


# Check if a column exists in a database
def check_col_exist(name: str, data: tuple) -> bool:
    for i in data:
        if name == i[0]:
            return True
    return False


def check_boss_exist(phase: int, boss_id: int) -> bool:
    reconnect()
    command = 'SELECT phase,id FROM pcr.boss_list'
    cursor.execute(command)
    data = cursor.fetchall()
    for i in data:
        if phase == i[0] and boss_id == i[1]:
            return True
    return False


def check_member_exist(target_id: int):
    reconnect()
    command = 'SELECT qq FROM pcr.member_list'
    cursor.execute(command)
    data = cursor.fetchall()
    return (target_id,) in data


# Generate the name of the boss
def generate_boss_name(phase: int, boss_id: int) -> str:
    s = 'p%d_boss%d' % (phase, boss_id)
    return s


# Add a user into the database
def register_user(qq: int = 10000, user_name: str = 'a', user_id: str = '1', guild='一会') -> bool:
    try:
        user_id = int(user_id)
    except ValueError:
        return False
    reconnect()
    c = "SELECT * FROM pcr.member_list WHERE qq=%d" % qq
    cursor.execute(c)
    if len(cursor.fetchall()) == 0:
        command = "INSERT INTO pcr.member_list" \
                  "(qq, user_name, user_id, roll, guild) VALUES " \
                  "(%d, %s, %d, 'member', %s)" % (qq, f"'{user_name}'", user_id, f"'{guild}'")
        cursor.execute(command)
        connection.commit()
        print("user created")
        connection.commit()
        return True
    else:
        connection.commit()
        return False


# Update the info of a user in the database
def update_user(qq: int = 10000, user_name: str = '\'a\'', user_id: str = '1'):
    try:
        user_id = int(user_id)
    except ValueError:
        return False
    reconnect()
    c = "SELECT * FROM pcr.member_list WHERE qq=%d" % qq
    cursor.execute(c)
    if not len(cursor.fetchall()) == 0:
        command = "UPDATE pcr.member_list SET " \
                  "user_name=%s,user_id=%d WHERE qq=%d" % ("'%s'" % user_name, user_id, qq)
        print(command)
        cursor.execute(command)
        connection.commit()
        print("user updated")
        connection.commit()
        return True
    else:
        connection.commit()
        return False


# Remove a user from the database
def remove_member(qq: int):
    reconnect()
    command = "DELETE FROM 'pcr'.'member_list' WHERE 'qq'=%d" % qq
    cursor.execute(command)
    connection.commit()


def add_boss_damage(qq: int, damage: str): # needs modification
    damage = int(damage)
    reconnect()

    command = f"SELECT guild FROM pcr.member_list WHERE qq={qq}"
    cursor.execute(command)
    t = cursor.fetchall()
    guild = t[0][0]

    command = f"SELECT value FROM pcr.config WHERE key_name='{guild}_phase' OR key_name='{guild}_boss'"
    cursor.execute(command)
    t = cursor.fetchall()

    phase = t[0][0]
    boss = t[1][0]

    command = f"SELECT value FROM pcr.config WHERE key_name='{guild}_health'"
    cursor.execute(command)
    t = cursor.fetchall()
    present_health = int(t[0][0])

    if present_health <= damage:
        return  # TODO: Raise exception
    else:
        present_health -= damage
        command = f"UPDATE pcr.config SET value={str(present_health)} WHERE key_name='{guild}_health'"
        cursor.execute(command)
        connection.commit()

    res = {"normal": {"damage": damage, "phase": phase, "boss": boss}}

    command = f"SELECT value FROM pcr.config WHERE key_name='day'"
    cursor.execute(command)
    t = cursor.fetchall()
    day = t[0][0]

    target = [f'd{day}t1', f'd{day}t2', f'd{day}t3']
    command = f"SELECT {target[0]},{target[1]},{target[2]},last FROM pcr.actual_damage WHERE qq=2034845390"
    cursor.execute(command)
    t = cursor.fetchall()
    print(t)

    if not t[0][3] == '':
        temp_dict = json.loads(t[0][4])
        res['last'] = temp_dict['last']
        command = f"UPDATE pcr.actual_damage SET last='' WHERE qq={qq}"

    res = json.dumps(res)

    if t[0][0] == '':
        command = f"UPDATE pcr.actual_damage SET {target[0]}='{res}' WHERE qq={qq}"
    elif t[0][1] == '':
        command = f"UPDATE pcr.actual_damage SET {target[1]}='{res}' WHERE qq={qq}"
    elif t[0][2] == '':
        command = f"UPDATE pcr.actual_damage SET {target[2]}='{res}' WHERE qq={qq}"
    else:
        print("ERROR")
        return # TODO: raise exception

    cursor.execute(command)
    connection.commit()


def add_trial_damage(target_id: int, phase: str, boss_id: str, team_id: str, damage: str):
    reconnect()

    # Convert type
    phase = int(phase)
    boss_id = int(boss_id)
    team_id = int(team_id)
    damage = int(damage)

    # Input check
    if not 1 <= boss_id <= 5:
        raise DataProcessError('boss序号错误')
    if not phase > 0:
        raise DataProcessError('阶段序号错误')
    if not 1 <= team_id <= 3:
        raise DataProcessError('队伍序号错误')
    if not damage >= 0:
        raise DataProcessError('伤害数值错误')

    # Check if boss exist
    if not check_boss_exist(phase, boss_id):
        raise DataProcessError('boss不存在')

    # Choose damage mode
    database_name = 'pcr.trial_damage'

    # Check if table exists
    cursor.execute('SHOW TABLES')
    data = cursor.fetchall()
    if not (database_name,) in data:
        cursor.execute('CREATE TABLE pcr.%s (qq INT UNIQUE)' % database_name)

    # Check column exists and creat if doesn't exist
    target_col = generate_boss_name(phase, boss_id) + '_t' + str(team_id)
    cursor.execute('DESC %s' % database_name)
    data = cursor.fetchall()
    if not check_col_exist(target_col, data):
        for i in range(1, 4):
            cursor.execute('ALTER TABLE pcr.%s ADD %s '
                           'INT NOT NULL DEFAULT 0' % (database_name,
                                                       generate_boss_name(phase, boss_id) + '_t' + str(i)))

    # Check if target exist and create if not, otherwise update data
    c = 'SELECT * FROM %s WHERE qq=%d' % (database_name, target_id)
    cursor.execute(c)
    data = cursor.fetchall()
    if len(data) == 0:
        c = 'INSERT INTO %s(qq, %s) VALUES (%d, %d)' % (database_name, target_col, target_id, damage)
    else:
        c = 'UPDATE %s SET %s=%d WHERE qq=%d' % (database_name, target_col, damage, target_id)
    cursor.execute(c)
    connection.commit()
    return


def last(qq: int):
    reconnect()

    command = f"SELECT guild FROM pcr.member_list WHERE qq={qq}"
    cursor.execute(command)
    t = cursor.fetchall()
    guild = t[0][0]

    command = f"SELECT value FROM pcr.config WHERE key_name='{guild}_phase' OR key_name='{guild}_boss'"
    cursor.execute(command)
    t = cursor.fetchall()

    phase = int(t[0][0])
    boss = int(t[1][0])

    command = f"SELECT value FROM pcr.config WHERE key_name='{guild}_health'"
    cursor.execute(command)
    t = cursor.fetchall()
    present_health = int(t[0][0])

    res = {'last': {"damage": present_health, "phase": phase, "boss": boss}}

    command = f"UPDATE pcr.actual_damage SET last='{json.dumps(res)}' WHERE qq={qq}"
    cursor.execute(command)
    connection.commit()

    if boss == 5:
        phase += 1
        boss = 1
    else:
        boss += 1

    command = f"SELECT health FROM pcr.boss_list WHERE id={boss}"
    cursor.execute(command)
    t = cursor.fetchall()
    health = t[0][0]

    command = f"UPDATE pcr.config SET value={str(health)} WHERE key_name='{guild}_health'"
    cursor.execute(command)

    command = f"UPDATE pcr.config SET value={str(boss)} WHERE key_name='{guild}_boss'"
    cursor.execute(command)

    command = f"UPDATE pcr.config SET value={str(phase)} WHERE key_name='{guild}_phase'"
    cursor.execute(command)


def redo_damage(qq: int):
    reconnect()

    command = f"SELECT value FROM pcr.config WHERE key_name='day'"
    cursor.execute(command)
    d = cursor.fetchall()
    day = d[0][0]

    command = f'SELECT last,d{day}t1,d{day}t2,d{day}t3 FROM pcr.actual_damage WHERE qq={qq}'
    cursor.execute(command)
    damage_data = cursor.fetchall()

    team: int
    if not damage_data[0][0] == '':
        team = 0
    elif damage_data[0][1] == '':
        team = -1
    elif damage_data[0][2] == '':
        team = 1
    elif damage_data[0][3] == '':
        team = 2
    else:
        team = 3

    raw_damage = damage_data[0][team]
    info = json.loads(raw_damage)

    if team == 0:
        actual_damage = info['last']['damage']
    elif team == -1:
        return
    else:
        actual_damage = info['normal']['damage']

    command = f"SELECT guild FROM pcr.member_list WHERE qq={qq}"
    cursor.execute(command)
    d = cursor.fetchall()
    guild = d[0][0]

    command = f"SELECT value FROM pcr.config WHERE key_name='{guild}_phase' OR key_name='{guild}_boss'"
    cursor.execute(command)
    t = cursor.fetchall()

    phase = int(t[0][0])
    boss = int(t[1][0])

    command = f"SELECT health FROM pcr.boss_list WHERE id={boss}"
    cursor.execute(command)
    t = cursor.fetchall()
    full_health = int(t[0][0])

    command = f"SELECT value FROM pcr.config WHERE key_name='{guild}_health'"
    cursor.execute(command)
    d = cursor.fetchall()
    actual_health = int(d[0][0])

    print(actual_health)
    print(actual_damage)
    actual_health += int(actual_damage)
    if actual_health > full_health:
        actual_health -= full_health
        boss -= 1
        if boss == 0:
            boss = 5
            phase -= 1

    if team == 0:
        command = f"UPDATE pcr.actual_damage SET last='' WHERE qq={qq}"
        cursor.execute(command)
        connection.commit()
    else:
        command = f"UPDATE pcr.actual_damage SET d{day}t{team}='' WHERE qq={qq}"
        cursor.execute(command)
        connection.commit()

    command = f"UPDATE pcr.config SET value={str(actual_health)} WHERE key_name='{guild}_health'"
    cursor.execute(command)

    command = f"UPDATE pcr.config SET value={str(boss)} WHERE key_name='{guild}_boss'"
    cursor.execute(command)

    command = f"UPDATE pcr.config SET value={str(phase)} WHERE key_name='{guild}_phase'"
    cursor.execute(command)

    connection.commit()


def display_damage(target: int) -> str:
    # Connect to database
    # connection, cursor = connect_database()

    # Fetch all tables
    command = 'DESC trial_damage'
    cursor.execute(command)
    col_list = cursor.fetchall()

    res = str(target) + ':\n'
    command = 'SELECT * FROM pcr.trial_damage WHERE qq=%d' % target
    cursor.execute(command)
    t = cursor.fetchall()
    if len(t) == 0:
        return '无模拟战数据'
    data = t[0]
    print(data)
    for i in range(1, int(len(data) / 3) + 1):
        res += col_list[i * 3][0][0:len(col_list[i * 3][0]) - 3] + ':' \
               + '[%d, %d, %d]' % (data[i * 3 - 2], data[i * 3 - 1], data[i * 3]) + '\n'
    connection.commit()
    return res


def set_day(val: str):
    # convert type
    try:
        val = int(val)
    except ValueError:
        raise DataProcessError('格式错误，请确保参数是数字')
    command = "UPDATE pcr.config SET value=%d WHERE key_name='day'" % val
    cursor.execute(command)
    command = f"CREATE TABLE pcr.actual_damage_d{val} (qq INT UNIQUE)"
    cursor.execute(command)
    connection.commit()
    return


def set_mod(target: str):
    try:
        target = int(target)
    except ValueError:
        raise DataProcessError('参数格式错误，应为数字')

    if check_member_exist(target):
        command = "'UPDATE member_list SET roll='mod' WHERE qq=%d" % target
        cursor.execute(command)
        connection.commit()
        return
    else:
        raise DataProcessError('成员不存在')


global cursor, connection
cursor, connection = connect_database()
