from datetime import timedelta, datetime

from pytz import timezone

from Model.dataValidation import DataValidation_transaction
from Serives import btcblock
from Serives import btctransaction
from flask import request, render_template
from flask import current_app
import math

from dao.datainterchange import search_transaction
# from es1 import es
from utils import ts2t
import json
from config import config
from log import log
from Serives import btctransaction
from dao import datainterchange
import time
from bee_var import perPage

log = log.init_logger(config.log_filepath)

def btc_home_trans_return(perPage, start):
    # ans = btctransaction.get_transaction(btctransaction.AllTranses(size=perPage, start=start, order=rule))
    body = {
        "query": {
            "match_all": {}
        },
        "size": perPage,
        "from": start,
        "sort": {"blockheight": {"order": "desc"}}  # 性能问题
    }
    ans=[]#search_transaction(body)
    total =0 #ans['hits']['total']['value']
    latestTransList = []#ans['hits']['hits']
    # log.error(ans)
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
        time_utc = datetime.strptime(item["_source"]['blocktime'].replace("T", " "), "%Y-%m-%d %H:%M:%S")
        item['time_bj'] = time_utc + timedelta(hours=8)

    log.info("交易总数为" + str(total))
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
        "took": [{'height':10}]#ans['took']
    }
    return context, latestTransList


def trans_return(perPage, start, rule='desc'):
    ans = btctransaction.get_transaction(btctransaction.AllTranses(size=perPage, start=start, order=rule))
    total = ans['total']
    latestTransList = ans['result']
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
        time_utc = datetime.strptime(item["_source"]['blocktime'].replace("T", " "), "%Y-%m-%d %H:%M:%S")
        item['time_bj'] = time_utc + timedelta(hours=8)

    log.info("交易总数为" + str(total))
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
    return context, latestTransList


def trans_detail_return(tsc_hash):
    result = btctransaction.get_transaction_byhash(tsc_hash)
    log.info("交易信息")
    context = {
        "page_title": '交易',
        "page_id": str(tsc_hash)
    }
    return result, context


def trans_search_return(start, perpage, rule):
    body1 = {
        "query": {
            "nested": {
                "path": "vin",
                "query": {
                    "regexp": {
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
            "nested": {
                "path": "vout",
                "query": {
                    "regexp": {
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
    result1 = btctransaction.transaction_ajax(body1)
    if result1 and result:  ##组合输入的结果和输出的结果
        took = result["took"]
        total = result["total"] + result1["total"]
        data = []
        i = 0
        j = 0
        while i < len(result) and j < len(result1):
            if result[i]["_source"]["blockheight"] > result1[j]["_source"]["blockheight"]:
                i = i + 1
                data.append(result[i])
            else:
                j = j + 1
                data.append(result1[j])
        while i < len(result):
            i = i + 1
            data.append(result[i])
        while j < len(result1):
            j = j + 1
            data.append(result1[j])
        result = {"took": took, "total": total, "result": data}
    elif result:
        pass
    elif result1:
        result = result1
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
        return {}, {}

def trans_ajax_tx(rule,starttime,endtime,minvalue,maxvalue,moneytype,perpage,start):  ###交易数据区间阈值筛选，根据时间以及交易金额筛选
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
def trans_ajax(rule, starttime, endtime, minvalue, maxvalue, inputaddr, outputaddr, height, fee,input_num,output_num,topic,specvalue, moneytype, perpage,start):  ###交易数据区间阈值筛选，根据时间以及交易金额筛选
    log.info(starttime)
    mustin = []
    mustout = []
    if rule == "":
        rule = "desc"
    if starttime == "":
        starttime = 1230998400##比特币诞生的时间
    else:
        starttime = time.strptime(starttime, '%Y-%m-%d %H:%M:%S')
        starttime = time.mktime(starttime)
    if endtime == "":
        endtime = time.time()
    else:
        endtime = time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S'))
    if minvalue == "":
        minvalue = 0
    if maxvalue == "":
        maxvalue = 10000000
    if specvalue == "":
        specvalue = 0
    if fee != "":
        fee = float(fee) * 100000000
    minvalue = float(minvalue) * 100000000
    maxvalue = float(maxvalue) * 100000000
    specvalue= float(specvalue) * 100000000
    starttime=starttime-28800.0
    starttime = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(starttime))
    endtime=endtime-28800.0
    endtime = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(endtime))
    inputaddr = ".*" + inputaddr + ".*"
    outputaddr = ".*" + outputaddr + ".*"
    log.info("输入的结束时间是：" + str(endtime))
    str_input = ',{"nested": {"path": "vin","query": {"regexp": {"vin.addresses.keyword": {"value": "' + inputaddr + '" }}}}} '
    str_output = ',{"nested": {"path": "vout","query": {"regexp": {"vout.scriptPubKey.addresses.keyword": {"value": "' + outputaddr + '"  }}}}}'
    str_rule = '"' + rule + '"'
    str_time = '{"range": {"blocktime": {"gte": "' + str(starttime) + '","lte": "' + str(endtime) + '"}}}'
    str_value = ',{"range": {"inputvalue":{"gte": ' + str(minvalue) + ',"lt": ' + str(maxvalue) + '}}}'
    str_row = '"from":  ' + str(start) + ',"size": ' + str(
        perpage) + ',"sort": {"blockheight": {"order":  ' + str_rule + ' }}, "track_total_hits": true'
    str_height = ',{"term": {"blockheight": "' + str(height) + '"}}'
    str_fee = ' ,{"term": {"fee":"' + str(fee) + '" }}'
    str_input_num=' ,{"term": {"vin_size":"'+ str(input_num) + '"}}'
    str_output_num=',{"term": {"vout_size":"' + str(output_num) + '" }}'
    str_topic=',{"term": {"topic_new":"' + str(topic) + '" }}'
    str_specvalue = ',{"term": {"inputvalue":"' + str(specvalue) + '" }}'
    if height == "":
        str_height = ''
    if inputaddr == ".*.*":
        str_input = ''
    if outputaddr == ".*.*":
        str_output = ''
    if fee == "":
        str_fee = ''
    if input_num == "":
        str_input_num = ''
    if output_num == "":
        str_output_num = ''
    if topic=="":
        str_topic=''
    if specvalue==0:
        str_specvalue=''
    if moneytype == 'BTC':
        body = """{
                "query":
                    {
                        "bool": {
                            "must": [""" + str(str_time).replace("'", "") + """
                                     """ + str(str_value).replace("'", "") + """
                                    """ + str(str_input).replace("'", "") + """
                                     """ + str(str_output).replace("'", "") + """
                                     """ + str(str_height).replace("'", "") + """
                                     """ + str(str_fee).replace("'", "") + """
                                     """ + str(str_input_num).replace("'", "") + """
                                     """ + str(str_output_num).replace("'", "") + """
                                     """ + str(str_topic).replace("'", "") + """
                                     """ + str(str_specvalue).replace("'", "") + """
                                     ]
                        }
                    },
                """ + str(str_row).replace("'", "") + """
            }"""

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
    log.error(body)
    result = btctransaction.transaction_ajax(body)
    if result:
        total = result['total']
        resultt = result['result']
        took=result['took']
    else:
        total = 0
        resultt=0
        took=0
    log.info("交易总数为" + str(total))
    # log.info(resultt)
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
        "took": took
        }
    return context, resultt

