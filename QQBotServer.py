from flask import Flask, request, make_response, jsonify
import flask_cors

from pymysql.err import InternalError

import json

from data_process_db import *
from data_fetching_db import *
from util_functions import send_group_message, send_private_message, find_qq

svr = Flask(__name__)
svr.config['JSON_AS_ASCII'] = False
flask_cors.CORS(svr, resources=r'/*')


def notification(msg: str) -> bool:
    key = ['出刀', '出完刀']
    for i in key:
        if not msg.find(i) == -1:
            return True
    return False


def process(raw_data: dict):
    command = raw_data['raw_message']
    proc = str.split(command, ' ')
    if not proc[0][0:2] == '--':
        return
    if notification(command):
        s = '出完刀后不要把伤害忘记录入到bot里，命令 --addactual [boss序号] [第几刀（队伍序号）] [伤害]'
        send_group_message(raw_data['group_id'], s)
        return
    else:
        if proc[0] == '--h':
            s = "现有命令：\n" \
                "--addtrial boss序号 第几刀(队伍序号) 伤害  " \
                "（输入伤害 举例：--addtrial 1 1 1000 则会为一王输入伤害为1000的第一刀模拟）\n" \
                "--addactual boss序号 第几刀(队伍序号) 伤害  " \
                "（输入伤害 举例：--addactual 2 3 1000 则会为二王输入伤害为1000的第三刀实际伤害）\n" \
                "--d （查看自己当前的伤害）\n" \
                "--r 玩家名 玩家id  （登记用户信息，游戏内id可在主菜单页面中的简介页看到，请不要带空格）\n" \
                "--u 玩家名 玩家id  （更新用户信息）\n" \
                "详细的出刀/伤害信息可以在 http://fredric-mix.com/ 查询\n" \
            # "--queue [qq] [boss序号] [第几刀（队伍序号）] （加入出刀队列）\n" \
            # "--finish [第几刀（队伍序号）] [伤害] （完成出刀）\n" \
            # "--la （显示排刀队列） \n"
            send_group_message(raw_data['group_id'], s)
            return
        if proc[0] == '--test':
            send_group_message(raw_data['group_id'], 'success')
            return
        elif proc[0] == '--r':  # --r [user_name] [user_id] [guild]
            if len(proc) == 4:
                target = raw_data['sender']['user_id']
                user_name = proc[1]
                user_id = proc[2]
                guild = proc[3]
            elif len(proc) == 5:
                target = find_qq(proc[1])
                user_name = proc[2]
                user_id = proc[3]
                guild = proc[4]
            else:
                send_group_message(raw_data['group_id'], '参数错误，正确格式为 --r [玩家名] [玩家id]')
                return
            if register_user(target, user_name, user_id, guild):
                send_group_message(raw_data['group_id'], '登记完成')
            else:
                send_group_message(raw_data['group_id'], '已存在，请使用--u更新')
            return
        elif proc[0] == '--u':  # --u [user_name] [user_id]
            if len(proc) == 3:
                target = raw_data['sender']['user_id']
                user_name = proc[1]
                user_id = proc[2]
            elif len(proc) == 4:
                target = find_qq(proc[1])
                user_name = proc[2]
                user_id = proc[3]
            else:
                send_group_message(raw_data['group_id'], '参数错误，正确格式为 --u [玩家名] [玩家id]')
                return
            if update_user(target, user_name, user_id):
                send_group_message(raw_data['group_id'], '更新完成')
            else:
                send_group_message(raw_data['group_id'], '信息不存在，请使用--r登记')
            return

        if not check_member_exist(raw_data['sender']['user_id']):
            send_group_message(raw_data['group_id'], '请先使用--r登记信息, 输入--h查看命令详情')
            return
        if proc[0] == '--addtrial':  # --addtrial ([phase]) [boss_id] [team_id] [damage]
            if len(proc) == 4:
                target = raw_data['sender']['user_id']
                phase = '1'
                boss_id = proc[1]
                team_id = proc[2]
                damage = proc[3]
                mode = 'trial'
            elif len(proc) == 5:
                target = find_qq(proc[1])
                phase = '1'
                boss_id = proc[2]
                team_id = proc[3]
                damage = proc[4]
                mode = 'trial'
            else:
                send_group_message(raw_data['group_id'], '参数错误，正确格式为 -addtrial [boss序号] [第几刀（队伍序号）] [伤害]')
                return
            try:
                input_data(target, phase, boss_id, team_id, damage, mode)
                send_group_message(raw_data['group_id'], '已录入')
            except DataProcessError as dpe:
                send_group_message(raw_data['group_id'], dpe.msg)
            return
        if proc[0] == '--addactual':  # --addactual ([phase]) [boss_id] [team_id] [damage]
            if len(proc) == 4:
                target = raw_data['sender']['user_id']
                phase = '1'
                boss_id = proc[1]
                team_id = proc[2]
                damage = proc[3]
                mode = 'actual'
            elif len(proc) == 5:
                target = find_qq(proc[1])
                phase = '1'
                boss_id = proc[2]
                team_id = proc[3]
                damage = proc[4]
                mode = 'actual'
            else:
                send_group_message(raw_data['group_id'], '参数错误，正确格式为 -addtrial [boss序号] [第几刀（队伍序号）] [伤害]')
                return
            try:
                input_data(target, phase, boss_id, team_id, damage, mode)
                send_group_message(raw_data['group_id'], '已录入')
            except DataProcessError as dpe:
                send_group_message(raw_data['group_id'], dpe.msg)
            return
        elif proc[0] == '--d':
            if len(proc) == 1:
                st = display_damage(raw_data['sender']['user_id'])
            elif len(proc) == 2:
                st = display_damage(int(find_qq(proc[1])))
            else:
                st = "参数数量错误"
            send_group_message(raw_data['group_id'], st)
            return
        elif proc[0] == '--addboss':  # --addboss [phase] [boss_id] [health]
            if not len(proc) == 3:
                send_group_message(raw_data['group_id'], '参数错误，正确格式为 -addboss [阶段] [boss序号]')
                return
            phase = proc[1]
            boss_id = proc[2]
            health = '1'
            try:
                add_boss(phase, boss_id, health)
                send_group_message(raw_data['group_id'], '已登记阶段%s的%s号boss' % (phase, boss_id))
            except DataProcessError as dpe:
                send_group_message(raw_data['group_id'], dpe.msg)
            return
        elif proc[0] == '--removeboss':  # --removeboss [phase] [boss_id]
            if not len(proc) == 3:
                send_group_message(raw_data['group_id'], '参数错误，正确格式为 -removeboss [阶段] [boss序号]')
            phase = proc[1]
            boss_id = proc[2]
            try:
                remove_boss(phase, boss_id)
                send_group_message(raw_data['group_id'], '已删除阶段%s的%s号boss' % (phase, boss_id))
            except DataProcessError as dpe:
                send_group_message(raw_data['group_id'], dpe.msg)
            return
        elif proc[0] == '--setday':
            if not raw_data['sender']['user_id'] in modList:
                return
            if len(proc) == 2:
                set_day(proc[1])
                send_group_message(raw_data['group_id'], '日期已变更')
            else:
                send_group_message(raw_data['group_id'], '参数数量错误，应为--setday [日期]')
        elif proc[0] == '--setmod':
            if raw_data['sender']['user_id'] in modList:
                set_mod(proc[1])
                send_group_message(raw_data['group_id'], '已设置管理权限')
        # elif proc[0] == '--queue':
        #     add_to_queue(data, proc)
        #     return
        # elif proc[0] == '--finish':
        #     finish_damage(data, proc)
        #     return
        # elif proc[0] == '--next':
        #     next_pl(data)
        #     return
        # elif proc[0] == '--la':
        #     list_all(data)
        #     return
        else:
            send_group_message(raw_data['group_id'], '未知命令，请输入--h查看帮助')
            return


@svr.route('/api/message', methods=['POST'])
def message_received():
    data = request.get_data().decode('utf-8')
    data = json.loads(data)
    print(data['raw_message'])
    if data['message_type'] == 'group':
        if not data['group_id'] in groupList:
            print('Unknown Group')
            return ""
        process(data)
        return ""
    elif data['message_type'] == 'private':
        if not data['sender']['user_id'] == 2034845390:
            return ""
        send_private_message(data['sender']['user_id'], 'received')
        return ""
    return ""


@svr.route('/request_info', methods=['POST'])
def get_info():
    print("received")
    if request.method == 'POST':
        a = request.get_data()
        dict1 = json.loads(a)

        req = dict1['request']
        if req == 'boss':
            boss_id = dict1['boss_id']
            mode = dict1['mode']
            arg = dict1['arg']
            try:
                res = fetch_boss(boss_id, mode, arg)
            except InternalError:
                res = {}
        elif req == 'member_list':
            res = fetch_member()

        print(res)
        response = make_response(jsonify(json.dumps(res)))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
        return response
    return ''


if __name__ == '__main__':
    modList = [2034845390, 1208354709]
    groupList = [966252547, 852735288]
    with open('config.json', 'r') as f:
        temp_d = json.load(f)
    svr.run(host=temp_d['server_address'], port=9961)

#
# docker run -ti --rm --name cqhttp-test \
# 	     -v /usr/share/qcool/test:/home/user/coolq \
#              -p 9000:9000 \
#              -p 5700:5700 \
#              -e COOLQ_ACCOUNT=2797339190 \
#              -e CQHTTP_POST_URL=http://host.docker.internal:9961/  \
#              -e CQHTTP_SERVE_DATA_FILES=yes \
# 	     -e VNC_PASSWD=20001115 \
# 	     richardchien/cqhttp:latest
