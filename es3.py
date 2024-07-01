# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch, NotFoundError
from loguru import logger

from utils import ts2t, day_stamp, time_quantum, today, judge_tr_endpoint, visit_mode_check
from es1 import deal_trans_targets, judge_trans_type
from flask import current_app
import json
import elasticsearch.helpers
# import myconfig
import datetime
import time
from bee_var import *
# from app import es

# es.tryagain_instance()
# es = es.instance


# 可用 不要运行，会持续输出
def get_all_blocks():  # scroll  test 参考https://www.cnblogs.com/blue163/p/8126156.html
    query_json = {
        "match_all": {}
    }

    queryData = es.search(index='eth_block', doc_type='eth_block', scroll='5m', timeout='3s', size=100,
                          body={"query": query_json})
    mdata = queryData.get("hits").get("hits")

    if not mdata:
        print('empty!')

    scroll_id = queryData["_scroll_id"]
    total = queryData["hits"]["total"]
    flag = mdata
    while flag != '':
        res = es.scroll(scroll_id=scroll_id, scroll='5m')  # scroll参数必须指定否则会报错
        flag = res["hits"]["hits"]
        mdata += mdata
    print(json.dumps(mdata))

    # for i in range(total/100):  # despatch
    #     res = es.scroll(scroll_id=scroll_id, scroll='5m')  # scroll参数必须指定否则会报错
    #     mdata += res["hits"]["hits"]
    #     print(i)
    # print(mdata)


# get_all_blocks()


def sb_for_trans(size=20, start=0, order="desc", time_rang_id=0, big_deal=False, blockNum=None, address=None,
                 detail=False):
    if big_deal:
        start_ts, end_ts = judge_tr_endpoint(0)
        return {
            "query": {
                "bool": {
                    "must": [{
                        "range": {"time":
                                      {"gte": start_ts,
                                       "lt": end_ts}}
                    }, {
                        "range": {"value": {
                            "gte": 1000
                        }}
                    }]
                }

            },
            "size": size,
            "from": start,
        }

    if blockNum == None and address == None:
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
                "sort": {"time": {"order": order}}
            }

    if blockNum != None:  # 区块内交易
        if detail:  # 查询全部
            return {
                "query": {
                    "match": {
                        "blockNumber": blockNum
                    }
                },
                "sort": {"time": {"order": order}},
            }
        else:
            return {
                "query": {
                    "match": {
                        "blockNumber": blockNum
                    }
                },
                "size": size,
                # "sort": {"time": {"order": order}},  # 时间都一样，没有意义
                "from": start
            }

    if address != None:
        query = {
            "query": {
                "bool": {
                    "should": [  # 或查询
                        {
                            "match": {
                                "to": address
                            }
                        },
                        {
                            "match": {
                                "from": address
                            }
                        }
                    ]
                },
            },
            "size": size,
            "from": start
        }
        if detail:
            del query['size']
            del query['from']
            # query['sort'] = {"time": {"order": order}},

        return query


def calu_trans_statistical_info(data):
    sinfo = {}

    sum_value = 0
    normal_trans_num = 0
    contract_trans_num = 0

    for item in data:  # 遍历交易
        # print(item['_source']['transactionIndex'])
        sum_value += item['_source']['value']
        trans_type_str = judge_trans_type(item['_source']['to'])
        if trans_type_str == trans_type['0']:
            normal_trans_num += 1
        if trans_type_str == trans_type['1']:
            contract_trans_num += 1

    # print(sum_value)
    sinfo['sum_value'] = sum_value
    sinfo['ntn'] = normal_trans_num
    sinfo['ctn'] = contract_trans_num
    return sinfo


def get_transes_v2(size=20, start=0, order="desc", time_rang_id=0, big_deal=False, blockNum=None, address=None,
                   detail=False):  # despatch 对应于get block 大额交易  rpby get_transes_v3
    # print('start')
    body = sb_for_trans(size, start, order, time_rang_id, big_deal, blockNum, address, detail)

    if detail:
        queryData = es.search(index='ethereum', doc_type='eth_transaction', scroll='5m', timeout='10s', size=10000,
                              body=body)
        mdata = queryData.get("hits").get("hits")
        # print(json.dumps(mdata))
        rpack = {}  # return package

        if not mdata:
            print('empty!')
            rpack.update(calu_trans_statistical_info(mdata))
            return rpack

        scroll_id = queryData["_scroll_id"]
        total = queryData["hits"]["total"]
        flag = mdata
        count = 1
        while flag != []:
            res = es.scroll(scroll_id=scroll_id, scroll='5m')  # scroll参数必须指定否则会报错
            scroll_id = res['_scroll_id']
            flag = res["hits"]["hits"]
            mdata += flag
            # count+=1
            # print(count)  # test
        # print(len(mdata))  # 查询出的交易数

        rpack['trans_num'] = len(mdata)
        if blockNum != None:
            sinfo = calu_trans_statistical_info(mdata)  #
            rpack.update(sinfo)
            return rpack

        if address != None:  # despatch replaced by getinfo.py
            # 对mdata按时间戳排序
            sdata = sorted(mdata, key=lambda value: value['_source']['time'], reverse=True)

            if len(sdata) >= 1:
                rpack['create_time'] = ts2t(sdata[-1]['_source']['time'])  # 创建时间
                rpack['last_active_time'] = ts2t(sdata[0]['_source']['time'])  # 最近活跃
            else:
                rpack['create_time'] = 'unknown'
                rpack['last_active_time'] = 'unknown'
            return rpack  # "keys":
    else:
        result = es.search(index='eth_transaction', body=body, doc_type='_doc')
        total = result['hits']['total']
        targets = result['hits']['hits']
        # print(json.dumps(result))
        rv = deal_trans_targets(targets)  # 仅限统计小规模数据
    # return total, rv
    return {"total": total, "result": rv, "took": result['took']}


class EsSearch():
    size = 20
    start = 0
    order = 'desc'
    trid = 0


# class BigDealTranses(EsSearch):

class AllTranses():
    def __init__(self, size=20, start=0, trid=0, order="desc"):  # asc
        self.size = size
        self.start = start
        self.trid = trid
        self.order = order

    def sbody(self):
        if self.trid == 4:
            return {
                "query": {
                    "match_all": {}
                },
                "size": self.size,
                "from": self.start,
                # "sort": {"time": {"order": order}}  # 性能问题
            }
        else:
            start_ts, end_ts = judge_tr_endpoint(self.trid)
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
                "size": self.size,
                "from": self.start,
                "sort": {"time": {"order": self.order}}  # 按时间降序排列
            }

    def deal_results(self, hit_data):
        return deal_trans_targets(hit_data)


class BigDealTranses():  # 大额交易/地址交易查询命令
    value = 1000
    addr = None

    # def __init__(self, size=20,start=0,order='desc',trid=0,value=1000, addr=None, unit=0):
    def __init__(self, size=20, start=0, order='desc', args=None):
        self.size = size
        self.start = start
        self.order = order
        self.trid = 0
        if args != None:  # 参数由前端传入，一定包含以下四种
            self.trid = args['tropId']
            if str(args['value']).isdigit():
                self.value = args['value']
            if args['address'] != '':
                # check address
                self.addr = args['address']
            self.unit = args['unitId']

    def sbody(self):  # search_body

        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {"value": {
                                "gte": self.value
                            }}
                        }
                    ]
                }
            },
            # "sort":{"time":{"order":order}}
            "track_total_hits": True,
            "size": self.size,
            "from": self.start
        }

        wrong_body = {
            "query": {

                "range": {"value": {
                    "gte": self.value
                }}
                , "bool": {
                    "should": [  # 或查询
                        {
                            "match": {
                                "to": self.addr
                            }
                        },
                        {
                            "match": {
                                "from": self.addr
                            }
                        }
                    ]
                }
            },
            "size": self.size,
            "from": self.start,
        }  # 不合法查询体

        # if self.trid != current_app.config['MAX_TR_ID']:
        if self.trid != 4:  # 按时间范围查询
            start_ts, end_ts = judge_tr_endpoint(self.trid)
            time_constraint = {
                "range": {"time":
                              {"gte": start_ts,
                               "lt": end_ts}}
            }
            body['query']['bool']['must'].append(time_constraint)

        if self.addr != None:  # 按地址查询
            addr_constraint = {"bool": {
                "should": [  # 或查询
                    {
                        "match": {
                            "to": self.addr
                        }
                    },
                    {
                        "match": {
                            "from": self.addr
                        }
                    }
                ]
            }}
            body['query']['bool']['must'].append(addr_constraint)
        return body

    def deal_results(self, hit_data):
        rl = deal_trans_targets(hit_data)
        return rl


class BlockDetail():  # 区块交易查询命令
    def __init__(self, size=None, start=0, block_id=7000000):
        self.size = size
        self.start = start
        self.block_id = block_id

    def sbody(self):
        # 查询区块全部交易或按分页查询
        body = {
            "query": {
                "term": {
                    "blockNumber": self.block_id
                }
            },
            "size": 7000 if (self.size == None) else self.size,
            "from": self.start
        }
        return body

        # 按分页查

    def deal_results(self, hit_data):
        # print(json.dumps(hit_data))
        return hit_data


def get_transaction(perpage, start):  # BigDealTranses BlockDetail AllTranses
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


def get_transes_v3(s_class):  # BigDealTranses BlockDetail AllTranses
    # 初始化s_class

    body = s_class.sbody()
    # try:
    #     if current_app.config['ONLINE_MODE']:
    #         es_results = es.search(index='ethereum', body=body, doc_type='eth_transaction')
    #     else:
    #         es_results = get_local_data("eth_transactions_sample.json")
    # except:
    #     es_results = get_local_data("eth_transactions_sample.json")
    es_results = es.search(index='eth_transaction', body=body)
    took = es_results['took']
    total = es_results['hits']['total']
    # logger.info(es_results)
    # logger.info(s_class.sbody())
    # result
    if s_class.size != None:
        result = s_class.deal_results(es_results['hits']['hits'][0:s_class.size])
    else:
        result = s_class.deal_results(es_results['hits']['hits'])
    return {"took": took, "total": total, "result": result}
    # print(json.dumps(results))


def get_item_by_id_from_es(doc_type, num, index='eth_block'):  # 'eth_transaction'
    body = {
        "query": {
            "term": {
                "blockNumber": num
            }
        }
    }
    return es.search(index=index, body=body, doc_type=doc_type)
    # try:
    #     if current_app.config['ONLINE_MODE']:
    #         return foo()
    #     else:
    #         return visit_mode_check(foo,"eth_block_sample.json")
    # except:   # 不能用finally
    #     return {}   # 有可能查不到块


# 调用示例
# id = '0049b2cf90d5ad985d70ad0837c56558225c25a8b67ecf239b15f301c5196510e5b081ff8040ba96fb350aaf6a66f4e4f3ccf9b114932e796af9ae0132eb0c87'
# id = 'ffee0c8a8b67310e7d2cfd16f21b33d61d4d631dc3de5350d1950cead19620b13dc2cad2876044e65f6425b904e7d06665e3d7baca5a7cbf66e1d284987d65a7'
# get_item_by_id_from_es('node',id,'ethnodes')

# 0x84295d5e054d8cff5a22428b195F5A1615bD644F 56W交易
# 0x72BCFA6932FeACd91CB2Ea44b0731ed8Ae04d0d3 16W交易
# 0x027f9F8575821365a70f3812Ea5F565946e7aC0d 435交易
# 0x04668Ec2f57cC15c381b461B9fEDaB5D451c8F7F 1.9W交易
# get_transes_v2(address='0x497A49648885f7aaC3d761817F191ee1AFAF399C', detail=True[False])  # 结果与get_info一样 1 获取区块下交易 2 获取地址下交易
# get_transes_v2(blockNum=7848959, detail=True[False])  # 19,333条交易  1 获取区块下交易 2 获取地址下交易
# get_transes_v2(blockNum=7925667, detail=False)  # 19,333条交易  1 获取区块下交易 2 获取地址下交易
# get_transes_v2(time_range_id=0)
# get_transes_v2(big_deal=True)


# size=20
# start=0
# order="desc"
# trid=0
# addr = '0xd8a83b72377476D0a66683CDe20A8aAD0B628713'
# bdt = BigDealTranses(addr=addr)
# get_transes_v3(bdt)

def basic(blockNumber):
    if blockNumber < 4380000:
        return 5.0
    elif blockNumber < 7280000:
        return 3.0
    return 2.0


def calu_trans_cost():
    pass


def get_block_detail(block_num, block_detail_flag=False):  # block_detail_flag = False：区块列表
    block_num = int(block_num)
    # 区块内交易
    txs = get_transes_v3(BlockDetail(block_id=block_num))['result']
    # logger.info(txs)
    # 区块
    # logger.info(get_item_by_id_from_es(doc_type='_doc', num=block_num, index='eth_block')['hits']['hits'])
    # logger.info(get_item_by_id_from_es(doc_type='_doc', num=block_num, index='eth_block')['hits']['hits'][0]['_source'])
    Block = get_item_by_id_from_es(doc_type='_doc', num=block_num, index='eth_block')['hits']['hits'][0]['_source']
    # Block=es.get(index='eth_block', doc_type='eth_block', id=block_num, request_timeout=120)['_source']
    Txs = {}
    RTxs = {}
    for tx in txs:
        Txs[tx['_id']] = tx['_source']
        try:
            # RTxs[tx['_id']]=es.get(index='eth_transaction_receipt', doc_type='raw', id=tx['_id'], request_timeout=120)['_source']
            RTxs[tx['_id']] = {'gasUsed': 0}  #
        except:
            RTxs[tx['_id']] = {'gasUsed': 0}
    basic_reward = basic(block_num)
    fees = 0
    total_gasPrice = 0
    total_value = 0
    for hash in Txs.keys():
        gp = float(Txs[hash]['gasPrice']) / (10 ** 18)
        fees += gp * (float(RTxs[hash]['gasUsed']))
        total_gasPrice += gp
        total_value += Txs[hash]['value']
    uncle_reward = 0
    for i in range(1, len(Block.get('uncles', [])) + 1):
        uncle_reward += basic_reward * (8 - i) / 8
    block_reward = basic_reward + basic_reward / 32 * len(Block.get('uncles', [])) + fees  #
    if len(txs) != 0:
        average_fee = fees / len(txs)
        average_gasPrice = total_gasPrice / len(txs)
    else:
        average_fee = 0
        average_gasPrice = 0

    if block_detail_flag:
        sinfo = calu_trans_statistical_info(txs)
        Block.update(sinfo)
        Block['height'] = block_num
        Block['fees'] = fees
        Block['block_reward'] = block_reward
        Block['basic_reward'] = basic_reward
        Block['uncle_reward'] = uncle_reward
        Block['average_fee'] = average_fee
        Block['average_gasPrice'] = average_gasPrice
        Block['total_value'] = total_value
        Block['trans_num'] = len(txs)
        Block['uncles'] = len(Block.get('uncles', []))

        return Block
    else:
        return {"fees": fees, "block_reward": block_reward, "basic_reward": basic_reward,
                "uncle_reward": uncle_reward, "average_fee": average_fee, "average_gasPrice": average_gasPrice,
                "total_value": round(total_value, 9),
                "trans_num": len(txs)}
    # print fees,block_reward,basic_reward,uncle_reward,average_fee,average_gasPrice,total_value

# res = get_block_detail(8068835,True)
# print(json.dumps(res))
# get_transes_v3(BlockDetail(block_id=8068835))
