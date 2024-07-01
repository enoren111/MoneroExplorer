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


class BlockDetail():  # 区块交易查询命令
    def __init__(self, size=10, start=0, block_id=7000000):
        self.size = size
        self.start = start
        self.block_id = block_id

    def sbody(self):
        # 查询区块全部交易或按分页查询
        body = {
            "query": {
                "term": {
                    "blockheight": self.block_id
                }
            },
            "from": self.start,
            "track_total_hits": True
        }
        return body

        # 按分页查

    def deal_results(self, hit_data):
        # print(json.dumps(hit_data))
        return hit_data


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
            "sort": {"blockheight": {"order": self.order}},
            "track_total_hits": True
            # "sort": {"time": {"order": order}}  # 性能问题
        }

    def deal_results(self, hit_data):
        return hit_data


def get_transaction(s_class):  # 处理返回的交易数据量
    body = s_class.sbody()
    result = dataValidation.DataValidation_transaction(body)
    took = result['took']
    total = result['hits']['total']['value']
    log.info("查询时间为" + str(took))
    log.info("总交易量为" + str(total))
    if s_class.size != None:
        result = s_class.deal_results(result['hits']['hits'][0:s_class.size])
    else:
        result = s_class.deal_results(result['hits']['hits'])
    return {"took": took, "total": total, "result": result}



def get_transaction_byhash(hash):  ##获取交易详情
    result = datainterchange.get_transaction(hash)
    log.info("交易信息")
    log.info("查询交易信息成功" + str(hash))
    vin = []  ##处理交易信息的输入和输出保存为[{"address":"value"},]
    vout = []
    for item in result["_source"]["vin"]:
        if "coinbase" in item.keys():
            address = "COINBASE"#自定义的
            value = result["_source"]['outputvalue'] / (10 ** 8)
            asm = item["coinbase"]
            vin_addr_tag = "unkown"#自定义的
        else:
            address = item["addresses"]
            total, tag ,result_list1000= get_address_mytags(address, "", "", "", "", 0, 10,"","")
            # log.error(total)
            # log.error(tag)
            if (tag ==[]):
                vin_addr_tag = "unkown"
            else:
                vin_addr_tag = tag[0]['name']
            value = item["value"] / (10 ** 8)
            asm = item["scriptSig"]["asm"]
        vin.append([address, value, asm,vin_addr_tag])
    for item in result["_source"]["vout"]:
        value = item["value"]
        address = item["scriptPubKey"]["addresses"]
        total,tag ,result_list1000= get_address_mytags(address, "", "", "","", 0, 10,"","")
        # log.error(total)
        # log.error(tag)
        if (tag==[]):
            addr_tag="unkown"
        else:
            addr_tag=tag[0]['name']
        asm = item["scriptPubKey"]["asm"]
        type = item["scriptPubKey"]["type"]
        vout.append([address, value, asm, type,addr_tag])
    result["vin"] = vin#自定义的
    result["vout"] = vout#自定义的
    result["status"] = "成功"#自定义的
    time_utc = datetime.strptime(result["_source"]['blocktime'].replace("T", " "), "%Y-%m-%d %H:%M:%S")
    result['time_bj'] = time_utc + timedelta(hours=8)
    timePrice=datetime.strptime(str(time_utc.date()),"%Y-%m-%d")
    re=getUSDCNY(str(timePrice))
    if "dayprice" in result["_source"].keys() and float(result["_source"]["dayprice"])!=0:
        result['USD'] = round(float(result["_source"]['outputvalue']/(10**8))*float(result["_source"]["dayprice"] ),2)
        if re:
            result['CNY'] = round(float(result["_source"]['outputvalue'] / (10 ** 8)) * float(re[0][1]), 2)
        else:
            result['CNY'] = 'unkown'
    elif re:
        result['CNY']=round(float(result["_source"]['outputvalue']/(10**8))*float(re[0][1]),2)
        result['USD']=round(float(result["_source"]['outputvalue']/(10**8))*float(re[0][0]),2)
    else:
        result['CNY']='unkown'
        result['USD']='unknow'
    # log.error(re)
    # 判断交易是否是夹带信息
    Flag, Carry_part = is_carry_tx(hash)
    if Flag == True:
        result["iscarry"] = True
        result["carrypart"] = Carry_part
    else:
        result["iscarry"] = False
        result["carrypart"] = Carry_part
    return result


def transaction_ajax(body):
    log.info("++++++++++++++++++开始交易查询+++++++++++++++++")
    result = dataValidation.DataValidation_transaction(body)
    if result:
        total = result["hits"]["total"]['value']
        log.info("符合条件的交易为" + str(total))
        if total == 0:
            return {}
        took = result['took']
        result = result['hits']['hits']
        for item in result:
            vin_times = len(item["_source"]["vin"])  ##交易的输入个数
            vout_times = len(item["_source"]["vout"])  ##交易的输出个数
            item["vin_times"] = vin_times
            item["vout_times"] = vout_times
            if item["_source"]["inputvalue"] == 0:
                item["value"] = item["_source"]["outputvalue"]
            else:
                item["value"] = item["_source"]["inputvalue"]
            if "dayprice" in item["_source"].keys():
                item["usdvalue"] = round(item["value"] * float(item["_source"]["dayprice"] )/ 100000000, 6)
            else:
                item["usdvalue"] = 0
            item["value"] = round(item["value"] / 100000000, 6)
            time_utc = datetime.strptime(item["_source"]['blocktime'].replace("T", " "), "%Y-%m-%d %H:%M:%S")
            item['time_bj'] = str(time_utc + timedelta(hours=8))
            item["_source"]["iscoinbase"] = str(item["_source"]["iscoinbase"])
            item["_score"] = str(item["_score"])

            # log.error(item['time_bj'])
        return {"took": took, "total": total, "result": result}
    else:
        log.error("errr")
        return {"took": "notfound", "total": 0, "result": result}


def searchQuery(body, perpage):
    result = datainterchange.search_transaction(body)
    total = result["hits"]["total"]["value"]
    latestTransList = result['hits']["hits"]
    for item in latestTransList:  ###代码重构
        vin_times = len(item["_source"]["vin"])  ##交易的输入个数
        vout_times = len(item["_source"]["vout"])  ##交易的输出个数
        item["vin_times"] = vin_times
        item["vout_times"] = vout_times
        if item["_source"]["inputvalue"] == 0:
            item["value"] = item["_source"]["outputvalue"]
        else:
            item["value"] = item["_source"]["inputvalue"]
        if "dayprice" in item["_source"].keys():
            item["usdvalue"] = item["_source"]["dayprice"]
            print(item["_source"]["dayprice"])
        else:
            item["usdvalue"] = 0
        item["value"] = round(item["value"] / 100000000, 6)
    log.info("交易总数为" + str(total))
    pages = math.ceil(float(total) / perpage)
    context = {
        "labels": ['1', '2', '3', '4', '5', '6', '7'],
        "dataset3": [20, 40, 30, 85, 10, -20, 60],
        "trans_total": total,
        "trans_fields": current_app.config['BTC_FIELDS'],
        "pages": pages,
        "tr_option_list": current_app.config['TIME_RANGE_OPTIONS'],
        "columns": current_app.config['TRANS_TB_KEYS'],
        "page_title": '交易',
        "took": result['took']
    }
    return context, latestTransList
