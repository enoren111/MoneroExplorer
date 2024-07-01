from datetime import timedelta, datetime

from pytz import timezone

from Model.dataValidation import DataValidation_transaction
from Serives import btcblock, xmrtransaction
from Serives import btctransaction
from flask import request, render_template
from flask import current_app
import math

from dao.datainterchange import search_transaction, xmr_search_transaction
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


from utils import ts2t, judge_tr_endpoint


def sb_for_block(size, start, order="desc", time_rang_id=4):  # search区块 body
    # print(time_rang_id)
    if time_rang_id == 4:
        return {
            "query": {
                "match_all": {}
            },
            "size": size,
            "from": start,
            "sort": {"block_height": {"order": order}},
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
            "sort": {"block_height": {"order": order}},
            "track_total_hits": True
        }
def xmr_trans_class(perPage, start,time_rang_id=0, order="desc",block_trade=150000000):
    body=sb_for_block(perPage, start, order, time_rang_id)
    # body['size']=0
    # body['query']['range']={
    #   "as_json.rct_signatures.txnFee":{
    #     "gte": block_trade#gte 是大于等于 gt是大于 lte是小于等于 lt是小于
    #   }
    # }
    # print(body)
    page_data=xmr_search_transaction(body)
    
    

    total = page_data['hits']['total']['value']
    pages = math.ceil(float(total) / perPage)
    latestTransList = page_data['hits']['hits']#['_source']
    
        
    for item in latestTransList:  ###代码重构
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


    body['size']=0
    body['from']=0
    if time_rang_id==4:
        del body['query']['match_all']
        # del body['query']['bool']['should']
        body['query']={'bool':{'must':[{"range": {"as_json.rct_signatures.txnFee":{"gte": block_trade}}}]}}#['bool']['must']=[{"range": {"as_json.rct_signatures.txnFee":{"gte": block_trade}}}]
    else:
        a=body['query']['bool']['should'][0]
        body['query']['bool']['must']=[a,{"range": {"as_json.rct_signatures.txnFee":
                                       {"gte": block_trade}}}]
        
    # print(body)
    ans=xmr_search_transaction(body)
    print('大于',ans)
    block_trade_total=ans['hits']['total']['value']
    if time_rang_id==4:
        
        body['query']['bool']['must'][0]={"range": {"as_json.rct_signatures.txnFee":
                                       {"lt": block_trade}}}
    else:
        body['query']['bool']['must'][1]={"range": {"as_json.rct_signatures.txnFee":{"lt": block_trade}}}
    
    # print(body)
    ans=xmr_search_transaction(body)
    print('小于',ans)
    no_block_trade_total=ans['hits']['total']['value']
    return block_trade_total,no_block_trade_total,latestTransList,total


    

def xmr_trans_statistics( order="desc"):

    datas=[]
    datas2=[]
    for i in range(5):
        body=sb_for_block(1, 1, order, i)
        

    
    
        sum_body=body
        sum_body['size']=0
        sum_body["aggs"]= {
                "my_stats": {
                    "stats": {
                        "field": "as_json.rct_signatures.txnFee"
                    }
                },
                "my_stats1": {
                    "stats": {
                        "field": "as_json.vout.amount"
                    }
                }
            }
        res=xmr_search_transaction(sum_body)
        
    
        datas.append(res['aggregations']['my_stats']['sum'])
        datas2.append(res['aggregations']['my_stats1']['sum'])


    # print(datas,datas2)
    return datas,datas2

    

def xmr_trans_return(perPage, start,time_rang_id=0, order="desc",d=False):
    body=sb_for_block(perPage, start, order, time_rang_id)
    if d:
        body['size']=10000
        body['from']=0
        ans=xmr_search_transaction(body)
        result=[]
        for i in ans['hits']['hits']:
            times = i["_source"]['block_timestamp']
            i['time1'] = datetime.utcfromtimestamp(times)
            i['time_bj'] = i['time1'] + timedelta(hours=8)
            txn=i['_source']['as_json']['rct_signatures'].get('txnFee','')
            result.append([i['_source']['tx_hash'],i['_source']['block_height'],i['time_bj'],i['_source']['as_json']['vout'][0]['amount'],txn,i['_source']['as_json']['version'],i['_type']])
        return None,result
        

    
    ans=xmr_search_transaction(body)
    sum_body=body
    sum_body['size']=0
    sum_body["aggs"]= {
            "my_stats": {
                "stats": {
                    "field": "as_json.rct_signatures.txnFee"
                }
            }
        }
    res=xmr_search_transaction(sum_body)
    print(res)
    total_txnFee=res['aggregations']['my_stats']['sum']


    total = ans['hits']['total']['value']
    latestTransList = ans['hits']['hits']#['_source']

    for item in latestTransList:  ###代码重构
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
        "took": ans['took'],
        'total_txnFee':total_txnFee
    }
    return context, latestTransList

def xmr_home_trans_return(perPage, start):
    # ans = btctransaction.get_transaction(btctransaction.AllTranses(size=perPage, start=start, order=rule))
    body = {
        "query": {
            "match_all": {}
        },
        "size": perPage,
        "from": start,
        "sort": {"block_height": {"order": "desc"}}  # 性能问题
    }
    ans=xmr_search_transaction(body)
    print("ans:;;;;;;;;;;;;;;;;;;;;",ans)

    total = ans['hits']['total']['value']
    latestTransList = ans['hits']['hits']
    # log.error(ans)
    for item in latestTransList:  ###代码重构
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
    result = xmrtransaction.get_transaction_byhash(tsc_hash)
    log.info("交易信息")
    context = {
        "page_title": '交易',
        "page_id": str(tsc_hash)
    }
    return result, context

def trans_return(perPage, start, rule='desc'):
    ans = xmrtransaction.get_transaction(xmrtransaction.AllTranses(size=perPage, start=start, order=rule))
    total = ans['total']
    latestTransList = ans['result']
    for item in latestTransList:  ###代码重构
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

def trans_ajax_tx(rule,starttime,endtime,minvalue,maxvalue,moneytype,perpage,start):  ###交易数据区间阈值筛选，根据时间以及交易金额筛选
    log.info(starttime)
    if rule=="":
        rule="desc"
    if starttime:
        starttime = time.strptime(starttime, '%Y-%m-%d %H:%M:%S')
        starttime = time.mktime(starttime)
    else:
        starttime = time.mktime((2014, 4, 18, 0, 0, 0, 0, 0, 0))  # 门罗币诞生时间
    if endtime:
        endtime = time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S'))
    else:
        endtime = time.time()

    if minvalue == "":
        minvalue=0
    if maxvalue =="":
        maxvalue = 10000000
    minvalue = float(minvalue)*100000000
    maxvalue = float(maxvalue)*100000000
    # starttime =time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(starttime))
    # endtime = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(endtime))
    log.info("输入的结束时间是：" + str(endtime))
    if moneytype=='XMR':
        body={ "query": {
                    "bool": {
                        "must":[
                            {
                                "range": {
                                    "block_timestamp": {
                                        "gte": starttime,
                                        "lte": endtime,
                                    }
                                }
                            }
                            # ,
                            # {
                            #     "range":
                            #         {
                            #             "outputvalue":{
                            #                 "gte": minvalue,
                            #                 "lt": maxvalue
                            #             }
                            #         }
                            # }
                        ],
                    }
                },
                "from":start,
                "size":perpage,
                "sort": {"block_height": {"order": rule}},
                "track_total_hits": True
        }
    else:
        body = {"query": {
            "bool": {
                "must": [
                    {"range": {
                        "block_timestamp": {
                            "gte": starttime,
                            "lte": endtime,
                        }
                    }}
                    # ,
                    # {"range": {"dayprice":
                    #                {"gte": minvalue,
                    #                 "lt": maxvalue}}}
                ],
            }
        },
            "from": start,
            "size": perpage,
            "sort": {"block_height": {"order": rule}},
            "track_total_hits": True
        }
    log.info("++++++++++++++++++Serives++++++++++++++++++++++")
    log.info(body)
    result = xmrtransaction.transaction_ajax(body)
    print("ajax starttime: ----",starttime)
    print("ajax endtime: ----",endtime)

    print("ajax transaction: ----",result)
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




