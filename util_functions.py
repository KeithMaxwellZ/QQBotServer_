import requests
import pymysql
import json
import random
from datetime import datetime, timedelta


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
        SSR = ["伊利亚", "镜华", "真琴", "真步", "静流", "杏奈", "初音", "咲恋", "伊绪", "吉塔", "莫妮卡", "妮侬", "望", "秋乃", "璃乃"]
        SR = ["香织", "美美", "绫音", "铃", "惠理子", "忍", "真阳", "栞",
              "千歌", "空花", "珠希", "美冬", "深月", "茜里", "宫子", "雪", "玲奈", "美里"]
        R = ["日和莉", "优衣", "怜", "未奏希", "胡桃", "依里", "铃莓",
             "由加莉", "碧", "美咲", "莉玛", "可可萝", "凯露"]
        res = {"SSR": SSR, "SR": SR, "R": R}
        json.dump(res, f)
    return


def lottery(mode: str):
    res: str
    if mode == "single":
        return draw_one()[0]
    elif mode == "ten":
        res = "以下为稻叶二号机预测的十连结果\n"
        for i in range(0, 9):
            r = draw_one()
            res += r[0]
        res += f'★★☆-{char_list["SR"][random.randrange(0, len(char_list["SR"]))]}\n'
        return res


def draw_one():
    prob = random.randrange(1, 10000)
    if prob < 250:
        return [f'★★★-{char_list["SSR"][random.randrange(0, len(char_list["SSR"]))]}\n', 3]
    elif prob < 2050:
        return [f'★★☆-{char_list["SR"][random.randrange(0, len(char_list["SR"]))]}\n', 2]
    else:
        return [f'★☆☆-{char_list["R"][random.randrange(0, len(char_list["R"]))]}\n', 1]


def divination(qq: int):
    global processed_list
    res = ""

    now = datetime.now() + timedelta(hours=12)

    if not now.day == today.day:
        processed_list = []

    if qq in processed_list:
        res = "今天已经抽过签了，请明天再来"
    else:
        processed_list.append(qq)
        i = random.randrange(0, len(dict.keys(divination_dict)))
        j = random.randrange(0, len(dict.keys(divination_dict)))
        while i == j:
            j = random.randrange(0, len(dict.keys(divination_dict)))

        temp = []
        for x in dict.keys(divination_dict):
            temp.append(x)

        i = temp[i]
        j = temp[j]

        res += "今日运势：\n"
        res += f"宜{i}: {divination_dict[i]['p'][random.randrange(0, len(divination_dict[i]['p']))]}\n" \
               f"忌{j}: {divination_dict[j]['n'][random.randrange(0, len(divination_dict[j]['n']))]}\n\n" \
               f"今日推荐：\n"

        rank = ['SSR', 'SR', 'R']
        k = rank[random.randrange(0, 3)]

        res += f"看板娘：{char_list[k][random.randrange(0, len(char_list[k]))]}\n"

        res += f"赛马：{random.randrange(1,5)}号角色"

    return res


cursor, connection = connect_database()

with open('character_list.json', 'r') as f:
    char_list = json.load(f)

processed_list = []
divination_dict = {'抽卡': {'p': ["十连保底稳定出彩", "单抽就能出货"],
                          'n': ["单抽全银，十连+19", "恰保底恰保底"]},
                   '刷碎片': {'p': ["碎片爆率100%", "碎片+6/+12"],
                           'n': ["碎片呢？我的碎片呢？", "别刷了，不会掉的"]},
                   '刷材料': {'p': ["扫荡一次掉一个"],
                           'n': ["一管体力啥都没有", "去行会找人捐吧"]},
                   '打jjc': {'p': ["刀刀烈火", "拳拳暴击"],
                            'n': ["狗拳又miss了", "你ub打布丁无敌帧上了"]},
                   '打pjjc': {'p': ["阵容全猜对", "赛马，赛tmd"],
                             'n': ["阵容全错", "被对面天克"]},
                   }

today = datetime.now() + timedelta(hours=12)
