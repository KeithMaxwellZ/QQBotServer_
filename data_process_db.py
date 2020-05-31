from util_functions import connect_database


class DataProcessError(RuntimeError):
    def __init__(self, msg: str):
        self.msg = msg


# Check if a column exists in a database
def check_col_exist(name: str, data: tuple) -> bool:
    for i in data:
        if name == i[0]:
            return True
    return False


def check_boss_exist(phase: int, boss_id: int) -> bool:
    command = 'SELECT phase,id FROM boss_list'
    cursor.execute(command)
    data = cursor.fetchall()
    for i in data:
        if phase == i[0] and boss_id == i[1]:
            return True
    return False


def check_member_exist(target_id: int):
    command = 'SELECT qq FROM member_list'
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
    c = "SELECT * FROM member_list WHERE qq=%d" % qq
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
    c = "SELECT * FROM member_list WHERE qq=%d" % qq
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
    command = "DELETE FROM 'pcr'.'member_list' WHERE 'qq'=%d" % qq
    cursor.execute(command)
    connection.commit()


# Add a boss into database
def add_boss(phase: str, boss_id: str, health: str):
    phase = int(phase)
    boss_id = int(boss_id)
    health = int(health)
    # Check if input is valid
    if not 1 <= boss_id <= 5:
        raise DataProcessError('boss序号错误')
    if phase < 1:
        raise DataProcessError('阶段序号错误')

    # Check if boss exists
    if check_boss_exist(phase, boss_id):
        raise DataProcessError('boss已存在')

    # Add boss info to table boss_list
    command = 'INSERT INTO boss_list(phase, id, health) VALUES (%d, %d, %d)' % (phase, boss_id, health)
    cursor.execute(command)
    connection.commit()

    # Create a column for boss in table trial_damage
    for i in range(1, 4):
        boss_name = generate_boss_name(phase=phase, boss_id=boss_id) + '_t' + str(i)
        command = 'ALTER TABLE trial_damage ADD %s INT NOT NULL DEFAULT 0' % boss_name
        cursor.execute(command)
    connection.commit()
    return


# Remove a boss into database
def remove_boss(phase: str, boss_id: str):
    phase = int(phase)
    boss_id = int(boss_id)

    # Delete the boss info table boss_list
    command = 'DELETE FROM boss_list WHERE phase=%d AND id=%d' % (phase, boss_id)
    cursor.execute(command)
    connection.commit()

    # Delete related columns in all tables
    cursor.execute('SHOW TABLES')
    table_list = cursor.fetchall()
    for i in range(1, 4):
        boss_name = generate_boss_name(phase=phase, boss_id=boss_id) + '_t' + str(i)
        for j in range(0, len(table_list)):
            # noinspection PyBroadException
            try:
                command = 'ALTER TABLE pcr.%s DROP %s' % (table_list[j][0], boss_name)
                cursor.execute(command)
            except:
                continue
    connection.commit()
    return


def input_data(target_id: int, phase: str, boss_id: str, team_id: str, damage: str, mode: str):
    # Convert type
    phase = int(phase)
    boss_id = int(boss_id)
    team_id = int(team_id)
    damage = int(damage)
    # Member existence check
    if not check_member_exist(target_id):
        raise DataProcessError('请先使用 --r [玩家用户名] [玩家id]登记，玩家id可在游戏的主菜单-简介，登记时请去掉空格')

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
    if mode == 'trial':
        database_name = 'trial_damage'
    elif mode == 'actual':
        command = 'SELECT value FROM pcr.config WHERE key_name="day"'
        cursor.execute(command)
        day = cursor.fetchall()[0][0]
        database_name = 'actual_damage_d' + day
    else:
        raise DataProcessError('Unknown damage mode')

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


def display_damage(target: int) -> str:
    # Connect to database
    # connection, cursor = connect_database()

    # Fetch all tables
    command = 'DESC trial_damage'
    cursor.execute(command)
    col_list = cursor.fetchall()

    res = str(target) + ':\n'
    command = 'SELECT * FROM trial_damage WHERE qq=%d' % target
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
    command = "UPDATE config SET value=%d WHERE key_name='day'" % val
    cursor.execute(command)
    connection.commit()
    return


def set_phase(guild: str, val: str):
    # convert type
    try:
        val = int(val)
    except ValueError:
        raise DataProcessError('格式错误，请确保参数是数字')
    command = f"UPDATE config SET value={val} WHERE key_name='{guild}_phase'"
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


cursor, connection = connect_database()
# connection, cursor = connect_database()
# command = 'desc actual_damage_d1'
# cursor.execute(command)
# data = cursor.fetchall()
# print(data)
# try:
#     add_boss(1, 3, 2000)
#     print('finish')
# except DataProcessError as err:
#     print(err.msg)
