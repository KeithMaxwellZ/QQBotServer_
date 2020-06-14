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


# Check if the sender is mod
def check_mod(target: int) -> bool:
    command = f"SELECT roll FROM pcr.member_list WHERE qq={target}"
    cursor.execute(command)
    res = cursor.fetchall()
    return res[0][0] == 'mod'


# Locate the QQ in the string
def find_qq(raw: str) -> str:
    if raw.isdigit():
        return int(raw)
    return int(raw[11:len(raw)])


# Debug only, send a private message to specific user
def send_private_message(user_id: int, message: str):
    data = {
        'user_id': user_id,
        'message': message,
        'auto_escape': False
    }

    api_url = 'http://127.0.0.1:5700/send_private_msg'

    r = requests.post(api_url, data=data)


# debug only, send message to specific group
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


def generate_char_list_file():
    with open('character_list.json', 'w') as f:
        SSR = ["真琴", "真步", "静流", "杏奈", "初音", "咲恋", "伊绪", "吉塔", "莫妮卡", "妮侬", "望", "秋乃", "璃乃"]
        SR = ["香织", "美美", "绫音", "铃", "惠理子", "忍", "真阳", "栞",
              "千歌", "空花", "珠希", "美冬", "深月", "茜里", "宫子", "雪", "玲奈"]
        R = ["日和莉", "优衣", "怜", "未奏希", "胡桃", "依里", "铃莓",
             "由加莉", "碧", "美咲", "莉玛", "佩可莉姆", "可可萝", "凯露"]
        res = {"SSR": SSR, "SR": SR, "R": R}
        json.dump(res, f)
    return

cursor, connection = connect_database()


