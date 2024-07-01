#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re

import elasticsearch.helpers
import requests
from networkx.generators.tests.test_small import null
from elasticsearch import Elasticsearch

from bee_var import darknet_clash, mybtctag_index, btctagseed_index, btctagclu_index, total_addr_index, \
    btc_cluster_search, cluster_info_index, btcblock_index, my_cluster_info
from dao.datainterchange import getTxbyHash
from mysql_dealer import mysql_dealer, startDb
from Model.dataValidation import DataValidation_btctag, DataValidation_mybtctag, DataValidation_btcmix, \
    DataValidation_tag_cluster, DataValidation_darknet_clash, DataValidation_cluster_search
from utils import ts2t
import json
import datetime
from config import config
from Serives.btcAddressDetail import getAddressTX, handleAddressBalance
from log import log
import time
# from app import es
from mutil.get_tx_by_rpc import getTxDetail
from dao.txTraceDao import getTxDetail1
from elasticsearch.exceptions import NotFoundError
from config import config

log = log.init_logger(config.log_filepath)
sql_dealer = mysql_dealer("btc_addr_tag")
# es.tryagain_instance()
# es = es.instance
es = Elasticsearch(hosts=config.es_ip, port=config.es_port, timeout=600)


#  地址标签所对应的四种搜索方法
# 1.无任何要求
# 2.地址要求
# 3.标签要求
# 4.标签地址都要求
def get_pure_address_tags(start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("btc_addr_tag")
    except Exception as e:
        print("the connection of the database btc_addr_tag) is wrong:")

    else:
        sql = "select AddressTag.sequence,AddressTag.addr,AddressTag.source,DomainCategory.category " \
              "from AddressTag,DomainCategory where AddressTag.source=DomainCategory.domain limit {0},{1}".format(start,
                                                                                                                  perpage)
        # sql_count = "select count(1) from AddressTag"
        sql_count = "select num from CountList where Category='total'"
        try:
            count = int(sql_dealer.get_cursor_exe_result(sql_count)[0][0])
            results = sql_dealer.get_cursor_exe_result(sql)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong " + str(sql))
            log.error("running sql wrong " + str(sql))
        else:
            # result_list = []
            for result in results:
                single = dict()
                (
                    single['sequence'], single['addr'], single['source'], single['category']) = (result)
                result_list.append(single)

    return count, result_list


def get_tags(start, perpage):
    body = {
        "query": {
            "match_all": {}
        },
        "size": perpage,
        "from": start,
        "track_total_hits": True
    }
    result = DataValidation_btctag(body)
    result_list = []
    total = result["hits"]["total"]['value']
    for item in result['hits']['hits']:
        addr = item['_id']
        source = item['_source']['sources']
        com = item['_source']['com']
        category = item['_source']['tags']
        single = dict()
        (single['addr'], single['source'], single['com'], single['category']) = (addr, source, com, category)
        result_list.append(single)
    return total, result_list


def get_monitor(start, page, userid):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("monitor")
    except Exception as e:
        print("the connection of the database monitor is wrong:")
    else:
        sql = "select address,min_value,max_value,detail,monitor_id from address_monitor where user_id=1 order by monitor_id desc limit {},{}".format(
            start, page)
        sql1 = "select count(monitor_id) from address_monitor where user_id=1 "
        print(sql1)
        try:
            results = sql_dealer.get_cursor_exe_result(sql)
            count = sql_dealer.get_cursor_exe_result(sql1)[0][0]
            print(count)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong " + str(sql))
            log.error("running sql wrong " + str(sql))
        else:
            # result_list = []
            # count = len(results)
            for result in results:
                # print(result)
                single = dict()
                (
                    single['addr'], single['min_value'], single['max_value'], single['detail'],
                    single["monitor_id"]) = (result)
                result_list.append(single)

    return count, result_list


def get_special_addr(start, perpage, userid, address, count):
    print("count:{}".format(count))
    result_list = []
    try:
        sql_dealer = mysql_dealer("monitor")
    except Exception as e:
        print("the connection of the database btc_addr_tag is wrong:")
    else:
        sql = "select address_monitor.address,monitor_list.tx_hash,monitor_list.tx_time,monitor_list.tx_num,monitor_list.id from address_monitor,monitor_list where address_monitor.user_id=1 and address_monitor.address like '%{}%' and address_monitor.monitor_id=monitor_list.monitor_id limit {},{}".format(
            address, start, perpage)
        sql1 = "select count(id) from address_monitor,monitor_list where address_monitor.user_id=1 and address_monitor.address like '%{}%' and address_monitor.monitor_id=monitor_list.monitor_id ".format(
            address)
        try:
            results = sql_dealer.get_cursor_exe_result(sql)
            print(count)
            if count == 0:
                count = sql_dealer.get_cursor_exe_result(sql1)[0][0]
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong " + str(sql))
            log.error("running sql wrong " + str(sql))
        else:
            # result_list = []
            # count = len(results)
            for result in results:
                single = dict()
                (
                    single['address'], single['txid'], single['tx_time'], single['volume'], single["list_id"]) = (
                    result)
                tx_time = single["tx_time"]
                timestamp = time.mktime(time.strptime(tx_time, '%Y-%m-%d %H:%M:%S'))
                datetime_struct = datetime.datetime.fromtimestamp(timestamp)
                datetime_obj = (datetime_struct + datetime.timedelta(hours=8))
                datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
                # print(datetime_str)
                single["tx_time"] = datetime_str
                tx_detail = getTxDetail1(single['txid'])
                # print(tx_detail)
                single["tx"] = tx_detail
                result_list.append(single)

    return count, result_list


def updateQueryHistory(address, domain, coin, sdate, edate, keyword, remark):
    addr_ = address
    domain_ = domain
    coin_ = coin
    sdate_ = sdate
    edate_ = edate
    keyword_ = keyword
    remark_ = remark
    if sdate_ == "":
        sdate_ = '1111-11-11 11:11:11'
    if edate_ == "":
        edate_ = '1111-11-11 11:11:11'

    sql_dealer = startDb("darknet_btc_analyze")
    cursor = sql_dealer.cursor()
    sql = "insert into query_history(addr,domain,coin,sdate,edate,keyword,remark) values(%s,%s ,%s, %s,%s,%s,%s)"
    try:
        cursor.execute(sql, (addr_, domain_, coin_, sdate_, edate_, keyword_, remark_))
        sql_dealer.commit()
        return 1
    except Exception as e:
        log.error("添加查询历史失败", e)
        return 0


def updateTxTopic(topic, hash):
    try:
        try:
            result = getTxbyHash(hash)
        except Exception as e:
            log.error(e)
            return 0
        if result:
            result['topic_new'] = topic
            actions = [
                {
                    "_op_type": "index",
                    "_index": "btc_tx_new",
                    "_type": "raw",
                    "_id": result['txid'],
                    "_source": result
                }
            ]  # 交易信息导入
            elasticsearch.helpers.bulk(es, actions, request_timeout=60)
        return 1
    except Exception as e:
        log.error("添加标签失败", e)
        return 0


def updateTransQueryHistory(maxvalue, minvalue, stime, etime, keyword, inputaddr, outputaddr, height, fee, inputnum,
                            outputnum, topic, specvalue, remark):
    inputaddr_ = inputaddr
    outputaddr_ = outputaddr
    maxv_ = maxvalue
    minv_ = minvalue
    stime_ = stime
    etime_ = etime
    keyword_ = keyword
    height_ = height
    fee_ = fee
    inputnum_ = inputnum
    outputnum_ = outputnum
    topic_ = topic
    specvalue_ = specvalue
    remark_ = remark

    if stime_ == "":
        stime_ = '1111-11-11 11:11:11'
    if etime_ == "":
        etime_ = '1111-11-11 11:11:11'
    # log.error("peng!", maxv_, minv_, stime_, etime_, keyword_)
    sql_dealer = startDb("darknet_btc_analyze")
    cursor = sql_dealer.cursor()
    sql = "insert into trans_query_history(blockheight,fee,maxval,minval,sdate,edate,keyword,inputaddr,outputaddr,username,inputnum,outputnum,topic,specvalue,remark) values(%s,%s,%s ,%s,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        cursor.execute(sql, (
            height_, fee_, maxv_, minv_, stime_, etime_, keyword_, inputaddr_, outputaddr_, 'guest', inputnum_,
            outputnum_,
            topic_, specvalue_, remark_))
        sql_dealer.commit()
        return 1
    except Exception as e:
        log.error("添加查询历史失败", e)
        return 0


def updateTransQueryHistoryPro(keyword, remark, text):
    keyword_ = keyword
    remark_ = remark
    text_ = text
    # log.error("peng!", maxv_, minv_, stime_, etime_, keyword_)
    sql_dealer = startDb("darknet_btc_analyze")
    cursor = sql_dealer.cursor()
    sql = "insert into trans_query_history_pro(keyword,username,remark,querytext) values(%s,%s,%s ,%s)"
    try:
        cursor.execute(sql, (keyword_, 'guest', remark_, text_))
        sql_dealer.commit()
        return 1
    except Exception as e:
        log.error("添加查询历史失败", e)
        return 0


def updateAddressTag(address, tag, source, com):
    try:
        actions = []
        id = address
        sources = [source]
        tags = [tag]
        com = [com]
        single = dict()
        (single['sources'], single['tags'], single['com']) = (sources, tags, com)
        action = {
            "_op_type": "index",
            "_index": "btc_tag",
            "_type": "raw",
            "_id": id,
            "_source": single
        }
        actions.append(action)
        elasticsearch.helpers.bulk(es, actions, request_timeout=60)
        return 1
    except Exception as e:
        log.error("添加标签失败", e)
        return 0


def modifySpecialAddr(monitor_id, remark, minvalue, maxvalue):
    try:
        sql_dealer = mysql_dealer("monitor")
        if remark != "":
            sql = "update address_monitor set detail='{}' where monitor_id='{}'".format(remark, monitor_id)
            sql_dealer.cursor.execute(sql)
        if minvalue != "":
            sql = "update address_monitor set min_value={} where monitor_id='{}'".format(int(minvalue), monitor_id)
            print(sql)
            sql_dealer.cursor.execute(sql)
        if maxvalue != "":
            sql = "update address_monitor set max_value={} where monitor_id='{}'".format(int(maxvalue), monitor_id)
            sql_dealer.cursor.execute(sql)
        sql_dealer.db.commit()
        return 1
    except Exception as e:
        print(e)
        sql_dealer.db.rollback()
        return 0


def updateSpecialAddr(address, remark, minvalue, maxvalue):
    try:
        # log.info("开始添加标签")
        sql = "insert into address_monitor(address,min_value,max_value,detail,user_id) values('{}',{},{},'{}',1)".format(
            address, minvalue, maxvalue, remark)
        print(sql)
        sql_dealer = mysql_dealer("monitor")
        sql_dealer.cursor.execute(sql)
        sql_dealer.db.commit()
        log.info("添加标签成功")
        return 1
    except Exception as e:
        sql_dealer.db.rollback()
        log.error("添加标签失败", e)
        return 0


def get_address_tags_with_two(address, servicename, start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("btc_addr_tag")
    except Exception as e:
        print("the connection of the database btc_addr_tag) is wrong:")

    else:
        sql = "select AddressTag.sequence,AddressTag.addr,AddressTag.source,DomainCategory.category " \
              "from AddressTag,DomainCategory where AddressTag.SOURCE=DomainCategory.domain and AddressTag.addr='{2}' and DomainCategory.category='{3}' limit {0},{1}".format(
            start, perpage, address, servicename)
        sql_count = "select count(1) from AddressTag,DomainCategory where AddressTag.source=DomainCategory.domain and AddressTag.addr='{2}' and DomainCategory.category='{3}' limit {0},{1}".format(
            start, perpage, address, servicename)

        try:
            count = int(sql_dealer.get_cursor_exe_result(sql_count)[0][0])
            results = sql_dealer.get_cursor_exe_result(sql)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong " + str(sql))
            log.error("running sql wrong " + str(sql))
        else:

            for result in results:
                single = dict()
                (
                    single['sequence'], single['addr'], single['source'], single['category']) = (result)
                result_list.append(single)
    return count, result_list


def get_address_tags(address, tag, source, com, start, perpage):
    if len(address) != 0:
        total = 1
        result = es.get(index='btc_tag', doc_type='raw', id=address)
        category = result["_source"]["tags"]
        result_list = []
        single = dict()
        (single['addr'], single['source'], single['com'], single['category']) = (
            address, result['_source']['sources'], result['_source']['com'], result['_source']['tags'])
        result_list.append(single)
    else:
        if tag:
            rule = '.*' + tag + '.*'
            body = {
                "query": {
                    "regexp": {
                        "tags": {
                            "value": rule,
                        }
                    }
                },
                "from": start,
                "size": perpage,
                "track_total_hits": True
            }
        elif source:
            rule = '.*' + source + '.*'
            body = {
                "query": {
                    "regexp": {
                        "sources": {
                            "value": rule,
                        }
                    }
                },
                "from": start,
                "size": perpage,
                "track_total_hits": True
            }
        elif com:
            rule = '.*' + com + '.*'
            body = {
                "query": {
                    "regexp": {
                        "com": {
                            "value": rule,
                        }
                    }
                },
                "from": start,
                "size": perpage,
                "track_total_hits": True
            }
        else:
            body = {
                "query":
                    {
                        "match_all": {},
                    },
                "track_total_hits": True,
                "from": start,
                "size": perpage,
            }
        result = DataValidation_btctag(body)
        result_list = []
        total = result["hits"]["total"]['value']
        for item in result['hits']['hits']:
            addr = item['_id']
            source = item["_source"]["sources"]
            com = item['_source']['com']
            category = item["_source"]["tags"]
            single = dict()
            (single['addr'], single['source'], single['com'], single['category']) = (addr, source, com, category)
            result_list.append(single)
    return total, result_list


def get_special_addrs(address, start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("btc_addr_tag")
    except Exception as e:
        print("the connection of the database btc_addr_tag is wrong:")

    else:
        sql = "select id,addr,last_tx,last_time,amount,flag " \
              "from specialAddr where addr like '%{2}%' limit {0},{1}".format(start, perpage, address)
        try:
            results = sql_dealer.get_cursor_exe_result(sql)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong " + str(sql))
            log.error("running sql wrong " + str(sql))
        else:
            count = len(results)
            for result in results:
                single = dict()
                (
                    single['id'], single['addr'], single['last_tx'], single['last_time'], single['amount'],
                    single['flag']) = (result)
                result_list.append(single)
    return count, result_list


def get_address_tags_with_service(servicename, start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("btc_addr_tag")
    except Exception as e:
        print("the connection of the database btc_addr_tag is wrong:")

    else:
        sql = "select AddressTag.sequence,AddressTag.addr,AddressTag.source,DomainCategory.category " \
              "from AddressTag,DomainCategory where AddressTag.source=DomainCategory.domain and DomainCategory.category='{2}' limit {0},{1}".format(
            start, perpage, servicename)
        sql_count = "select num from CountList where Category='{}'".format(servicename)
        # sql_count ="select count(1) from AddressTag,DomainCategory where AddressTag.source=DomainCategory.domain and DomainCategory.category='{0}'".format(servicename)
        try:
            count = int(sql_dealer.get_cursor_exe_result(sql_count)[0][0])
            results = sql_dealer.get_cursor_exe_result(sql)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong " + str(sql))
            log.error("running sql wrong " + str(sql))
        else:
            # result_list = []
            for result in results:
                single = dict()
                (
                    single['sequence'], single['addr'], single['source'], single['category']) = (result)
                result_list.append(single)
    return count, result_list


def get_address_tags_with_address(address, start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("btc_addr_tag")
    except Exception as e:
        print("the connection of the database btc_addr_tag is wrong:")

    else:
        sql = "select AddressTag.sequence,AddressTag.addr,AddressTag.source,DomainCategory.category " \
              "from AddressTag,DomainCategory where AddressTag.source=DomainCategory.domain and AddressTag.ADDR='{2}' limit {0},{1}".format(
            start, perpage, address)
        sql_count = "select count(1) from AddressTag,DomainCategory where AddressTag.source=DomainCategory.domain and AddressTag.addr='{2}' limit {0},{1}".format(
            start, perpage, address)
        try:
            count = int(sql_dealer.get_cursor_exe_result(sql_count)[0][0])
            results = sql_dealer.get_cursor_exe_result(sql)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong " + str(sql))
            log.error("running sql wrong " + str(sql))
        else:
            # result_list = []
            for result in results:
                single = dict()
                (
                    single['sequence'], single['addr'], single['source'], single['category']) = (result)
                result_list.append(single)
    return count, result_list


# syc--------------------------------------------------

# SYC Tag
def get_my_tags(start, perpage):
    body = {
        "query": {
            "match_all": {}
        },
        "size": perpage,
        "from": start,
        "track_total_hits": True
    }
    result = []#DataValidation_mybtctag(body, 'seed')
    result_list = []
    total = 0#result["hits"]["total"]['value']
    for item in []:
        addr = item['_id']
        labels = item['_source']['labels']
        labels_num = item['_source']['label_sum']

        for i in labels:
            i['addr'] = addr
            i['labels_sum'] = labels_num

            # i['balance'] = balance
            result_list.append(i)
        # result_list.append(single)

    return total, result_list


def get_tag_cluster(start, perpage):
    body = {
        "query": {
            "match_all": {}
        },
        "size": perpage,
        "from": start,
        "track_total_hits": True
    }
    result = DataValidation_tag_cluster(body)
    result_list = []
    total = result["hits"]["total"]['value']
    for item in result['hits']['hits']:
        addr = item['_id']

        labels = item['_source']['labels']
        labels_num = item['_source']['label_sum']

        for i in labels:
            i['addr'] = addr
            i['labels_sum'] = labels_num
            result_list.append(i)
        # result_list.append(single)

    return total, result_list


def get_darknet_clash(start, perpage):
    body = {
        "query": {
            "match_all": {}
        },
        "size": perpage,
        "from": start,
        "track_total_hits": True
    }
    result = DataValidation_darknet_clash(body)
    result_list = []
    total = result["hits"]["total"]['value']

    rule = r"http://(.*)/"

    for item in result['hits']['hits']:
        addr = item['_id']

        labels = item['_source']['labels']
        labels_num = item['_source']['label_sum']
        domain = item['_source']['domain']
        link = item['_source']['link']

        try:
            website = re.findall(rule, domain)[0]
            sql = "select tag from website_tag where website='{0}'".format(website)
            tag = sql_dealer.get_cursor_exe_result(sql)[0][0]
        except:
            tag = None

        for i in labels:
            i['addr'] = addr
            i['labels_sum'] = labels_num
            i['domain'] = domain
            i['link'] = link
            i['tag'] = tag
            result_list.append(i)
        # result_list.append(single)

    return total, result_list


# SYC Clustering
def get_addr_cluster(start, perpage):
    body = {
        "query": {
            "match_all": {}
        },
        "size": perpage,
        "from": start,
        "track_total_hits": True
    }
    result = DataValidation_cluster_search(body)
    result_list = []
    total = result["hits"]["total"]['value']
    for item in result['hits']['hits']:
        addr = item['_id']

        labels = item['_source']
        labels['addr'] = addr
        result_list.append(labels)

    return total, result_list


def get_cluster_search(address, start, perpage):
    result_list = []
    if len(address) != 0:
        try:
            result = es.get(index='total_addr', doc_type='_doc', id=address)
            cluster_id = result['_source']['cluster_id']
            print("id +++++++++++++++++++=", cluster_id)
            cluster_tags = es.get(index='clusters', doc_type='_doc', id=cluster_id)
            cluster_balance = cluster_tags['_source']['balance']
            try:
                cluster_tags = cluster_tags['_source']['tags']
            except Exception as e:
                cluster_tags = None
            body = {
                "query": {
                    "match": {
                        "cluster_id": cluster_id
                    }
                },
                "track_total_hits": True
            }
            result = DataValidation_cluster_search(body)
            total = result["hits"]["total"]['value']
            for item in result['hits']['hits']:
                addr = item['_id']
                try:
                    res = es.get(index=btctagseed_index, doc_type='_doc', id=address)
                    tags = res["_source"]["labels"][0]['label_name']
                except NotFoundError as e:
                    tags = 'unknown'
                labels = item['_source']
                labels['addr'] = addr
                labels['tags'] = tags
                result_list.append(labels)
        except NotFoundError as e:
            total = 0
            result_list = []
            cluster_tags = None
            cluster_balance = 0
    return total, result_list, cluster_tags, cluster_balance


Hash_map = dict()


def takeitem(elem):
    return elem['addr_count']


# 获取所有集群信息
def get_all_cluster(start, perpage, type):
    if (type == None):
        try:
            # 获取集群总数
            body3 = {
                "size": 0,
                "aggs": {
                    "distinct_clusters": {
                        "cardinality": {
                            "field": "cluster_id"
                        }
                    }
                }
            }
            result3 = DataValidation_cluster_search(body3)
            cluster_total = result3["aggregations"]["distinct_clusters"]['value']

            body = {
                "query": {
                    "match_all": {}
                },
                "collapse": {
                    "field": "cluster_id"
                },
                "size": perpage,
                "from": start,
                "track_total_hits": True
            }
            result = DataValidation_cluster_search(body)
            total = cluster_total
            print(result)
            res = result['hits']['hits']
            result_list = []
            for item in res:
                mydict = {}
                mydict["addr"] = item["_id"]
                cluster_id = item['_source']['cluster_id']
                mydict["cluster_id"] = cluster_id
                # 获取集群地址数量
                try:
                    body = {
                        "query": {
                            "term": {
                                "cluster_id": {
                                    "value": cluster_id
                                }
                            }
                        }
                    }
                    res2 = es.count(body=body, index=total_addr_index)
                    addr_count = res2['count']
                except NotFoundError as e:
                    addr_count = 'unknown'
                mydict["addr_count"] = addr_count

                # 获取集群的标签
                try:
                    cluster_tags = es.get(index=my_cluster_info, doc_type='_doc', id=cluster_id)
                    cluster_tags = cluster_tags['_source']['labels'][0]['name']
                except Exception as e:
                    cluster_tags = None
                mydict['cluster_tags'] = cluster_tags
                result_list.append(mydict)
        except Exception as e:
            total = 0
            result_list = []
    else:
        body = {
            "query": {
                "regexp": {
                    "labels.name": ".*"
                }
            },
            "track_total_hits": True,
            "sort": [
                {
                    "addr_count": {
                        "order": "desc"
                    }
                }
            ],
            "size": perpage,
            "from": start,
        }
        res = es.search(body=body, index=my_cluster_info)
        total = res['hits']['total']['value']
        result_list = []
        for item in res['hits']['hits']:
            result_dict = {}
            result_dict['cluster_id'] = item['_id']
            body3 = {
                "query": {
                    "match": {
                        "cluster_id": item['_id']
                    }
                },
                "size": 1
            }

            res3 = es.search(index=total_addr_index, body=body3)
            addr = res3['hits']['hits'][0]['_id']
            result_dict['addr_count'] = item['_source']['addr_count']
            result_dict['addr'] = addr
            # for label in item['_source']['labels']:
            #     if(label['name'].)

            result_dict['cluster_tags'] = item['_source']['labels'][0]['name']
            result_list.append(result_dict)

    return total, result_list


# 获取地址集群信息
def get_cluster_api(address, start, perpage):
    try:
        res = es.get(index=total_addr_index, id=address)
        cluster_id = res['_source']['cluster_id']
        body = {
            "query": {
                "term": {
                    "cluster_id": cluster_id
                }
            },
            "size": perpage,
            "from": start,
            "track_total_hits": True
        }
        result = DataValidation_cluster_search(body)
        total = result['hits']['total']['value']
        print(result)
        res = result['hits']['hits']
        result_list = []
        for item in res:
            mydict = {}
            mydict["cluster_id"] = item['_source']['cluster_id']
            mydict["addr"] = item['_id']
            try:
                res = es.get(index=btctagseed_index, doc_type='_doc', id=mydict["addr"])
                tags = res["_source"]["labels"][0]['name']
            except NotFoundError as e:
                tags = 'unknown'

            try:
                res = es.get(index=my_cluster_info, doc_type='_doc', id=cluster_id)
                clu_tags = res["_source"]["labels"][0]['name']
            except Exception as e:
                clu_tags = 'unknown'

            mydict["clu_tags"] = clu_tags
            mydict["tags"] = tags
            result_list.append(mydict)
        try:
            # res = es.get(index='clusters', doc_type='_doc', id=cluster_id)
            res = es.get(index=my_cluster_info, doc_type='_doc', id=cluster_id)
            cluster_tags = res['_source']['labels']
            tag_count = res['_source']['label_sum']
        except Exception as e:
            cluster_tags = []
            tag_count = 0
        try:
            history = res['_source']['history']
        except Exception as e:
            history = None
        cluster_balance = 0.0
        # try:
        #     cluster_cate =  res['_source']['category']
        #     cluster_detail = res['_source']['detail']
        # except Exception as e:
        #     cluster_cate= 'unknown'
        #     cluster_detail='unknown'
        # cluster_info = {}
        # cluster_info['cluster_cate']=cluster_cate
        # cluster_info['cluster_detail'] =cluster_detail
    except Exception as e:
        print("!!!!!!!!!!!!!!!", e)
        total = 0
        history = None
        result_list = []
        cluster_tags = []
        cluster_balance = 0
        # cluster_info = {}
        tag_count = 0

    return total, result_list, cluster_tags, cluster_balance, tag_count, history


# GET CLUSTER_NAME
def get_cluster_name_api(cluster_name, start, perpage):
    try:
        body = {
            "query": {
                "regexp": {
                    "labels.name": ".*" + cluster_name + ".*"
                }
            },
            "track_total_hits": True,
            "sort": [
                {
                    "addr_count": {
                        "order": "desc"
                    }
                }
            ],
            "size": perpage,
            "from": start,
        }
        res = es.search(body=body, index=my_cluster_info)
        total = res['hits']['total']['value']
        result_list = []
        for item in res['hits']['hits']:
            result_dict = {}
            result_dict['cluster_id'] = item['_id']
            body3 = {
                "query": {
                    "match": {
                        "cluster_id": item['_id']
                    }
                },
                "size": 1
            }

            res3 = es.search(index=total_addr_index, body=body3)
            addr = res3['hits']['hits'][0]['_id']
            result_dict['addr_count'] = item['_source']['addr_count']
            result_dict['addr'] = addr
            # for label in item['_source']['labels']:
            #     if(label['name'].)
            result_dict['cluster_tags'] = item['_source']['labels'][0]['name']
            result_list.append(result_dict)
    except Exception as e:
        print(e)

    return total, result_list


# SYC Mix
def get_my_mix(start, perpage):
    body = {
        "query": {
            "match_all": {}
        },
        "size": perpage,
        "from": start,
        "track_total_hits": True
    }
    result = DataValidation_btcmix(body)
    result_list = []
    total = result["hits"]["total"]['value']
    for item in result['hits']['hits']:
        txid = item['_id']

        labels = item['_source']['info']

        for i in labels:
            i['txid'] = txid
            result_list.append(i)
        # result_list.append(single)

    return total, result_list


# Syc tag search
# Syc tag search
def get_address_mytags(address, name, source, num, category, start, perpage, label_clash, flag):
    print('flag is', flag)
    if len(address) != 0:
        try:
            # result = es.get(index=mybtctag_index, doc_type='_doc', id=address)
            body = {
                "query": {
                    "terms": {
                        "_id": [
                            address
                        ]
                    }
                }
            }
            # 设置一下查询的index
            if (flag == ''):
                address_index = btctagseed_index
            if (flag == 'seed'):
                address_index = btctagseed_index
            if (flag == 'clu'):
                address_index = btctagclu_index
            result = es.search(index=address_index, body=body)
            labels = []
            res = result["hits"]["hits"]
            for item in res:
                for j in item['_source']['labels']:
                    labels.append(j)
            label_num = len(labels)
            try:
                balance = result["_source"]["balance"]
            except Exception as e:
                balance = 'unknown'
            result_list = []
            print(labels)
            if (labels != []):
                total = 1
            else:
                total = 0
            for label in labels:
                label['addr'] = address
                label['labels_sum'] = label_num
                label['balance'] = balance
                result_list.append(label)
            result_list_1000 = result_list
        except NotFoundError as e:
            total = 0
            print(e)
            result_list = []
    else:
        if not name:
            name = '.*'
        if not source:
            source = '.*'
        if not category:
            category = '.*'
        if not label_clash:
            if num:
                body = {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "regexp": {
                                        "labels.source": ".*" + source + ".*"
                                    }
                                },
                                {
                                    "regexp": {
                                        "labels.name": ".*" + name + ".*"
                                    }
                                },
                                {
                                    "regexp": {
                                        "labels.category": ".*" + category + ".*"
                                    }
                                },
                                {
                                    "term": {
                                        "label_sum": num
                                    }
                                }
                            ]
                        }
                    },
                    "size": perpage,
                    "from": start,
                    "track_total_hits": True,
                }
            else:
                body = {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "regexp": {
                                        "labels.source": ".*" + source + ".*"
                                    }
                                },
                                {
                                    "regexp": {
                                        "labels.name": ".*" + name + ".*"
                                    }
                                },
                                {
                                    "regexp": {
                                        "labels.category": ".*" + category + ".*"
                                    }
                                }
                            ]
                        }
                    },
                    "size": perpage,
                    "from": start,
                    "track_total_hits": True,
                }
        else:
            if num:
                body = {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "regexp": {
                                        "labels.source": ".*" + source + ".*"
                                    }
                                },
                                {
                                    "regexp": {
                                        "labels.name": ".*" + name + ".*"
                                    }
                                },
                                {
                                    "regexp": {
                                        "labels.category": ".*" + category + ".*"
                                    }
                                },
                                {
                                    "term": {
                                        "label_sum": num
                                    }
                                },
                                {
                                    "term": {
                                        "label_clash": label_clash
                                    }
                                }
                            ]
                        }
                    },
                    "size": perpage,
                    "from": start,
                    "track_total_hits": True
                }
            else:
                body = {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "regexp": {
                                        "labels.source": ".*" + source + ".*"
                                    }
                                },
                                {
                                    "regexp": {
                                        "labels.name": ".*" + name + ".*"
                                    }
                                },
                                {
                                    "regexp": {
                                        "labels.category": ".*" + category + ".*"
                                    }
                                },
                                {
                                    "term": {
                                        "label_clash": label_clash
                                    }
                                }
                            ]
                        }
                    },
                    "size": perpage,
                    "from": start,
                    "track_total_hits": True
                }

        print(body)
        result = DataValidation_mybtctag(body, flag)

        body2 = body
        body2['size'] = 1000
        print('body2:      ', body2)
        # print(result)
        result_list = []
        total = result["hits"]["total"]['value']
        for item in result['hits']['hits']:
            addr = item['_id']
            labels = item['_source']['labels']
            # labels_num = item['_source']['label_sum']
            labels_num = len(labels)
            # 地址余额
            try:
                balance = item['_source']['balance']
            except Exception as e:
                balance = 'unknown'
            for i in labels:
                i['addr'] = addr
                i['labels_sum'] = labels_num
                i['balance'] = balance
                result_list.append(i)

        result_1000 = DataValidation_mybtctag(body2, flag)
        result_list_1000 = []
        for item in result_1000['hits']['hits']:
            addr = item['_id']
            labels = item['_source']['labels']

            # labels_num = item['_source']['label_sum']
            labels_num = len(labels)
            # 地址余额
            try:
                balance = item['_source']['balance']
            except Exception as e:
                balance = 'unknown'
            for i in labels:
                i['addr'] = addr
                i['labels_sum'] = labels_num
                i['balance'] = balance
                detail = str(i['detail'])
                detail = detail.replace('"', ' ')
                detail = detail.replace("'", " ")
                detail = eval(repr(detail).replace('\\', '@'))

                i['detail'] = detail
                if (i['category'] == None):
                    i['category'] = 'Null'
                if (i['detail'] == None):
                    i['detail'] = 'Null'
                name = str(i['name'])
                name = name.replace('"', ' ')
                name = name.replace("'", " ")
                name = eval(repr(name).replace('\\', '@'))

                i['name'] = name
                result_list_1000.append(i)
    print(result_list)
    return total, result_list, result_list_1000


# SYC Darknet Search
def get_darknet_tags(address, tag, domain, url, start, perpage):
    if len(address) != 0:
        try:
            total = 1
            result = es.get(index='darknet_btc_crush', doc_type='_doc', id=address)
            labels = result["_source"]["labels"]
            label_num = result["_source"]["label_sum"]
            darknet_domain = result["_source"]["domain"]
            darknet_link = result["_source"]["link"]

            rule = r"http://(.*)/"
            try:
                website = re.findall(rule, darknet_domain)[0]
                sql = "select tag from website_tag where website='{0}'".format(website)
                darknet_tag = sql_dealer.get_cursor_exe_result(sql)[0][0]
            except:
                darknet_tag = None

            result_list = []
            for label in labels:
                label['addr'] = address
                label['labels_sum'] = label_num
                label['domain'] = darknet_domain
                label['link'] = darknet_link
                label['tag'] = darknet_tag
                result_list.append(label)
        except NotFoundError as e:
            total = 0
            print(e)
            result_list = []
    else:
        if not tag:
            tag = '.*'
        if not domain:
            domain = '.*'
        if not url:
            url = '.*'
        # if not dark_tag:
        #     dark_tag = '.*'
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "regexp": {
                                "labels.name": ".*" + tag + ".*"
                            }
                        },
                        {
                            "regexp": {
                                "domain": ".*" + domain + ".*"
                            }
                        },
                        {
                            "regexp": {
                                "link": ".*" + url + ".*"
                            }
                        }
                    ]
                }
            },
            "size": perpage,
            "from": start,
            "track_total_hits": True
        }
        result = es.search(index=darknet_clash, body=body)
        result_list = []
        total = result["hits"]["total"]['value']

        rule = r"http://(.*)/"

        for item in result['hits']['hits']:
            addr = item['_id']

            labels = item['_source']['labels']
            labels_num = item['_source']['label_sum']
            domain = item['_source']['domain']
            link = item['_source']['link']

            try:
                website = re.findall(rule, domain)[0]
                sql = "select tag from website_tag where website='{0}'".format(website)
                tag = sql_dealer.get_cursor_exe_result(sql)[0][0]
            except:
                tag = None

            for i in labels:
                i['addr'] = addr
                i['labels_sum'] = labels_num
                i['domain'] = domain
                i['link'] = link
                i['tag'] = tag
                result_list.append(i)
            # result_list.append(single)

        return total, result_list

    return total, result_list


# Syc Tag Add


def updateClusterTag(cluster_id, tag, type, detail, source):
    # #添加集群标签
    # body = {
    #     'label': tag,
    #     'category':type,
    #     'detail':detail
    # }
    # res = es.index(index='clusters', id=cluster_id, body=body)
    # # log.error("添加标签失败", e)
    #
    # #给地址添加标签
    # zz_address=None
    # res = add_tag_chuanbo(zz_address,cluster_id,tag,type,detail)
    body = {
        "query": {
            "term": {
                "cluster_id": {
                    "value": cluster_id
                }
            }
        }
    }
    count = es.count(index=total_addr_index, body=body)
    total = count['count']
    today = datetime.date.today()
    try:
        result = es.get(index=my_cluster_info, doc_type="_doc", id=cluster_id)
        # 如果之前没有标签的话
    except Exception as e:
        data = {
            "labels": [{
                "name": tag,
                "category": type,
                "source": source,
                "createtime": today,
                "currency": "Bitcoin",
                "detail": detail
            }
            ],
            "addr_count": total,
            "label_sum": 1
        }
        res = es.index(index=my_cluster_info, id=cluster_id, body=data)
        # print(res)
        return 1
        # 如果有的话，继续添加
    labels = result["_source"]["labels"]
    label_sum = result["_source"]["label_sum"] + 1

    new_label = {
        "name": tag,
        "category": type,
        "source": source,
        "createtime": today,
        "currency": "Bitcoin",
        "detail": detail
    }

    # 判断新增label是否与以前的相同（增量）
    if new_label not in labels:
        labels.append(new_label)
    else:
        return 0
    # 把新的labels加到ES中
    new_labels = dict()
    new_labels["labels"] = labels;
    new_labels["label_sum"] = label_sum;
    new_labels['addr_count'] = total
    res = es.index(index=my_cluster_info, id=cluster_id, body=new_labels)
    return 1


def get_tag_all_info():
    today = datetime.date.today()
    body = {
        "query": {
            "match_all": {}
        },
        "track_total_hits": True
    }
    result = DataValidation_mybtctag(body, 'seed')
    tag_total = result["hits"]["total"]['value']
    body2 = {
        "query": {
            "match": {
                "labels.createtime": today
            }
        },
        "track_total_hits": True
    }
    result2 = DataValidation_mybtctag(body2, 'seed')
    today_total = result2["hits"]["total"]['value']

    # body3 = {
    #     "query": {
    #         "term": {
    #             "label_sum": 2
    #         }
    #     },
    #     "track_total_hits": True
    #
    # }
    # result3 = DataValidation_mybtctag(body3,'seed')
    body3 = {
        "size": 0,
        "aggs": {
            "get_sum": {
                "stats": {
                    "field": "addr_count"
                }
            }
        },
        "query": {
            "match": {
                "label_sum": "2"
            }
        }

    }
    result3 = es.search(body=body3, index=my_cluster_info)
    two_total = int(result3["aggregations"]["get_sum"]['sum'])

    body4 = {
        "size": 0,
        "aggs": {
            "get_sum": {
                "stats": {
                    "field": "addr_count"
                }
            }
        },
        "query": {
            "match": {
                "label_sum": "1"
            }
        }

    }

    result4 = es.search(body=body4, index=my_cluster_info)
    one_total = int(result4["aggregations"]["get_sum"]['sum'])

    body5 = {
        "query": {
            "exists": {
                "field": "label_clash"
            }
        },
        "track_total_hits": True
    }
    result5 = DataValidation_mybtctag(body5, 'seed')
    label_clash = result5["hits"]["total"]["value"]

    body6 = {
        "query": {
            "match_all": {}
        },
        "track_total_hits": True
    }
    result6 = DataValidation_tag_cluster(body6)
    clu_tag_total = result6['hits']['total']['value']

    body7 = {
        "size": 0,
        "query": {
            "range": {
                "label_sum": {
                    "gte": 1,
                    "lte": 50000
                }
            }
        },
        "aggs": {
            "get_sum": {
                "stats": {
                    "field": "addr_count"
                }
            }
        }

    }
    result7 = es.search(body=body7, index=my_cluster_info)
    all_total = int(result7["aggregations"]["get_sum"]["sum"])

    result_info = {}
    result_info["tag_total"] = tag_total
    result_info["today_total"] = today_total
    result_info["two_total"] = two_total
    result_info["one_total"] = one_total
    result_info["label_clash"] = label_clash
    result_info['clu_tag_total'] = clu_tag_total
    result_info['all_total'] = all_total
    result_info['three_more_total'] = result_info['all_total'] - two_total - one_total
    print(result_info)
    return result_info


def get_tag_source(sources):
    result_list = []
    print(11111111111111)
    for source in sources:
        # 用户标签
        if (source == 'BitcoinTalk Forum' or source == 'Twitter' or source == 'Github' or source == 'Telegram'):
            if (source == 'BitcoinTalk Forum'):
                table = 'user'
            else:
                table = source
            sql = 'SELECT bitcoin_addr,user_name FROM `{}` GROUP BY bitcoin_addr'.format(table)
            sql_dealer = mysql_dealer('bitcoin_tags')
            res_list = sql_dealer.get_cursor_exe_result(sql)
            count = len(res_list)
            result_dict = {}
            result_dict['source'] = source
            result_dict['count'] = count
            result_list.append(result_dict)

            # return result_list
        else:
            result_dict = {}
            body = {
                "size": 0,
                "aggs": {
                    "distinct_labels": {
                        "cardinality": {
                            "field": "labels.name"
                        }
                    }
                },
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "labels.source": source
                                }
                            },
                            {
                                "match": {
                                    "label_sum": 1
                                }
                            }
                        ]
                    }
                },
                "track_total_hits": True
            }

            result = DataValidation_mybtctag(body, "seed")
            count = result["aggregations"]["distinct_labels"]['value']
            result_dict['source'] = source
            result_dict['count'] = count
            result_list.append(result_dict)
    return result_list


def top_tags():
    body = {
        "size": 0,
        "aggs": {
            "messages": {
                "terms": {
                    "field": "labels.name",
                    "size": 10
                }
            }
        }
    }
    result = DataValidation_mybtctag(body, 'seed')
    toptags = result['aggregations']['messages']['buckets']
    return toptags


def top_category():
    body = {
        "size": 0,
        "aggs": {
            "messages": {
                "terms": {
                    "field": "labels.category",
                    "size": 15
                }
            }
        }
    }
    result = DataValidation_mybtctag(body, '')
    topcategory = result['aggregations']['messages']['buckets']
    return topcategory


def today_tag():
    today = datetime.date.today()
    body = {
        "query": {
            "match": {
                "labels.createtime": today
            }
        },
        "size": 10
    }
    result = DataValidation_mybtctag(body, 'seed')
    todaytag = result['hits']['hits']
    return todaytag


# SYC Mix Search
def get_my_mix_search(txid, type, start, perpage):
    if len(txid) != 0:
        total = 1
        result = es.get(index='btc_mix_tx', doc_type='_doc', id=txid)
        labels = result["_source"]["info"]
        result_list = []
        for label in labels:
            label['txid'] = txid
            result_list.append(label)
        return total, result_list
    else:
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "regexp": {
                                "info.category.keyword": ".*" + type + ".*"
                            }
                        }
                    ]
                }
            },
            "size": perpage,
            "from": start,
            "sort": {"info.height.keyword": {"order": "desc"}},
            "track_total_hits": True
        }
    print(body)
    result = DataValidation_btcmix(body)
    # print(result)
    result_list = []
    total = result["hits"]["total"]['value']
    for item in result['hits']['hits']:
        txid = item['_id']
        labels = item['_source']['info']
        for i in labels:
            i['txid'] = txid
            result_list.append(i)
    return total, result_list


# SYC GET BIG TRANS
def get_big_trans(address):
    sql_dealer = mysql_dealer('whale_alert')
    sql = 'select * from bitcoin where from_addr="{}"or to_addr="{}"'.format(address, address)
    result_list = sql_dealer.get_cursor_exe_result(sql)
    # print(result_list)
    list = []
    flag = 'unknown'
    for result in result_list:
        my_dict = {}
        my_dict['txid'] = result[1]
        if (result[5] != 'None'):
            my_dict['from_owner'] = result[5]
        else:
            my_dict['from_owner'] = 'unknown'
        if (result[8] != 'None'):
            my_dict['to_owner'] = result[8]
        else:
            my_dict['to_owner'] = 'unknown'
        timestamp = int(result[10])
        dt = datetime.datetime.fromtimestamp(timestamp)
        my_dict['from_addr'] = result[4]
        my_dict['to_addr'] = result[7]
        my_dict['time'] = dt.strftime("%Y-%m-%d %H:%M:%S")
        my_dict['btc'] = result[11]
        my_dict['btc_usd'] = result[12]
        # 以前没有标签，现在有标签
        if (my_dict['from_addr'] == address):
            if (my_dict['from_owner'] != 'unknown'):
                flag = my_dict['from_owner']
        if (my_dict['to_addr'] == address):
            if (my_dict['to_owner'] != 'unknown'):
                flag = my_dict['to_owner']
        list.append(my_dict)
        for item in list:
            if (item['from_addr'] == address):
                item['from_owner'] = flag
            if (item['to_addr'] == address):
                item['to_owner'] = flag
    return list


# BTC Cluster info
def get_cluster_info():
    today = datetime.date.today()
    body = {
        "query": {
            "match_all": {}
        }
    }

    result = es.count(index=total_addr_index, body=body)
    addr_total = result['count']

    body3 = {
        "size": 0,
        "aggs": {
            "distinct_clusters": {
                "cardinality": {
                    "field": "cluster_id"
                }
            }
        }
    }
    result3 = DataValidation_cluster_search(body3)
    cluster_total = result3["aggregations"]["distinct_clusters"]['value']

    body2 = {
        "query": {
            "match_all": {}
        }
    }
    result4 = es.count(body=body2, index=my_cluster_info)
    total = result4['count']
    result_info = {}
    result_info["addr_total"] = addr_total
    result_info["cluster_total"] = cluster_total
    result_info["have_tag_total"] = total
    print(result_info)
    return result_info


# Syc 获取有标签的集群Top10
def top_label_clusters():
    body = {
        "query": {
            "range": {
                "label_sum": {
                    "gte": 1,
                    "lte": 100000000
                }
            }
        },
        "sort": [
            {
                "addr_count": {
                    "order": "desc"
                }
            }
        ],
        "size": 10
    }
    result = es.search(index=my_cluster_info, body=body)
    # print(11111111111111111111)
    return result['hits']['hits']


# Syc 获取集群Top10
def top_clusters():
    body = {
        "size": 0,
        "aggs": {
            "aaa": {
                "terms": {
                    "field": "cluster_id",
                    "size": 10,
                    "execution_hint": "map"
                }
            }
        },
    }
    res = es.search(index=total_addr_index, body=body)
    return res['aggregations']['aaa']['buckets']


# Syc Tag Add
def updateAddressMyTag(address, tag, source, detail, type):
    today = datetime.date.today()
    try:
        try:
            result = es.get(index=btctagseed_index, doc_type="_doc", id=address)
        except Exception as e:
            log.error(e)
            data = {
                "labels": [{
                    "name": tag,
                    "category": type,
                    "source": source,
                    "createtime": today,
                    "currency": "Bitcoin",
                    "detail": detail
                }
                ],
                "label_sum": 1
            }
            res = es.index(index=btctagseed_index, id=address, body=data)
            result = {}

        if result:
            labels = result["_source"]["labels"]
            label_sum = result["_source"]["label_sum"] + 1
            new_label = {
                "name": tag,
                "category": type,
                "source": source,
                "createtime": today,
                "currency": "Bitcoin",
                "detail": detail
            }

            # 判断新增label是否与以前的相同（增量）
            if new_label not in labels:
                labels.append(new_label)

            # 把新的labels加到ES中
            new_labels = dict()
            new_labels["labels"] = labels
            new_labels["label_sum"] = label_sum
            res = es.index(index=btctagseed_index, id=address, body=new_labels)
        # 进行标签传播
        try:
            res2 = es.get(index=total_addr_index, id=address, doc_type='_doc')
            cluster_id = res2["_source"]["cluster_id"]
            add_tag_chuanbo(address, cluster_id, tag, type)
        except NotFoundError as e:
            print('标签传播失败')

        return 1
    except Exception as e:
        log.error("添加标签失败", e)
        return 0


# syc add tag 同时传播
def add_tag_chuanbo(zz_address, cluster_id, tag, type):
    today = datetime.date.today()
    body = {
        "query": {
            "term": {
                "cluster_id": {
                    "value": cluster_id
                }
            }
        }
    }

    res3 = es.count(index=total_addr_index, body=body)
    addr_count = res3['count']
    detail = 'label spread, seed address:' + zz_address
    # 给集群添加标签
    try:
        result = es.get(index=my_cluster_info, doc_type="_doc", id=cluster_id)
        # 如果之前没有标签的话
    except Exception as e:
        data = {
            "labels": [{
                "name": tag,
                "category": type,
                "source": 'Label Spread',
                "createtime": today,
                "currency": "Bitcoin",
                "detail": detail
            }
            ],
            "addr_count": addr_count,
            "label_sum": 1
        }
        res = es.index(index=my_cluster_info, id=cluster_id, body=data)
        # print(res)
        return 1
    # 如果有的话，继续添加
    labels = result["_source"]["labels"]
    label_sum = result["_source"]["label_sum"] + 1

    new_label = {
        "name": tag,
        "category": type,
        "source": 'Label Spread',
        "createtime": today,
        "currency": "Bitcoin",
        "detail": detail
    }

    # 判断新增label是否与以前的相同（增量）
    if new_label not in labels:
        labels.append(new_label)
    else:
        return 0
    # 把新的labels加到ES中
    new_labels = dict()
    new_labels["labels"] = labels;
    new_labels["label_sum"] = label_sum;
    new_labels['addr_count'] = addr_count
    res = es.index(index=my_cluster_info, id=cluster_id, body=new_labels)
    return 1
    # data = {
    #     'label': tag,
    #     'category':type,
    #     'detail':detail
    # }
    # my_res = es.index(index=cluster_info_index,id=cluster_id,body=data)
    # if(zz_address!=None):
    #     detail = 'label spread, seed address:'+zz_address

    # for item in result:
    #     addr = item['_id']
    #     #跳过原标签
    #     if(addr == zz_address):
    #         continue
    #     #添加标签到clu索引中
    #     try:
    #         result = es.get(index="my_btc_tag_cluster", doc_type="_doc", id=addr)
    #     except Exception as e:
    #         log.error(e)
    #         data = {
    #             "labels": [{
    #                 "name": tag,
    #                 "category": type,
    #                 "source": 'Label Spread',
    #                 "createtime": today,
    #                 "currency": "Bitcoin",
    #                 "detail": detail
    #             }
    #             ],
    #             "label_sum": 1
    #         }
    #         res = es.index(index="my_btc_tag_cluster", id=addr, body=data)
    #         result = {}
    #
    #     if result:
    #         labels = result["_source"]["labels"]
    #         label_sum = result["_source"]["label_sum"] + 1
    #         new_label = {
    #             "name": tag,
    #             "category": type,
    #             "source": 'Label Spread',
    #             "createtime": today,
    #             "currency": "Bitcoin",
    #             "detail": detail
    #         }
    #
    #         # 判断新增label是否与以前的相同（增量）
    #         if new_label not in labels:
    #             labels.append(new_label)
    #
    #         # 把新的labels加到ES中
    #         new_labels = dict()
    #         new_labels["labels"] = labels
    #         new_labels["label_sum"] = label_sum
    #         res = es.index(index="my_btc_tag_cluster", id=addr, body=new_labels)


# ywj graph
def get_tag_type():  # 得到种子标签和聚类标签的总数
    body = {
        "query": {
            "match_all": {}
        },
        "track_total_hits": True
    }
    result = DataValidation_mybtctag(body, 'seed')
    tag_total = result["hits"]["total"]['value']

    body6 = {
        "query": {
            "match_all": {}
        },
        "track_total_hits": True
    }
    result6 = DataValidation_tag_cluster(body6)
    clu_tag_total = result6['hits']['total']['value']

    body7 = {
        "query": {
            "match_all": {}
        },
        "track_total_hits": True
    }
    result7 = DataValidation_mybtctag(body7, 'all')
    tag_all = result7["hits"]["total"]["value"]

    result_info = {}
    result_info["tag_total"] = tag_total
    result_info['clu_tag_total'] = clu_tag_total
    result_info['tag_all'] = tag_all
    result_info["unmarked"] = tag_all - tag_total - clu_tag_total

    print(result_info)
    return result_info


def top_seed_tags():
    body = {
        "size": 0,  # 只关心聚合结果
        "aggs": {
            "messages": {  # 给聚合起了个名字
                "terms": {
                    "field": "labels.name",  # 按照 name来划分
                    "size": 10  # 只留前10个
                }
            }
        }
    }
    result = DataValidation_mybtctag(body, 'seed')
    topseedtags = result['aggregations']['messages']['buckets']  # key:".com" , doc_count:7689000
    return topseedtags


def top_cluster_tags():
    body = {
        "size": 0,
        "aggs": {
            "messages": {
                "terms": {
                    "field": "labels.name",
                    "size": 10
                }
            }
        }
    }
    result = DataValidation_mybtctag(body, 'clu')
    topclutags = result['aggregations']['messages']['buckets']
    return topclutags


# 查出来 种子标签，数量排前20的，为了拼出总的前10作准备
def pre_seed_tags():
    body = {
        "size": 0,  # 只关心聚合结果
        "aggs": {
            "messages": {  # 给聚合起了个名字
                "terms": {
                    "field": "labels.name",  # 按照 name来划分
                    "size": 1000  # 只留前10个
                }
            }
        }
    }
    result = DataValidation_mybtctag(body, 'seed')
    preseedtags = result['aggregations']['messages']['buckets']  # key:".com" , doc_count:7689000
    return preseedtags


# 查出来 聚类标签，数量排前20的，为了拼出总的前10作准备
def pre_cluster_tags():
    body = {
        "size": 0,
        "aggs": {
            "messages": {
                "terms": {
                    "field": "labels.name",
                    "size": 1000
                }
            }
        }
    }
    result = DataValidation_mybtctag(body, 'clu')
    preclutags = result['aggregations']['messages']['buckets']
    return preclutags


def top_tags_all():
    body = {
        "size": 0,
        "aggs": {
            "messages": {
                "terms": {
                    "field": "labels.name",
                    "size": 10
                }
            }
        }
    }
    result = DataValidation_mybtctag(body, '')
    print(result)
    toptagsall = result['aggregations']['messages']['buckets']
    return toptagsall


def getlastblocktime(height):
    body = {
        "query": {
            "match": {
                "height": height
            }
        }
    }
    res = es.search(body=body, index=btcblock_index)
    ts = res['hits']['hits'][0]['_source']['time']
    lt = time.localtime(ts)
    now = time.strftime("%Y-%m-%d %H:%M:%S", lt)
    return now


def getKG(item):
    sql_dealer = mysql_dealer("kg")
    sql = "select * from sanlie where 主体='{}' ".format(item, item)
    res = sql_dealer.get_cursor_exe_result(sql)
    # print(res)
    atti_list = []
    des_list = []
    if (res is not None):

        for i in res:
            weici = i[2]
            keti = i[3]
            if (weici == 'isA'):
                des_list.append(keti)
            else:
                new_dict = {}
                new_dict['weici'] = i[2]
                new_dict['keti'] = i[3]
                atti_list.append(new_dict)

    return atti_list, des_list


# 获取某个类型实体数量
def get_identi_info(list):
    result_list = []
    total = 0
    for item in list:
        result_dict = {}
        body = {
            "size": 0,
            "aggs": {
                "distinct_labels": {
                    "cardinality": {
                        "field": "labels.name"
                    }
                }
            },
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "labels.category": item
                            }
                        },
                        {
                            "match": {
                                "label_sum": 1
                            }
                        }
                    ]
                }
            }
        }
        result = es.search(index=btctagseed_index, body=body)
        count = result["aggregations"]["distinct_labels"]['value']
        result_dict['source'] = item
        result_dict['count'] = count
        if (result_dict['source'] == 'Exchanges'):
            result_dict['info'] = '交易平台'
        if (result_dict['source'] == 'Services'):
            result_dict['info'] = '数字货币服务商'
        if (result_dict['source'] == 'Gambling'):
            result_dict['info'] = '赌博网站'
        if (result_dict['source'] == 'Historic'):
            result_dict['info'] = '历史标签，目前已经被关闭的服务'
        if (result_dict['source'] == 'Pools'):
            result_dict['info'] = '矿池'
        if (result_dict['source'] == 'user'):
            result_dict['info'] = '论坛或社交网站用户'
        if (result_dict['source'] == 'other'):
            result_dict['info'] = '其他一些不属于以上几种类型的标签'
        if (result_dict['source'] == 'scam'):
            result_dict['info'] = '诈骗事件的地址'
        if (result_dict['source'] == 'Ransomware'):
            result_dict['info'] = '勒索软件地址'
        if (result_dict['source'] == 'victim'):
            result_dict['info'] = '受害者地址'

        if (result_dict['source'] == 'user'):
            result_dict['count'] = 72003
        result_list.append(result_dict)
        total = total + result_dict['count']
    return result_list, total


def get_category_identi(category):
    if (category != None):
        body = {
            "size": 0,
            "aggs": {
                "messages": {
                    "terms": {
                        "field": "labels.name",
                        "size": 3500
                    }
                }
            },
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "labels.category": category
                            }
                        },
                        {
                            "term": {
                                "label_sum": {
                                    "value": "1"
                                }
                            }
                        }
                    ]
                }
            },
            "track_total_hits": True
        }
    else:
        body = {
            "size": 0,
            "aggs": {
                "messages": {
                    "terms": {
                        "field": "labels.name",
                        "size": 200000
                    }
                }
            },
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_all": {}
                        },
                        {
                            "term": {
                                "label_sum": {
                                    "value": "1"
                                }
                            }
                        }
                    ]
                }
            },
            "track_total_hits": True
        }
    res = DataValidation_mybtctag(body, 'seed')
    result_list = []
    for item in res['aggregations']['messages']['buckets']:
        result_dict = {}
        identi = item['key']
        seed_tags = item['doc_count']
        result_dict['identi'] = identi
        result_dict['seed_tags'] = seed_tags
        result_list.append(result_dict)
    return result_list
