'''
Author: @xiaonancheng
Date: 2023-03-27 15:09:12
https://www.cnblogs.com/xiaonancheng
Copyright (c) 2023 by @xiaonancheng, All Rights Reserved. 
'''
from datetime import datetime, timedelta

from dao.btcAddressData import getAddressTX,getAddressSent,getAddressRecv
def handleAddressTx(address,page):
    result=getAddressTX(address,page)
    try:
        result2=getAddressRecv(address)
        recv=round(result2['aggregations']['sum']['value_count']['value'],4)
        recv_num=result2['hits']['total']['value']
    except Exception as e:
        print(e.args)
        recv="error"
        recv_num="error"
    try:
        result3=getAddressSent(address)
        sent = round(result3['aggregations']['sum']['value_count']['value']/10**8,4)
        sent_num=result3['hits']['total']['value']
    except Exception as e:
        print(e.args)
        sent="error"
        sent_num="error"
    if recv=="error" or sent=="error":
        balance="error"
    else:
        balance=round(recv-sent,4)
    txs = result['hits']['hits']
    total = int(result['hits']['total']['value'])
    tx_list = []
    if len(txs)>0:
        first_seen=txs[0]['_source']['blocktime']
        time_utc = datetime.strptime(txs[0]['_source']['blocktime'].replace("T", " "), "%Y-%m-%d %H:%M:%S")
        first_seen_bj = time_utc + timedelta(hours=8)

    else:
        first_seen = "暂无信息"
        first_seen_bj="暂无信息"
    for tx in txs:
        single_tx = dict()
        tx_source = tx['_source']
        single_tx['inputvalue']=tx_source['inputvalue']/10**8
        single_tx['outputvalue'] = tx_source['outputvalue'] / 10 ** 8
        single_tx['fee'] = tx_source['fee'] / 10 ** 8
        single_tx['hash'] = tx_source['hash']
        single_tx["txid"]=tx_source["txid"]
        # single_tx['blocktime'] = tx_source['blocktime'].replace("T", " ")
        time_utc = datetime.strptime(tx_source['blocktime'].replace("T", " "), "%Y-%m-%d %H:%M:%S")
        single_tx['time_bj'] = time_utc + timedelta(hours=8)
        txin_list = []
        txout_list = []
        vin = tx_source['vin']
        vout = tx_source['vout']
        for single_vin in vin:
            address = single_vin['addresses']
            value = single_vin['value']
            single_vin_info = {
                "address": address,
                "value": value / 10 ** 8
            }
            txin_list.append(single_vin_info)
        for single_vout in vout:
            value = single_vout['value']
            address = single_vout['scriptPubKey']['addresses']
            single_vout_info = {
                "address": address,
                "value": value
            }
            txout_list.append(single_vout_info)
        single_tx['vin'] = txin_list
        single_tx['vout'] = txout_list
        tx_list.append(single_tx)
    return tx_list,total,first_seen,recv,sent,recv_num,sent_num,balance,first_seen_bj

def handleAddressBalance(address):
    try:
        result2=getAddressRecv(address)
        recv=round(result2['aggregations']['sum']['value_count']['value'],4)
        recv_num=result2['hits']['total']['value']
    except Exception as e:
        print(e.args)
        recv="error"
        recv_num="error"
    try:
        result3=getAddressSent(address)
        sent = round(result3['aggregations']['sum']['value_count']['value']/10**8,4)
        sent_num=result3['hits']['total']['value']
    except Exception as e:
        print(e.args)
        sent="error"
        sent_num="error"
    if recv=="error" or sent=="error":
        balance="error"
    else:
        balance=round(recv-sent,4)
    return balance