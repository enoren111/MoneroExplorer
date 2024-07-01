from Serives import btcblock
from Serives import btctransaction
from flask import request
from flask import current_app
import math
from utils import ts2t
import json
from config import config
from log import log
from Serives import btctransaction
from dao import datainterchange
import time
from bee_var import perPage
log = log.init_logger(config.log_filepath)


# 重写
def my_trans_return(perPage, start, rule='desc'):
    ans = btctransaction.get_my_transaction(btctransaction.AllTranses(size=perPage, start=start,  order=rule))
    total = ans['total']
    latestTransList = ans['result']
    result_list = []
    for item in latestTransList:
        tran_hash = item['_id']
        for tran in item['_source']['trans']:
            hash = tran_hash
            id = tran['id']
            time = tran['time']
            amount = tran['amount']
            from_addr = tran['input']['addr']
            to_addr = tran['output']['addr']
            list = {'hash': hash, 'id': id, "time": time, 'amount': amount,
                    'from_addr': from_addr, 'to_addr': to_addr}
            result_list.append(list)

    pages = math.ceil(float(total) / perPage)
    context = {
        "labels": ['1', '2', '3', '4', '5', '6', '7'],
        "dataset3": [20, 40, 30, 85, 10, -20, 60],
        "trans_total": total,
        "trans_fields": current_app.config['BTC_FIELDS'],
        "pages": pages,
        "tr_option_list": current_app.config['TIME_RANGE_OPTIONS'],
        "columns": current_app.config['TRANS_TB_KEYS'],
        "page_title": '大额交易',
        "took": ans['took']
    }
    return context, result_list


def trans_detail_return(tsc_hash):
    result = btctransaction.get_transaction_byhash(tsc_hash)
    log.info("交易信息")
    context = {
        "page_title": '交易',
        "page_id": str(tsc_hash)
    }
    return result,context


def trans_search_return(start,perpage,rule):
    rule=".*"+rule+".*"
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
        "track_total_hits": True
    }
    print(body1)
    result =btctransaction.transaction_ajax(body1)
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


def trans_ajax(rule,starttime, endtime,minvalue,maxvalue,moneytype,perpage,start):  ###交易数据区间阈值筛选，根据时间以及交易金额筛选
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

