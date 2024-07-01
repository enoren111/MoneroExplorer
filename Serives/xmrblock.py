from sqlalchemy import false

from Model import dataValidation
from Serives import btctransaction
from utils import ts2t, judge_tr_endpoint
import json
from config import config
from log import log
from dao.datainterchange import xmr_get_block, search_transaction, xmr_search_block, xmr_search_transaction
import time
from datetime import timedelta, datetime

log = log.init_logger(config.log_filepath)


def get_item_by_id_from_es(blockhash):  # 查询指定高度btc区块
    body = {
        "query": {
            "term": {
                "block_header.hash": blockhash
            }
        },
        "track_total_hits": True
    }
    return body


# def xmr_home_get_blocks(size, start):  # 获得区块信息 按出块时间降序排序  latest blocks
#     rv = []
#     body = {
#         "query": {
#             "match_all": {}
#         },
#         "size": size,
#         "from": start,
#         "sort": {"block_header.height": {"order": "desc"}}
#     }

    

#     result = xmr_search_block(body)
#     log.info(json.dumps(len(result)))
#     total = result['hits']['total']['value']
#     took = result['took']
#     targets = result['hits']['hits']
#     log.info("total为：" + str(total))
#     start = time.time()
#     for item in targets:
#         block = item['_source']
#         block['default'] = 'null'
#         block['height'] = block["block_header"]["height"]
#         times = block["block_header"]['timestamp']
#         block['time1'] = datetime.utcfromtimestamp(times)
#         block['time_bj'] = block['time1'] + timedelta(hours=8)
#         block['trans_num'] = block["block_header"]["num_txes"]+1
#         rv.append(block)
#     print("用时" + str(time.time() - start))
#     return {"total": total, "blocks": rv, "took": took}

# def get_blocks_new(size, start, order="desc", time_rang_id=4, miner=None):  # 获得区块信息 按出块时间降序排序  latest blocks
#     rv = []
#     body = sb_for_block_new(size, start, order, time_rang_id)
#     result = dataValidation.XMR_DataValidation_block_new(body)
#     log.info(json.dumps(len(result)))
#     # took = result['took']
#     print("asasasasasasaasdasdadadaads",result)
#     total = result['hits']['total']['value']  # hits-total-value
#     targets = result['hits']['hits']
#     log.info("total为：" + str(total))
#     start = time.time()
#     for item in targets:
#         # blockdetail = get_block_detail(item["_id"],0,True)
#         block = item['_source']
#         print(item)
#         block['default'] = 'null'
#         block['height'] = block["block_header"]["height"]
#         times = block["block_header"]['timestamp']
#         # block['time'] = ts2t(block['time'])
#         block['trans_num'] = block["block_header"]["num_txes"]+1
#         block['time1'] = datetime.utcfromtimestamp(times)
#         block['time_bj'] = block['time1'] + timedelta(hours=8)
#         rv.append(block)
#     print("用时" + str(time.time() - start))
#     return {"total": total, "blocks": rv, }#"took": took


def get_blocks(size, start, order="desc", time_rang_id=4, miner=None):  # 获得区块信息 按出块时间降序排序  latest blocks
    rv = []
    body = sb_for_block(size, start, order, time_rang_id)
    result = dataValidation.XMR_DataValidation_block(body)
    log.info(json.dumps(len(result)))
    took = result['took']
    total = result['hits']['total']['value']  # hits-total-value
    targets = result['hits']['hits']
    log.info("total为：" + str(total))
    start = time.time()
    for item in targets:
        # blockdetail = get_block_detail(item["_id"],0,True)
        block = item['_source']
        block['default'] = 'null'
        block['height'] = block["block_header"]["height"]
        times = block["block_header"]['timestamp']
        # block['time'] = ts2t(block['time'])
        block['trans_num'] = block["block_header"]["num_txes"]+1
        block['time1'] = datetime.utcfromtimestamp(times)
        block['time_bj'] = block['time1'] + timedelta(hours=8)
        rv.append(block)
    print("用时" + str(time.time() - start))
    return {"total": total, "blocks": rv, "took": took}


def get_detail(hash, start=0, size=10):  # 区块详细信息处理部分block_detail_flag = False：区块列表
    body = {
        "query": {
            "term": {
                "block_hash": hash
            }
        },
        "size": size,
        "from": start,
        "track_total_hits": True
    }
    result = dataValidation.xmr_DataValidation_transaction(body)
    if result:
        log.info("查询结果为：" + str(result["hits"]["total"]))
        for tx in result["hits"]["hits"]:
            amount = 0
            tx["vin"] = len(tx["_source"]["as_json"]["vin"])
            tx["vout"] = len(tx["_source"]["as_json"]["vout"])
            for data in tx["_source"]["as_json"]["vout"]:
                amount += data["amount"]
            tx["value"] = round(amount / 10000000, 6)

        return result["hits"]["hits"]
    return [{
        "_index": "monero_tx",
        "_type": "raw",
        "_id": "d2506ef459b950a565ca540ba5316dbbf35f8cb004be5090c84d43ba9b71cc02",
        "_score": 10.534563,
        "_source": {
            "as_json": {
                "version": 1,
                "unlock_time": 65,
                "vin": [
                    {
                        "gen": {
                            "height": 5
                        }
                    }
                ],
                "vout": [
                    {
                        "amount": 158495,
                        "target": {
                            "key": "d0c454b68501f0fe499f3a27f2f2678a85c59a7986fd375982b02b427dcbc971"
                        }
                    },
                    {
                        "amount": 2000000,
                        "target": {
                            "key": "a15ea1c6b968bddde35a6654d34c065d5603cd51313ab20fb5ba3b46cdfce4af"
                        }
                    },
                    {
                        "amount": 100000000,
                        "target": {
                            "key": "b2f6e972af235d063e39926e3c4e373b270bc61239900b22a1a0c5941446e5e4"
                        }
                    },
                    {
                        "amount": 2000000000,
                        "target": {
                            "key": "300849c032debc25ed2e67e29989e2fbe031c2bb3d335ae93462e8086db741d2"
                        }
                    },
                    {
                        "amount": 90000000000,
                        "target": {
                            "key": "4669c0f525afc81c9d41ff87e8577eaac3a353d5a149a1b2967b1e53753c738e"
                        }
                    },
                    {
                        "amount": 500000000000,
                        "target": {
                            "key": "2b683f34abb9c54abed7292a3606c5f39ed3542811c5608aa4d3bdc7805ca51f"
                        }
                    },
                    {
                        "amount": 7000000000000,
                        "target": {
                            "key": "73eb6c7af88b4ae907680a842fa811adaaac2e13ae653afdcf2bd28e64172b7d"
                        }
                    },
                    {
                        "amount": 10000000000000,
                        "target": {
                            "key": "d53485d57ab005a409b3ed7d853a8308d53bbe72298b9504654b6efc58de276e"
                        }
                    }
                ],
                "extra": [
                    1,
                    140,
                    118,
                    97,
                    53,
                    147,
                    206,
                    145,
                    250,
                    127,
                    190,
                    103,
                    161,
                    162,
                    251,
                    31,
                    203,
                    239,
                    12,
                    134,
                    71,
                    250,
                    116,
                    28,
                    234,
                    101,
                    143,
                    142,
                    60,
                    10,
                    44,
                    52,
                    11
                ]
            },
            "block_height": 5,
            "block_timestamp": 1397818225,
            "double_spend_seen": false,
            "in_pool": false,
            "output_indices": [
                0,
                1,
                4,
                4,
                4,
                4,
                4,
                4
            ],
            "prunable_as_hex": "",
            "prunable_hash": "0000000000000000000000000000000000000000000000000000000000000000",
            "pruned_as_hex": "014101ff05089fd60902d0c454b68501f0fe499f3a27f2f2678a85c59a7986fd375982b02b427dcbc97180897a02a15ea1c6b968bddde35a6654d34c065d5603cd51313ab20fb5ba3b46cdfce4af80c2d72f02b2f6e972af235d063e39926e3c4e373b270bc61239900b22a1a0c5941446e5e480a8d6b90702300849c032debc25ed2e67e29989e2fbe031c2bb3d335ae93462e8086db741d28088aca3cf02024669c0f525afc81c9d41ff87e8577eaac3a353d5a149a1b2967b1e53753c738e8090cad2c60e022b683f34abb9c54abed7292a3606c5f39ed3542811c5608aa4d3bdc7805ca51f80e08d84ddcb010273eb6c7af88b4ae907680a842fa811adaaac2e13ae653afdcf2bd28e64172b7d80c0caf384a30202d53485d57ab005a409b3ed7d853a8308d53bbe72298b9504654b6efc58de276e21018c76613593ce91fa7fbe67a1a2fb1fcbef0c8647fa741cea658f8e3c0a2c340b",
            "tx_hash": "d2506ef459b950a565ca540ba5316dbbf35f8cb004be5090c84d43ba9b71cc02",
            "block_hash": "68a271cac6ab97ccdf5fdf5e93cf36efff9686dd179763f45c9b0febabfda99a"
        }
    }]


def get_searchblock(size, start, rule, starttime, endtime):  # 获得区块信息 按出块时间降序排序  latest blocks
    rv = []
    if rule == "":
        rule = "desc"
    if starttime:
        starttime = time.strptime(starttime, '%Y-%m-%d %H:%M:%S')
        starttime = time.mktime(starttime)
    else:
        starttime = time.mktime((2014, 4, 18, 0, 0, 0, 0, 0, 0))  # 门罗币诞生时间
    if endtime:
        endtime = time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S'))
    else:
        endtime = time.time()

    body = {"query": {
        "bool": {
            "should": [
                {"range": {
                    "block_header.timestamp":
                               {"gte": starttime,
                                "lt": endtime}}},
            ]
        }
    },
        "from": start,
        "size": size,
        "sort": {"block_header.timestamp": {"order": rule}},
        "track_total_hits": True
    }
    log.info(body)
    result = dataValidation.XMR_DataValidation_block(body)
    log.info(json.dumps(len(result)))
    total = result['hits']['total']['value']
    took = result['took']
    targets = result['hits']['hits']
    log.info("total为：" + str(total))
    for item in targets:
        blockdetail = get_block_detail(item["_id"], 0, True)
        block = item['_source']
        block['default'] = 'null'
        times = block['block_header']['timestamp']
        block['time'] = ts2t(block['block_header']['timestamp'])
        block['time1'] = datetime.utcfromtimestamp(times)
        block['time_bj'] = block['time1'] + timedelta(hours=8)
        block['trans_num'] = blockdetail["trans_num"]
        block['total_value'] = blockdetail['total_value']
        block['miner'] = len(blockdetail["miner"])
        # block["reward"] = blockdetail["block_reward"]
        rv.append(block)
    return {"total": total, "blocks": rv, "took": took}




def sb_for_block(size, start, order="desc", time_rang_id=4):  # search区块 body
    if time_rang_id == 4:
        return {
            "query": {
                "match_all": {}
            },
            "size": size,
            "from": start,
            "sort": {"block_header.height": {"order": order}},
            "track_total_hits": True
        }
    else:
        start_ts, end_ts = judge_tr_endpoint(time_rang_id)
        return {
            "query": {
                "bool": {
                    "should": [
                        {"range": {"block_header.timestamp":
                                       {"gte": start_ts,
                                        "lt": end_ts}}},
                    ]
                }
            },
            "size": size,
            "from": start,
            "sort": {"block_header.height": {"order": order}},
            "track_total_hits": True
        }


def get_block_detail(hash, start=0, block_detail_flag=False):  # 区块详细信息处理部分block_detail_flag = False：区块列#待改
    body = {
              "query": {
                "term": {
                  "block_hash": {
                    "value": hash
                  }

               }
              },
              "from":0,
              "size":5000
            }

    block_reward = 50  ##默认为50
    miner = []
    result = xmr_search_transaction(body)
    txs = []
    total = 0
    amount = 0
    # print("transaction result", result)

    if result and result["hits"]["total"]['value'] != 0:
        total = result["hits"]["total"]['value']
        # print("transaction number",total)
        txs = result["hits"]["hits"]
        for item in result["hits"]["hits"]:
            for data in item["_source"]["as_json"]["vout"]:
                if "key" in data["target"].keys():  # 这里暂且将有多少key作为miner
                    key = data["target"]["key"]
                    miner.append(key)
                amount += data["amount"]
            # block_reward = round(item["_source"]["outputvalue"] / 100000000, 6)
    log.info("矿工数量为" + str(len(miner)))
    log.info("区块总交易额为：" + str(amount))
    body = get_item_by_id_from_es(hash)
    Block = dataValidation.XMR_DataValidation_block(body)
    try:
        Block = Block["hits"]["hits"][0]['_source']["block_header"]
    except Exception as e:
        log.info(e)
        Block = {}
    Txs = {}

    for tx in txs:
        Txs[tx['_id']] = tx['_source']["as_json"]
        tx["vin"] = len(tx["_source"]["as_json"]["vin"])
        tx["vout"] = len(tx["_source"]["as_json"]["vout"])
    # total_value = 0
    # for item in Txs.keys():
    #     total_value += round(Txs[item]['v'] / 100000000, 6)
    # log.info("区块总交易额为：" + str(total_value))

    if block_detail_flag:
        # Block['block_reward'] = block_reward
        # Block['height'] = Block['height']
        Block['total_value'] = amount
        Block['trans_num'] = total
        Block["transactions"] = txs
        Block['miner'] = miner
        Block['mineres'] = len(miner)
        return Block
    else:
        return {"total_value": round(amount, 9),
                "trans_num": total,
                "block_reward": 50,
                "miner": "coinbase"
                }


def xmr_home_get_blocks(size, start): #获得区块信息 按出块时间降序排序  latest blocks
    rv = []
    body = {
        "query": {
            "match_all": {}
        },
        "size": size,
        "from": start,
        "sort": {"block_header.timestamp": {"order": "desc"}}
    }
    result = xmr_search_block(body)
    log.info(json.dumps(len(result)))
    total = result['hits']['total']['value']
    took = result['took']
    targets = result['hits']['hits']
    log.info("total为："+str(total))
    start=time.time()
    for item in targets:
        #blockdetail = get_block_detail(item["_id"],0,True)
        block = item['_source']
        block['default'] = 'null'
        times = block['block_header']['timestamp']
        # block['time'] = ts2t(block['time'])
        block['time1'] = datetime.utcfromtimestamp(times)
        block['time_bj'] = block['time1'] + timedelta(hours=8)
        block['trans_num'] = block['block_header']["num_txes"]
        rv.append(block)
    print("用时"+str(time.time()-start))
    return {"total":total,"blocks":rv,"took":took}

def get_block_total():  ##获取区块总数
    body = {
        "query": {
            "match_all": {}
        }
    }
    result = dataValidation.xmr_DataValidation_blocknums(body)
    log.info("区块总数result为：" + str(result))
    return result


def block_reverse(height):  ###区块高度返回区块hash值
    body = {
        "query": {
            "term": {
                "block_header.height": height
            }
        },
        "track_total_hits": True
    }
    result = xmr_search_block(body)
    if result and result["hits"]["total"]['value']!=0:
        log.info("区块查询结果为"+str(result["hits"]["total"]['value']))
        return result["hits"]["hits"][0]["_id"]
    else:
        return ""