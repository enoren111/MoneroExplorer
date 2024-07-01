'''

'''
from flask import url_for
from es3 import get_item_by_id_from_es
from utils import t2ts,judge_node_online,get_dict_key_value

import os
import time
import json

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
'''
from data.sample import get_local_data
from data.local_data_dealer import json_dealer

json_dealer.write("D:\\Develop\\flask\\darkbee\\darkbee\\static\\data\\sample", "eth_transactions_sample.json",
                  json.dumps(es_results))
'''

class json_dealer():
    @staticmethod
    def read(path,file):
        return json.loads(open(os.path.join(path, file)).read())


    @staticmethod
    def write(path,file,data):
        # jsonData = json.dumps({"key":"value"})
        fileObject = open(os.path.join(path, file), 'w')
        # fileObject = open(file, 'w')
        fileObject.write(data)
        fileObject.close()

def read_from_txt(path, filename):
    # print(url_for('static'))
    data_path = os.path.join(path, filename)
    # data_path = url_for('static',filename='data/kbuckets.txt')
    lines = open(data_path, 'r', encoding='utf-8').read().split('\n')
    split_lines = []
    for line in lines:
        split_lines.append(line.split(' '))
    # print(split_lines)
    return split_lines


def get_node_kbuckets_data2(nodeid):   # online
    # nodeid = 'ffee0c8a8b67310e7d2cfd16f21b33d61d4d631dc3de5350d1950cead19620b13dc2cad2876044e65f6425b904e7d06665e3d7baca5a7cbf66e1d284987d65a7'
    # 数据已被删除
    result = get_item_by_id_from_es('node', nodeid, 'ethnodes')
    try:
        kbuckets_data = result['_source']['nodeBuckets']['nodes']
        k_total = len(kbuckets_data)

        result = []
        rnum = 17  # 行数
        cnum = 16  # 列数
        for idx in range(rnum):
            result.append({"buckets": []})
        # cid = 0~15
        for item in kbuckets_data:
            rid = item['bucket']

            '''
            try:
                lastReach = get_item_by_id_from_es('node', item['nodeID'], 'ethnodes')['_source']['nodeStatus']['lastReach']
            except:
                lastReach = None
            if lastReach:
                lastReachTs = t2ts(lastReach.replace('T', ' '))
                item['online'] = judge_node_online(lastReachTs)  
            else:
                item['online'] = '0'
            '''
            node = get_item_by_id_from_es('node', item['nodeID'], 'ethnodes')['_source']
            if get_dict_key_value(node,['nodeStatus','lastReach'])!='':
                item['online'] = 'g'
            elif get_dict_key_value(node,['nodeStatus','lastListen'])!='':
                item['online'] = 'y'
            else:
                item['online'] = 'r'


            result[int(rid)]['buckets'].append(item)  # 可设置在线在前，离线在后
        # print(kbuckets_data)

        # k桶数据格式转换
        for idx_i, item_i in enumerate(result):
            for idx_j, item_j in enumerate(item_i['buckets']):
                prop_name = 'c' + str(idx_j)
                item_i[prop_name] = item_j
            item_i['rname'] = str(idx_i) + '(' + str(len(item_i['buckets'])) + ')'
            del item_i['buckets']

        # 填空
        call = []
        for idx in range(cnum):
            call.append('c' + str(idx))

        for item in result:
            diff_set = set(call) - set(item.keys())
            for item2 in diff_set:
                item[item2] = 'null'
    except:
        result = {}

    return result


def get_node_kbuckets_data():   # offline
    rnum = 17
    cnum = 16
    # path = basedir + '\\static\\data'  # linux 报错
    path = basedir + '/static/data'
    data_list = read_from_txt(path, 'kbuckets.txt')

    result = []
    for idx in range(rnum):
        result.append({})
    for item in data_list:
        rid = item[0].split('_')[0]
        cid = item[0].split('_')[1]
        cname = 'c' + cid
        result[int(rid)][cname] = {"online": 'r'}
        # result[int(rid)][cname] = {"port": item[3]}

    # 行首
    for idx in range(rnum):
        nums = len(result[idx])
        result[idx]['rname'] = str(idx) + '(' + str(nums) + ')'

    # 填空
    call = []
    for idx in range(cnum):
        call.append('c' + str(idx))
    for item in result:
        diff_set = set(call) - set(item.keys())
        for item2 in diff_set:
            item[item2] = 'null'


    return result

# get_node_kbuckets_data2()
