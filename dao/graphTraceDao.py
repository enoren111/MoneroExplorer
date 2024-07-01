# from app import es
from bee_var import btcblock_index, btctransaction_index,btctag_index,api_url,btc_cluster_search
from mutil.get_change_address import get_blockchair_change,get_optimal_change
# es = es.instance
from Serives.btcAddressDetail import *
from dao.txTraceDao import getAddressCluster,getAddressTag
import requests
import json
import time
import datetime
def get_change_address(txid,change):
    change_address = ""
    if change == "no":
        change_address = ""
    elif change == "blockchair":
        change_address = get_blockchair_change(txid)
    elif change == "optimal":
        change_address = get_optimal_change(txid)
    else:
        change_address = ""
    return change_address
def generateGraphData(txid,change):
    change_address=get_change_address(txid,change)
    print("change address:{}".format(change_address))
    result=es.get(index=btctransaction_index, id=txid)
    nodeid=0
    edgeid=0
    data = dict()
    node = []
    edge = []
    single_node={
        "id":str(nodeid),
        "name":txid,
        "txid":txid,
        "type":1,
        "in_len":len(result["_source"]["vin"]),
        "out_len":len(result["_source"]["vout"])
    }
    node.append(single_node)
    nodeid+=1
    # print(result)
    for i in range(len(result["_source"]["vin"])):
        item=result["_source"]["vin"][i]
        address=item["addresses"]
        value=item["value"]/(10**8)
        n=item["vout"]
        utxo=item["txid"]
        single_node={
            "id":str(nodeid),
            "name":address,
            "txid":txid,
            "type": 0,
            "utxo":utxo,
            "n":n,
            "cluster_id":getAddressCluster(address),
            "tag":getAddressTag(address)
        }
        single_edge={
            "id":"e"+str(edgeid),
            "value":value,
            "source":str(nodeid),
            "target":"0",
            "type":"in",
            "n":i,
            "txid":txid,
            "change":0
        }
        edgeid+=1
        nodeid+=1
        node.append(single_node)
        edge.append(single_edge)
    for item in result["_source"]["vout"]:
        address=item["scriptPubKey"]["addresses"]
        value=item["value"]
        n=item["n"]
        single_node = {
            "id": str(nodeid),
            "name": address,
            "txid": txid,
            "type":0,
            "n":n,
            "cluster_id": getAddressCluster(address),
            "tag": getAddressTag(address)
        }
        if address==change_address:
            change=1
        else:
            change=0
        single_edge = {
            "id": "e" + str(edgeid),
            "value": value,
            "target": str(nodeid),
            "source": "0",
            "type":"out",
            "n":n,
            "txid":txid,
            "change":change
        }
        edgeid += 1
        nodeid += 1
        node.append(single_node)
        edge.append(single_edge)
    data["node"] = node
    data["edge"] = edge
    data["nodeid"] = nodeid
    data["edgeid"] = edgeid
    print(data)
    return data
def addressTrace(utxo,n):
    body = {
        "query": {
            "bool":
                {
                    "must":
                        [
                            {
                                "nested": {
                                    "path": "vin",
                                    "query": {
                                        "term": {
                                            "vin.txid.keyword": {
                                                "value": utxo
                                            }
                                        }
                                    }
                                }
                            },
                            {
                                "nested": {
                                    "path": "vin",
                                    "query": {
                                        "term": {
                                            "vin.vout": {
                                                "value": n
                                            }
                                        }
                                    }
                                }
                            }
                        ]}
        }
    }
    tx = es.search(index=btctransaction_index, body=body)
    tx1 = None
    if tx["hits"]["total"]["value"] > 0:
        txs = tx["hits"]["hits"]
        for single_tx in txs:
            # print(single_tx)
            tag = 0
            vin = single_tx["_source"]["vin"]
            for i in range(len(vin)):
                item=vin[i]
                if item["txid"] == utxo and int(item["vout"]) == int(n):
                    tag = 1
                    tx1 = single_tx
                    single_node_value=item["value"]/(10**8)
                    single_node_out=i
                    break
            if tag == 1:
                break
    txid = tx1["_source"]['txid']
    single_node={
        "name": txid,
        "txid": txid,
        "type": 1,
        "value":single_node_value,
        "vout":single_node_out,
        "in_len":len(tx1["_source"]["vin"]),
        "out_len":len(tx1["_source"]["vout"])
    }
    return single_node
def graphtxTraceData(txid):
    result=es.get(index=btctransaction_index,id=txid)
    # print(result)
    node_list=[]
    for item in result["_source"]["vout"]:
        if "addresses" in item["scriptPubKey"]:
            address=item["scriptPubKey"]["addresses"]
            value=item["value"]
            n=item["n"]
            single_node={
                "name":address,
                "value":value,
                "n":n,
                "cluster_id": getAddressCluster(address),
                "tag": getAddressTag(address)
            }
            node_list.append(single_node)
    return node_list
def graphtxTraceBeforeData(txid):
    result=es.get(index=btctransaction_index,id=txid)
    node_list=[]
    for i in range(len(result["_source"]["vin"])):
        item=result["_source"]["vin"][i]
        if "addresses" in item:
            address=item["addresses"]
            value=item["value"]/(10**8)
            n=item["vout"]
            # print(item)
            single_node={
                "name":address,
                "value":value,
                "n":n,
                "num":i,
                "utxo":item["txid"],
                "cluster_id": getAddressCluster(address),
                "tag": getAddressTag(address)
            }
            node_list.append(single_node)
    return node_list
def graphAddressTraceBeforeData(txid,n):
    result=es.get(index=btctransaction_index,id=txid)
    value=result["_source"]["vout"][n]["value"]
    return {
        "value":value,
        "in_len":len(result["_source"]["vin"]),
        "out_len":len(result["_source"]["vout"])
    }