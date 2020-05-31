from util_functions import connect_database


def sort(damage_list: list, arg: str):
    if arg == 'expand_all':
        tmp = []
        for i in damage_list:
            command = f"SELECT user_name FROM pcr.member_list WHERE qq={i[0]}"
            cursor.execute(command)
            user_name = cursor.fetchall()[0][0]
            for j in range(1, 4):
                tmp.append([i[0], f"{user_name}_队伍{j}", i[j]])
        tmp = sorted(tmp, key=lambda l: l[2], reverse=True)
        return {'result': tmp}
    elif arg == 'total_max':
        damage_list = sorted(damage_list, key=lambda l: sum(l), reverse=True)
    else:
        pass
    res = {'order': []}
    for i in damage_list:
        command = f"SELECT user_name FROM pcr.member_list WHERE qq={i[0]}"
        cursor.execute(command)
        user_name = cursor.fetchall()[0][0]
        res['order'].append(str(i[0]))
        res[str(i[0])] = [user_name, i[1], i[2], i[3]]
    return res


def fetch_boss(boss_id: str, mode: str, arg: str, guild: str) -> dict:
    col_name = []
    command = f"SELECT * FROM pcr.config WHERE key_name='{guild}_phase' OR key_name='day'"
    cursor.execute(command)
    temp = cursor.fetchall()
    day = temp[0][1]
    if mode == 'trial':
        phase = 1
        database_name = 'trial_damage'
    else:
        phase = temp[1][1]
        database_name = f'actual_damage_d{day}'
    for i in range(1,4):
        col_name.append(f"p{phase}_{boss_id}_t{i}")
    command = f'SELECT qq,{col_name[0]},{col_name[1]},{col_name[2]} FROM pcr.{database_name}'
    cursor.execute(command)
    temp_list = cursor.fetchall()

    command = f'SELECT qq,guild FROM member_list'
    cursor.execute(command)
    m_list = cursor.fetchall()
    member_dict = {}
    for i in m_list:
        member_dict[i[0]] = i[1]
    damage_list = []
    for i in temp_list:
        if str.find(member_dict[i[0]], guild) >= 0:
            damage_list.append(i)
    res = sort(list(damage_list), arg)
    connection.commit()
    return res


def fetch_member(guild: str) -> dict:
    command = "SELECT * FROM pcr.config WHERE key_name='day'"
    cursor.execute(command)
    day = cursor.fetchall()[0][1]
    database_name = f"actual_damage_d{day}"
    command = f'SELECT qq,user_name,guild FROM member_list'
    cursor.execute(command)
    temp_list = cursor.fetchall()
    all_data = []
    for i in temp_list:
        print(i[2] + ' ' + guild + ' ' + str(str.find(i[2], guild)))
        if str.find(i[2], guild) >= 0:
            all_data.append(i)
    t = []
    for i in all_data:
        command = f'SELECT * FROM {database_name} WHERE qq={i[0]}'
        cursor.execute(command)
        damage_list = cursor.fetchall()
        count = -1
        if len(damage_list) == 0:
            count = 0
        else:
            for j in damage_list[0]:
                if j > 0:
                    count += 1
        t.append([i[0], i[1], count])
    t = sorted(t, key=lambda k: k[2], reverse=False)
    res = {'order': []}
    for i in t:
        res['order'].append(i[0])
        res[i[0]] = [i[1], i[2]]
    connection.commit()
    return res


cursor, connection = connect_database()

