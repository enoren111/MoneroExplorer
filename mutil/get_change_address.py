import requests
import json
from elasticsearch import Elasticsearch
from config import config

ES_IP = config.es_ip
ES_PORT = config.es_port
TIMEOUT = 60
TX_INDEX = 'btc_tx_new'
es = Elasticsearch(hosts=ES_IP,port=ES_PORT,timeout=TIMEOUT)
def get_blockchair_change(tx):
    api="https://api.blockchair.com/bitcoin/dashboards/transaction/{}?privacy-o-meter=true".format(tx)
    result=requests.get(api)
    data=json.loads(result.text)
    clusters=data["data"][tx]["privacy-o-meter"]["clusterized"]
    # print(clusters)
    tx_data=get_address_by_txid(tx)
    # print(tx_data)
    for item in tx_data["vout"]:
        if item["address"] in clusters:
            return item["address"]
    return ""
def get_optimal_change(txid):
    tx = get_address_by_txid(txid)
    address=""
    if len(tx["vout"]) == 2:
        address1 = tx["vout"][0]["address"]
        address2 = tx["vout"][1]["address"]
        value1 = tx["vout"][0]["value"]
        value2 = tx["vout"][1]["value"]
        judge1 = 1
        judge2 = 1
        for item in tx["vin"]:
            if value1 > item["value"]:
                judge1 = 0
            if value2 > item["value"]:
                judge2 = 0
        if judge1 == 1 and judge2 == 0:
            address = address1
        if judge1 == 0 and judge2 == 1:
            address = address2
    else:
        address=""
    return address
def get_address_by_txid(txid):
    result=es.get(index=TX_INDEX,id=txid)
    tx={}
    tx["vin"]=[]
    tx["vout"]=[]
    for item in result["_source"]["vin"]:
        address=item["addresses"]
        value=item["value"]/(10**8)
        tx["vin"].append({
            "address":address,
            "value":value
        })
    for item in result["_source"]["vout"]:
        address=item["scriptPubKey"]["addresses"]
        value=item["value"]
        tx["vout"].append({
            "address":address,
            "value":value
        })
    return tx
