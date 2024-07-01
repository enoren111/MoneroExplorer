from Model import dataValidation
from Serives import btctransaction
from utils import ts2t, judge_tr_endpoint
import json
from config import config
from log import log
from dao.datainterchange import get_block,search_transaction,search_block
import time
from datetime import timedelta, datetime
log = log.init_logger(config.log_filepath)


def get_item_by_id_from_es(blockhash):    #查询指定高度btc区块
    body = {
        "query": {
            "term": {
                "hash": blockhash
            }
        },
        "track_total_hits": True
    }
    return body


def get_block_detail(hash,start=0,block_detail_flag=False):  #区块详细信息处理部分block_detail_flag = False：区块列
    body = {
        "query": {
            "term": {
                "blockhash": hash

            }
        },
        "from":0,
        "size":5000,
        "track_total_hits": True
    }
    block_reward = 50  ##默认为50
    miner = []
    result = search_transaction(body)
    txs=[]
    total =0
    if result and result["hits"]["total"]['value']!=0:
        total = result["hits"]["total"]['value']
        txs = result["hits"]["hits"]
        for item in result["hits"]["hits"]:
            if item["_source"]["iscoinbase"]:
                for data in item["_source"]["vout"]:
                    if "addresses" in data["scriptPubKey"].keys():
                        address = data["scriptPubKey"]["addresses"][0]
                        miner.append(address)
                block_reward = round(item["_source"]["outputvalue"] / 100000000, 6)
    log.info("矿工数量为"+str(len(miner)))
    log.info("区块奖励为："+str(block_reward))
    # s_class = btctransaction.BlockDetail(start=start,block_id=block_num)
    # # 区块内部的交易
    # txs = btctransaction.get_transaction(s_class)
    # total = txs["total"]
    # txs = txs["result"]
    body = get_item_by_id_from_es(hash)
    Block = dataValidation.DataValidation_block(body)
    try:
        Block = Block["hits"]["hits"][0]['_source']
    except Exception as e:
        log.info(e)
        Block = {}
    Txs = {}

    for tx in txs:
        # if tx["_source"]["iscoinbase"]:
        #     block_reward = round(tx["_source"]["inputvalue"]/10000000,2)
        #     miner=tx["_source"]["vout"][0]["scriptPubKey"]["addresses"][0]
        Txs[tx['_id']]=tx['_source']
        tx["vin"] = len(tx["_source"]["vin"])
        tx["vout"] = len(tx["_source"]["vout"])
    total_value = 0
    for item in Txs.keys():
        total_value += round(Txs[item]['outputvalue']/100000000,6)
    log.info("区块总交易额为："+str(total_value))

    if block_detail_flag:
        Block['block_reward'] = block_reward
        Block['height'] = Block['height']
        Block['total_value'] = total_value
        Block['trans_num'] = total
        Block["transactions"] = txs
        Block['miner'] = miner
        Block['mineres'] = len(miner)
        return Block
    else:
        return {"total_value": round(total_value, 9),
                "trans_num": total,
                "block_reward":50,
                "miner": "coinbase"
                }


def get_detail(hash,start=0,size=10):  #区块详细信息处理部分block_detail_flag = False：区块列表
    body = {
        "query": {
            "term": {
                "blockhash": hash
            }
        },
        "size":size,
        "from": start,
        "track_total_hits": True
    }
    result = dataValidation.DataValidation_transaction(body)
    if result:
        log.info("查询结果为："+str(result["hits"]["total"]))
        for tx in result["hits"]["hits"]:
            tx["vin"] = len(tx["_source"]["vin"])
            tx["vout"] = len(tx["_source"]["vout"])
            tx["value"] = round(tx["_source"]["inputvalue"]/10000000,6)
        return result["hits"]["hits"]
    return [{"_index": "btc_tx_new", "_type": "raw", "_id": "d520ad675a2392779468b6c467a1124a94b22c0d113da2bc1f396db192133f1c", "_score": 1.0, "_source": {"dayprice": 4.3, "iscoinbase": False, "fee": 0, "hash": "d520ad675a2392779468b6c467a1124a94b22c0d113da2bc1f396db192133f1c", "vout": [{"n": 0, "value": 111.87936321, "scriptPubKey": {"type": "pubkeyhash", "hex": "76a914ad284083f76c9140d71acd9a225048b7806967bd88ac", "addresses": ["1Gna7wr1BY8o42E8WErsu9hcYwrm4TgYeH"], "asm": "OP_DUP OP_HASH160 ad284083f76c9140d71acd9a225048b7806967bd OP_EQUALVERIFY OP_CHECKSIG", "reqSigs": 1}}, {"n": 1, "value": 0.12063679, "scriptPubKey": {"type": "pubkeyhash", "hex": "76a914ab9041c3216610649123cdfb21b4b0a9677fd91688ac", "addresses": ["1Ge9MwvhtBxJvXLep4aLoqjLjAq7r3r6Hz"], "asm": "OP_DUP OP_HASH160 ab9041c3216610649123cdfb21b4b0a9677fd916 OP_EQUALVERIFY OP_CHECKSIG", "reqSigs": 1}}], "weight": 1036, "hex": "0100000001614f419cfbff004ab5c07d2883161c58e018c40a4b806ddb6f2378f949e999dd010000008c493046022100f4576eaa569677fd286d06a31014ed78eaf0b88a89704b7ddb60770a659af82c022100e9d357efcd90f84f077a9e8a085bd83afea9aab6367af71506a05c69c48f1094014104cf0693c91ac78abeb619188dd83ce70acf14017633b71142a5f841e9f20571f47d128ef9677015f7134cb2803e25a2906e3b24000318139cbcc1684f8d87826effffffff02415cda9a020000001976a914ad284083f76c9140d71acd9a225048b7806967bd88acbf13b800000000001976a914ab9041c3216610649123cdfb21b4b0a9677fd91688ac00000000", "blockhash": "0000000000000a008e8a6cae76b9e9bbf2321f0e24cbde1c77299c1a3673a3b5", "vin": [{"scriptSig": {"hex": "493046022100f4576eaa569677fd286d06a31014ed78eaf0b88a89704b7ddb60770a659af82c022100e9d357efcd90f84f077a9e8a085bd83afea9aab6367af71506a05c69c48f1094014104cf0693c91ac78abeb619188dd83ce70acf14017633b71142a5f841e9f20571f47d128ef9677015f7134cb2803e25a2906e3b24000318139cbcc1684f8d87826e", "asm": "3046022100f4576eaa569677fd286d06a31014ed78eaf0b88a89704b7ddb60770a659af82c022100e9d357efcd90f84f077a9e8a085bd83afea9aab6367af71506a05c69c48f1094[ALL] 04cf0693c91ac78abeb619188dd83ce70acf14017633b71142a5f841e9f20571f47d128ef9677015f7134cb2803e25a2906e3b24000318139cbcc1684f8d87826e"}, "vout": 1, "sequence": 4294967295, "value": 11200000000, "txid": "dd99e949f978236fdb6d804b0ac418e0581c1683287dc0b54a00fffb9c414f61", "addresses": "1CLVnMWEwzuGVcQ6L2WBoUJQFj3B9XeVmx"}], "txid": "d520ad675a2392779468b6c467a1124a94b22c0d113da2bc1f396db192133f1c", "volume": 11200000000, "blocktime": "2012-02-21T16:19:37", "version": 1, "inputvalue": 11200000000, "blockheight": 167835, "locktime": 0, "vsize": 259, "outputvalue": 11200000000, "size": 259}}]


def sb_for_block(size, start, order="desc", time_rang_id=4):  # search区块 body
    if time_rang_id == 4:
        return {
            "query": {
                "match_all": {}
            },
            "size": size,
            "from": start,
            "sort": {"time": {"order": order}},
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
            "sort": {"time": {"order": order}},
            "track_total_hits": True
        }


def btc_home_get_blocks(size, start): #获得区块信息 按出块时间降序排序  latest blocks
    rv = [{'height':10}]
    body = {
        "query": {
            "match_all": {}
        },
        "size": size,
        "from": start,
        "sort": {"time": {"order": "desc"}}
    }
    result = []#search_block(body)
    log.info(json.dumps(len(result)))
    print(result)
    total = 0#result['hits']['total']['value']
    took = 0#result['took']
    targets = []#result['hits']['hits']
    log.info("total为："+str(total))
    start=time.time()
    for item in targets:
        #blockdetail = get_block_detail(item["_id"],0,True)
        block = item['_source']
        block['default'] = 'null'
        block['height'] = block["height"]
        times = block['time']
        # block['time'] = ts2t(block['time'])
        block['time1'] = datetime.utcfromtimestamp(times)
        block['time_bj'] = block['time1'] + timedelta(hours=8)
        block['trans_num'] = block["nTx"]
        rv.append(block)
    print("用时"+str(time.time()-start))
    return {"total":total,"blocks":rv,"took":took}

def get_blocks(size, start, order="desc", time_rang_id=4, miner=None): #获得区块信息 按出块时间降序排序  latest blocks
    rv = []
    body = sb_for_block(size, start, order, time_rang_id)
    result = dataValidation.DataValidation_block(body)
    print("result:             ============     ",result)

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
        block['height'] = block["height"]
        times = block['time']
        # block['time'] = ts2t(block['time'])
        block['time1'] = datetime.utcfromtimestamp(times)
        block['time_bj'] = block['time1'] + timedelta(hours=8)
        block['trans_num'] = block["nTx"]
        # block['total_value'] = blockdetail['total_value']
        # block['miner'] = len(blockdetail["miner"])
        # block["reward"] = blockdetail["block_reward"]
        rv.append(block)
    print("用时"+str(time.time()-start))
    return {"total":total,"blocks":rv,"took":took}


def get_searchblock(size, start, rule,starttime,endtime): #获得区块信息 按出块时间降序排序  latest blocks
    rv = []
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
    body = { "query": {
            "bool": {
                "should": [
                    {"range": {"time":
                                   {"gte": starttime,
                                    "lt": endtime}}},
                ]
            }
        },
        "from":start,
        "size":size,
        "sort": {"time": {"order": rule}},
        "track_total_hits": True
    }
    log.info(body)
    result = dataValidation.DataValidation_block(body)
    log.info(json.dumps(len(result)))
    total = result['hits']['total']['value']
    took = result['took']
    targets = result['hits']['hits']
    log.info("total为："+str(total))
    for item in targets:
        blockdetail = get_block_detail(item["_id"],0,True)
        block = item['_source']
        block['default'] = 'null'
        block['height'] = block["height"]
        times = block['time']
        block['time'] = ts2t(block['time'])
        block['time1'] = datetime.utcfromtimestamp(times)
        block['trans_num'] = blockdetail["trans_num"]
        block['total_value'] = blockdetail['total_value']
        block['miner'] = len(blockdetail["miner"])
        block["reward"] = blockdetail["block_reward"]
        rv.append(block)
    return {"total":total,"blocks":rv,"took":took}

def get_block_total(): ##获取区块总数
    body = {
        "query": {
            "match_all": {}
        }
    }
    result = dataValidation.DataValidation_blocknums(body)
    log.info("区块总数result为："+str(result))
    return result


def get_block_trans_total(hash):
    body = {
        "query": {
            "term": {
                "blockhash":hash
            }
        }
    }
    result = dataValidation.DataValidation_transactionnums(body)
    log.info("区块内的交易总数result为：" + str(result))
    return result


def block_reverse(height):  ###区块高度返回区块hash值
    body = {
        "query": {
            "term": {
                "height": height
            }
        },
        "track_total_hits": True
    }
    result = search_block(body)
    if result and result["hits"]["total"]['value']!=0:
        log.info("区块查询结果为"+str(result["hits"]["total"]['value']))
        return result["hits"]["hits"][0]["_id"]
    else:
        return ""
