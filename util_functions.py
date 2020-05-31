import requests
import pymysql
import json


# Connect to the database
def connect_database():
    with open('config.json', 'r') as f:
        temp_d = json.load(f)
    connection = pymysql.connect(host=temp_d['database_address'],
                                 port=temp_d['database_port'],
                                 user=temp_d['user'],
                                 passwd=temp_d['password'],
                                 db='pcr')
    cursor = connection.cursor()
    print("Database Connected")
    return cursor, connection


def check_mod(target: int) -> bool:
    command = f"SELECT roll FROM pcr.member_list WHERE qq={target}"
    cursor.execute(command)
    res = cursor.fetchall()
    return res[0][0] == 'mod'


def find_qq(raw: str) -> str:
    if raw.isdigit():
        return int(raw)
    return int(raw[11:len(raw)])


def send_private_message(user_id: int, message: str):
    data = {
        'user_id': user_id,
        'message': message,
        'auto_escape': False
    }

    api_url = 'http://127.0.0.1:5700/send_private_msg'

    r = requests.post(api_url, data=data)


def send_group_message(group_id: int, message: str):
    data = {
        'message_type': 'group',
        'group_id': group_id,
        'message': message,
        'auto_escape': False
    }

    api_url = 'http://127.0.0.1:5700/send_msg'

    r = requests.post(api_url, data=data)
    return r


cursor, connection = connect_database()
