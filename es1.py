# -*- coding: utf-8 -*-
import requests
from elasticsearch import Elasticsearch, NotFoundError

import es3

from utils import ts2t, day_stamp, time_quantum, today, judge_tr_endpoint, DateEncoder, get_dict_key_value, \
    visit_mode_check
from flask import current_app
import json
import elasticsearch.helpers
# from mysql_dealer import get_node_detail_info
# import myconfig
import datetime
import time
from bee_var import *
# from app import es
from loguru import logger

# from data.local_data_dealer import json_dealer

# es.tryagain_instance()
# es = es.instance

'''

'''


class es_dealer:

    @staticmethod
    def search():
        pass


# result = es.get(index='eth_block', id='700000', doc_type='eth_block')

# result = es.search(index='eth_block', body={
#     "query": {
#         "match_all": {}
#     },
#     "size": perPage,
#     "from":start,
#     "sort": {"timestamp": {"order": "desc"}}
#
# }, doc_type='eth_block')
# print (json.dumps(result))

# result = es.search(index='ethereum', body={
#   "query": {
#     "match_all": {}
#   }
# }, doc_type='eth_contract')


# result = es.get(index='ethereum', id='0xb41f6b003dcee0d04fcc829bc0656b63bf1abe0d3348cf49ca63e5e19c819f1f', doc_type='eth_transaction')
# print(json.dumps(result))

##### start block #####
def get_block_byid(blockNum):  # despatch 没有费用相关详情 rpby get_block_detail
    result = es.get(index='ethereum_block', id=blockNum, doc_type='ethereum_block')
    if 'uncles' in result['_source']:
        result['_source']['uncles'] = len(result['_source']['uncles'])
        # result['_source']['uncles'] = str(result['_source']['uncles'][0])[2:-2]  # is it a list？
    else:
        result['_source']['uncles'] = 0
    result['_source']['height'] = result['_id']
    return result['_source']


# print (json.dumps(get_block_byid(7285499)))


def search_block(body):
    return es.search(index='eth_block', body=body)
def eth_get_transaction(perpage, start):  # BigDealTranses BlockDetail AllTranses
    body = {
        "query": {
            "match_all": {}
        },
        "size": perpage,
        "from": start,
        "track_total_hits": True,
        "sort": {"time": {"order": "desc"}}  # 性能问题
    }
    es_results = es.search(index='eth_transaction', body=body)
    took = es_results['took']
    total = es_results['hits']['total']
    # logger.info(total)
    result = es_results["hits"]["hits"]
    for item in result:
        item['_source']['trans_type'] = judge_trans_type(item['_source']['to'])  # trans_type
        # item['_source']['trans_fee'] = float(item['_source']['gasPrice']) / (10 ** 18) * (
        #     float(item['_source']['gasUsed']))  # 手续费   # gp*gused
        # item['_source']['trans_fee'] = round(item['_source']['trans_fee'], 8)
        item['_source']['time'] = ts2t(item['_source']['time'])

    return {"took": took, "total": total, "result": result}
def eth_home_show():
    r = requests.get("https://api.blockchair.com/ethereum/stats")
    re = json.loads(r.text)
    result = get_blocks(5,0)
    blocks = result['blocks']
    ans = eth_get_transaction(5, 0)
    total = ans['total']['value']

    latestTransList = ans['result']

    context={
        "blocks":blocks,
        "trans_sum":re['data']['transactions'],
        "marketCap":re['data']['market_cap_usd'],
        "difficulty": re['data']['difficulty']
    }
    return latestTransList,context
def sb_for_block(size=20, start=0, order="desc", time_rang_id=0):  # search body
    logger.info(size)
    logger.info(start)
    if time_rang_id == 4:
        return {
            "query": {
                "match_all": {}
            },
            "size": size,
            "from": start,
            "sort": {"timestamp": {"order": order}},
            "track_total_hits": True
        }
    else:
        start_ts, end_ts = judge_tr_endpoint(time_rang_id)
        return {
            "query": {
                "bool": {
                    "should": [
                        {"range": {"timestamp":
                                       {"gte": start_ts,
                                        "lt": end_ts}}},
                    ]
                }
            },
            "size": size,
            "from": start,
            "sort": {"timestamp": {"order": order}},
            "track_total_hits": True
        }


def get_blocks(size=20, start=0, order="desc", time_rang_id=4, miner=None):  # 按出块时间降序排序  latest blocks
    rv = []
    body = sb_for_block(size, start, order, time_rang_id)
    from es3 import get_block_detail
    result = search_block(body)
    total = result['hits']['total']
    took = result['took']
    targets = result['hits']['hits']
    for item in targets:
        # logger.info(item['_id'])
        cost = get_block_detail(item['_source']['blockNumber'])
        block = item['_source']
        block['cost'] = cost
        block['default'] = 'null'
        block['height'] = item['_source']['blockNumber']
        block['time'] = ts2t(block['timestamp'])
        block['time1'] = datetime.datetime.utcfromtimestamp(block['timestamp'])  # eth_home moment计算已出块时间用
        # block交易笔数
        # block['trans_num'] = get_trans_in_block(block['height'], 0)[0]
        block['trans_num'] = cost['trans_num']
        # print(block['time1'])
        if 'uncles' in block:
            # block['uncles'] = str(block['uncles'][0])[2:-2]  # is it a list？
            block['uncles'] = len(block['uncles'])  # is it a list？
        else:
            block['uncles'] = 0
        rv.append(block)

    return {"total": total, "blocks": rv, "took": took}


# get_blocks(size=1, order="asc")
# get_blocks()

def get_block_total():
    body = {
        "query": {
            "match_all": {}
        },
        "track_total_hits": True
    }

    return es.search(index='eth_block', body=body)['hits']['total']


def judge_height(item):
    try:
        height = item['blockNumber']
    except:
        height = item['_id']
    logger.info(height)
    return height


def trans_ajax(rule, starttime, endtime, minvalue, maxvalue, perpage, start):  ###交易数据区间阈值筛选，根据时间以及交易金额筛选
    from es3 import get_block_detail
    perpage = perpage * 2
    if rule == "":
        rule = "desc"
    if starttime:
        starttime = time.strptime(starttime, '%Y-%m-%d %H:%M:%S')
        starttime = time.mktime(starttime)
    else:
        starttime = 1230998400  ##比特币诞生的时间
    if endtime:
        endtime = time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S'))
    else:
        endtime = time.time()
    if minvalue == "":
        minvalue = 0
    if maxvalue == "":
        maxvalue = 100000
    body = {"query": {
        "bool": {
            "must": [
                {"range": {"time":
                               {"gte": starttime,
                                "lt": endtime}}},
                {
                    "range": {
                        "value": {
                            "gte": minvalue,
                            "lt": maxvalue
                        }
                    }
                }
            ]
        }
    },
        "from": start,
        "size": perpage,
        "sort": {"time": {"order": rule}},
        "track_total_hits": True
    }
    es_results = es.search(index='eth_transaction', body=body)
    took = es_results['took']
    total = es_results['hits']['total']
    # logger.info(total)
    result = es_results["hits"]["hits"]
    for item in result:
        item['_source']['trans_type'] = judge_trans_type(item['_source']['to'])  # trans_type
        try:
            item['_source']['trans_fee'] = float(item['_source']['gasPrice']) / (10 ** 18) * (
            float(item['_source']['gasUsed']))  # 手续费   # gp*gused
        except:
            item['_source']['trans_fee']= 0
        item['_source']['trans_fee'] = round(item['_source']['trans_fee'], 8)
        item['_source']['time'] = ts2t(item['_source']['time'])
    return {"took": took, "total": total, "result": result}


##### end block #####


##### start transactions #####

def get_trans_total():  ##读取交易数量
    body = {
        "query": {
            "match_all": {}
        }
    }

    try:
        if current_app.config['ONLINE_MODE']:
            return es.search(index='ethereum', body=body, doc_type='eth_transaction')['hits']['total']
        else:
            return 500024857
    except:
        return 0


def judge_trans_type(to):
    # 判断to地址，null contract地址 普通地址;也可以用来判断地址类型
    # print(to)
    def foo():
        try:
            es.get(index='eth_contract', id=to, doc_type='_doc')
            return trans_type['1']  # 合约交易
        except NotFoundError:
            return trans_type['0']  # 默认只有20条，所以报错少, 总是在控制台输出get 404错误

    if to != None:  # 不是"null",不是""
        # 方案1
        # result = es.search(index='ethereum', body={
        #     "query": {
        #         "match": {
        #             "_id": to
        #         }
        #     }
        # }, doc_type='eth_contract')
        #
        # if result['hits']['total']==0:
        #     return "普通交易"
        # else:
        #     return "合约交易"
        # 方案2
        return visit_mode_check(foo(), data=trans_type['0'])

    else:
        return trans_type['2']
    # 返回 创建 合约 普通


# print(judge_trans_type("0x6400B5522f8D448C0803e6245436DD1c81dF09ce"))   # 合约交易

def get_trans_in_block(blockNumber, perPage, start=0):  # despatch replaced by get_transes
    result = es.search(index='ethereum', body={
        "query": {
            "match": {
                "blockNumber": blockNumber
            }
        },
        "size": perPage,
        "from": start
    }, doc_type='eth_transaction')
    total = result['hits']['total']
    # targets = result['hits']['hits']
    rv = []
    # print(json.dumps(result))
    for item in result['hits']['hits']:
        # print (json.dumps(item))
        item['_source']['hash'] = item['_id']
        # item['_source']['type'] = item['_type']  # 文档类型而不是交易类型
        item['_source']['time'] = ts2t(item['_source']['time'])
        item['_source']['trans_type'] = judge_trans_type(item['_source']['to'])
        item['_source']['sc'] = 'NaN'  # 手续费
        rv.append(item['_source'])
    # print(json.dumps(rv))
    # print(total)
    return total, rv


# get_trans_in_block(	7285498, 20, 0)

def judge_to_type(t_type):
    if t_type == trans_type['1']:
        return True  # 合约地址
    else:
        return False


def block_search(perpage, start, rule, starttime, endtime):
    from es3 import get_block_detail
    if rule == "":
        rule = "desc"
    if starttime:
        starttime = time.strptime(starttime, '%Y-%m-%d %H:%M:%S')
        starttime = time.mktime(starttime)
    else:
        starttime = 1230998400  ##比特币诞生的时间
    if endtime:
        endtime = time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S'))
    else:
        endtime = time.time()
    body = {"query": {
        "bool": {
            "should": [
                {"range": {"timestamp":
                               {"gte": starttime,
                                "lt": endtime}}},
            ]
        }
    },
        "from": start,
        "size": perpage,
        "sort": {"timestamp": {"order": rule}},
        "track_total_hits": True
    }
    rv = []
    result = search_block(body)
    total = result['hits']['total']
    took = result['took']
    targets = result['hits']['hits']
    for item in targets:
        cost = get_block_detail(item['_id'])
        block = item['_source']
        block['cost'] = cost
        block['default'] = 'null'
        block['height'] = item['_id']
        block['time'] = ts2t(block['timestamp'])
        block['time1'] = datetime.datetime.utcfromtimestamp(block['timestamp'])  # eth_home moment计算已出块时间用
        # block交易笔数
        # block['trans_num'] = get_trans_in_block(block['height'], 0)[0]
        block['trans_num'] = cost['trans_num']
        # print(block['time1'])
        if 'uncles' in block:
            # block['uncles'] = str(block['uncles'][0])[2:-2]  # is it a list？
            block['uncles'] = len(block['uncles'])  # is it a list？
        else:
            block['uncles'] = 0
        rv.append(block)

    return {"total": total, "blocks": rv, "took": took}


def deal_trans_targets(targets):  # deal_trans_item
    rv = []
    value_acc = current_app.config['VALUE_ACC']

    def foo(id):
        try:
            rtxs = es.get(index='eth_transaction_receipt', doc_type='raw', id=id, request_timeout=120)['_source']
        except:
            rtxs = {'gasUsed': 0, 'status': 'null'}
        finally:
            return rtxs

    for item in targets:
        # print(item['_source']['from'])
        item['_source']['time'] = ts2t(item['_source']['time'])  #
        item['_source']['hash'] = item['_id']
        item['_source']['trans_type'] = judge_trans_type(item['_source']['to'])  # trans_type
        item['_source']['to_type'] = judge_to_type(item['_source']['trans_type'])  # to地址类型 合约地址 or 普通地址
        # item['_source']['fee'] = 'NaN'  # 手续费   # gp*gused
        # rtxs = visit_mode_check(foo(item['_id']), data={'gasUsed': 0, 'status': 'null'})
        # item['_source']['gasUsed'] = rtxs['gasUsed']
        # item['_source']['status'] = rtxs['status']
        try:
            item['_source']['trans_fee'] = float(item['_source']['gasPrice']) / (10 ** 18) * (
                float(item['_source']['gasUsed']))  # 手续费   # gp*gused
            item['_source']['trans_fee'] = round(item['_source']['trans_fee'], 8)
        except:
            item['_source']['trans_fee'] = 0
        item['_source']['default'] = 'NaN'  # 确实字段
        item['_source']['value'] = round(item['_source']['value'], value_acc)  # 保留value小数位数
        # logger.info()
        rv.append(item['_source'])
    return rv


def get_all_trans(perPage=20, start=0):  # despatch 返回最近交易列表 ，处理全部交易数据
    result = es.search(index='ethereum', body={
        "query": {
            "match_all": {}
        },
        # "sort": {"time": {"order": "desc"}},  # 不排序，返回的非最新交易
        "from": start,
        "size": perPage,
        "track_total_hits": True

    }, doc_type='eth_transaction')
    total = result['hits']['total']
    # targets = result['hits']['hits']
    # rv = []
    # print(json.dumps(targets))
    rv = deal_trans_targets(result['hits']['hits'])
    return total, rv


def get_latest_trans(perPage=20, start=0):  # 返回最近交易列表，处理最新块内的交易数据
    # 获取最新size区块
    total, blocks_list = get_blocks(size=10000)

    # 查询区块内交易&按transactionIndex降序排列
    body = {
        "query": {
            "terms": {
                "blockNumber": [blocks_list[0]['height'], blocks_list[1]['height']]
            }
        },
        "sort": {"blockNumber": {"order": "desc"}},
        "size": perPage,
        "from": start
    }
    result = es.search(index='ethereum', body=body, doc_type='eth_transaction')
    total = result['hits']['total']
    rv = deal_trans_targets(result['hits']['hits'])
    # print(total)
    return total, rv


# get_latest_trans()


'''
get_transes 过滤用
'''


def sb_for_trans(size=20, start=0, order="desc", time_rang_id=0, blockNum=None):
    if blockNum == None:  # 全部交易
        if time_rang_id == 4:
            return {
                "query": {
                    "match_all": {}
                },
                "size": size,
                "from": start,
                # "sort": {"time": {"order": order}}  # 性能问题
            }
        else:
            start_ts, end_ts = judge_tr_endpoint(time_rang_id)
            return {
                "query": {
                    "bool": {
                        "should": [
                            {"range": {"time":
                                           {"gte": start_ts,
                                            "lt": end_ts}}},
                        ]
                    }
                },
                "size": size,
                "from": start,
                "track_total_hits": True,
                "sort": {"time": {"order": order}}  # 按时间降序排列
            }
    else:  # 区块内交易
        return {
            "query": {
                "match": {
                    "blockNumber": blockNum
                }
            },
            "size": size,
            "track_total_hits": True,
            "sort": {"transactionIndex": {"order": order}},
            "from": start
        }


def get_transes(size=20, start=0, order="desc", time_rang_id=0,
                blockNum=None):  # despatch rpby get_transes_v2/v3   对应于get block , 按时间排序
    body = sb_for_trans(size, start, order, time_rang_id, blockNum)

    def foo():
        return es.search(index='eth_transaction', body=body, doc_type='_doc')

    result = es.search(index='eth_transaction', body=body, doc_type='_doc')
    # logger.info(result)
    total = result['hits']['total']
    # targets = result['hits']['hits']
    # print(json.dumps(targets))
    rv = deal_trans_targets(result['hits']['hits'][0:size])
    return total, rv


# get_transes()

def get_transaction_byhash(hash):  # 获取交易详情，一张表格

    result = es.get(index='eth_transaction', id=hash, doc_type='_doc')
    # result['time'] = ts2t(result['time'])
    # trans_receipt = get_receipt(hash)
    # result['status'] = trans_receipt['status']

    # print(json.dumps(result))
    res = deal_trans_targets([result])
    if len(res) == 1:
        return res[0]
    else:
        return {}


# 生成合约的交易hash 0xd87e878d71ecb7db43849722f979a8840ef0dfb6d897d0f10d2eed35af77b356
# 生成合约交易中from地址 0xdabae13cfB6A9CAe0426baA456e97EE6A888a360
# 普通交易hash 0x5e2bc021b92f72d8569c71d95813600f001fa41522d426adf764e38aa9453bd5

# get_transaction_byhash('0xd87e878d71ecb7db43849722f979a8840ef0dfb6d897d0f10d2eed35af77b356')
# get_latest_trans(start=40039240)
# total,rv = get_latest_trans()
# print(json.dumps(rv))


def trans_info_per_day(ftime1, ftime2=None):  # despatch  手工统计
    start_stamp, end_stamp = day_stamp(ftime1, ftime2)

    res = es.search(index='ethereum', doc_type='eth_transaction',
                    body={
                        "query": {
                            "range": {
                                "time": {
                                    "gte": start_stamp,
                                    "lte": end_stamp
                                }
                            }
                        }
                    })
    # print(json.dumps(res))
    sum_value = 0
    normal_trans = 0
    contract_call = 0
    contract_create = 0

    # bug
    for item in res['hits']['hits']:  # 统计交易额 合约类型数目
        sum_value += item['_source']['value']
        # trans_type = judge_trans_type(item['_source']['to'])
        # if trans_type == '合约交易':
        #     contract_call += 1
        # elif trans_type == '普通交易':
        #     contract_create += 1
        # elif trans_type == '普通交易':
        #     normal_trans += 1
        # else:
        #     print("fatal error! at trans_info_per_day")

    trans_info = {ftime1: {"num": res['hits']['total'],  # 日交易笔数
                           "value": sum_value,
                           "normal_trans": normal_trans,
                           "contract_call": contract_call,
                           "contract_create": contract_create}}
    # print(res['hits']['total'])

    return trans_info


# trans_info_per_day('2019-03-02')


def scan_trans_info_per_day(ftime1, ftime2=None):  # despatch不好用，卡死
    start_stamp, end_stamp = day_stamp(ftime1, ftime2)
    body = {
        "query": {
            "range": {
                "time": {
                    "gte": start_stamp,
                    "lte": end_stamp
                }
            }
        }
    }

    # print(json.dumps(res))
    scan_resp = elasticsearch.helpers.scan(
        client=es,
        scroll="10m",
        timeout="120m",
        query=body,
        size=1000,
        index='ethereum',
        doc_type='eth_transaction'
    )
    sum_value = 0
    normal_trans = 0
    contract_call = 0
    contract_create = 0
    count = 0
    for item in scan_resp:
        # print(item)
        count += 1
    # bug

    print(count)

    # return trans_info


# scan_trans_info_per_day('2019-03-02')


##### end transactions #####
##### start receipt #####

def qbody_for_receipt():  # query body
    pass


def get_receipt(hash=None):
    if hash != None:  # 查询交易
        try:
            result = es.get(index='eth_transaction_receipt', id=hash, doc_type='raw')
            if result['_source']['status'] == None:
                result['_source']['status'] = 'null'
            return result['_source']
        except NotFoundError:
            return {'status': 'null'}
    else:
        result = es.search(index='eth_transaction_receipt', doc_type='raw',
                           body={
                               "query": {
                                   "match_all": {}
                               }
                           })


##### end transactions #####


##### start node #####

def sb_for_node(perPage=20, start=0):
    return {
        "query": {
            "match_all": {}
        },
        # "sort": {"time": {"order": "desc"}},  # 不排序，返回的非最新交易
        "from": start,
        "size": perPage
    }


def get_nodes(perPage=20, start=0, node_id=None):
    body = sb_for_node(perPage, start, node_id)
    result = es.search(index='ethnodes', body=body, doc_type='node')
    total = result['hits']['total']
    targets = result['hits']['hits']
    rl = []
    # print(json.dumps(result))
    for item in targets:
        item['_source']['id'] = item['_id']
        rl.append(item['_source'])
    return total, rl


# get_nodes()

def get_node(nodeid):
    def foo():
        return es.get(index='ethnodes', id=nodeid, doc_type='node')

    # print(json.dumps(result))
    result = visit_mode_check(foo, "eth_node_sample.json")
    node_item = deal_node_item(result['_source'])
    return node_item


def search_node(node_ip):
    body = {
        "query": {
            "term": {
                "nodeIP": node_ip
            }
        }
    }
    result = es.search(index='ethnodes', body=body, doc_type='node')
    return result


# nodeId = '00263de54abd8b12832120580672ffc098197fb60dd45f8ae7a29724e1bde88e3198dc8696023a623328871cb891e9a68f9d507cbe6b62a08eba5aece720cdcb'
# print(get_node(nodeId))


def deal_node_item(item):  #

    if get_dict_key_value(item, ['nodeStatus', 'lastListen']) != '':
        item['lastOnline'] = get_dict_key_value(item, ['nodeStatus', 'lastListen'])
    else:
        item['lastOnline'] = get_dict_key_value(item, ['nodeStatus', 'lastReach'])
    item['networkID'] = get_dict_key_value(item, ['networkID'])
    item['bestHash'] = get_dict_key_value(item, ['bestHash'])
    item['height'] = get_node_height(item['networkID'], item['bestHash'])
    item['client'] = get_dict_key_value(item, ['client'])
    item['clientVersion'] = get_dict_key_value(item, ['clientVersion'])
    item['os'] = get_dict_key_value(item, ['os'])
    item['capabilities'] = get_dict_key_value(item, ['capabilities'])
    item['networkID'] = get_dict_key_value(item, ['networkID'])
    item['tDifficulty'] = get_dict_key_value(item, ['tDifficulty'])
    item['bestHash'] = get_dict_key_value(item, ['bestHash'])
    item['genesisHash'] = get_dict_key_value(item, ['genesisHash'])
    item['country'] = get_dict_key_value(item, ['nodeLocation', 'country'])
    item['asnum'] = get_dict_key_value(item, ['nodeLocation', 'asNumber'])

    # item['height'] = 'height'
    # item['country'] = 'country'
    # item['asnum'] = 'asnum'
    # item['default'] = 'null'
    # item['id'] = item['nodeID']
    # item['client'] = 'null'
    # item['clientVersion'] = 'null'
    # item['os'] = 'null'
    # item['nodePort'] = str(item['nodePort'])

    return item


def get_node_height(networkId, besthash):
    # print(besthash)
    # besthash = '0xc6c08e53ab68a53333577cce1a936334721c8c9a4e0517a0caa5cf69358615bd'
    def foo():  # 根据beshhash查询block id==节点高度
        body = {
            "query": {
                "term": {
                    "hash": besthash
                }
            }
        }
        return es.search(index='eth_block', body=body, doc_type='eth_block')

    if networkId == 1 and besthash != '':

        # es_result = es.search(index='ethereum', body=body, doc_type='block')  # 根据beshhash查询block id==节点高度
        es_result = visit_mode_check(foo, data={'hits': {'hits': []}})
        if len(es_result['hits']['hits']) == 1:
            return es_result['hits']['hits'][0]['_id']
        else:
            return 'null-s'
    else:
        return ''


def get_node_list(perPage=20, start=0):  # despatch

    body = {
        "query": {
            "match_all": {}
        },
        # "sort": {"time": {"order": "desc"}},  # 不排序，返回的非最新交易
        "from": start,
        "size": perPage
    }

    def foo():
        return es.search(index='ethnodes', body=body, doc_type='node')

    es_result = visit_mode_check(foo, "eth_nodes_sample.json")
    # print(json.dumps(es_result))

    total = es_result['hits']['total']
    targets = es_result['hits']['hits']
    rl = []

    # deal_node_item(targets[2]['_source'])
    for item in targets:
        rl.append(deal_node_item(item['_source']))
        # item['_source']['id'] = item['_id']
        # item['_source']['lastReach'] = item['_source']['nodeStatus']['lastReach']
        # item['_source']['default'] = 'NaN'
        # item['_source']['country'] = get_node_detail_info(item['_id'])['country']
        # rl.append(item['_source'])

    return {"total": total, "result": rl, "took": es_result['took']}


# get_node_list()


##### end node #####

##### start address #####
def test_contract_address(addr, perPage=20, start=0):  # 作用等同于get_trans_at_address
    result = es.search(index='ethereum', body={
        "query": {
            "bool": {
                "filter": {
                    "bool": {
                        "should": [
                            {"term": {
                                "from": addr
                            }}, {
                                "term": {
                                    "to": addr
                                }
                            }
                        ]
                    }
                }
            },
        },
        "size": perPage,
        "from": start
    }, doc_type='eth_transaction')
    # print(json.dumps(result))


# test_contract_address("0x233857FdbFd65B55AE0253685e0Ad674D4560f90")
# test_contract_address("null")          # 合约创建


def get_trans_at_address(addr, perPage=20, start=0):  # despatch 获取（合约）地址下的交易列表，addr不能为空， replace by get_transes_v3
    result = es.search(index='ethereum', body={
        "query": {
            "bool": {
                "should": [  # 或查询
                    {
                        "match": {
                            "to": addr
                        }
                    },
                    {
                        "match": {
                            "from": addr
                        }
                    }
                ]
            },
        },
        "size": perPage,
        "from": start
    }, doc_type='eth_transaction')
    total = result['hits']['total']
    # print(json.dumps(result))
    rv = deal_trans_targets(result['hits']['hits'])
    return total, rv


# get_trans_at_address('0xdabae13cfB6A9CAe0426baA456e97EE6A888a360', 20, 0)
# get_trans_at_address("", 20, 0)   # 合约创建
# address: 0x00B32FF033e8241843BbAa7403D6A729dD8bc1B8
# miner: 0x497A49648885f7aaC3d761817F191ee1AFAF399C
# 合约地址1: 0xF79b5f717002076FF1aFF924bdd60BE1AbDd19C4 不返回任何交易
# 合约地址2: 0xC96B4695FC3fab3547C157B12D013B65E7F5926D
# 有调用的合约地址: 0x6400B5522f8D448C0803e6245436DD1c81dF09ce
# 生成合约交易中from地址: 0xdabae13cfB6A9CAe0426baA456e97EE6A888a360


def block_byminer(miner, size=20, start=0):  # 爆块
    def foo():
        return es.search(index='eth_block', body={
            "query": {
                "match": {
                    "miner": miner
                }
            },
            "track_total_hits": True,
            "size": size,
            "from": start
        }, doc_type='_doc')

    result = visit_mode_check(foo(), "eth_blocks_sample.json")
    # print(json.dumps(result))
    total = result['hits']['total']['value']
    rv = []
    for item in result['hits']['hits']:
        item['_source']['height'] = item['_id']
        blockInfo = es3.get_block_detail(item['_id'], True)
        item['_source']['time'] = ts2t(item['_source']['timestamp'])
        if 'uncles' in item:
            item['_source']['nou'] = len(item['uncles'])  # number of uncles
        else:
            item['_source']['nou'] = 0
        rv.append(item['_source'])

        # logger.info(item['_source'])
        item['_source']['not'] = blockInfo['ntn'] + blockInfo['ctn']  # number of transactions
        item['_source']['sbt'] = round(blockInfo['total_value'], 8)  # sum of business  transactions
        item['_source']['award'] = blockInfo['block_reward']  # number of transactions

    return total, rv


# block_byminer('0x497A49648885f7aaC3d761817F191ee1AFAF399C', 20, 0)

##### end address #####

##### start contract #####
def get_contract_list(perPage=20, start=0):
    def foo():
        return es.search(index='eth_contract', body={
            "query": {
                "match_all": {}
            },
            "size": perPage,
            "from": start
            # "sort": {"timestamp": {"order": "desc"}}
        }, doc_type='eth_contract')

    result = foo()

    total = result['hits']['total']
    rv = []
    for item in result['hits']['hits']:
        item['_source']['id'] = item['_id']
        rv.append(item['_source'])
    # print(json.dumps(result))
    return total, rv


# get_contract_list()

# get_trans_at_address 与 address公用

def get_contract_code(c_address):
    # 获取 合约地址 hash
    def foo():
        return es.get(index='ethereum', id=c_address, doc_type='eth_contract')

    result = visit_mode_check(foo, data={'_source': {
        'hash': 0xa9059cbb00000000000000000000000050c2c9dffa07d68ec9c49fea327164e31c7bad920000000000000000000000000000000000000000000010d5b42176f2a2b00000}})
    hash = result['_source']['hash']
    # 根据hash找交易，交易附加信息
    trans_info = get_transaction_byhash(hash)
    c_code = trans_info['input']
    return c_code


# get_contract_code("0x6400B5522f8D448C0803e6245436DD1c81dF09ce")

def get_cin_perday(ftime1, ftime2=None):  # contract issue number
    start_stamp, end_stamp = day_stamp(ftime1, ftime2)
    res = es.search(index='ethereum', doc_type='eth_transaction',
                    body={
                        "query": {
                            "bool": {
                                "must": [
                                    {"range": {"time": {"gte": start_stamp,
                                                        "lte": end_stamp}}},
                                    {"term": {"to": ""}}  # "null"改为""
                                ]
                            }
                        }
                    })
    # must 均返回0， should返回全部
    # print(res['hits']['total'])
    # print(json.dumps(res))
    return {start_stamp: res['hits']['total']}

# get_cin_perday('2019-03-01')
# get_cin_perday('2019-01-22')   # 该日期下存在结果，但结果为0

# date_list = time_quantum('2019-03-02', 30)
# for date in date_list:
#     get_cin_perday(date)


##### end contract #####

# result =
# print(json.dumps(result))
# total = result['hits']['total']
# rv = []
# for item in result[hits][hits]:
#     rv.append(item['_source'])


# get_blocks()
# get_receipt(hash='0x54c181b6cce0ead484b8c13e59d2d345d5bc450f42a7236009212594e3e7095f')  # 查不到 0x62ae4eeb9bf61b6d29c16a24aa4f436d7c407803d0491d5373afd2434b3786b7
# get_receipt(hash='0x2e1ae9ad5188e88ff342cc9dd203301093338fc942f87e93e226276ea6e691fe')

# get_transes(size=10, start=90,order='asc', blockNum=7944887)

# print(json.dumps(get_node("00a9f63e5d33b5d1d3cf4c49658c79e19af94f5d49c6ed8119d3e1c04695910816f8317543f3beeef96bb9c83ecc0a19d323586afbf1bfc3ae1c7c48f2694f69")))
