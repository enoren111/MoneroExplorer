# from app import es
from bee_var import btcblock_index, btctransaction_index,btctag_index,api_url,btc_cluster_search
# es = es.instance
from Serives.btcAddressDetail import *
import requests
import json
import time
import datetime
def getTransByAddress(address):
    body = {
        "query":
            {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "vin",
                                "query": {
                                    "term": {
                                        "vin.addresses.keyword": {
                                            "value": address
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "nested": {
                                "path": "vout",
                                "query": {
                                    "term": {
                                        "vout.scriptPubKey.addresses.keyword": {
                                            "value": address
                                        }
                                    }
                                }
                            }
                        }
                    ]
                }
            },
        "size": 3000
    }
    result = es.search(index=btctransaction_index, body=body)
    return result
def getTransById(txid):
    result = es.get(index=btctransaction_index, id=txid)
    # print(result)
    return result
def getTransByUTXO(utxo):
    result = es.get(index=btctransaction_index, id=utxo)
    return result
def getBeforeTrans(txid):
    result = es.get(index=btctransaction_index, id=txid)
    return result
def getNextTrans(txid,n):
    body={
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
                "value": txid
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
    result = es.search(index=btctransaction_index, body=body)
    return result
def getTxDetail1(txid):
    vin = []
    vout = []
    result = es.get(index=btctransaction_index, id=txid)
    # print(result)
    result=result["_source"]
    for item in result["vin"]:
        single_vin = {
            "address": item["addresses"],
            "value": item["value"]/10**8
        }
        vin.append(single_vin)
    for item in result["vout"]:
        single_out = {
            "address": item["scriptPubKey"]["addresses"],
            "value": item["value"]
        }
        vout.append(single_out)
    return {
        "vin": vin,
        "vout": vout
    }
def getTraceTxDetail(txid):
    result = es.get(index=btctransaction_index, id=txid)
    result=result['_source']
    result_dict={}
    blocktime=result["blocktime"]
    timestamp = time.mktime(time.strptime(blocktime, '%Y-%m-%dT%H:%M:%S'))
    datetime_struct = datetime.datetime.fromtimestamp(timestamp)
    datetime_obj = (datetime_struct + datetime.timedelta(hours=8))
    datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    result_dict["tx_time"]=datetime_str
    result_dict["input_num"]=len(result["vin"])
    result_dict["output_num"] = len(result["vout"])
    result_dict["height"]=result["blockheight"]
    result_dict["volume"]=str(result["volume"]/10**8)+" BTC"
    print(result_dict)
    return result_dict
def getTraceAddressDetail(address):
    result = getAddressTX(address, 1)
    try:
        result2 = getAddressRecv(address)
        recv = round(result2['aggregations']['sum']['value_count']['value'], 4)
        recv_num = result2['hits']['total']['value']
    except Exception as e:
        print(e.args)
        recv = "error"
        recv_num = "error"
    try:
        result3 = getAddressSent(address)
        sent = round(result3['aggregations']['sum']['value_count']['value'] / 10 ** 8, 4)
        sent_num = result3['hits']['total']['value']
    except Exception as e:
        print(e.args)
        sent = "error"
        sent_num = "error"
    if recv == "error" or sent == "error":
        balance = "error"
    else:
        balance = round(recv - sent, 4)
    txs = result['hits']['hits']
    total = int(result['hits']['total']['value'])
    tx_list = []
    if len(txs) > 0:
        first_seen = txs[0]['_source']['blocktime'].replace("T", " ")
    else:
        first_seen = ""
    result_dict={}
    result_dict["total"]=total
    result_dict["first_seen"] = first_seen
    result_dict["recv"] = str(recv)+" BTC"
    result_dict["sent"] = str(sent)+" BTC"
    result_dict["recv_num"] = recv_num
    result_dict["sent_num"] = sent_num
    result_dict["balance"] = str(balance)+" BTC"
    result_dict["cluster_id"]=getAddressCluster(address)
    return result_dict
def traceBeforeTx(utxo):
    # print(utxo)
    result=es.get(index=btctransaction_index,id=utxo)
    # print(result)
    vins=result["_source"]["vin"]
    addresses = []
    for item in vins:
        if 'addresses' in item:
            address=item["addresses"]
            if address != 'nonstandard':
                value = item['value']
                n = item['vout']
                address_dict = {
                    'utxo':item["txid"],
                    'txid': item["txid"],
                    'n': n,
                    'address': address,
                    'value': value/(10**8),
                    'tag': getAddressTag(address)
                }
                addresses.append(address_dict)
    return addresses
def traceAferTx(utxo,n):
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
    tx1=None
    if tx["hits"]["total"]["value"] > 0:
        txs = tx["hits"]["hits"]
        # print(len(txs))
        for single_tx in txs:
            # print(single_tx)
            tag=0
            vin = single_tx["_source"]["vin"]
            for item in vin:
                # print("txid:{} n:{}".format(item["txid"],item["vout"]))
                # print("source_txid:{} source_n:{}".format(utxo,n))
                if item["txid"] == utxo and int(item["vout"]) == int(n):
                    print("correct")
                    tag=1
                    tx1= single_tx
                    break
            if tag==1:
                break
    # print(tx1)
    #返回点的集合
    txid=tx1["_source"]['txid']
    vouts=tx1["_source"]["vout"]
    change=optimalChange(txid)
    # print(tx)
    # vouts=tx["vout"]
    # print(vouts)
    # for item in vouts:
    #     print(item)
    addresses=[]
    for item in vouts:
        if 'addresses' in item['scriptPubKey']:
            address=item['scriptPubKey']["addresses"]
            if address !='nonstandard':
                value=item['value']
                n=item['n']
                if change!=None and change["address"]==address:
                    change_tag=1
                else:
                    change_tag=0
                address_dict={
                    'txid':txid,
                    'n':n,
                    'address':address,
                    'value':value,
                    'tag':getAddressTag(address),
                    'change_tag':change_tag,
                    "cluster_id":getAddressCluster(address)
                }
                addresses.append(address_dict)
    # print(addresses)
    return addresses
def getAddressTag(address):
    # address="1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s"
    # print(address)
    try:
        result = es.get(index=btctag_index, id=address)
        result=result["_source"]["labels"]
        return result
    except:
        return None
def getTxDetail(txid):
    result = es.get(index=btctransaction_index, id=txid)
    result=result["_source"]
    vin=result["vin"]
    vout=result["vout"]
    vin_list=[]
    vout_list=[]
    # print(result)
    for item in vout:
        if "addresses" in item["scriptPubKey"]:
            address=item["scriptPubKey"]["addresses"]
            if address !="nonstandard":
                value=item["value"]
                vout_list.append(
                    {
                        "address":address,
                        "value":value
                    }
                )
    for item in vin:
        address=item["addresses"]
        value=item["value"]
        if address !="nonstandard":
            vin_list.append({
            "address":address,
            "value":value/(10**8)
        })
    result_dict={}
    result_dict["vin"]=vin_list
    result_dict["vout"]=vout_list
    # print(result_dict)
    return result_dict
def optimalChange(txid):
    tx_detail=getTxDetail(txid)
    result_list=[]
    for item in tx_detail["vout"]:
        address=item["address"]
        value=item["value"]
        flag=1
        for vin_item in tx_detail["vin"]:
            in_value=vin_item["value"]
            if value<in_value:
                continue
            else:
                flag=0
                break
        if flag==1:
            result_list.append({
                "address":address,
                "value":value
            })
    print(result_list)
    if len(result_list)==1:
        return result_list[0]
    else:
        return None
def getAddressCluster(address):
    try:
        result=es.get(index=btc_cluster_search, id=address)
        if result["found"]==True:
            cluster_id="U"+str(result["_source"]["cluster_id"])
        else:
            cluster_id="无聚类信息"
    except:
        cluster_id="无聚类信息"
    print("cluster:{}".format(cluster_id))
    return cluster_id