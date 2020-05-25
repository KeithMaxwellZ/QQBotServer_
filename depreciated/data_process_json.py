from flask import Flask, request
import json
import requests
import csv
import os
from util_functions import send_private_message, send_group_message


# --r [game_user_name] [game_id_no_space]
def register_user(report_group: int, target: int, game_name: str, game_id: str):
    fp = open('../memberInfo.json', 'r')
    dt = json.load(fp)
    fp.close()
    if not str(target) in dict.keys(dt):
        dt[str(target)] = ['', game_name, game_id]
        with open('../memberInfo.json', 'w') as f:
            json.dump(dt, f)
        send_group_message(report_group, '已登记')
    else:
        send_group_message(report_group, '用户已存在，请使用--u更新信息')


# --u [game_user_name] [game_id_no_space]
def update_user(report_group: int, target: int, game_name: str, game_id: str):
    fp = open('../memberInfo.json', 'r')
    dt = json.load(fp)
    fp.close()
    if str(target) in dict.keys(dt):
        dt[str(target)] = ['', game_name, game_id]
        send_group_message(report_group, '已更新')
    else:
        send_group_message(report_group, '用户不存在，请使用--r登记信息')


# --addtrial/addactual [boss_id] [team_id] [damage_value]
def input_data(data: dict, target: int, damage: str, team: str, boss_id: str, mode: str):
    if not str.isdigit(damage) or int(damage) <= 0:
        send_group_message(data['group_id'], '伤害数值错误')
        return
    src = 'data/boss' + str(boss_id) + '/'
    if not os.path.isdir(src):
        send_group_message(data['group_id'], 'boss序号错误')
        return
    file_name = src + str(target) + '.json'
    print(os.path.isfile('/' + file_name))
    if not os.path.isfile(file_name):
        open(file_name, 'w')
        damage = {'trial': [-1, -1, -1], 'actual': [-1, -1, -1]}
    else:
        with open(file_name, 'r') as f:
            damage = json.load(f)
    if 1 <= int(team) <= 3:
        damage[mode][int(team) - 1] = int(damage)
        fp = open(file_name, 'w')
        json.dump(damage, fp)
        fp.close()
        send_group_message(data['group_id'], '已录入')
    else:
        send_group_message(data['group_id'], '队伍序号错误')
    return


def display_damage(data: dict, proc: list):
    if not len(proc) == 1:
        send_group_message(data['group_id'], '参数数量错误')
        print('Invalid Command')
        return
    fp = open('../memberInfo.json', 'r')
    ml = json.load(fp)
    fp.close()
    s = str(data['sender']['user_id']) + ' ' + ml[str(data['sender']['user_id'])][1] + ": \n"
    src = 'data/'
    boss_list = os.listdir(src)

    for i in boss_list:
        file_name = src + str(i) + '/' + str(data['sender']['user_id']) + '.json'
        print(file_name)
        if os.path.isfile(file_name):
            with open(file_name, 'r') as f:
                temp = json.load(f)
                s += str(i) + ': ' + str(temp['trial']) + '\n'

    send_group_message(data['group_id'], s)


def add_to_queue(data: dict, proc: list):  # --queue [qq] [boss_id] [team_id]
    if not len(proc) == 4:
        send_group_message(data['group_id'], '参数数量错误')
        print('Invalid Command')
        return
    if not 1 <= int(proc[3]) <= 3:
        send_group_message(data['group_id'], '队伍序号错误')
        print('Invalid Command')
        return
    with open('../memberInfo.json', 'r') as f:
        member_list = json.load(f)
    if os.path.isfile('data/boss' + proc[2] + '/' + proc[1] + '.json'):
        with open('data/boss' + proc[2] + '/' + proc[1] + '.json', 'r') as f:
            damage = json.load(f)
    else:
        send_group_message(data['group_id'], '没有模拟战数据！')
    if proc[1] in member_list:
        with open('queue.json', 'r') as f:
            queue = json.load(f)['a']
        if [str(proc[1]), str(proc[2]), str(proc[3])] in queue:
            send_group_message(data['group_id'], member_list[str(proc[1])][1] + '已存在！')
            return
        elif not damage['actual'][int(proc[3]) - 1] == -1:
            send_group_message(data['group_id'], member_list[str(proc[1])][1] + '第' + proc[3] + '刀已出刀！')
            return
        queue.append([str(proc[1]), str(proc[2]), str(proc[3])])
        with open('queue.json', 'w') as f:
            json.dump({"a": queue}, f)
        send_group_message(data['group_id'], member_list[str(proc[1])][1] + '已加入队列')
        return
    else:
        send_group_message(data['group_id'], '目标成员不存在')


def check_exist(id: str, queue: list):
    for i in queue:
        if i[0] == id:
            return True
    return False


def finish_damage(data: dict, proc: list):  # --finish [team_id] [damage]
    with open('queue.json', 'r') as f:
        queue = json.load(f)['a']
    if not check_exist(str(data['sender']['user_id']), queue):
        send_group_message(data['group_id'], '不在队列中，请联系管理')
        print('Invalid Command')
        return
    if not len(proc) == 3:
        send_group_message(data['group_id'], '参数数量错误')
        print('Invalid Command')
        return
    if not 1 <= int(proc[1]) <= 3:
        send_group_message(data['group_id'], '队伍序号错误')
        print('Invalid Command')
        return
    i = queue[0]
    file_name = 'data/boss' + i[1] + '/' + i[0] + '.json'
    if not os.path.isfile(file_name):
        send_group_message(data['group_id'], '模拟战数据不存在')
    with open(file_name, 'r') as f:
        damage = json.load(f)
        damage['actual'][int(proc[1]) - 1] = int(proc[2])
        difference = int(damage['actual'][int(proc[1]) - 1]) - int(damage['trial'][int(proc[1]) - 1])
    with open(file_name, 'w') as f:
        json.dump(damage, f)
    queue.pop(0)
    with open('queue.json', 'w') as f:
        json.dump({"a": queue}, f)
    member_list = json.load(open('../memberInfo.json', 'r'))
    send_group_message(data['group_id'], str(i[0]) + ',' + member_list[str(i[0])][1] +
                       '第' + i[1] + '队已出刀，造成' + str(proc[1]) + '伤害, 与模拟战伤害差距为' + str(difference))


def next_pl(data:dict):
    with open('../memberInfo.json', 'r') as f:
        member_list = json.load(f)
    with open('queue.json', 'r') as f:
        queue = json.load(f)['a']
        i = queue[0]
    send_group_message(data['group_id'], '下一位：' + str(i[0]) + ','
                       + member_list[str(i[0])][1] + ',第' + str(i[2]) + '刀')


def list_all(data: dict):
    with open('../memberInfo.json', 'r') as f:
        member_list = json.load(f)
    with open('queue.json', 'r') as f:
        queue = json.load(f)['a']
    s = ''
    for i in queue:
        s += str(i[0]) + ',' + member_list[str(i[0])][1] + ',第' + str(i[2]) + '刀\n'
    send_group_message(data['group_id'], s)
