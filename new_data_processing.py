from util_functions import connect_database


class DataProcessError(RuntimeError):
    def __init__(self, msg: str):
        self.msg = msg


# Check if the database is connected and reconnect if necessary
def reconnect():
    try:
        connection.ping()
    except Exception:
        global cursor, connection
        cursor, connection = connection()


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


def add_boss_damage(qq: int, damage: str, phase: str, boss: str)

cursor, connection = connect_database()