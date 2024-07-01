import math
from datetime import timedelta, datetime

from flask import current_app

import mysql_dealer
from Model import dataValidation
import json
from Serives.bitcoinmessage import is_carry_tx
from Serives.btcaddrtag import get_address_mytags
from blueprint.btc import getUSDCNY
from config import config
from log import log
from bee_var import VALUE_ACC
from utils import ts2t

log = log.init_logger(config.log_filepath)
from dao import datainterchange
import time


def get_transaction_byhash(hash):  ##获取交易详情
    result = datainterchange.xmr_get_transaction(hash)  # 通过哈希值查询交易信息
    log.info("门罗币交易信息")
    log.info("门罗币查询交易信息成功" + str(hash))
    vin = []  ##处理交易信息的输入和输出保存为[{"address":"value"},]
    vout = []
    unlocktime = result["_source"]["as_json"]["unlock_time"]
    extra = result["_source"]["as_json"]["extra"]
    double_spent = result["_source"]["double_spend_seen"]
    inputvalue = 0
    outputvalue = 0
    for item in result["_source"]["as_json"]["vin"]:
        if "gen" in item.keys():
            address = "COINBASE"
            coinheight = item["gen"]["height"]
            vin_addr_tag = "unkown"
            value = 0
            keyoffsets = []
            keyimage = "None"
        else:
            address = "NON-COINBASE"
            value = item["key"]["amount"]
            print('inputamout:       ', inputvalue)
            coinheight = 0
            keyoffsets = item["key"]["key_offsets"]
            keyimage = item["key"]["k_image"]
            vin_addr_tag = "unkown"
        inputvalue += value
        print("keyoffsets",keyoffsets)
        vin.append([address, value, keyoffsets, keyimage, coinheight, vin_addr_tag, ])

    for item in result["_source"]["as_json"]["vout"]:
        value = item["amount"]
        key = item["target"]["tagged_key"]["key"]
        addr_tag = item["target"]["tagged_key"]["view_tag"]
        outputvalue += value
        vout.append([value, key, addr_tag])

        print('outputvalue:       ', outputvalue)

    result["vin"] = vin
    result["vout"] = vout
    result["status"] = "成功"
    times = result["_source"]['block_timestamp']
    result['time1'] = datetime.utcfromtimestamp(times)
    result['time_bj'] = result['time1'] + timedelta(hours=8)
    result['inputvalue'] = inputvalue
    result['outputvalue'] = outputvalue
    result['extra_pub'], result['extra_paymentid'] = parseExtra(extra)
    print(result['extra_pub'], result['extra_paymentid'])
    if double_spent:
        result['doublespend'] = "存在双花"
    else:
        result['doublespend'] = "不存在双花"
    return result


def get_transaction(s_class):  # 处理返回的交易数据量
    body = s_class.sbody()
    result = dataValidation.xmr_DataValidation_transaction(body)
    took = result['took']
    value = 0
    # for item in result['hits']['hits']["_source"]["as_json"]["vout"]:
    #     value += item["amount"]
    total = result['hits']['total']['value']
    log.info("查询时间为" + str(took))
    log.info("总交易量为" + str(total))
    if s_class.size != None:
        result = s_class.deal_results(result['hits']['hits'][0:s_class.size])
    else:
        result = s_class.deal_results(result['hits']['hits'])
    return {"took": took, "total": total, "result": result}


class AllTranses():
    def __init__(self, size=20, start=0, order="desc"):  # asc
        self.size = size
        self.start = start
        self.order = order

    def sbody(self):
        return {
            "query": {
                "match_all": {}
            },
            "size": self.size,
            "from": self.start,
            "sort": {"block_height": {"order": self.order}},
            "track_total_hits": True
            # "sort": {"time": {"order": order}}  # 性能问题
        }

    def deal_results(self, hit_data):
        return hit_data


def transaction_ajax(body):
    log.info("++++++++++++++++++开始交易查询+++++++++++++++++")
    result = dataValidation.xmr_DataValidation_transaction(body)
    if result:
        total = result["hits"]["total"]['value']
        log.info("符合条件的交易为" + str(total))
        if total == 0:
            return {}
        took = result['took']
        result = result['hits']['hits']
        for item in result:
            vin_times = len(item["_source"]["as_json"]["vin"])  ##交易的输入个数
            vout_times = len(item["_source"]["as_json"]["vout"])  ##交易的输出个数
            item["vin_times"] = vin_times
            item["vout_times"] = vout_times
            inputvalue = 0
            outputvalue = 0
            if 'key' in item["_source"]["as_json"]["vin"]:
                for it in item["_source"]["as_json"]["vin"]:
                    inputvalue += it["key"]["amount"]
            else:

                inputvalue = 0

            for it in item["_source"]["as_json"]["vout"]:
                outputvalue += it["amount"]

            if outputvalue == 0:
                item["value"] = inputvalue
            else:
                item["value"] = outputvalue

            item["value"] = round(item["value"] / 100000000, 6)
            times = item["_source"]['block_timestamp']
            item['time1'] = datetime.utcfromtimestamp(times)
            item['time_bj'] = item['time1'] + timedelta(hours=8)

            # item["_source"]["iscoinbase"] = str(item["_source"]["iscoinbase"])
            item["_score"] = str(item["_score"])

            # log.error(item['time_bj'])
        return {"took": took, "total": total, "result": result}
    else:
        log.error("errr")
        return {"took": "notfound", "total": 0, "result": result}


def parseExtra(dec):
    rawpub = dec[1:33]
    extra_nonce_tag = dec[33]
    extra_nonce_size = dec[34]

    pub = dectohex(rawpub)
    if (dec[0] == 1):  # pubkey is tag 1
        print('Extra :', dec)  # pubkey is 32 bytes
        print('Extra nonce :', dec[34:])  # pubkey is 32 bytes
        print('payment ID in extra_nonce :', dec[36:])  # pubkey is 32 bytes
        if dec[33] == 2 and (dec[35] == 0 or dec[35] == 1):
            paymentID = dectohex(dec[36:36 + int(extra_nonce_size) - 1])
        return pub, paymentID


def dectohex(dec):
    out = []
    for i in range(len(dec)):
        if dec[i] < 16:
            out.append("0" + hex(dec[i])[-1])
        else:
            out.append(hex(dec[i])[-2:])
    return "".join(out)
