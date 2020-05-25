import csv
import json
import os
from data_process_db import register_user, DataProcessError


# Depreciated
def export_csv(file_name: str):
    sr = open(file_name, 'r')
    output = 'output.csv'
    f = open(output, 'w', newline='', encoding='utf-8')
    w = csv.writer(f)
    d = json.load(sr)
    w.writerow(['qq', '一刀', '二刀', '三刀', '群名片'])
    for i in dict.keys(d):
        lst = [str(i)]
        for x in d[i]:
            lst.append(x)
        w.writerow(lst)
    f.close()
    sr.close()


# Depreciated
def clear_actual():
    for i in os.listdir('data'):
        for j in os.listdir('data/'+i):
            with open('data/'+i+'/'+j, 'r') as f:
                data = json.load(f)
            data['actual'] = [-1, -1, -1]
            with open('data/'+i+'/'+j, 'w') as f:
                json.dump(data, f)

