from queue import Queue
from dao.txTraceDao import *
from mysql_dealer import mysql_dealer
import json
def getInDict(tx):
    res_list = []
    result = tx["_source"]
    # utxo = result["txid"]
    vin = result["vin"]
    for item in vin:
        try:
            address = item["addresses"]
            if address != "nonstandard":
                res_list.append(
                    {
                        "utxo": item["txid"],
                        "n": item['vout'],
                        "address": address,
                        "value": item["value"]/(10**8)
                    }
                )

        except:
            pass
    return res_list
def getOutDict(tx):
    res_list=[]
    result=tx["_source"]
    utxo=result["txid"]
    vout=result["vout"]
    for item in vout:
        try:
            address=item["scriptPubKey"]["addresses"]
            if address!="nonstandard":
                res_list.append(
                    {
                        "utxo":utxo,
                        "n":item['n'],
                        "address":address,
                        "value":item["value"]
                    }
                )

        except:
            pass
    return res_list
def txTrace(origin_tx):
    try:
        tx=getTransById(origin_tx)
    except:
        return []
    out_list=getOutDict(tx)
    depth=3
    tx_list=[]
    tx_list.append(origin_tx)
    q = Queue()
    for single_utxo in out_list:
        q.put(single_utxo)
    while depth>=0:
        print("depth:{}".format(depth))
        q_size=q.qsize()
        for _ in range(0,q_size):
            utxo_dict=q.get()
            tx=getNextTrans(utxo_dict["utxo"],utxo_dict["n"])
            if tx["hits"]["total"]["value"]>0:
                tx=tx["hits"]["hits"][0]
                txid=tx["_id"]
                if txid not in tx_list:
                    tx_list.append(txid)
                    print(txid)
                out_list=getOutDict(tx)
                for single_utxo in out_list:
                    q.put(single_utxo)
        depth=depth-1
    return tx_list
def txTrace1Before(origin_tx,depth):
    data = dict()
    node = []
    edge = []
    nodeid = 0
    edgeid = 0
    try:
        tx = getTransById(origin_tx)
    except Exception as e:
        print(e)
        return []
    single_node = {
        "id": str(nodeid),
        "address": "终"
    }
    node.append(single_node)
    nodeid += 1
    in_list = getInDict(tx)
    source_id = 0
    # print(out_list)
    q = Queue()
    for single_in in in_list:
        # print("single_out:{}".format(single_out))
        single_in["id"] = nodeid
        single_node = {
            "id": str(nodeid),
            "address": single_in["address"],
            "utxo": single_in["utxo"],
            "n": single_in["n"],
            "tag": getAddressTag(single_in["address"]),
            "cluster_id":getAddressCluster(single_in["address"])
        }
        node.append(single_node)
        single_edge = {
            "id": "e" + str(edgeid),
            "value": single_in["value"],
            "txid": origin_tx,
            "source": source_id,
            "target": single_node["id"]
        }
        queue_dict = {
            "id": str(nodeid),
            "utxo": single_in["utxo"]
        }
        nodeid += 1
        edgeid += 1
        edge.append(single_edge)
        # print(single_node)
        # print(single_edge)
        q.put(queue_dict)
    depth = depth - 1
    while depth >= 1:
        print("depth:{}".format(depth))
        q_size = q.qsize()
        # print(q_size)
        for _ in range(0, q_size):
            utxo_dict = q.get()
            print(utxo_dict)
            tx = getBeforeTrans(utxo_dict["utxo"])
            if "_source" in tx:
                txid = tx["_source"]["txid"]
                source_id = utxo_dict["id"]
                in_list = getInDict(tx)
                for single_utxo in in_list:
                    # print(single_utxo)
                    single_node = {
                        "id": str(nodeid),
                        "address": single_utxo["address"],
                        "utxo": single_utxo["utxo"],
                        "n": single_utxo["n"],
                        "tag": getAddressTag(single_utxo["address"])
                    }
                    single_edge = {
                        "id": "e" + str(edgeid),
                        "value": single_utxo["value"],
                        "source": source_id,
                        "target": nodeid,
                        "txid": txid
                    }
                    queue_dict = {
                        "id": str(nodeid),
                        "address": single_node["address"],
                        "utxo": single_utxo["utxo"],
                        "n": single_utxo["n"]
                    }

                    node.append(single_node)
                    edge.append(single_edge)
                    q.put(queue_dict)
                    nodeid += 1
                    edgeid += 1
                    # print(single_node)
                    # print(single_edge)
        depth = depth - 1
    data["node"] = node
    data["edge"] = edge
    data["nodeid"] = nodeid
    data["edgeid"] = edgeid
    # print(data)
    return data
def txTrace1(origin_tx,depth,findChange):
    data=dict()
    node=[]
    edge=[]
    nodeid=0
    edgeid=0
    try:
        tx=getTransById(origin_tx)
        change=findChange(origin_tx)
    except Exception as e:
        print(e)
        return []
    single_node={
        "id":str(nodeid),
        "address":"源"
    }
    node.append(single_node)
    nodeid+=1
    out_list=getOutDict(tx)
    source_id=0
    # print(out_list)
    q = Queue()
    for single_out in out_list:
        # print("single_out:{}".format(single_out))
        single_out["id"]=nodeid
        single_node={
            "id":str(nodeid),
            "address":single_out["address"],
            "utxo":single_out["utxo"],
            "n":single_out["n"],
            "tag":getAddressTag(single_out["address"]),
            "cluster_id":getAddressCluster(single_out["address"])
        }
        node.append(single_node)
        if change!=None and change["address"]==single_out["address"]:
            change_tag=1
        else:
            change_tag=0
        single_edge={
            "id":"e"+str(edgeid),
            "value":single_out["value"],
            "txid":origin_tx,
            "source":source_id,
            "target":single_node["id"],
            "tag":change_tag,
            "cluster_id": getAddressCluster(single_out["address"])
        }
        queue_dict={
            "id":str(nodeid),
            "utxo":single_out["utxo"],
            "n":single_out["n"]
        }
        nodeid += 1
        edgeid+=1
        edge.append(single_edge)
        # print(single_node)
        # print(single_edge)
        q.put(queue_dict)
    depth=depth-1
    while depth>=1:
        print("depth:{}".format(depth))
        q_size=q.qsize()
        # print(q_size)
        for _ in range(0,q_size):
            utxo_dict=q.get()
            # print(utxo_dict)
            tx=getNextTrans(utxo_dict["utxo"],utxo_dict["n"])
            if tx["hits"]["total"]["value"]>0:
                txs=tx["hits"]["hits"]
                for single_tx in txs:
                    # print(single_tx)
                    vin=single_tx["_source"]["vin"]
                    for item in vin:
                        if item["txid"]==utxo_dict["utxo"] and item["vout"]==utxo_dict["n"]:
                            tx=single_tx
                            break
                # tx=tx["hits"]["hits"][0]
                # print(tx)
                if "_source" in tx:
                    txid=tx["_source"]["txid"]
                    change=findChange(txid)
                    source_id=utxo_dict["id"]
                    out_list=getOutDict(tx)
                    for single_utxo in out_list:
                        # print(single_utxo)
                        single_node={
                            "id":str(nodeid),
                            "address":single_utxo["address"],
                            "utxo":txid,
                            "n":single_utxo["n"],
                            "tag":getAddressTag(single_utxo["address"]),
                            "cluster_id": getAddressCluster(single_utxo["address"])
                            # "cluster_id": getAddressCluster(single_utxo["address"])
                        }
                        if change!=None and change["address"]==single_utxo["address"]:
                            change_tag=1
                        else:
                            change_tag=0
                        single_edge={
                            "id":"e"+str(edgeid),
                            "value":single_utxo["value"],
                            "source":source_id,
                            "target":nodeid,
                            "txid":txid,
                            "tag":change_tag
                        }
                        queue_dict={
                            "id":str(nodeid),
                            "address":single_node["address"],
                            "utxo":single_utxo["utxo"],
                            "n":single_utxo["n"]
                        }

                        node.append(single_node)
                        edge.append(single_edge)
                        q.put(queue_dict)
                        nodeid+=1
                        edgeid+=1
                        # print(single_node)
                        # print(single_edge)
        depth=depth-1
    data["node"]=node
    data["edge"]=edge
    data["nodeid"]=nodeid
    data["edgeid"]=edgeid
    # print(data)
    return data
def saveTraceTxData(beizhu,data):
    data=json.dumps(data,ensure_ascii=False)
    # print(data)
    print(beizhu)
    sql_dealer = mysql_dealer("txTrace")
    sql="insert into traceTx (beizhu,jsondata) VALUES ('{}','{}')".format(beizhu,data)
    sql_dealer.get_cursor_exe_result(sql)
    sql_dealer.db.commit()
def txTraceHistory():
    sql_dealer = mysql_dealer("txTrace")
    sql="select id,beizhu from traceTx"
    result=sql_dealer.get_cursor_exe_result(sql)
    print(result)
    result_dict=[]
    for single in result:
        result_dict.append({
            "id":single[0],
            "beizhu":single[1]
        })
    return result_dict
def gettraceHistoryData(id):
    sql_dealer = mysql_dealer("txTrace")
    print(id)
    sql="select jsondata from traceTx where id={}".format(id)
    result = sql_dealer.get_cursor_exe_result(sql)
    result=result[0][0]
    result=json.loads(result)
    print(result)
    return result