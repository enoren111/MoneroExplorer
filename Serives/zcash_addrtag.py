#!/usr/bin/env python
# -*- coding:utf-8 -*-

import elasticsearch.helpers
from flask import request

from mysql_dealer import mysql_dealer
from Model.dataValidation import DataValidation_btctag
from utils import ts2t
import json
import datetime
from config import config
from Serives.btcAddressDetail import getAddressTX
from log import log
import time
# from app import es
log = log.init_logger(config.log_filepath)
sql_dealer = mysql_dealer("btc_addr_tag")
# es.tryagain_instance()
# es = es.instance
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
              "from AddressTag,DomainCategory where AddressTag.source=DomainCategory.domain limit {0},{1}".format(start, perpage)
        # sql_count = "select count(1) from AddressTag"
        sql_count="select num from CountList where Category='total'"
        try:
            count = int(sql_dealer.get_cursor_exe_result(sql_count)[0][0])
            results = sql_dealer.get_cursor_exe_result(sql)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong "+str(sql))
            log.error("running sql wrong "+str(sql))
        else:
            # result_list = []
            for result in results:
                single = dict()
                (
                single['sequence'], single['addr'], single['source'], single['category']) = (result)
                result_list.append(single)

    return count,result_list

def get_tags(start, perpage):
    body={
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
        source =item['_source']['sources']
        com = item['_source']['com']
        category=item['_source']['tags']
        single = dict()
        (single['addr'], single['source'], single['com'],single['category']) = (addr,source,com,category)
        result_list.append(single)
    return total,result_list

def get_i2ps(start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("new_addr")
    except Exception as e:
        print("the connection of the database heuristic_test is wrong:")
    else:
        sql_count = "select * from i2p_addr order by id"
        sql = "select addr,domain,url,createtime,addrtype from i2p_addr order by id limit {0},{1}".format(start,perpage)
        try:
            results = sql_dealer.get_cursor_exe_result(sql)
            results_count = sql_dealer.get_cursor_exe_result(sql_count)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong "+str(sql))
            log.error("running sql wrong "+str(sql))
        else:
            # result_list = []
            count = len(results_count)
            for result in results:
                single = dict()
                (
                 single['addr'], single['domain'], single['url'],single['createtime'],single['addrtype']) = (result)
                result_list.append(single)

    return count,result_list
def get_i2ps_by(addr,domain,coin,start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("new_addr")
    except Exception as e:
        print("the connection of the database heuristic_test is wrong:")
    else:
        sql_count = "select * from i2p_addr where addrtype = '%{}%'order by id".format(coin)
        sql = "select addr,domain,url,createtime,addrtype from i2p_addr where addrtype = '%{2}%' order by id limit {0},{1}".format(start,perpage,coin)
        try:
            results = sql_dealer.get_cursor_exe_result(sql)
            results_count = sql_dealer.get_cursor_exe_result(sql_count)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong "+str(sql))
            log.error("running sql wrong "+str(sql))
        else:
            # result_list = []
            count = len(results_count)
            for result in results:
                single = dict()
                (
                 single['addr'], single['domain'], single['url'],single['createtime'],single['addrtype']) = (result)
                result_list.append(single)

    return count,result_list

def zcash_get_rtt(start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("heuristic_test")
    except Exception as e:
        print("the connection of the database heuristic_test is wrong:")
    else:
        sql_count = "select amount,source_tx,source_height,dest_tx,dest_height from rtt_list order by source_height"
        sql = "select amount,source_tx,source_height,dest_tx,dest_height from rtt_list order by source_height limit {0},{1}".format(start,perpage)
        try:
            results = sql_dealer.get_cursor_exe_result(sql)
            results_count = sql_dealer.get_cursor_exe_result(sql_count)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong "+str(sql))
            log.error("running sql wrong "+str(sql))
        else:
            # result_list = []
            count = len(results_count)
            for result in results:
                single = dict()
                (
                 single['amount'], single['s_tx'], single['s_height'],single['d_tx'],single['d_height']) = (result)
                result_list.append(single)

    return count,result_list
def get_query_history(start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("darknet_btc_analyze")
    except Exception as e:
        print("the connection of the database heuristic_test is wrong:")
    else:
        sql_count = "select * from query_history order by id"
        sql = "select keyword,remark,addr,domain,coin,sdate,edate from query_history order by id limit {0},{1}".format(start,perpage)
        try:
            results = sql_dealer.get_cursor_exe_result(sql)
            results_count = sql_dealer.get_cursor_exe_result(sql_count)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong "+str(sql))
            log.error("running sql wrong "+str(sql))
        else:
            count = len(results_count)
            for result in results:
                log.error(result)
                single = dict()
                (single['kw'], single['remark'],single['addr'], single['domain'],single['coin'],single['sdate'],single['edate']) = (result)
                if single['sdate'] == datetime.datetime(1111,11,11,11,11,11):
                    single['sdate'] = ""
                if single['edate'] == datetime.datetime(1111,11,11,11,11,11):
                    single['edate'] = ""
                single['sdate']=str(single['sdate'])
                single['edate']=str(single['edate'])
                log.error(single['sdate'])
                result_list.append(single)

    return count,result_list
def get_trans_query_history_pro(start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("darknet_btc_analyze")
    except Exception as e:
        print("the connection of the database heuristic_test is wrong:")
    else:
        sql_count = "select * from trans_query_history_pro order by id"
        sql = "select keyword,remark,querytext from trans_query_history_pro order by id limit {0},{1}".format(start,perpage)
        try:
            results = sql_dealer.get_cursor_exe_result(sql)
            results_count = sql_dealer.get_cursor_exe_result(sql_count)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong "+str(sql))
            log.error("running sql wrong "+str(sql))
        else:
            count = len(results_count)
            for result in results:
                log.error(result)
                single = dict()
                (single['kw'],single['remark'], single['text']) = (result)
                log.error(single)
                result_list.append(single)

    return count,result_list
def get_trans_query_history(start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("darknet_btc_analyze")
    except Exception as e:
        print("the connection of the database heuristic_test is wrong:")
    else:
        sql_count = "select * from trans_query_history order by id"
        sql = "select blockheight,fee,keyword,maxval,minval,sdate,edate,inputaddr,outputaddr,inputnum,outputnum,topic,specvalue,remark from trans_query_history order by id limit {0},{1}".format(start,perpage)
        try:
            results = sql_dealer.get_cursor_exe_result(sql)
            results_count = sql_dealer.get_cursor_exe_result(sql_count)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong "+str(sql))
            log.error("running sql wrong "+str(sql))
        else:
            count = len(results_count)
            for result in results:
                log.error(result)
                single = dict()
                (single['height'],single['fee'],single['kw'], single['maxval'], single['minval'],single['sdate'],single['edate'],single['input'],single['output'],single['inputnum'],single['outputnum'],single['topic'],single['specvalue'],single['remark']) = (result)
                if single['sdate'] == datetime.datetime(1111,11,11,11,11,11):
                    single['sdate'] = ""
                if single['edate'] == datetime.datetime(1111,11,11,11,11,11):
                    single['edate'] = ""
                single['sdate']=str(single['sdate'])
                single['edate']=str(single['edate'])
                log.error(single['sdate'])
                result_list.append(single)

    return count,result_list
def zcash_get_rtt_by_differ(differ,start, perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("heuristic_test")
    except Exception as e:
        print("the connection of the database heuristic_test is wrong:")
    else:
        sql_count = "select amount,source_tx,source_height,dest_tx,dest_height from rtt_list where (unix_timestamp(dest_time)-unix_timestamp(source_time)) >0 and (unix_timestamp(dest_time)-unix_timestamp(source_time)) < %s order by source_height" % differ
        sql = "select amount,source_tx,source_height,dest_tx,dest_height from rtt_list where (unix_timestamp(dest_time)-unix_timestamp(source_time)) >0 and (unix_timestamp(dest_time)-unix_timestamp(source_time)) < %s order by source_height limit {0},{1}".format(start,perpage) % differ
        try:
            results = sql_dealer.get_cursor_exe_result(sql)
            results_count = sql_dealer.get_cursor_exe_result(sql_count)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong "+str(sql))
            log.error("running sql wrong "+str(sql))
        else:
            # result_list = []
            count = len(results_count)
            for result in results:
                single = dict()
                (
                 single['amount'], single['s_tx'], single['s_height'],single['d_tx'],single['d_height']) = (result)
                result_list.append(single)

    return count,result_list

def updateAddressTag(address,tag,source,com):
    try:
        actions=[]
        id=address
        sources=[source]
        tags =[tag]
        com=[com]
        single = dict()
        (single['sources'], single['tags'], single['com']) = (sources,tags,com)
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
        log.error("添加标签失败",e)
        return 0


def updateSpecialAddr(address,remark,minvalue,maxvalue):
    txs = getAddressTX(address,1)
    tx=""
    amout=0
    lasttime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if txs:
        tx = txs["hits"]["hits"][0]['_id']
        amout = txs["hits"]["hits"][0]['_source']['volume']/10000000
        lasttime=txs["hits"]["hits"][0]['_source']['blocktime']
        last_time = time.mktime(time.strptime(lasttime, "%Y-%m-%dT%H:%M:%S"))
        struct_time = time.localtime(last_time)  # 得到结构化时间格式
        lasttime = time.strftime("%Y-%m-%d %H:%M:%S", struct_time)
    try:
        log.info("开始添加标签")
        sql ="insert into addr_monitor(addr,remark,last_tx,last_time,amout,minvalue,bigvalue) values(%s,%s,%s,%s,%s,%s,%s)"
        sql_dealer.cursor.execute(sql,(address,remark,tx,lasttime,amout,minvalue,maxvalue))
        sql_dealer.db.commit()
        log.info("添加标签成功")
        return 1
    except Exception as e:
        sql_dealer.db.rollback()
        log.error("添加标签失败",e)
        return 0


def get_address_tags_with_two(address,servicename,start,perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("btc_addr_tag")
    except Exception as e:
        print("the connection of the database btc_addr_tag) is wrong:")

    else:
        sql = "select AddressTag.sequence,AddressTag.addr,AddressTag.source,DomainCategory.category " \
              "from AddressTag,DomainCategory where AddressTag.SOURCE=DomainCategory.domain and AddressTag.addr='{2}' and DomainCategory.category='{3}' limit {0},{1}".format(start,perpage,address, servicename)
        sql_count ="select count(1) from AddressTag,DomainCategory where AddressTag.source=DomainCategory.domain and AddressTag.addr='{2}' and DomainCategory.category='{3}' limit {0},{1}".format(start,perpage,address, servicename)

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
    return count,result_list


def get_address_tags(address,tag,source,com,start,perpage):
    if len(address)!=0:
        total=1
        result=es.get(index='btc_tag',doc_type='raw',id=address)
        category =result["_source"]["tags"]
        result_list=[]
        single = dict()
        (single['addr'], single['source'], single['com'], single['category']) = (address, result['_source']['sources'], result['_source']['com'],result['_source']['tags'] )
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
            rule = '.*'+com+'.*'
            body = {
                "query":{
            "regexp":{
                "com": {
                    "value": rule,
                }
            }
            },
        "from":start,
         "size":perpage,
        "track_total_hits": True
    }
        else:
            body = {
                "query":
                  {
                    "match_all":{},
                  },
          "track_total_hits": True,
                "from":start,
                "size":perpage,
            }
        result = DataValidation_btctag(body)
        result_list = []
        total = result["hits"]["total"]['value']
        for item in result['hits']['hits']:
            addr = item['_id']
            source =item["_source"]["sources"]
            com = item['_source']['com']
            category =item["_source"]["tags"]
            single = dict()
            (single['addr'], single['source'], single['com'], single['category']) = (addr, source, com, category)
            result_list.append(single)
    return total, result_list


def get_special_addrs(address,start,perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("btc_addr_tag")
    except Exception as e:
        print("the connection of the database btc_addr_tag is wrong:")

    else:
        sql = "select id,addr,last_tx,last_time,amount,flag " \
              "from specialAddr where addr like '%{2}%' limit {0},{1}".format(start,perpage,address)
        try:
            results = sql_dealer.get_cursor_exe_result(sql)
            log.info("run sql successful" + str(sql))
        except Exception as e:
            print("running sql wrong " + str(sql))
            log.error("running sql wrong " + str(sql))
        else:
            count =len(results)
            for result in results:
                single = dict()
                (
                    single['id'], single['addr'], single['last_tx'], single['last_time'],single['amount'],single['flag']) = (result)
                result_list.append(single)
    return count,result_list


def get_address_tags_with_service(servicename,start,perpage):
    count = 0
    result_list = []
    try:
        sql_dealer = mysql_dealer("btc_addr_tag")
    except Exception as e:
        print("the connection of the database btc_addr_tag is wrong:")

    else:
        sql = "select AddressTag.sequence,AddressTag.addr,AddressTag.source,DomainCategory.category " \
              "from AddressTag,DomainCategory where AddressTag.source=DomainCategory.domain and DomainCategory.category='{2}' limit {0},{1}".format(start,perpage,servicename)
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
    return count,result_list


def get_address_tags_with_address(address,start,perpage):
    count=0
    result_list = []
    try:
        sql_dealer = mysql_dealer("btc_addr_tag")
    except Exception as e:
        print("the connection of the database btc_addr_tag is wrong:")

    else:
        sql = "select AddressTag.sequence,AddressTag.addr,AddressTag.source,DomainCategory.category " \
              "from AddressTag,DomainCategory where AddressTag.source=DomainCategory.domain and AddressTag.ADDR='{2}' limit {0},{1}".format(start,perpage,address)
        sql_count ="select count(1) from AddressTag,DomainCategory where AddressTag.source=DomainCategory.domain and AddressTag.addr='{2}' limit {0},{1}".format(start,perpage,address)
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
    return count,result_list
