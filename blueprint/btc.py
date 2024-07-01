import math

import requests
from flask import Blueprint, current_app, render_template, request, jsonify, session
from flask_paginate import Pagination, get_page_parameter
from Serives import blockreturn, transactionreturn, btcblock, zcash_blockreturn, btctransaction, my_transaction
from Serives.BodyUtils import buildQueryBody
from Serives.bitcoinmessage import get_by_newsearch, get_by_newsearch_new
from Serives.btcAddressDetail import handleAddressTx
from Serives.zcash_addrtag import get_trans_query_history, get_trans_query_history_pro
from dao.bitcoin_node import get_btc_node, get_btc_node_analyse, get_max_height, get_btc_node_byIP
from dao.mybtc import cluster, get_tag_info
from utils import validation_address, get_dict_key_value, my_validation_address
from dao import datainterchange
from flask_login import login_required, current_user
from Serives.btcaddrtag import *
import re
from dao.txTraceDao import getTraceAddressDetail,getTraceTxDetail,traceAferTx,getAddressTag
from Serives.txTraceService import *

btc_bp = Blueprint('btc', __name__)
from config import config
from log import log
from bee_var import perPage, perPage_10
from mysql_dealer import mysql_dealer
import time
from datetime import datetime
# from app import es
from Serives.btcaddrtag import get_address_tags_with_address, get_address_tags_with_service, \
    get_address_tags_with_two, get_pure_address_tags, updateAddressTag, get_tags, get_address_tags, get_special_addr, \
    updateSpecialAddr, get_special_addrs, updateQueryHistory, updateTransQueryHistory, get_my_tags, updateAddressMyTag, \
    get_address_mytags, get_my_mix
from dao.graphTraceDao import generateGraphData,addressTrace,graphtxTraceData,graphtxTraceBeforeData,graphAddressTraceBeforeData
log = log.init_logger(config.log_filepath)

# es.tryagain_instance()
# es = es.instance


#
# qpr BLOCK页面
@btc_bp.route('/btc')
def btc_home():
    # blocks, context1 = blockreturn.block_return(5, 0)
    # context2, latestTransList = transactionreturn.trans_return(5, 0)
    # return render_template('btc/btc_home.html', blocks=blocks, **context1)
    # return render_template('btc/btc_home.html',**context)
    latestTransList, context = blockreturn.btc_home_show()
    return render_template('btc/btc_home.html', latestTransList=latestTransList, **context)
@btc_bp.route('/btc/graphAddressTraceBefore',methods=['GET'])
def graphAddressTraceBefore():
    txid = request.args.get("txid", "")
    n=int(request.args.get("n", ""))
    result=graphAddressTraceBeforeData(txid,n)
    return jsonify(result)
@btc_bp.route('/btc/graphtxTraceBefore',methods=['GET'])
def graphtxTraceBefore():
    txid = request.args.get("txid", "")
    result=graphtxTraceBeforeData(txid)
    return jsonify(result)
@btc_bp.route('/btc/graphtxTrace',methods=['GET'])
def graphtxTrace():
    txid = request.args.get("txid", "")
    result=graphtxTraceData(txid)
    return jsonify(result)
@btc_bp.route('/btc/addrTrace',methods=['GET'])
def addrTrace():
    txid = request.args.get("txid", "")
    n=request.args.get("n", "")
    result=addressTrace(txid,n)
    return jsonify(result)
@btc_bp.route('/btc/traceGraph',methods=['GET'])
def traceGraph():
    return render_template("btc/traceGraph.html")
@btc_bp.route('/btc/generateGraph/<string:txid>', methods=['GET'])
def generateGraph(txid):
    change = request.args.get("change", "")
    result = generateGraphData(txid,change)
    return jsonify(result)
@btc_bp.route('/btc/traceTxHistory',methods=['GET'])
def traceHistory():
    result=txTraceHistory()
    return render_template("btc/txTraceHistory.html",result=result)
@btc_bp.route('/btc/savetraceTx/',methods=['POST'])
def savetraceTx():
    args = request.get_json()
    print(args)
    data=args["data"]
    beizhu=args["beizhu"]
    saveTraceTxData(beizhu,data)
    return "0"
@btc_bp.route('/btc/traceTest')
def traceTest():
    txid = request.args.get("txid", "")
    if txid == "":
        status = 0
    else:
        status = 2
    return render_template("btc/traceTx.html", status=status, result={}, txid=txid)
@btc_bp.route('/btc/traceTx/<string:txid>',methods=['POST','GET'])
def trace(txid):
    # print(txid)
    depth = request.args.get("depth", type=int, default=3)
    print("depth:{}".format(depth))
    findChange=optimalChange
    data=txTrace1(txid,depth,findChange)
    # print(data)
    return jsonify(data)
@btc_bp.route('/btc/traceTag/<string:address>',methods=['GET'])
def traceAddress(address):
    result=getAddressTag(address)
    result_dict={}
    result_dict["data"]=result
    result_dict["msg"]=""
    result_dict["code"]=0
    return jsonify(result_dict)
@btc_bp.route('/btc/txtrace/txDetail/<string:txid>')
def txDetail(txid):
    result=getTraceTxDetail(txid)
    return jsonify(result)
@btc_bp.route('/btc/txtrace/addressDetail/<string:address>')
def addressDetail(address):
    result=getTraceAddressDetail(address)
    return jsonify(result)
@btc_bp.route('/btc/txtrace/traceAfterTx')
def traceAfterTx():
    utxo=request.values["utxo"]
    n=request.values["n"]
    result=traceAferTx(utxo,n)
    return jsonify(result)
@btc_bp.route('/btc/gettxTraceHistory',methods=['GET'])
def gettraceHistory():
    id=int(request.args.get("id"))
    result=gettraceHistoryData(id)
    # print(id)
    return render_template("btc/traceTx.html",result=result,status=1,txid="")
@btc_bp.route('/btc/block')
def btc_block():
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    blocks, context = blockreturn.block_return(perPage, start)  # pagination默认perPage20
    total = context['block_total']
    log.info("区块信息总数为" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='blocks')
    return render_template('btc/btc_block.html', blocks=blocks, pagination=pagination, **context)


@btc_bp.route('/btc/block_detail/<string:hash>')
def btc_block_detail(hash):
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, blocktrans = blockreturn.blockdetail_return(hash, start, perpage, True)
    total = context["total"]
    log.info("交易总量为" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('btc/block_detail.html', pagination=pagination, blocktrans=blocktrans,
                           **context)  # **context


# YZY 比特币交易详情页
@btc_bp.route('/btc/tsc_detail/<string:hash>')  ##后端数据已经准备完毕，前端页面还未处理！
def btc_tsc_detail(hash):
    tsc_info, context = transactionreturn.trans_detail_return(hash)
    log.info("交易详细信息为：")
    log.info("返回页面tsc_detail")
    return render_template('btc/tsc_detail.html', tsc_info=tsc_info, **context)


@btc_bp.route('/btc/trans/static')
def btc_trans_static():
    return render_template('btc/btc_transaction_static.html')


@btc_bp.route('/btc/trans/big_deal')
def btc_big_deal():
    return render_template('btc/big_deal.html')


@btc_bp.route('/btc/query')
def btc_query():
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, latestTransList = transactionreturn.trans_return(perpage, start)
    total = 0
    log.info("交易信息总数为" + str(total))
    context = {}
    # latestTransList=[]
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('btc/query.html', latestTransList=latestTransList,
                           pagination=pagination, **context)


@btc_bp.route('/btc/query_trans')
def btc_query_test():
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, latestTransList = transactionreturn.trans_return(perpage, start)
    total = context["trans_total"]
    log.info("交易信息总数为" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('btc/query_trans.html', latestTransList=latestTransList, pagination=pagination, **context)



# ADDRESS

@btc_bp.route('/btc/address')
def btc_address():
    # 富豪榜 获取地址余额
    # address: 0x00B32FF033e8241843BbAa7403D6A729dD8bc1B8
    # miner: 0x497A49648885f7aaC3d761817F191ee1AFAF399C
    # richList = [[1, '0x497A49648885f7aaC3d761817F191ee1AFAF399C', 0, 0, 0]]  # 模拟数据
    richList = [
        {'rank': 1, 'address': '0x497A49648885f7aaC3d761817F191ee1AFAF399C', 'trans_num': 0, 'value': 0, 'perc': 0},
        {'rank': 2, 'address': '0x72BCFA6932FeACd91CB2Ea44b0731ed8Ae04d0d3', 'trans_num': 0, 'value': 0, 'perc': 0},
        {'rank': 3, 'address': '0xb692703a8f3f62EAB1369e5C36A191D6a3C06D1d', 'trans_num': 0, 'value': 0, 'perc': 0},
        {'rank': 4, 'address': '0x01d78C68D00F6040D6f4dC54952F54682923d23D', 'trans_num': 0, 'value': 0, 'perc': 0},
        {'rank': 5, 'address': '0x074Ee87c21afd18FD5534970A3e0664932bC2E65', 'trans_num': 0, 'value': 0, 'perc': 0},
        {'rank': 6, 'address': '0xd95209a707F17B6E8B68c9664DBf26027d15f897', 'trans_num': 0, 'value': 0, 'perc': 0},
        {'rank': 7, 'address': '0x268f6E92dAF22e5FC92ea1EE63774c4F9D47Dfa7', 'trans_num': 0, 'value': 0, 'perc': 0},
        {'rank': 8, 'address': '0x6E0052c3032F76034A9CD85F5018Da41b174a323', 'trans_num': 0, 'value': 0, 'perc': 0},
        {'rank': 9, 'address': '0x027f9F857581365a70f3812Ea5F565946e7aC0d', 'trans_num': 0, 'value': 0, 'perc': 0},
        {'rank': 10, 'address': '0x38743aEc8e71277B44a06e40A7af9c20d3C262c2', 'trans_num': 0, 'value': 0, 'perc': 0},
    ]

    # def foo():
    #     return get_transes_v2(size=0, address=item['address'])['total']
    #
    # for item in richList:
    #     item['trans_num'] = visit_mode_check(foo, data=100)
    #
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(bs_version=4, page=page, total=20, per_page=10, record_name='rich')

    # fields, content = get_daily_eth_a_info()
    chart_data = []
    # for id,item in enumerate(content['date']):
    #     data = {}
    #     data['date'] = item
    #     data['new_address'] = content['new_address'][id]
    #     data['active_address'] = content['active_address'][id]
    #     chart_data.append(data)
    content = {}
    content["active_address"] = 100
    content['new_address'] = 100
    content['date'] = "2020-4-20"
    context = {
        'active_address': content['active_address'],
        'new_address': content['new_address'],
        'date': content['date'],
        "page_title": '地址',
        "pages": 2
        # chart_data:chart_data
    }

    return render_template('zcash/address_static.html', richList=richList, pagination=pagination, **context)


# YZY地址标签
@btc_bp.route('/btc/addrtag', methods=['GET', 'POST'])
def btc_addrtag():
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    count, list = get_pure_address_tags(start, perpage)
    usetime = round(time.time() - t, 3)
    content = {
        "page_title": '地址标签',
        "count": count,
        "address": None,
        "servicename": None,
        "usetime": usetime
    }
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/btc_addrtag.html', list=list, pagination=pagination, **content)


@btc_bp.route('/btc/tag', methods=['GET', 'POST'])
def btc_tag():
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    count, list = get_tags(start, perpage)
    usetime = round(time.time() - t, 3)
    content = {
        "page_title": '地址标签',
        "count": count,
        "address": None,
        "servicename": None,
        "usetime": usetime
    }
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/btc_tag.html', list=list, pagination=pagination, **content)


# @btc_bp.route('/QueryAgain/',methods=['POST'])
# def query_again():
#
##构造查询
@btc_bp.route('/saveQuery/', methods=['POST'])
def btc_saveQuery():
    args = request.get_json()
    remark = args['remark']
    addr = args['addr']
    domain = args['domain']
    coin = args['coin']
    sdate = args['sdate']
    edate = args['edate']
    keyword = args['kw']
    # keyword="forTest"
    log.error("peng!", addr, domain, coin, sdate, edate, keyword, remark)
    log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    try:
        log.info("---------------------------------------------------")
        # if validation_address('btc',addr):
        if 2 > 1:
            flag = updateQueryHistory(addr, domain, coin, sdate, edate, keyword, remark)
            # flag=1
            if flag == 1:
                result = {"code": "0000", "message": "添加成功"}  ##更新成功
            else:
                result = {"code": '1111', "message": "添加失败"}
            return result
    except Exception as e:
        log.error("输入的地址有误，请检查", e)
        return {"code": '1111', "message": "地址输入有误，请检查"}


@btc_bp.route('/saveTransQuery/', methods=['POST'])
def btc_saveTransQuery():
    args = request.get_json()
    inputaddr = args['input']
    outputaddr = args['output']
    maxvalue = args['maxvalue']
    minvalue = args['minvalue']
    stime = args['stime']
    etime = args['etime']
    keyword = args['kw']
    height = args['height']
    fee = args['fee']
    inputnum = args['inputnum']
    outputnum = args['outputnum']
    topic = args['topic']
    specvalue = args['specvalue']
    remark = args['remark']
    log.error("peng!", maxvalue, minvalue, stime, etime, keyword, height, fee, inputnum, outputnum, topic, specvalue,
              remark)
    log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    try:
        log.info("---------------------------------------------------")
        # if validation_address('btc',addr):
        if 2 > 1:
            flag = updateTransQueryHistory(maxvalue, minvalue, stime, etime, keyword, inputaddr, outputaddr, height,
                                           fee, inputnum, outputnum, topic, specvalue, remark)
            # flag=1
            if flag == 1:
                result = {"code": "0000", "message": "添加成功"}  ##更新成功
            else:
                result = {"code": '1111', "message": "添加失败"}
            return result
    except Exception as e:
        log.error("输入的地址有误，请检查", e)
        return {"code": '1111', "message": "地址输入有误，请检查"}
@btc_bp.route('/saveTransQueryPro/', methods=['POST'])
def btc_saveTransQueryPro():
    args = request.get_json()
    keyword = args['kw']
    remark = args['remark']
    text = args['text']

    log.error("peng!", keyword,remark,text)
    log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    try:
        log.info("---------------------------------------------------")
        # if validation_address('btc',addr):
        if 2 > 1:
            flag = updateTransQueryHistoryPro(keyword,remark,text)
            # flag=1
            if flag == 1:
                result = {"code": "0000", "message": "添加成功"}  ##更新成功
            else:
                result = {"code": '1111', "message": "添加失败"}
            return result
    except Exception as e:
        log.error("输入的地址有误，请检查", e)
        return {"code": '1111', "message": "地址输入有误，请检查"}

@btc_bp.route('/queryhistory_detail/', methods=['POST'])
def btc_queryhistory_detail():
    # rule = request.values['sortname']
    kw = request.values['keyword']
    remark = request.values['remark']
    inputaddr = request.values['inputaddr']
    outputaddr = request.values['outputaddr']
    starttime = request.values['starttime']
    endtime = request.values['endtime']
    minvalue = request.values['minvalue']
    maxvalue = request.values['maxvalue']
    height = request.values['height']
    fee = request.values['fee']
    input_num = request.values['input_num']
    output_num = request.values['output_num']
    topic = request.values['topic']
    specvalue = request.values['specvalue']
    log.error(remark)
    return render_template('btc/query_history_detail.html', stime=starttime, etime=endtime, maxvalue=maxvalue,
                           minvalue=minvalue,
                           inputaddr=inputaddr, outputaddr=outputaddr, height=height, fee=fee, inputnum=input_num,
                           outputnum=output_num, topic=topic, specvalue=specvalue, kw=kw, remark=remark)


@btc_bp.route('/i2p_queryhistory_detail/', methods=['POST'])
def i2p_query_detail():
    remark = request.values['remark']
    kw = request.values['keyword']
    address = request.form['address']
    domain = request.form['domain'].replace(" ", "")
    coin = request.form['coin']
    sdate = request.form['sdate']
    edate = request.form['edate']
    log.error(kw + sdate + edate + domain + coin + address)
    return render_template('btc/i2p_query_history_detail.html', sdate=sdate, edate=edate, domain=domain, addr=address,
                           coin=coin, kw=kw, remark=remark)


@btc_bp.route('/darknet/test/', methods=['POST'])
def test():
    return render_template('btc/query_trans.html')


##添加标签
@btc_bp.route('/btc/saveTag/', methods=['POST'])
def btc_saveTag():
    args = request.get_json()
    addr = args['addr']
    tag = args['tag']
    source = args['source']
    com = args['com']
    log.error(addr)
    log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    try:
        log.info("---------------------------------------------------")
        if validation_address('btc', addr):
            flag = updateAddressTag(addr, tag, source, com)
            if flag == 1:
                result = {"code": '0000', "message": "添加成功"}  ##更新成功
            else:
                result = {"code": '1111', "message": "添加失败"}
            return result
    except Exception as e:
        log.error("输入的地址有误，请检查", e)
        return {"code": '1111', "message": "地址输入有误，请检查"}


@btc_bp.route('/btc/sepcialAddr', methods=['GET', 'POST'])
def btc_sepcialAddr():
    perpage = 10  # pagination默认
    page = request.args.get("page", type=int, default=1)
    type = request.args.get("type", default="monitor")
    address = request.args.get("address", default="")
    count = int(request.args.get("count", default="0"))
    print("address:" + address)
    userid = "1"
    start = (page - 1) * perpage
    t = time.time()
    if type == 'monitor_list':
        count, list = get_special_addr(start, perpage, userid, address, count)
        # print(list)
        usetime = round(time.time() - t, 3)
        content = {
            "page_title": '地址监控',
            "count": count,
            "search_address": address,
            "servicename": None,
            "usetime": usetime,
            "type": type
        }
        pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
        return render_template('btc/btc_special_addr.html', list=list, pagination=pagination, **content)
    if type == "monitor":
        count, list = get_monitor(start, 10, userid)
        usetime = round(time.time() - t, 3)
        content = {
            "page_title": '地址监控',
            "count": count,
            "address": None,
            "servicename": None,
            "usetime": usetime,
            "type": type
        }
        pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
        return render_template('btc/btc_special_addr.html', list=list, pagination=pagination, **content)


##添加标签
@btc_bp.route('/btc/saveAddr/',methods=['POST'])
def btc_saveAddr():
    args = request.get_json()
    address =args['addr']
    remark = args['remark']
    minvalue = args['minvalue']
    maxvalue = args['maxvalue']
    if address=="":
        result = {"code": '1111', "message": "添加失败"}
    if minvalue=="":
        minvalue=0
    if maxvalue=="":
        maxvalue=1000000
    # print(remark)
    # log.error(addr)
    # log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    try:
        # log.info("---------------------------------------------------")
        # if validation_address('btc',addr):
        print(args)
        flag = updateSpecialAddr(address,remark,minvalue,maxvalue)
        flag=1
        if flag==1:
            result={"code":'0000',"message":"添加成功"}  ##更新成功
        else:
            result={"code":'1111',"message":"添加失败"}
        return result
    except Exception as e:
        log.error("输入的地址有误，请检查",e)
        return {"code":'1111',"message":"地址输入有误，请检查"}
@btc_bp.route('/btc/modifyAddr/',methods=['POST'])
def btc_modifyAddr():
    args = request.get_json()
    remark = args['remark']
    minvalue = args['minvalue']
    maxvalue = args['maxvalue']
    monitor_id=args['monitor_id']
    try:
        print(args)
        flag = modifySpecialAddr(monitor_id,remark,minvalue,maxvalue)
        flag=1
        if flag==1:
            result={"code":'0000',"message":"添加成功"}  ##更新成功
        else:
            result={"code":'1111',"message":"添加失败"}
        return result
    except Exception as e:
        log.error("输入的地址有误，请检查",e)
        return {"code":'1111',"message":"地址输入有误，请检查"}
@btc_bp.route('/btc/delete_monitor_list',methods=['GET','POST'])
def btc_delete_monitor_list():
    # id=request.data["list_id"]
    args = request.get_json()
    id = args['list_id']
    print(id)
    dealer=mysql_dealer("monitor")
    sql="delete from monitor_list where id={}".format(id)
    dealer.cursor.execute(sql)
    dealer.db.commit()
    return "success"
@btc_bp.route('/btc/delete_monitor_id',methods=['GET','POST'])
def btc_delete_monitor_id():
    # id=request.data["list_id"]
    args = request.get_json()
    id = args['monitor_id']
    print(id)
    dealer=mysql_dealer("monitor")
    sql="delete from address_monitor where monitor_id={}".format(id)
    dealer.cursor.execute(sql)
    sql="delete from monitor_list where monitor_id={}".format(id)
    dealer.cursor.execute(sql)
    dealer.db.commit()
    return "success"
# YZY地址标签搜索
@btc_bp.route('/btc/addrtagsearch', methods=['GET', 'POST'])
def btc_addrtag_search():
    address = request.values['address']
    servicename = request.values['servicename']
    # 是否存在地址  是否存在类别
    # len(address)!=0 servicename!=None
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    if (len(address) != 0) & (servicename != "None"):
        print("two use")
        count, list = get_address_tags_with_two(address, servicename, start, perpage)
        content = {
            "page_title": '地址标签',
            "count": count,
            "address": address,
            "servicename": servicename
        }
    elif (len(address) == 0) & (servicename != "None"):
        print("use service")
        print(servicename)
        count, list = get_address_tags_with_service(servicename, start, perpage)
        content = {
            "page_title": '地址标签',
            "count": count,
            "address": "",
            "servicename": servicename
        }
    elif (len(address) != 0) & (servicename == "None"):
        print("use address")
        count, list = get_address_tags_with_address(address, start, perpage)
        content = {
            "page_title": '地址标签',
            "count": count,
            "address": address,
            "servicename": None
        }
    else:
        #     (len(address)==0) & (servicename==None)
        print("use nothing")
        count, list = get_pure_address_tags(start, perpage)
        content = {
            "page_title": '地址标签',
            "count": count,
            "address": "",
            "servicename": None
        }
    usetime = round(time.time() - t, 3)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/btc_addrtag.html', list=list, **content, pagination=pagination, usetime=usetime)


@btc_bp.route('/btc/tagsearch', methods=['GET', 'POST'])
def btc_tag_search():
    address = request.values['address']
    tag = request.values['tags']
    source = request.values['sources']
    com = request.values['coms']
    # 是否存在地址  是否存在类别
    # len(address)!=0 servicename!=None
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    count, list = get_address_tags(address, tag, source, com, start, perpage)
    content = {
        "page_title": '地址标签',
        "count": count,
        "address": address,
    }
    usetime = round(time.time() - t, 3)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/btc_tag.html', list=list, **content, pagination=pagination, usetime=usetime)


@btc_bp.route('/btc/specialAddrsearch', methods=['GET', 'POST'])
def btc_special_addr_search():
    address = request.values['address']
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    if (len(address) != 0):
        print("two use")
        count, list = get_special_addrs(address, start, perpage)
        content = {
            "page_title": '地址监控',
            "count": count,
            "address": address,
        }
    else:
        print("use nothing")
        count, list = get_special_addr(start, perpage)
        content = {
            "page_title": '地址监控',
            "count": count,
            "address": "",
            "servicename": None
        }
    usetime = round(time.time() - t, 3)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/btc_special_addr.html', list=list, **content, pagination=pagination, usetime=usetime)


# YZY夹带信息
@btc_bp.route('/btc/carryinfor', methods=['GET', 'POST'])
def btc_carryinfor():
    # str = request.values['txhash']
    perpage = perPage_10
    str = "bitcoin"
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    order = "asc"
    list, context = get_by_newsearch(perpage, start, str, order)
    total = context['total_num']
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='bitcoincarry')
    return render_template('btc/btc_carryinfor.html', list=list, pagination=pagination, **context)


# YZY夹带信息搜索
@btc_bp.route('/btc/carryinforsearch', methods=['GET', 'POST'])
def btc_carryinfor_search():
    str = request.values['txhash']
    starttime = request.values['starttime']
    endtime = request.values['endtime']
    lanuage = request.values['lanname']
    order = request.values['sorttype']
    perpage = perPage_10
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    list, context = get_by_newsearch_new(perpage, start, str, order, starttime, endtime,
                                         lanuage)  # pagination默认perPage20
    total = context['total_num']
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='bitcoincarry')
    return render_template('btc/btc_carryinfor.html', list=list, pagination=pagination, **context)


# YZY bitcoin node
@btc_bp.route('/btc/node/')
def btc_node():
    perpage = perPage_10
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()

    node_dist = get_btc_node_analyse()
    print(node_dist)
    pie_series = {}  # 饼图数据
    interval = 30

    for key in node_dist:
        sum_nums = sum(item['value'] for item in node_dist[key][:])
        others_nums = sum(item['value'] for item in node_dist[key][interval:])
        pie_series[key] = node_dist[key][0:interval]
        pie_series[key].append({"value": (sum(item['value'] for item in node_dist[key][interval:])), "name": "others",
                                "p": str(round(others_nums / sum_nums * 100, 2)) + '%'})
        # pie_series[key].append({"value":(sum(item['value'] for item in node_dist[key][interval:])),"name":"others","p":str(round(sum(item['pv'] for item in node_dist[key][interval:])*100,2)) +'%' })
    print(pie_series)
    node_list, count = get_btc_node(perpage, start)  # pagination默认perPage20
    total = count
    took = round(time.time() - t, 2)
    maxheight = get_max_height()
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcoinnode')
    context = {
        "page_title": '节点',
        "node_dist": node_dist,
        "total": total,
        "took": took,
        "pie_series": pie_series,
        #  "maxheight": 999999
        "maxheight": maxheight
    }
    return render_template('btc/btc_node.html', node_list=node_list, pagination=pagination, **context)


# YZY bitcoin checknode
@btc_bp.route('/btc/ajax/check_node', methods=['POST'])
def check_node():
    # print(request.args.get('ip'))
    # ip = request.values['ip']
    # port = request.values['port']
    node_ip = '67.203.1.170'
    node_port = '30303'
    url = 'http://192.168.126.52:5600/?addr=' + node_ip + ':' + node_port
    try:
        r = requests.get(url)
        response_dict = r.json()
    except:
        response_dict = {"result": 0, "ret": "error"}
    status = get_dict_key_value(response_dict, ['result']);
    # status = 0
    node_info = {
        'node_ip': node_ip,
        'node_port': node_port
    }
    if status == 1:
        node_info['status'] = 'online'
        # node_info = search_node(node_ip)
    else:
        node_info['status'] = 'offline'

    return jsonify(node_info)


@btc_bp.route('/btc/ajax/search_btc_node', methods=['POST'])
def search_btc_node():
    data = request.get_json()
    node_info = get_btc_node_byIP(data)
    return jsonify(node_info)


# GPY 地址网络出现
@btc_bp.route('/btc/block2', methods=['GET'])
def btc_block2():
    page_size = 5
    address = request.args.get("address", "")
    domain = request.args.get("domain", "")
    try:
        page = int(request.args.get("page", 1))
    except:
        page = 1
    order = request.args.get("order", "desc")
    sql1 = "select * from view3 order by balance {2} limit {0},{1}".format((page - 1) * page_size, page_size, order)
    sql2 = "select * from view3 where domain='{2}' order by balance {3} limit {0},{1}".format((page - 1) * page_size,
                                                                                              page_size, domain, order)
    sql3 = "select * from view3 where addr='{2}' order by balance {3} limit {0},{1}".format((page - 1) * page_size,
                                                                                            page_size, address, order)

    sql4 = "select * from view3 where addr='{2}' and domain='{3}' order by balance {4} limit {0},{1}".format(
        (page - 1) * page_size, page_size, address, domain, order)
    if domain == "" and address == "":
        sql = sql1
    if domain == "" and address != "":
        sql = sql3
    if domain != "" and address == "":
        sql = sql2
    if domain != "" and address != "":
        sql = sql4
    sql_dealer = mysql_dealer()
    results = sql_dealer.get_cursor_exe_result(sql)
    result_list = []
    for result in results:
        single = dict()
        (single['addr'], single['balance'], single['domain'], single['addrtype'], single['url'],
         single['createtime']) = (result)
        if single['balance'] == None:
            single['balance'] = 0
        result_list.append(single)
        sql = "select SOURCE from ADDRESS_TAG where address='{}'".format(single['addr'])
        try:
            single['tag'] = sql_dealer.get_cursor_exe_result(sql)[0][0]
        except:
            single['tag'] = ""
    return jsonify(result_list)


@btc_bp.route('/darknet/tor', methods=['POST', 'GET'])
def btc_block1():
    page_size = 10
    if request.method == 'POST':
        count = ""
        page = 1
        address = request.form['address']
        domain = request.form['domain'].replace(" ", "")
        coin = request.form['coin']
        order = "desc"
        re_order = "asc"
    elif request.method == 'GET':
        count = request.args.get("count", "")
        address = request.args.get("address", "")
        domain = request.args.get("domain", "")
        coin = request.args.get("coin", "bitcoin")
        try:
            page = int(request.args.get("page", 1))
        except:
            page = 1
        order = request.args.get("order", "desc")
        if order == "desc":
            re_order = "asc"
        else:
            re_order = "desc"
    sql1 = "select addr,balance,domain,addrtype,url,createtime from {3} order by balance {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, coin)
    count_sql1 = "select count(1) from {}".format(coin)
    sql2 = "select addr,balance,domain,addrtype,url,createtime from {4} where domain like '%{2}%' order by balance {3} limit {0},{1}".format(
        (page - 1) * page_size, page_size, domain, order, coin)
    count_sql2 = "select count(1) from {1} where domain like '%{0}%'".format(domain, coin)
    sql3 = "select addr,balance,domain,addrtype,url,createtime from {4} where addr='{2}' order by balance {3} limit {0},{1}".format(
        (page - 1) * page_size, page_size, address, order, coin)
    count_sql3 = "select count(1) from {1} where addr='{0}'".format(address, coin)
    sql4 = "select addr,balance,domain,addrtype,url,createtime from {5} where addr='{2}' and domain LIKE '%{3}%' order by balance {4} limit {0},{1}".format(
        (page - 1) * page_size, page_size, address, domain, order, coin)
    count_sql4 = "select count(1) from {2} where domain LIKE '%{0}%' and addr='{1}'".format(domain, address, coin)
    if domain == "" and address == "":
        sql = sql1
        count_sql = count_sql1
    if domain == "" and address != "":
        sql = sql3
        count_sql = count_sql3
    if domain != "" and address == "":
        sql = sql2
        count_sql = count_sql2
    if domain != "" and address != "":
        sql = sql4
        count_sql = count_sql4
    sql_dealer = mysql_dealer("darknet_btc_analyze")
    try:
        results = sql_dealer.get_cursor_exe_result(sql)
    except:
        results = []
    result_list = []
    if count == "":
        count = int(sql_dealer.get_cursor_exe_result(count_sql)[0][0])
    else:
        count = int(count)
    for result in results:
        single = dict()
        (single['addr'], single['balance'], single['domain'], single['addrtype'], single['url'],
         single['createtime']) = (result)
        if single['balance'] == None:
            single['balance'] = 0
        rule = r"http://(.*)/"
        log.info(single)
        print(single)
        try:
            website = re.findall(rule, single["domain"])[0]
            sql = "select tag from website_tag where website='{0}'".format(website)
            tag = sql_dealer.get_cursor_exe_result(sql)[0][0]
            single["tag"] = tag
            result_list.append(single)
        except:
            single["tag"] = ""
            result_list.append(single)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=page_size)
    return render_template('btc/tor_addr.html', pagination=pagination, result=result_list, address=address,
                           domain=domain, order=order, re_order=re_order, count=count, coin=coin)


@btc_bp.route('/darknet/i2p', methods=['POST', 'GET'])
def get_i2p():
    global count_sql, count
    page_size = 10
    if request.method == 'POST':
        count = ""
        page = 1
        address = request.form['address']
        domain = request.form['domain'].replace(" ", "")
        coin = request.form['coin']
        sdate = request.form['sdate']
        edate = request.form['edate']
        order = "desc"
        re_order = "asc"
    elif request.method == 'GET':
        count = request.args.get("count", "")
        address = request.args.get("address", "")
        domain = request.args.get("domain", "")
        coin = request.args.get("coin", "btc")
        sdate = request.args.get("sdate", "")
        edate = request.args.get("edate", "")
        try:
            page = int(request.args.get("page", 1))
        except:
            page = 1
        order = request.args.get("order", "desc")
        if order == "desc":
            re_order = "asc"
        else:
            re_order = "desc"
    sql1 = "select addr,domain,addrtype,url,createtime from i2p_addr where addrtype = '{3}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, coin)
    count_sql1 = "select count(1) from i2p_addr where addrtype = '{}'".format(coin)
    sql2 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{2}%' and  addrtype = '{4}' order by createtime {3} limit {0},{1}".format(
        (page - 1) * page_size, page_size, domain, order, coin)
    count_sql2 = "select count(1) from i2p_addr where domain like '%{0}%' and  addrtype = '{1}' ".format(domain, coin)
    sql3 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr='{2}' and  addrtype = '{4}' order by createtime {3} limit {0},{1}".format(
        (page - 1) * page_size, page_size, address, order, coin)
    count_sql3 = "select count(1) from i2p_addr where addr='{0}' and  addrtype = '{1}' ".format(address, coin)
    sql4 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr='{2}' and domain LIKE '%{3}%' and  addrtype = '{5}' order by createtime {4} limit {0},{1}".format(
        (page - 1) * page_size, page_size, address, domain, order, coin)
    count_sql4 = "select count(1) from i2p_addr where domain LIKE '%{0}%' and addr='{1}' and  addrtype = '{2}'".format(
        domain, address, coin)
    sql5 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr = '{3}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, address)
    count_sql5 = "select count(1) from i2p_addr where addr = '{}'".format(address)
    sql6 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{3}%' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, domain)
    count_sql6 = "select count(1) from i2p_addr where domain like '%{}%'".format(domain)
    sql7 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{3}%' and addr ='{4}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, domain, address)
    count_sql7 = "select count(1) from i2p_addr where domain like '%{0}%' and addr ='{1}'".format(domain, address)
    sql_sdate = "select addr,domain,addrtype,url,createtime from i2p_addr where createtime >= '{3}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, sdate)
    count_sql_sdate = "select count(1) from i2p_addr where createtime <= '{}'".format(sdate)
    sql_edate = "select addr,domain,addrtype,url,createtime from i2p_addr where createtime <= '{3}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, edate)
    count_sql_edate = "select count(1) from i2p_addr where createtime <= '{}'".format(edate)
    sql8 = "select addr,domain,addrtype,url,createtime from i2p_addr where addrtype = '{3}' and createtime >= '{4}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, coin, sdate)
    count_sql8 = "select count(1) from i2p_addr where addrtype = '{0}'and createtime >= '{1}' ".format(coin, sdate)
    sql9 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr = '{3}' and createtime >= '{4}'  order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, address, sdate)
    count_sql9 = "select count(1) from i2p_addr where addr = '{0}' and createtime >= '{1}' ".format(address, sdate)
    sql10 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr='{2}' and  addrtype = '{4}' and createtime >= '{5}' order by createtime {3} limit {0},{1}".format(
        (page - 1) * page_size, page_size, address, order, coin, sdate)
    count_sql10 = "select count(1) from i2p_addr where addr='{0}' and  addrtype = '{1}' and createtime >= '{2}' ".format(
        address, coin, sdate)
    sql11 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{3}%' and createtime >= '{4}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, domain, sdate)
    count_sql11 = "select count(1) from i2p_addr where domain like '%{0}%'and createtime >= '{1}' ".format(domain,
                                                                                                           sdate)
    sql12 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{2}%' and  addrtype = '{4}' createtime >= '{5}' order by createtime {3} limit {0},{1}".format(
        (page - 1) * page_size, page_size, domain, order, coin, sdate)
    count_sql12 = "select count(1) from i2p_addr where domain like '%{0}%' and  addrtype = '{1}' createtime >= '{2}' ".format(
        domain, coin, sdate)
    sql13 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{3}%' and addr ='{4}' and createtime >= '{5}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, domain, address, sdate)
    count_sql13 = "select count(1) from i2p_addr where domain like '%{0}%' and addr ='{1}' and createtime >= '{2}'".format(
        domain, address, sdate)
    sql14 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr='{2}' and domain LIKE '%{3}%' and  addrtype = '{5}' and createtime >= '{6}' order by createtime {4} limit {0},{1}".format(
        (page - 1) * page_size, page_size, address, domain, order, coin, sdate)
    count_sql14 = "select count(1) from i2p_addr where domain LIKE '%{0}%' and addr='{1}' and  addrtype = '{2}' and createtime >= '{3}' ".format(
        domain, address, coin, sdate)
    sql15 = "select addr,domain,addrtype,url,createtime from i2p_addr where addrtype = '{3}' and createtime <= '{4}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, coin, edate)
    count_sql15 = "select count(1) from i2p_addr where addrtype = '{0}'and createtime <= '{1}' ".format(coin, edate)
    sql16 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr = '{3}' and createtime <= '{4}'  order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, address, edate)
    count_sql16 = "select count(1) from i2p_addr where addr = '{0}' and createtime <= '{1}' ".format(address, edate)
    sql17 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr='{2}' and  addrtype = '{4}' and createtime <= '{5}' order by createtime {3} limit {0},{1}".format(
        (page - 1) * page_size, page_size, address, order, coin, edate)
    count_sql17 = "select count(1) from i2p_addr where addr='{0}' and  addrtype = '{1}' and createtime <= '{2}' ".format(
        address, coin, edate)
    sql18 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{3}%' and createtime <= '{4}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, domain, edate)
    count_sql18 = "select count(1) from i2p_addr where domain like '%{0}%'and createtime <= '{1}' ".format(domain,
                                                                                                           edate)
    sql19 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{2}%' and  addrtype = '{4}' and createtime <= '{5}' order by createtime {3} limit {0},{1}".format(
        (page - 1) * page_size, page_size, domain, order, coin, edate)
    count_sql19 = "select count(1) from i2p_addr where domain like '%{0}%' and  addrtype = '{1}' and createtime <= '{2}' ".format(
        domain, coin, edate)
    sql20 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{3}%' and addr ='{4}' and createtime <= '{5}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, domain, address, edate)
    count_sql20 = "select count(1) from i2p_addr where domain like '%{0}%' and addr ='{1}' and createtime <= '{2}'".format(
        domain, address, edate)
    sql21 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr='{2}' and domain LIKE '%{3}%' and  addrtype = '{5}' and createtime <= '{6}' order by createtime {4} limit {0},{1}".format(
        (page - 1) * page_size, page_size, address, domain, order, coin, edate)
    count_sql21 = "select count(1) from i2p_addr where domain LIKE '%{0}%' and addr='{1}' and  addrtype = '{2}' and createtime <= '{3}' ".format(
        domain, address, coin, edate)
    sql_sedate = "select addr,domain,addrtype,url,createtime from i2p_addr where createtime between '{3}' and '{4}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, sdate, edate)
    count_sql_sedate = "select count(1) from i2p_addr where  createtime between '{0}' and '{1}'".format(sdate, edate)
    sql22 = "select addr,domain,addrtype,url,createtime from i2p_addr where addrtype = '{3}' and createtime BETWEEN '{4}' and '{5}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, coin, sdate, edate)
    count_sql22 = "select count(1) from i2p_addr where addrtype = '{0}'and createtime BETWEEN '{1}' and '{2}' ".format(
        coin, sdate, edate)
    sql23 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr = '{3}' and createtime BETWEEN '{4}' and '{5}'  order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, address, sdate, edate)
    count_sql23 = "select count(1) from i2p_addr where addr = '{0}' and createtime BETWEEN '{1}' and '{2}' ".format(
        address, sdate, edate)
    sql24 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr='{2}' and  addrtype = '{4}' and createtime BETWEEN '{5}' and '{6}' order by createtime {3} limit {0},{1}".format(
        (page - 1) * page_size, page_size, address, order, coin, sdate, edate)
    count_sql24 = "select count(1) from i2p_addr where addr='{0}' and  addrtype = '{1}' and createtime BETWEEN '{2}' and '{3}' ".format(
        address, coin, sdate, edate)
    sql25 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{3}%' and createtime BETWEEN '{4}' and '{5}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, domain, sdate, edate)
    count_sql25 = "select count(1) from i2p_addr where domain like '%{0}%'and createtime BETWEEN '{1}' and '{2}' ".format(
        domain,
        sdate, edate)
    sql26 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{2}%' and  addrtype = '{4}' and createtime BETWEEN '{5}' and '{6}' order by createtime {3} limit {0},{1}".format(
        (page - 1) * page_size, page_size, domain, order, coin, sdate, edate)
    count_sql26 = "select count(1) from i2p_addr where domain like '%{0}%' and  addrtype = '{1}' and createtime BETWEEN '{2}' and '{3}' ".format(
        domain, coin, sdate, edate)
    sql27 = "select addr,domain,addrtype,url,createtime from i2p_addr where domain like '%{3}%' and addr ='{4}' and createtime BETWEEN '{5}' and '{6}' order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order, domain, address, sdate, edate)
    count_sql27 = "select count(1) from i2p_addr where domain like '%{0}%' and addr ='{1}' and createtime BETWEEN '{2}' and '{3}'".format(
        domain, address, sdate, edate)
    sql28 = "select addr,domain,addrtype,url,createtime from i2p_addr where addr='{2}' and domain LIKE '%{3}%' and  addrtype = '{5}' and createtime BETWEEN '{6}' and '{7}' order by createtime {4} limit {0},{1}".format(
        (page - 1) * page_size, page_size, address, domain, order, coin, sdate, edate)
    count_sql28 = "select count(1) from i2p_addr where domain LIKE '%{0}%' and addr='{1}' and  addrtype = '{2}' and createtime BETWEEN '{3}' and '{4}' ".format(
        domain, address, coin, sdate, edate)
    if edate == "" and sdate == "":
        if domain == "" and address == "":
            sql = sql1
            count_sql = count_sql1
        if domain == "" and address != "":
            if coin == "":
                sql = sql5
                count_sql = count_sql5
            else:
                sql = sql3
                count_sql = count_sql3
        if domain != "" and address == "":
            if coin == "":
                sql = sql6
                count_sql = count_sql6
            else:
                sql = sql2
                count_sql = count_sql2
        if domain != "" and address != "":
            if coin == "":
                sql = sql7
                count_sql = count_sql7
            else:
                sql = sql4
                count_sql = count_sql4
    if edate == "" and sdate != "":
        if domain == "" and address == "":
            if coin == "":
                sql = sql_sdate
                count_sql = count_sql_sdate
            else:
                sql = sql8
                count_sql = count_sql8
        if domain == "" and address != "":
            if coin == "":
                sql = sql9
                count_sql = count_sql9
            else:
                sql = sql10
                count_sql = count_sql10
        if domain != "" and address == "":
            if coin == "":
                sql = sql11
                count_sql = count_sql11
            else:
                sql = sql12
                count_sql = count_sql12
        if domain != "" and address != "":
            if coin == "":
                sql = sql13
                count_sql = count_sql13
            else:
                sql = sql14
                count_sql = count_sql14
    if edate != "" and sdate == "":
        if domain == "" and address == "":
            if coin == "":
                sql = sql_edate
                count_sql = count_sql_edate
            else:
                sql = sql15
                count_sql = count_sql15
        if domain == "" and address != "":
            if coin == "":
                sql = sql16
                count_sql = count_sql16
            else:
                sql = sql17
                count_sql = count_sql17
        if domain != "" and address == "":
            if coin == "":
                sql = sql18
                count_sql = count_sql18
            else:
                sql = sql19
                count_sql = count_sql19
        if domain != "" and address != "":
            if coin == "":
                sql = sql20
                count_sql = count_sql20
            else:
                sql = sql21
                count_sql = count_sql21
    if edate != "" and sdate != "":
        if domain == "" and address == "":
            if coin == "":
                sql = sql_sedate
                count_sql = count_sql_sedate
            else:
                sql = sql22
                count_sql = count_sql22
        if domain == "" and address != "":
            if coin == "":
                sql = sql23
                count_sql = count_sql23
            else:
                sql = sql24
                count_sql = count_sql24
        if domain != "" and address == "":
            if coin == "":
                sql = sql25
                count_sql = count_sql25
            else:
                sql = sql26
                count_sql = count_sql26
        if domain != "" and address != "":
            if coin == "":
                sql = sql27
                count_sql = count_sql27
            else:
                sql = sql28
                count_sql = count_sql28
    sql_dealer = mysql_dealer("darknet_btc_analyze")
    try:
        results = sql_dealer.get_cursor_exe_result(sql)
    except:
        results = []
    result_list = []
    if count == "":
        count = int(sql_dealer.get_cursor_exe_result(count_sql)[0][0])
    else:
        count = int(count)
    for result in results:
        single = dict()
        (single['addr'], single['domain'], single['addrtype'], single['url'], single['createtime']) = (result)
        single['balance'] = 0
        result_list.append(single)
        sql = "select SOURCE from ADDRESS_TAG where address='{}'".format(single['addr'])
        single['tag'] = ""
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=page_size)
    return render_template('btc/i2p_addr_search_result.html', pagination=pagination, result=result_list,
                           address=address,
                           domain=domain, order=order, re_order=re_order, count=count, coin=coin, edate=edate,
                           sdate=sdate)


@btc_bp.route('/darknet/i2p_all', methods=['POST', 'GET'])
def get_i2p_all():
    global count_sql, count
    page_size = 10
    if request.method == 'POST':
        count = ""
        page = 1
        address = request.form['address']
        domain = request.form['domain'].replace(" ", "")
        coin = request.form['coin']
        sdate = request.form['sdate']
        edate = request.form['edate']
        order = "desc"
        re_order = "asc"
    elif request.method == 'GET':
        count = request.args.get("count", "")
        address = request.args.get("address", "")
        domain = request.args.get("domain", "")
        coin = request.args.get("coin", "btc")
        sdate = request.args.get("sdate", "")
        edate = request.args.get("edate", "")
        try:
            page = int(request.args.get("page", 1))
        except:
            page = 1
        order = request.args.get("order", "desc")
        if order == "desc":
            re_order = "asc"
        else:
            re_order = "desc"
    sql = "select addr,domain,addrtype,url,createtime from i2p_addr order by createtime {2} limit {0},{1}".format(
        (page - 1) * page_size, page_size, order)
    count_sql = "select count(1) from i2p_addr"

    sql_dealer = mysql_dealer("darknet_btc_analyze")
    try:
        results = sql_dealer.get_cursor_exe_result(sql)
    except:
        results = []
    result_list = []
    if count == "":
        count = int(sql_dealer.get_cursor_exe_result(count_sql)[0][0])
    else:
        count = int(count)
    for result in results:
        single = dict()
        (single['addr'], single['domain'], single['addrtype'], single['url'], single['createtime']) = (result)
        single['balance'] = 0
        result_list.append(single)
        sql = "select SOURCE from ADDRESS_TAG where address='{}'".format(single['addr'])
        single['tag'] = ""
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=page_size)
    return render_template('btc/i2p_addr_all.html', pagination=pagination, result=result_list, address=address,
                           domain=domain, order=order, re_order=re_order, count=count, coin=coin, edate=edate,
                           sdate=sdate)


def getUSDCNY(time_str):
    sql = "select * from PriceRate where Pricetime = '" + str(time_str) + "'"

    sql_dealer = mysql_dealer("darknet_btc_analyze")
    try:
        results = sql_dealer.get_cursor_exe_result(sql)
        # log.error(sql)
    except:
        results = []
        # log.error('erroe', sql)
    return results


@btc_bp.route('/btc/historyRate/', methods=['POST', 'GET'])
def historyRate():
    try:
        page = int(request.args.get("page", 1))
    except:
        page = 1
    page_size = 10
    sql = "select * from PriceRate order by Pricetime {0} limit {1},{2}".format('desc', (page - 1) * page_size,
                                                                                page_size)
    sql_all = "select * from PriceRate order by Pricetime {} ".format('desc')
    count_sql = "select count(1) from PriceRate"
    sql_dealer = mysql_dealer("darknet_btc_analyze")
    try:
        results = sql_dealer.get_cursor_exe_result(sql)
        results_all = sql_dealer.get_cursor_exe_result(sql_all)
        count = int(sql_dealer.get_cursor_exe_result(count_sql)[0][0])
    except:
        results = []
    result_list = []
    result_list_all = []
    for result in results:
        single = dict()
        (single['USD'], single['CNY'], single['date']) = (result)
        single['date'] = str(datetime.strptime(str(single['date']), "%Y-%m-%d %H:%M:%S").date())
        result_list.append(single)
    for result in results_all:
        single = dict()
        (single['USD'], single['CNY'], single['date']) = (result)
        single['date'] = str(datetime.strptime(str(single['date']), "%Y-%m-%d %H:%M:%S").date())
        result_list_all.append(single)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=page_size)
    return render_template('btc/btcRatehistory.html', pagination=pagination, result=result_list,
                           results_all=result_list_all)


def news_return():
    page_size = 5
    sql = "select title,date ,source,detail from news order by date {2} limit {0},{1}".format(
        0, page_size, 'desc')
    count_sql = "select count(1) from news"

    sql_dealer = mysql_dealer("darknet_btc_analyze")
    try:
        results = sql_dealer.get_cursor_exe_result(sql)
    except:
        results = []
    result_list = []
    for result in results:
        single = dict()
        (single['title'], single['date'], single['source'], single['detail']) = (result)
        single['date'] = str(single['date'])
        result_list.append(single)
    return result_list


# tcy Add txtopic
@btc_bp.route('/btc/saveTxTopic/', methods=['POST'])
def btc_saveTopic():
    args = request.get_json()
    topic = args['topic']
    hash = args['hash']
    # log.error(topic+hash)
    log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    try:
        log.info("---------------------------------------------------")
        if 2 > 1:
            flag = updateTxTopic(topic, hash)
            # flag=1
            if flag == 1:
                result = {"code": '0000', "message": "添加成功"}  ##更新成功
            else:
                result = {"code": '1111', "message": "添加失败"}
            return result
    except Exception as e:
        log.error("输入的地址有误，请检查", e)
        return {"code": '1111', "message": "地址输入有误，请检查"}


# POOL
@btc_bp.route('/btc/pool')
def btc_pool():
    context = {
        "page_title": '矿池'
    }
    return render_template('btc/pool.html', **context)


#
# # CONTRACT
# @btc_bp.route('/btc/contract')
# def btc_contract():
#     return render_template('btc/contract.html')

@btc_bp.route('/btc/transaction/search_tx',methods=['GET', 'POST'])
def btc_transaction_search_tx():
    rule = request.values['sortname']
    starttime = request.values['starttime']
    endtime = request.values['endtime']
    minvalue = request.values['minvalue']
    maxvalue = request.values['maxvalue']
    valuetype = 'BTC'
    log.info("排序规则为"+str(rule))
    log.info("货币类型为："+str(valuetype))
    log.info("++++++++++++++++++++++++++++++++++++++++")
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context,result = transactionreturn.trans_ajax_tx(rule,starttime,endtime,minvalue,maxvalue,valuetype,perpage,start)
    log.info("查询结果为"+str(len(result)))
    total = context["trans_total"]
    log.info("区块信息总数为" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('btc/transaction.html',latestTransList=result, pagination=pagination, **context)
@btc_bp.route('/btc/transaction/search', methods=['GET', 'POST'])
def btc_transaction_search():
    # rule = request.values['sortname']
    inputaddr = request.values['inputaddr']
    outputaddr = request.values['outputaddr']
    starttime = request.values['starttime']
    endtime = request.values['endtime']
    minvalue = request.values['minvalue']
    maxvalue = request.values['maxvalue']
    height = request.values['height']
    fee = request.values['fee']
    input_num = request.values['input_num']
    output_num = request.values['output_num']
    topic = request.values['topic']
    specvalue = request.values['specvalue']
    page = int(request.args.get("page", 1))
    # valuetype = request.values['servicename']
    valuetype = "BTC"
    rule = "desc"
    log.info("排序规则为" + str(rule))
    log.info("货币类型为：" + str(valuetype))
    log.info("++++++++++++++++++++++++++++++++++++++++")
    perpage = perPage  # pagination默认
    log.error(page)
    start = (page - 1) * perpage
    context, result = transactionreturn.trans_ajax(rule, starttime, endtime, minvalue, maxvalue, inputaddr, outputaddr,
                                                   height, fee, input_num, output_num, topic, specvalue,
                                                   valuetype, perpage,
                                                   start)
    context_1000, result_1000 = transactionreturn.trans_ajax(rule, starttime, endtime, minvalue, maxvalue, inputaddr,
                                                             outputaddr,
                                                             height, fee, input_num, output_num, topic, specvalue,
                                                             valuetype, 1000,
                                                             start)
    if result:
        log.info("查询结果为" + str(len(result)))
        total = context["trans_total"]
        log.info("区块信息总数为" + str(total))
        pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')

        return render_template('btc/trans_senior_search_result.html', latestTransList=result, result_1000=result_1000,
                               pagination=pagination,
                               **context, stime=starttime, etime=endtime, maxvalue=maxvalue, minvalue=minvalue,
                               inputaddr=inputaddr, outputaddr=outputaddr, height=height, fee=fee, inputnum=input_num,
                               outputnum=output_num, topic=topic, specvalue=specvalue)
    else:
        return render_template('search_error_message.html')


@btc_bp.route('/btc/block/search', methods=['GET', 'POST'])
def btc_block_search():
    rule = request.values['sortname']
    starttime = request.values['starttime']
    endtime = request.values['endtime']
    log.info("排序规则为" + str(rule))
    log.info("++++++++++++++++++++++++++++++++++++++++")
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    blocks, context = blockreturn.block_search(perPage, start, rule, starttime, endtime)  # pagination默认perPage20
    total = context['block_total']
    log.info("区块信息总数为" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='blocks')
    return render_template('btc/btc_block.html', blocks=blocks, pagination=pagination, **context)


# QPR search功能的实现，查询对应的区块高度，交易hash的详细信息，或者地址信息。
@btc_bp.route('/btc/search', methods=['GET', 'POST'])
def btc_search():
    text = request.values['search_text']
    perpage = perPage
    rull = r"^(1|3)[a-zA-Z\d]{24,33}$"
    if len(text) > 2 and text[0] == '0' and text[1] == 'x':
        rule = "^0x(.*)"
        text = re.findall(rule, text)[0]
    if text.isdigit():
        log.info("输入信息为：" + str(text))
        hash = btcblock.block_reverse(int(text))
        if hash:
            page = request.args.get(get_page_parameter(), type=int, default=1)
            start = (page - 1) * perpage
            context, blocktrans = blockreturn.blockdetail_return(hash, start, perpage, True)
            total = context["total"]
            log.info("交易总量为" + str(total))
            pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
            return render_template('btc/block_detail.html', pagination=pagination, blocktrans=blocktrans, **context)
        else:
            return render_template('search_error_message.html')
    elif len(text) == 64:  ##交易hash
        result = datainterchange.get_block(text)
        tx_result = datainterchange.get_transaction(text)
        if result:
            page = request.args.get(get_page_parameter(), type=int, default=1)
            start = (page - 1) * perpage
            context, blocktrans = blockreturn.blockdetail_return(text, start, perpage, True)
            total = context["total"]
            log.info("交易总量为" + str(total))
            pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
            return render_template('btc/block_detail.html', pagination=pagination, blocktrans=blocktrans, **context)
        elif tx_result:
            tsc_info, context = transactionreturn.trans_detail_return(text)
            log.info("交易详细信息为：")
            log.info("返回页面tsc_detail")
            return render_template('btc/tsc_detail.html', tsc_info=tsc_info, **context)
        else:
            return render_template('search_error_message.html')
    elif re.findall(rull, text) and validation_address("btc", text):  # 最后一个为地址
        page_size = 10
        final_address = text
        page = int(request.args.get("page", "1"))
        tx_list, total, first_seen, recv, sent, recv_num, sent_num, balance, first_seen_bj = handleAddressTx(
            final_address, page)
        pagination = Pagination(bs_version=4, page=page, total=total, per_page=page_size)
        return render_template('btc/address_detail.html', txs=tx_list, pagination=pagination, address=final_address,
                               recv=recv, sent=sent, balance=balance, first_seen=first_seen, recv_num=recv_num,
                               sent_num=sent_num, first_seen_bj=first_seen_bj)
    else:
        page = request.args.get(get_page_parameter(), type=int, default=1)
        start = (page - 1) * perpage
        context, latestTranList = transactionreturn.trans_search_return(start, perpage, text)
        if context:
            total = context["trans_total"]
            log.info("交易信息总数为" + str(total))
            pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
            return render_template('btc/transaction.html', latestTransList=latestTranList, pagination=pagination,
                                   **context)
        else:

            return render_template('search_error_message.html')


@btc_bp.route('/btc/address/<string:address>')
def btc_address_detail(address):
    page_size = 10
    final_address = address
    page = int(request.args.get("page", "1"))
    tx_list, total, first_seen, recv, sent, recv_num, sent_num, balance, first_seen_bj = handleAddressTx(final_address,
                                                                                                         page)
    cluster_id=getAddressCluster(address)
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=page_size)
    return render_template('btc/address_detail.html', txs=tx_list, pagination=pagination, address=final_address,
                           recv=recv, sent=sent, balance=balance, first_seen=first_seen, recv_num=recv_num,
                           sent_num=sent_num, first_seen_bj=first_seen_bj,cluster_id=cluster_id)


# qpr交易标签
@btc_bp.route('/btc/transaction')
def btc_transaction():
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, latestTransList = transactionreturn.trans_return(perpage, start)
    total = context["trans_total"]
    log.info("交易信息总数为" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('btc/transaction.html', latestTransList=latestTransList, pagination=pagination, **context)


# GPY
@btc_bp.route('/btc/day_trans')
def day_trans():
    sql_dealer = mysql_dealer("darknet_btc_analyze")
    sql = "select end_date,trans_num,trans_sum from statistics ORDER by end_date"
    results = sql_dealer.get_cursor_exe_result(sql)
    json_dict = dict()
    json_dict['end_date'] = []
    json_dict['trans_num'] = []
    json_dict['trans_sum'] = []
    for result in results:
        json_dict['end_date'].append(result[0].split(" ")[0])
        json_dict['trans_num'].append(result[1])
        json_dict['trans_sum'].append(result[2])
    return jsonify(json_dict)


# GPY
@btc_bp.route('/btc/day_address')
def day_address():
    sql_dealer = mysql_dealer("darknet_btc_analyze")
    sql = "select * from (select end_date,active_address,new_address from statistics ORDER by end_date desc limit 300) as stat order by stat.end_date asc;"
    results = sql_dealer.get_cursor_exe_result(sql)
    json_dict = dict()
    json_dict['end_date'] = []
    json_dict['active_address'] = []
    json_dict['new_address'] = []
    for result in results:
        json_dict['end_date'].append(result[0].split(" ")[0])
        json_dict['active_address'].append(result[1])
        json_dict['new_address'].append(result[2])
    return jsonify(json_dict)


# syc---------------------------------------------------------------------
# SYC tag---------------------------------------------------------------------------------------------------------
# SYC tag---------------------------------------------------------------------------------------------------------
@btc_bp.route('/btc/my_tag', methods=['GET', 'POST'])
def syc_btc_tag():
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    count, list = get_my_tags(start, perpage)
    addr_list, single_list, repeat_list = cluster(list, 'addr')
    # result_info = get_tag_all_info()
    usetime = round(time.time() - t, 3)
    content = {
        "page_title": '地址标签',
        "count": count,
        "address": None,
        "servicename": None,
        "usetime": usetime
    }
    reback = {}
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/my_btc_tag.html', username=session.get("username"), repeat_addr=addr_list,
                           repeat_list=repeat_list, single_list=single_list, pagination=pagination, **content,
                           reback=reback)


# syc Add Tag
@btc_bp.route('/btc/saveMyTag/', methods=['POST', 'GET'])
def btc_savemytag():
    args = request.get_json()
    addr = args['addr']
    tag = args['tag']
    source = args['source']
    detail = args['detail']
    type = args['type']
    print(addr, tag, source,detail,type)
    log.error(addr)
    log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    try:
        log.info("---------------------------------------------------")
        if (my_validation_address(addr) ==1):
            flag = updateAddressMyTag(addr, tag, source,detail,type)
            if flag == 1:
                result = {"code": '0000', "message": "添加成功"}  ##更新成功
            else:
                result = {"code": '1111', "message": "添加失败"}
            return result
        else:
            return {"code": '1111', "message": "添加失败"}
    except Exception as e:
        log.error("输入的地址有误，请检查", e)
        return {"code": '1111', "message": "地址输入有误，请检查"}


# syc Tag search
# syc Tag search

# syc Tag search
@btc_bp.route('/btc/my_tag/search', methods=['GET', 'POST'])
def syc_btc_tag_search():
    address = request.values['address']
    tag = request.values['tags']
    source = request.values['sources']
    num = request.values['num']
    category = request.values['category']
    label_clash = request.values['label_clash']
    flag = request.values['flag']
    # result_info = get_tag_all_info()
    sort = ''
    reback = {
        "address": address,
        "tag": tag,
        "source": source,
        "num": num,
        "category": category,
        "sort": sort,
        "flag":flag,
        "label_clash":label_clash
    }
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    count, list,list_1000 = get_address_mytags(address, tag, source, num, category, start, perpage, label_clash, flag)
    addr_list, single_list, repeat_list = cluster(list, 'addr')
    content = {
        "page_title": '地址标签',
        "count": count,
        "address": address
    }
    usetime = round(time.time() - t, 3)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/my_btc_tag.html', username=session.get("username"), repeat_addr=addr_list,
                           source=source,
                           repeat_list=repeat_list, single_list=single_list, **content, pagination=pagination,
                           usetime=usetime, reback=reback,result_1000=list_1000)


##SYC Mixing
@btc_bp.route('/btc/mix', methods=['GET', 'POST'])
def syc_btc_mix():
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    count, list = get_my_mix(start, perpage)
    addr_list, single_list, repeat_list = my_cluster(list)
    usetime = round(time.time() - t, 3)
    content = {
        "page_title": '混币交易列表',
        "count": count,
        "address": None,
        "servicename": None,
        "usetime": usetime
    }
    reback = {}
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/my_btc_mix.html', username=session.get("username"), repeat_addr=addr_list,
                           repeat_list=repeat_list, single_list=single_list, pagination=pagination, **content,
                           reback=reback)


# SYC Big Transaction

@btc_bp.route('/btc/my_transaction')
def btc_my_transaction():
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, result_list = my_transaction.my_trans_return(perpage, start)
    print("result_list is ", result_list)
    hash_list, single_list, repeat_list = cluster(result_list, 'hash')
    total = context["trans_total"]
    log.info("交易信息总数为" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('btc/my_transaction.html', username=session.get("username"), hash_list=hash_list,
                           single_list=single_list, repeat_list=repeat_list, pagination=pagination, **context)


def my_cluster(list):
    address = ""
    addr_list = []
    single_list = []
    repeat_list = []

    for l in list:
        if address != l["txid"]:
            address = l["txid"]
            single_list.append(l)
        else:
            addr_list.append(l["txid"])
            repeat_list.append(l)
    return addr_list, single_list, repeat_list


# syc btc tag
@btc_bp.route('/btc/tag/<string:address>')
def btc_tag_detail(address):
    page_size = 10
    final_address = address
    res = get_tag_info(final_address)
    try:
        res2 = es.get(index=total_addr_index,id= final_address,doc_type='_doc')
        cluster_id = res2['_source']['cluster_id']
    except Exception as e:
        print(e)
        cluster_id = None
    try:
        res3 = es.get(index=my_cluster_info,id=cluster_id,doc_type='_doc')
        cluster_tags = res3['_source']['labels']
        cluster_tags_final = []
        for i in range(0,len(cluster_tags)):
            my_list=[]
            detail = cluster_tags[i]['detail']
            if (address in detail):
                # cluster_tags=[]
                # break
                continue
            my_list.append(detail)
            cluster_tags[i]['detail'] =my_list
            cluster_tags_final.append(cluster_tags[i])
    except Exception as e:
        # cluster_tags = []
        cluster_tags_final = []
    # print('!!!!!!!!!!!!! ',res)
    if res:
        res = res['hits']['hits']
        final_labels = []
        for item in res:
            labels = item['_source']['labels']
            try:
                label_clash = item['_source']['label_clash']
            except Exception as e:
                label_clash = 'unknown'
            for label in labels:
                detail = label['detail']
                if(detail is not None):
                    label['detail'] = label['detail'].split(";")
                else:
                    label['detail']= '无详细信息'
                if (label['source'] == 'whale alert'):
                    label['detail'] = get_big_trans(address)
                    # print(label['detail'])
                # if (label['category'] == 'user'):
                if(label['source'] == 'BitcoinTalk Forum'):
                    user_id = label['detail'][-1]
                    user_id = user_id[8:]
                    link = 'link: https://bitcointalk.org/index.php?action=profile;u=' + user_id
                    label['detail'].append(link)
                final_labels.append(label)
            seed_count = len(final_labels)
            final_labels = final_labels+cluster_tags_final
            count = len(final_labels)
            # final_labels.append(labels)
            # print(labels)
    else:
        final_labels =  cluster_tags_final
        seed_count = 0
        count = len(final_labels)
        label_clash = 'unknow'

    return render_template('btc/tag_detail.html', username=session.get("username"), labels=final_labels, count=count,
                           address=address, label_clash=label_clash,other_info =cluster_id,seed_count = seed_count)


# SYC Mixing Count
@btc_bp.route('/btc/mix_trans')
def day_mix_trans():
    sql_dealer = mysql_dealer("bitcoin_mixing")
    sql = "select end_date,trans_num,trans_sum from statistics_coinjoin ORDER by end_date"
    results = sql_dealer.get_cursor_exe_result(sql)
    json_dict = dict()
    json_dict['end_date'] = []
    json_dict['trans_num'] = []
    json_dict['trans_sum'] = []
    for result in results:
        if result[2] == None:
            json_dict['trans_sum'].append(0)
        else:
            json_dict['trans_sum'].append(result[2])

        json_dict['end_date'].append(result[0].split(" ")[0])
        json_dict['trans_num'].append(result[1])
    # print(json_dict['trans_num'])
    return jsonify(json_dict)


@btc_bp.route('/btc/stealth_address_trans')
def day_steal_trans():
    sql_dealer = mysql_dealer("bitcoin_mixing")
    sql = "select end_date,trans_num from statistics_stealthaddress ORDER by end_date"
    results = sql_dealer.get_cursor_exe_result(sql)
    json_dict = dict()
    json_dict['end_date'] = []
    json_dict['trans_num'] = []
    for result in results:
        json_dict['end_date'].append(result[0].split(" ")[0])
        json_dict['trans_num'].append(result[1])
    return jsonify(json_dict)


@btc_bp.route('/btc/mix_analysis')
def mix_analysis():
    content = {
        "page_title": '混币交易列表',
    }
    pagination = None
    sql_dealer = mysql_dealer("bitcoin_mixing")
    sql = "select sum(trans_num),max(trans_num),min(trans_num),sum(trans_per) from statistics_coinjoin "
    results = sql_dealer.get_cursor_exe_result(sql)
    result_list = dict()
    for result in results:
        result_list['coinjoin'] = int(result[0])
        result_list['coinjoin_per_day_max'] = int(result[1])
        result_list['coinjoin_per_day_min'] = int(result[2])
        result_list['coinjoin_per_day'] = round(int(result[0]) / 2710, 2)
        result_list['coinjoin_per_day_range'] = round(result[3] / 2620, 6)
    sql2 = 'select sum(trans_num),max(trans_num),sum(trans_per) from statistics_stealthaddress'
    results2 = sql_dealer.get_cursor_exe_result(sql2)
    for result in results2:
        result_list['stealth_address'] = int(result[0])
        result_list['stealth_address_per_day'] = round(int(result[0]) / 1962, 2)
        result_list['stealth_addr_per_day_max'] = int(result[1])
        result_list['stealth_addr_per_day'] = round(result[2] / 1858, 6)
    sql3 = 'select * from coinjoin where input_value=(select max(input_value) from coinjoin)'
    results3 = sql_dealer.get_cursor_exe_result(sql3)
    for result in results3:
        result_list['coinjoin_max_txid'] = result[1]
        result_list['coinjoin_value_max'] = result[4]
        # result_list['coinjoin_value_min'] = '{:.10f}'.format(result[1])
    sql4 = 'select * from coinjoin where input_value=(select min(input_value) from coinjoin)'
    results4 = sql_dealer.get_cursor_exe_result(sql4)
    for result in results4:
        result_list['coinjoin_min_txid'] = result[1]
        result_list['coinjoin_value_min'] = '{:.10f}'.format(result[4])
    return render_template('btc/btc_mix_analysis.html', username=session.get("username"), pagination=pagination,
                           **content, result_list=result_list)


# syc Mix search
@btc_bp.route('/btc/mix/search', methods=['GET', 'POST'])
def syc_btc_mix_search():
    txid = request.values['txid']
    type = request.values['type']

    reback = {
        "txid": txid,
        "type": type
    }
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    count, list = get_my_mix_search(txid, type, start, perpage)
    addr_list, single_list, repeat_list = my_cluster(list)
    content = {
        "page_title": '地址标签',
        "count": count,
        "txid": txid
    }
    usetime = round(time.time() - t, 3)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/my_btc_mix.html', username=session.get("username"), repeat_addr=addr_list,
                           repeat_list=repeat_list, single_list=single_list, **content, pagination=pagination,
                           usetime=usetime, reback=reback)


@btc_bp.route('/btc/tag_home', methods=['GET', 'POST'])
def syc_btc_tag_home():
    sources = ['WalletExplorer', 'Bitcoinwhoswho', 'BitcoinTalk Forum', 'whale alert','Twitter','Github','Ransomwhere','BitcoinAbuse','Charitycoin','user-defined']
    sources_count = get_tag_source(sources)
    tag_types_count = get_tag_type()    #  找出种子标签 聚类标签 未标记标签数量 的方法
    topseedtags = top_seed_tags()
    topclutags = top_cluster_tags()
    toptagsall=top_tags_all() #combine 2 banks
    preseedtags = pre_seed_tags()
    preclutags = pre_cluster_tags()
    topcategory = top_category()
    todaytag = today_tag()
    result_info = get_tag_all_info()
    identi_info,identi_total = get_identi_info(['Exchanges', 'Services', 'Gambling', 'Historic','Pools','user','other','scam','Ransomware','victim'])
    datas1 = []
    for s in sources_count:
        temp = {"value": s['count'], "name": s['source']}
        datas1.append(temp)
    pie1_datas = {'sources': sources, 'datas': datas1}

    #all tags --> in order to find the SOURCE NAME of top 10
    labels3 = []
    counts3 = []
    for t in range(len(toptagsall) - 1, -1, -1):
        labels3.append(toptagsall[t]['key'])
        counts3.append(toptagsall[t]['doc_count'])
    bar_datas3 = {'labels3': labels3,'counts3': counts3}

    #总的里面 聚类的tops
    labels4=[]
    counts4=[]
    count_tempt1 = 0

    for m in range(len(toptagsall) - 1,-1,-1):

        tagName = toptagsall[m]['key']
        labels4.append(tagName)

        same1 = False
        for n in range(len(preclutags) - 1, -1, -1):
            if tagName == preclutags[n]['key']:
                same1 = True
                count_tempt1 = preclutags[n]['doc_count']

        if same1:
            counts4.append(count_tempt1)
        else:
            counts4.append(0)

    bar_datas4 = {'labels4': labels4, 'counts4': counts4}


    #总的里面 种子的 tops
    labels5 = []
    counts5 = []
    count_tempt2 = 0
    for p in range(len(toptagsall) - 1, -1, -1):

        tagName = toptagsall[p]['key']
        labels5.append(tagName)

        same2 = False
        for q in range(len(preseedtags) - 1, -1, -1):
            if tagName == preseedtags[q]['key']:
                same2 = True
                count_tempt2 = preseedtags[q]['doc_count']

        if same2:
            counts5.append(count_tempt2)
        else:
            counts5.append(0)

    bar_datas5 = {'labels5': labels5, 'counts5': counts5}


    # 标签类型分布
    labels = []
    counts = []
    for l in range(len(topcategory) - 1, -1, -1):
    # for l in top_category:
        labels.append(topcategory[l]['key'])
        counts.append(topcategory[l]['doc_count'])
    bar_datas = {'labels': labels, 'counts': counts}

    # cluster
    labels2 = []
    counts2 = []
    for a in range(len(topclutags) - 1, -1, -1):
        labels2.append(topclutags[a]['key'])
        counts2.append(topclutags[a]['doc_count'])
    bar_datas2 = {'labels2': labels2, 'counts2': counts2}

    return render_template('btc/tag_home.html', username=session.get("username"), pie1_datas=pie1_datas,
                           tag_types_count=tag_types_count,
                           bar_datas=bar_datas,
                           bar_datas2=bar_datas2,
                           bar_datas3=bar_datas3,
                           bar_datas4=bar_datas4,
                           bar_datas5=bar_datas5,
                           sources_count=sources_count, top_seed_tags=topseedtags, top_category=topcategory, today_tag=todaytag,
                           result_info=result_info,
                           identi_info= identi_info,identi_total=identi_total)



@btc_bp.route('/btc/tag_cluster', methods=['GET', 'POST'])
def syc_tag_cluster():
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    count, list = get_tag_cluster(start, perpage)
    addr_list, single_list, repeat_list = cluster(list, 'addr')
    result_info = get_tag_all_info()
    usetime = round(time.time() - t, 3)
    content = {
        "page_title": '地址标签',
        "count": count,
        "address": None,
        "servicename": None,
        "usetime": usetime
    }
    reback = {}
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/my_btc_tag.html', username=session.get("username"), repeat_addr=addr_list,
                           repeat_list=repeat_list, single_list=single_list, pagination=pagination, **content,
                           reback=reback,
                           result_info=result_info)


@btc_bp.route('/btc/darknet_clash', methods=['GET', 'POST'])
def syc_darknet_clash():
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    count, list = get_darknet_clash(start, perpage)
    addr_list, single_list, repeat_list = cluster(list, 'addr')
    result_info = get_tag_all_info()
    usetime = round(time.time() - t, 3)
    content = {
        "page_title": '地址标签',
        "count": count,
        "address": None,
        "servicename": None,
        "usetime": usetime
    }
    reback = {}
    # 查暗网标签————————————————————————

    # ————————————————————————————————————————————————————————
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/darknet_btc_tag.html', username=session.get("username"), repeat_addr=addr_list,
                           repeat_list=repeat_list, single_list=single_list, pagination=pagination, **content,
                           reback=reback,
                           result_info=result_info)


# Syc Darknet Search
@btc_bp.route('/btc/darknet_clash/search', methods=['GET', 'POST'])
def syc_darknet_search():
    address = request.values['address']
    tag = request.values['tags']
    domain = request.values['domain']
    url = request.values['url']
    # dark_tag = request.values['dark_tag']
    result_info = get_tag_all_info()
    print("-----------------------", address)
    reback = {
        "address": address,
        "tag": tag,
        "domain": domain,
        "url": url
    }
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t = time.time()
    count, list = get_darknet_tags(address, tag, domain, url, start, perpage)
    addr_list, single_list, repeat_list = cluster(list, 'addr')
    content = {
        "page_title": '地址标签',
        "count": count,
        "address": address
    }
    usetime = round(time.time() - t, 3)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    return render_template('btc/darknet_btc_tag.html', username=session.get("username"), repeat_addr=addr_list,
                           repeat_list=repeat_list, single_list=single_list, **content, pagination=pagination,
                           usetime=usetime, reback=reback, result_info=result_info)

@btc_bp.route('/btc/kg',methods=['GET'])
def syc_kg():
    reback = {}
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage

    # pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='bitcointags')

    return render_template('btc/btc_kg.html', username=session.get("username"),
                           reback=reback)

#实体信息
@btc_bp.route('/btc/identi_info',methods=['GET','POST'])
def syc_identi_info():
    identi = request.args.get('identi')
    if(identi ==''):
        identi = None
    reback = {}
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    result = get_category_identi(identi)
    count =len(result)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    reback['category']=identi
    return render_template('btc/identi_info.html', username=session.get("username"),
                           reback=reback,result = result,count = count)


@btc_bp.route('/btc/kg_search',methods=['GET','POST'])
def syc_kg_search():
    reback = {}
    item = request.values['address']
    reback['address'] = item
    print("item is ", item)
    atti_list,des_list = getKG(item)
    print(des_list)
    if(atti_list ==[]):
        reback['info'] = 1
        return render_template('btc/btc_kg.html', username=session.get("username"),
                               reback=reback)
    else:
        return render_template('btc/btc_kg_search.html', username=session.get("username"),
                               reback=reback,des_list=des_list,atti_list=atti_list)

@btc_bp.route('/btc/cluster', methods=['GET'])
def syc_add_cluster():
    type = request.args.get('type')
    print('type is ',type)
    if(type ==''):
        type=None
    reback = {
        'type':type
    }
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage

    total, list = get_all_cluster(start, perpage,type)
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='bitcointags')

    return render_template('btc/btc_cluster.html', username=session.get("username"),
                           reback=reback,info_list=list,total=total,pagination=pagination)



@btc_bp.route('/btc/cluster_info',methods = ['GET'])
def syc_cluster_info():
    info_list = get_cluster_info()
    top_clu_have_label = top_label_clusters()
    # top_clu = top_clusters()
    #有标签的数据Top10
    labels = []
    counts = []
    for l in range(len(top_clu_have_label) - 1, -1, -1):
        key = top_clu_have_label[l]['_source']['labels'][0]['name']
        labels.append(key)
        counts.append(top_clu_have_label[l]['sort'][0])
    bar_datas2 = {'labels':labels,'counts':counts}
    # print(bar_datas2,11111111111111)
    res = es.get(index='last_cluster_block', id=1, doc_type='_doc')
    blockheight = res['_source']['block']

    last_block_time = getlastblocktime(blockheight)
    labels = []
    counts = []
    bar_datas = {'labels': labels, 'counts': counts}
    #无标签的数据Top10
    # for l in range(len(top_clu) - 1, -1, -1):
    #     key_ori = top_clu[l]['key']
    #     try:
    #         res = es.get(index=cluster_info_index,id=key_ori)
    #         key_name = res['_source']['label']
    #         key = key_name
    #     except Exception as e:
    #         key = '集群id:'+str(key_ori)
    #     labels.append(key)
    #     counts.append(top_clu[l]['doc_count'])
    return render_template('btc/btc_cluster_info.html', username=session.get("username"),
                           info_list= info_list,bar_datas2=bar_datas2,bar_datas=bar_datas,last_block_time=last_block_time,last_block_height=blockheight)
@btc_bp.route('/btc/query_pro', methods=['GET', 'POST'])
def query_pro():
    reback = {}
    perpage = 50  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    count, list = get_trans_query_history_pro(start, perpage)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='history')
    # perpage = perPage_10  # pagination默认
    # page = request.args.get(get_page_parameter(), type=int, default=1)
    # start = (page - 1) * perpage
    # t = time.time()
    # count, list = get_addr_cluster(start, perpage)
    # print(list)
    #
    # pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
    # a ,b,c,d =get_cluster_api('16SyMdqgEAmie7Fmqs6vhn562Lg8ZGc9c7',1,1)
    # print(a,b,c,d)
    return render_template('btc/btc_query_pro.html', username=session.get("username"),pagination=pagination,list=list,
                           reback=reback)


@btc_bp.route('/btc/cluster/search', methods=['POST', 'GET'])
def syc_cluster_search():
    address = request.values['address']
    print("address is ", address)
    pattern =r'\b(bc(0([ac-hj-np-z02-9]{39}|[ac-hj-np-z02-9]{59})|1[ac-hj-np-z02-9]{8,87})|[13][a-km-zA-HJ-NP-Z1-9]{25,35})\b'
    regex = re.compile(pattern)
    res = regex.findall(address)
    print(res)
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)

    if res:
        print('输入的是地址')
        reback = {}
        reback['address'] = address
        page = request.args.get(get_page_parameter(), type=int, default=1)
        start = (page - 1) * perpage
        t = time.time()
        count, list, cluster_tags, cluster_balance,tag_count,history = get_cluster_api(address, start, perpage)
        pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
        flag=1
    else:
        print('输入的是集群标签')
        reback = {}
        reback['address'] = address
        cluster_name = address
        start = (page - 1) * perpage
        t = time.time()
        count, list = get_cluster_name_api(cluster_name,start,perpage)
        pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='bitcointags')
        flag=0
    if (count == 0):
        reback['info'] = 'no'
        return render_template('btc/no_cluster.html', username=session.get("username"), reback=reback)
    if(flag ==1):
        return render_template('btc/add_cluster.html', username=session.get("username"), result_list=list, count=count,
                               pagination=pagination, reback=reback,
                               cluster_balance=cluster_balance,labels=cluster_tags,tag_count=tag_count,clu_history=history)
    if(flag==0):
        return  render_template('btc/btc_cluster.html', username=session.get("username"),
                           reback=reback,info_list=list,total=count,pagination=pagination)


@btc_bp.route('/btc/query_pro/search', methods=['POST', 'GET'])
def query_pro_search():
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    text = request.values['kw']
    log.error(text)
    body = buildQueryBody(text, start, perpage)
    latestTransList = btctransaction.transaction_ajax(body)
    context = {
        "labels": ['1', '2', '3', '4', '5', '6', '7'],
        "dataset3": [20, 40, 30, 85, 10, -20, 60],
        "trans_total": latestTransList['total'],
        "trans_fields": current_app.config['BTC_FIELDS'],
        "pages": math.ceil(latestTransList['total'] / perPage),
        "tr_option_list": current_app.config['TIME_RANGE_OPTIONS'],
        "columns": current_app.config['TRANS_TB_KEYS'],
        "page_title": '交易',
        "took": latestTransList['took']
    }
    total = context["trans_total"]
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('btc/trans_pro_search_result.html', username=session.get("username"),
                           latestTransList=latestTransList['result'], text=text,
                           pagination=pagination, **context)


# SYC Add cluster Tag
@btc_bp.route('/btc/saveClusTag/', methods=['POST', 'GET'])
def btc_saveClustag():
    args = request.get_json()
    cluster_id = args['addr']
    tag = args['tag']
    type = args['type']
    detail = args['detail']
    source =  args['source']
    print(cluster_id, tag,source)
    log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    try:
        log.info("---------------------------------------------------")
        flag = updateClusterTag(cluster_id, tag,type,detail,source)
        if flag == 1:
            result = {"code": '0000', "message": "添加成功"}  ##更新成功
        else:
            result = {"code": '1111', "message": "添加失败"}
        return result

    except Exception as e:
        log.error("输入的地址有误，请检查", e)
        return {"code": '1111', "message": "地址输入有误，请检查"}
