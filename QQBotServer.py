from flask import Flask, request, make_response, jsonify
import flask_cors

from pymysql.err import InternalError

from data_processing_db import *
from data_fetching_db import *
from util_functions import send_group_message, send_private_message, find_qq, check_mod, lottery, divination

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
    command_list = {'lottery_ten': '--十连',
                    'lottery_one': '--单抽',
                    'register': '--登记信息 玩家名 玩家id',
                    'update': '--更新信息 玩家名 玩家id',
                    'display': '--显示模拟战伤害',
                    'add_actual': '--出刀 伤害',
                    'last': '--尾刀',
                    'add_trial': '--添加模拟战数据 周目 boss序号 第几刀(队伍序号) 伤害',
                    'divination': '--抽签'}

    command = raw_data['raw_message']
    proc = str.split(command, ' ')
    if not proc[0][0:2] == '--':
        return
    # if notification(command):
    #     s = '出完刀后不要把伤害忘记录入到bot里，命令 --添加实战数据 boss序号 第几刀（队伍序号） 伤害'
    #     send_group_message(raw_data['group_id'], s)
    #     return
    else:
        if proc[0] == '--h' or proc[0] == '--帮助':
            s = "现有命令：\n" \
                f"{command_list['lottery_ten']}  (十连，概率为白金池概率，有保底)\n" \
                f"{command_list['lottery_one']}  （单抽，也是白金池概率）\n" \
                f"{command_list['divination']}  （抽签）\n" \
                f"{command_list['add_trial']}  \n" \
                "（输入伤害 举例：--添加模拟战数据 2 1 1 1000 则会为二周目一王输入伤害为1000的第一刀模拟）\n" \
                f"{command_list['add_actual']}  \n" \
                "（输入伤害 举例：--出刀 100000 则会记录100000伤害的一刀）\n" \
                f"{command_list['last']} \n" \
                f"(输入尾刀，伤害会自动记录为boss当前剩余血量)\n" \
                f"{command_list['register']}  （登记用户信息，游戏内id可在主菜单页面中的简介页看到，请不要带空格）\n" \
                f"{command_list['update']}  （更新用户信息）\n" \
                "详细的出刀/伤害信息可以在 http://fredric-mix.com/ 查询\n"
            # "--queue [qq] [boss序号] [第几刀（队伍序号）] （加入出刀队列）\n" \
            # "--finish [第几刀（队伍序号）] [伤害] （完成出刀）\n" \
            # "--la （显示排刀队列） \n"
            send_group_message(raw_data['group_id'], s)
            return
        elif proc[0] == '--test':
            send_group_message(raw_data['group_id'], 'success')
            return
        elif proc[0] == '--十连':
            send_group_message(raw_data['group_id'], lottery('ten'))
            return
        elif proc[0] == '--单抽':
            send_group_message(raw_data['group_id'], lottery('single'))
            return
        elif proc[0] == '--抽签':
            send_group_message(raw_data['group_id'], divination(raw_data['sender']['user_id']))
            return
        if temp_d['develop']:
            send_group_message(raw_data['group_id'], '功能维护中')
            return
        elif proc[0] == '--r' or proc[0] == '--登记信息':  # --r [user_name] [user_id] [guild]
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
                send_group_message(raw_data['group_id'], f"参数错误，正确格式为 {command_list['register']}")
                return
            if register_user(target, user_name, user_id, guild):
                send_group_message(raw_data['group_id'], '登记完成')
            else:
                send_group_message(raw_data['group_id'], f"已存在，请使用 {command_list['update']} 进行更新")
            return
        elif proc[0] == '--u' or proc[0] == '--更新信息':  # --u [user_name] [user_id]
            if len(proc) == 3:
                target = raw_data['sender']['user_id']
                user_name = proc[1]
                user_id = proc[2]
            elif len(proc) == 4:
                target = find_qq(proc[1])
                user_name = proc[2]
                user_id = proc[3]
            else:
                send_group_message(raw_data['group_id'], f"参数错误，正确格式为 {command_list['update']} 玩家名 玩家id")
                return
            if update_user(target, user_name, user_id):
                send_group_message(raw_data['group_id'], '更新完成')
            else:
                send_group_message(raw_data['group_id'], f"信息不存在，请使用 {command_list['register']} 登记")
            return

        if not check_member_exist(raw_data['sender']['user_id']):
            send_group_message(raw_data['group_id'],
                               f"请先使用 {command_list['register']} 进行登记, 输入 --帮助 查看命令详情")
            return

        if proc[0] == '--addtrial' or proc[0] == '--添加模拟战数据':  # --addtrial [phase] [boss_id] [team_id] [damage]
            if len(proc) == 5:
                target = raw_data['sender']['user_id']
                phase = proc[1]
                boss_id = proc[2]
                team_id = proc[3]
                damage = proc[4]
            elif len(proc) == 6:
                target = find_qq(proc[1])
                phase = proc[2]
                boss_id = proc[3]
                team_id = proc[4]
                damage = proc[5]
            else:
                send_group_message(raw_data['group_id'],
                                   f"参数错误，正确格式为 {command_list['add_trial']} 伤害")
                return
            try:
                add_trial_damage(target, phase, boss_id, team_id, damage)
                send_group_message(raw_data['group_id'], '已录入')
            except DataProcessError as dpe:
                send_group_message(raw_data['group_id'], dpe.msg)
            return
        elif proc[0] == '--出刀':
            if len(proc) == 2:
                target = raw_data['sender']['user_id']
                damage = proc[1]
            elif len(proc) == 3:
                target = find_qq(proc[1])
                damage = proc[2]
            else:
                st = "参数数量错误"
                send_group_message(raw_data['group_id'], st)
                return
            try:
                add_boss_damage(target, damage)
                send_group_message(raw_data['group_id'], '已录入')
            except DataProcessError as dpe:
                send_group_message(raw_data['group_id'], dpe.msg)
            return
        elif proc[0] == '--尾刀':
            target = raw_data['sender']['user_id']
            last(target)
            try:
                last(target)
                send_group_message(raw_data['group_id'], '已录入')
            except DataProcessError as dpe:
                send_group_message(raw_data['group_id'], dpe.msg)
            return
        elif proc[0] == '--d' or proc[0] == '--显示模拟战伤害':
            if len(proc) == 1:
                st = display_damage(raw_data['sender']['user_id'])
            elif len(proc) == 2:
                st = display_damage(int(find_qq(proc[1])))
            else:
                st = "参数数量错误"
            send_group_message(raw_data['group_id'], st)
            return
        elif check_mod(raw_data['sender']['user_id']):
            if proc[0] == '--setday':
                if not raw_data['sender']['user_id'] in modList:
                    return
                if len(proc) == 2:
                    set_day(proc[1])
                    send_group_message(raw_data['group_id'], '日期已变更')
                else:
                    send_group_message(raw_data['group_id'], '参数数量错误，应为--setday 日期')
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
    if request.method == 'POST':
        a = request.get_data()
        dict1 = json.loads(a)
        req = dict1['request']
        guild = dict1['guild']
        if req == 'boss':
            boss_id = dict1['boss_id']
            mode = dict1['mode']
            arg = dict1['arg']
            try:
                res = fetch_boss(boss_id, mode, arg, guild)
            except InternalError:
                res = {}
        elif req == 'member_list':
            res = fetch_member(guild)

        response = make_response(jsonify(json.dumps(res)))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
        return response
    return ''


if __name__ == '__main__':
    modList = [2034845390, 1208354709]
    groupList = [966252547, 852735288, 1107794448, 851613122]
    with open('config.json', 'r') as f:
        temp_d = json.load(f)
    svr.run(host=temp_d['server_address'], port=9961)
