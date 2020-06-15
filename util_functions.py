import requests
import pymysql
import json
import random


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


def lottery(mode: str) -> str:
    res: list
    with open('character_list.json', 'r') as f:
        char_list = json.load(f)
    if mode == "single":
        return draw_one(char_list)
    elif mode == "ten":
        res = "以下为稻叶二号机预测的十连结果\n"
        hasSR = False
        for i in range(0, 9):
            r = draw_one(char_list)
            res += r[0]
            if r[1] == 2:
                hasSR = True
        if not hasSR:
            res += f'★★☆-{char_list["SR"][random.randrange(0, len(char_list["SR"]))]}\n'
        else:
            res += draw_one(char_list)[0]
        return res


def draw_one(char_list: list):
    prob = random.randrange(1, 10000)
    if prob < 250:
        return [f'★★★-{char_list["SSR"][random.randrange(0, len(char_list["SSR"]))]}\n', 3]
    elif prob < 2050:
        return [f'★★☆-{char_list["SR"][random.randrange(0, len(char_list["SR"]))]}\n', 2]
    else:
        return [f'★☆☆-{char_list["R"][random.randrange(0, len(char_list["R"]))]}\n', 1]


cursor, connection = connect_database()
