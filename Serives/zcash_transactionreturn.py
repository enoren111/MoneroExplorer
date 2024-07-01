from Model.dataValidation import DataValidation_transaction, Zcash_DataValidation_transaction
from Serives import btcblock, zcashtransaction
from Serives import btctransaction
from flask import request
from flask import current_app
import math

from dao.datainterchange import zcash_search_transaction
from utils import ts2t
import json
from config import config
from log import log
from Serives import btctransaction
from dao import datainterchange
import time
from bee_var import perPage
log = log.init_logger(config.log_filepath)


def zcash_home_trans_return(perPage,start):
    body = {
        "query": {
            "match_all": {}
        },
        "size": perPage,
        "from": start,
        "sort": {"height": {"order": "desc"}}  # 性能问题
    }
    ans = zcash_search_transaction(body)
    total = ans['hits']['total']['value']
    latestTransList = ans['hits']['hits']
    for item in latestTransList:    ###代码重构
        if item["_source"]['vjoinsplit_size']==0:
            if item["_source"]["vin"] and "coinbase" in item["_source"]["vin"][0].keys():
                item["trans_type"] = 'Coinbase'
            else:
                item["trans_type"]='Transparent'
        elif item["_source"]['vin_size']==0 and item["_source"]['vout_size']!=0:
            item["trans_type"] = 'z-to-t'
        elif item["_source"]['vin_size'] != 0 and item["_source"]['vout_size'] == 0:
            item["trans_type"] = 't-to-z'
        else:
            item["trans_type"] = 'z-to-z'
        # if vin_times ==0:
        #     if vout_times==0:
        #         item["trans_type"] = 'z-to-z'
        #     else:
        #         item["trans_type"] = 'z-to-t'
        # elif "coinbase" in item["_source"]["vin"][0].keys():
        #     item["trans_type"] = 'Coinbase'
        # elif vout_times==0:
        #     item["trans_type"] = 't-to-z'
        # else:
        #     item["trans_type"]='Transparent'
        item["_time"] = ts2t(item["_source"]["blocktime"])
    log.info("交易总数为"+str(total))
    pages = math.ceil(float(total) / perPage)
    context = {
        "labels": ['1', '2', '3', '4', '5', '6', '7'],
        "dataset3": [20, 40, 30, 85, 10, -20, 60],
        "trans_total": total,
        "trans_fields": current_app.config['BTC_FIELDS'],
        "pages": pages,
        "tr_option_list": current_app.config['TIME_RANGE_OPTIONS'],
        "columns": current_app.config['TRANS_TB_KEYS'],
        "page_title": '交易',
        "took": ans['took']
    }
    return context,latestTransList
def zcash_trans_return(perPage,start,rule='desc'):
    ans = zcashtransaction.zcash_get_transaction(zcashtransaction.ZcashAllTranses(size=perPage, start=start,order=rule))
    total = ans['total']
    latestTransList = ans['result']
    for item in latestTransList:    ###代码重构
        vin_times = len(item["_source"]["vin"])  ##交易的输入个数
        vout_times = len(item["_source"]["vout"]) ##交易的输出个数
        item["vin_times"] = vin_times
        item["vout_times"] = vout_times
        item["value_shield"] = 0;
        value = 0
        for i in item["_source"]["vout"]:
            value+=i["value"]
        # while (i < vout_times):
        #     value += item["_source"]["vout"][i]["value"]
        if vin_times ==0:

            item['value_transparent'] = value
            if vout_times==0:
                item["trans_type"] = 'z-to-z'
            else:
                item["trans_type"] = 'z-to-t'
        elif "coinbase" in item["_source"]["vin"][0].keys():
            item["trans_type"] = 'Coinbase'
            item['value_transparent'] = value
        elif vout_times==0:
            item["trans_type"] = 't-to-z'
            for i in item["_source"]["vin"]:
                # value += i["value"]
                log.error(i)
            item['value_transparent'] =  0
        else:
            item["trans_type"]='Transparent'
            item['value_transparent'] = value
        item["_time"] = ts2t(item["_source"]["blocktime"])
    log.info("交易总数为"+str(total))
    pages = math.ceil(float(total) / perPage)
    context = {
        "labels": ['1', '2', '3', '4', '5', '6', '7'],
        "dataset3": [20, 40, 30, 85, 10, -20, 60],
        "trans_total": total,
        "trans_fields": current_app.config['BTC_FIELDS'],
        "pages": pages,
        "tr_option_list": current_app.config['TIME_RANGE_OPTIONS'],
        "columns": current_app.config['TRANS_TB_KEYS'],
        "page_title": '交易',
        "took": ans['took']
    }
    return context,latestTransList


def zcash_trans_detail_return(tsc_hash):
    result = zcashtransaction.zcash_get_transaction_byhash(tsc_hash)
    log.info("交易信息")
    context = {
        "page_title": '交易',
        "page_id": str(tsc_hash)
    }
    return result,context


def trans_search_return(start,perpage,rule):
    body1 = {
        "query": {
            "nested":{
                "path":"vin",
                "query":{
            "regexp":{
                "vin.addresses.keyword": {
                    "value": rule,
                }
            }
                }}},
        "from": start,
        "size": perpage,
        "sort": {"blockheight": {"order": "desc"}},
        "track_total_hits": True
    }
    body = {
        "query": {
            "nested":{
                "path":"vout",
                "query":{
            "regexp":{
                "vout.addresses.keyword": {
                    "value": rule,
                },
                "vin.addresses.keyword": {
                    "value": rule,
                }
            }
                }}},
        "from": start,
        "size": perpage,
        "sort": {"blockheight": {"order": "desc"}},
        "track_total_hits": True
    }
    result = btctransaction.transaction_ajax(body)
    result1 =btctransaction.transaction_ajax(body1)
    if result1 and result:            ##组合输入的结果和输出的结果
        took = result["took"]
        total = result["total"]+result1["total"]
        data = []
        i = 0
        j = 0
        while i < len(result) and j < len(result1):
            if result[i]["_source"]["blockheight"]>result1[j]["_source"]["blockheight"]:
                i = i+1
                data.append(result[i])
            else:
                j = j+1
                data.append(result1[j])
        while i<len(result):
            i = i + 1
            data.append(result[i])
        while j<len(result1):
            j = j + 1
            data.append(result1[j])
        result = {"took":took,"total":total,"result":data}
    elif result:
        pass
    elif result1:
        result =result1
    if result:
        total = result['total']
        resultt = result['result']
        log.info("交易总数为" + str(total))
        log.info(resultt)
        pages = math.ceil(total / perPage)
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
        return context, resultt
    else:
        return {},{}


def trans_ajax(rule,starttime,endtime,minvalue,maxvalue,moneytype,perpage,start):  ###交易数据区间阈值筛选，根据时间以及交易金额筛选
    log.info(starttime)
    if rule=="":
        rule="desc"
    if starttime=="":
        starttime = 1230998400
    else:
        starttime = time.strptime(starttime, '%Y-%m-%d %H:%M:%S')  ##比特币诞生的时间
        starttime = time.mktime(starttime)
    if endtime=="":
        endtime = time.time()
    else:
        endtime = time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S'))
    if minvalue == "":
        minvalue=0
    if maxvalue =="":
        maxvalue = 10000000
    minvalue = float(minvalue)*100000000
    maxvalue = float(maxvalue)*100000000
    starttime =time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(starttime))
    endtime = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(endtime))
    log.info("输入的结束时间是：" + str(endtime))
    if moneytype=='BTC':
        body={ "query": {
                "bool": {
                     "must":[
        {"range": {
        "blocktime": {
        "gte": starttime,
        "lte": endtime,
        }
        }},
        {"range": {"outputvalue":
                                       {"gte": minvalue,
                                        "lt": maxvalue}}}],
                }
            },
            "from":start,
            "size":perpage,
            "sort": {"blockheight": {"order": rule}},
            "track_total_hits": True
        }
    else:
        body = {"query": {
            "bool": {
                "must": [
                    {"range": {
                        "blocktime": {
                            "gte": starttime,
                            "lte": endtime,
                        }
                    }},
                    {"range": {"dayprice":
                                   {"gte": minvalue,
                                    "lt": maxvalue}}}],
            }
        },
            "from": start,
            "size": perpage,
            "sort": {"blockheight": {"order": rule}},
            "track_total_hits": True
        }
    log.info("++++++++++++++++++Serives++++++++++++++++++++++")
    log.info(body)
    result = btctransaction.transaction_ajax(body)
    total = result['total']
    resultt = result['result']
    log.info("交易总数为" + str(total))
    log.info(resultt)
    pages = math.ceil(total/ perPage)
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
    return context, resultt

