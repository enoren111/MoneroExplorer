# qpr BLOCK页面
import math

import requests
from flask import Blueprint, current_app, render_template, request, jsonify, session
from flask_paginate import Pagination, get_page_parameter
from Serives import blockreturn, transactionreturn, btcblock, xmrblock, zcash_blockreturn, xmrreturn, \
    btctransaction, \
    my_transaction, xmr_transactionreturn

from Serives.btcaddrtag import *
import re

from dao import datainterchange
from utils import validation_address

xmr_bp = Blueprint('xmr', __name__)
from config import config
from log import log
from bee_var import perPage, perPage_10
from mysql_dealer import mysql_dealer, get_xmr_tag_info, get_xmr_spent_info, get_xmr_nodes_info, \
    get_xmr_nodes_detail, get_xmr_supernodes_detail, get_xmr_search_node,get_addr_num
import time
from datetime import datetime
from app import es

log = log.init_logger(config.log_filepath)

es.tryagain_instance()
es = es.instance


@xmr_bp.route('/xmr')  # 需要继续完善
def xmr_home():
    latestTransList, context = xmrreturn.xmr_home_show()
    return render_template('xmr/xmr_home.html', latestTransList=latestTransList, **context)


# # # # # # Ljhxt # # # # # # 

##导出数据
import time
from io import BytesIO
from flask import send_file
# from openpyxl import Workbook
from loguru import logger

import xlsxwriter as xw


def export_excel(data):
    """excel 报表导出"""
    output = BytesIO()
    workbook=xw.Workbook(output)
    worksheet1=workbook.add_worksheet("sheet1")
    worksheet1.activate()
    title=['Hash',"Block","Time","Transaction quantity(XMR)","Total transaction amount of tx","Transaction format",'Type']
    worksheet1.write_row("A1",title)
    i=2
    for j in range(len(data)):
        insertData=data[j]
        row="A"+str(i)
        worksheet1.write_row(row,insertData)
        i+=1
    workbook.close()
    # 使用字节流存储
    # output = BytesIO()
    
    # 保存文件
    # wb.save(output)

    # 文件seek位置，从头(0)开始
    output.seek(0)
    filename = "%s.xls" % str(int(time.time()))

    # 打印文件大小
    logger.info("{} -> {} b".format(filename, len(output.getvalue())))

    # as_attachment：是否在headers中添加Content-Disposition
    # attachment_filename：下载时使用的文件名
    # conditional: 是否支持断点续传
    fv = send_file(output, as_attachment=True, attachment_filename=filename, conditional=True)
    fv.headers['Content-Disposition'] += "; filename*=utf-8''{}".format(filename)
    fv.headers["Cache-Control"] = "no_store"
    fv.headers["max-age"] = 1

    logger.info("Export EXCEL---------%s" % filename)

    return fv




@xmr_bp.route('/xmr/num_money')  # 交易数量和金额
def num_money():
    # 分页
    p = int(request.args.get("page",1))#页码
    
    t=request.args.get("t",'all')#all 总览，day 一天，week 一周，month 月，year 年
    print(p,t)
    # 下载
    d=request.args.get('d',None)#下载标志 为true下载
    #交易金额获取
    perpage = 10#默认分页大小
    start = (p - 1) * perpage
    dateMap = {

        "day":0 ,
        "week": 1,
        "month": 2,
        "year": 3,
        "all": 4
    }
    if d=="true":
        blocks, _ = xmrreturn.block_return_new(perPage, start,dateMap[t],d=True)

        return export_excel(blocks)

    blocks, context = xmrreturn.block_return_new(perPage, start,dateMap[t])  # pagination默认perPage 10
    # print("context:###############", blocks)
    total =context['trans_total']
    all_money=context['total_txnFee']
    log.info("The total number of block information is" + str(total))
    pagination = Pagination(bs_version=4, page=p, total=total, per_page=perPage, record_name='blocks')
    # print(context)
    return render_template('xmr/num_money.html',all_money=all_money,p=p,t=t,blocks=blocks, pagination=pagination, **context )

from Serives.xmr_transactionreturn import xmr_trans_class


@xmr_bp.route('/xmr/class_stat')  # 分类统计
def class_stat():

    t=request.args.get("t",'all')#all 总览，day 一天，week 一周，month 月，year 年 时间
    title="All" if t=="all" else "Last day" if t=="day" else "Last week" if t=="week" else 'Last month' if t=="month" else "Last year"
    dateMap = {
        "day":0 ,
        "week": 1,
        "month": 2,
        "year": 3,
        "all": 4
    }
    block_trade=150000000#大宗交易限制
    p = int(request.args.get("page",1))#页码
    perpage = 10#默认分页大小
    start = (p - 1) * perpage
    block_trade_total,no_block_trade_total,blocks,total=xmr_trans_class(perPage, start,time_rang_id=dateMap[t],block_trade=block_trade)
    pagination = Pagination(bs_version=4, page=p, total=total, per_page=perPage, record_name='blocks')
    v=request.args.get("v",'')
    templts_name='xmr/class_stat.html' if not v else 'xmr/class_stat_vis.html'
    
    return render_template(templts_name,p=p,t=t,title=title,block_trade_total=block_trade_total,no_block_trade_total=no_block_trade_total,blocks=blocks,pagination=pagination )

@xmr_bp.route('/xmr/use_stat')  # 地址使用统计
def use_stat():
    t=request.args.get("t",'all')#all 总览，day 一天，week 一周，month 月，year 年 时间
    title="All" if t=="all" else "Last day" if t=="day" else "Last week" if t=="week" else 'Last month' if t=="month" else "Last year"
    dateMap = {
        "day":0 ,
        "week": 1,
        "month": 2,
        "year": 3,
        "all": 4
    }
    v=request.args.get("v",'')
    p = int(request.args.get("page",1))#页码
    perpage = 10#默认分页大小
    start = (p - 1) * perpage
    dates,total=get_addr_num(str(dateMap[t]),v,perpage,start)

    

    if not v:
        pagination = Pagination(bs_version=4, page=p, total=total, per_page=perPage, record_name='blocks')
        return render_template('xmr/use_stat.html',title=title,p=p,t=t,pagination=pagination,blocks=dates )
    else:
        return render_template('xmr/use_stat_vis.html',title=title,major=dates[0],sub=dates[1],p=p,t=t)

@xmr_bp.route('/xmr/statistics') 
def statistics():
    datas,datas2=xmrreturn.get_statistics()
    data=[{'type':'Last day','quan':datas[0],'amount':datas2[0]},{'type':'Last week','quan':datas[1],'amount':datas2[1]},{'type':'Last month','quan':datas[2],'amount':datas2[2]},{'type':'Last year','quan':datas[3],'amount':datas2[3]},{'type':'All','quan':datas[4],'amount':datas2[4]}]

    return render_template('xmr/statistics.html',data=data)


    

# # # # # # Ljhxt # # # # # # 

@xmr_bp.route('/xmr/block')
def xmr_block():
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    blocks, context = xmrreturn.block_return(perPage, start)  # pagination默认perPage20
    # print("context:###############", blocks)
    total = context['block_total']
    log.info("The total number of block information is" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='blocks')
    print(context)
    return render_template('xmr/xmr_block.html', blocks=blocks, pagination=pagination, **context)


@xmr_bp.route('/xmr/rings')
def xmr_rings():
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    rings = get_xmr_tag_info(perpage, start)
    # print("=======================================我是分割线===============================================")
    # print("content:--------------------------------------------------------------------")
    print(rings)
    blocks, context = xmrreturn.block_return(perPage, start)  # pagination默认perPage20
    total = context['block_total']
    log.info("The total number of block information is" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='rings')
    return render_template('xmr/xmr_rings.html', rings=rings, pagination=pagination, **context)


@xmr_bp.route('/xmr/spents')
def xmr_spentstatus():
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    spents, context = get_xmr_spent_info(perpage, start)
    print("=======================================Dividing Line===============================================")
    print("content:--------------------------------------------------------------------")
    print(spents)
    total = 207488
    log.info("The total cost ring information is" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='spents')
    return render_template('xmr/xmr_spent.html', spents=spents, pagination=pagination, **context)


@xmr_bp.route('/xmr/nodes')
def xmr_nodes():
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    nodes, context = get_xmr_nodes_info('data_monero', perpage, start)
    total = 3322
    log.info("The number of the queried nodes is" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='nodes')
    return render_template('xmr/xmr_nodes.html', nodes=nodes, pagination=pagination, **context)


@xmr_bp.route('/xmr/supernodes')
def xmr_supernodes():
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    nodes, context = get_xmr_nodes_info("supernode_monero_mainnet", perpage, start)
    total = 64536
    log.info("The number of the queried nodes is" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='supernodes')
    return render_template('xmr/xmr_supernodes.html', nodes=nodes, pagination=pagination, **context)


@xmr_bp.route('/xmr/node_detail/<string:address>')
def xmr_node_detail(address):  # 暂定是根据地址进行索引
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, nodeInfo , supernodeInf = get_xmr_supernodes_detail("109.124.212.31", "18080", start, perpage)

    context, nodeInfo = get_xmr_nodes_detail(address, start, perpage)
    pagination = Pagination(bs_version=4, page=page, total=3322, per_page=perpage, record_name='node')
    return render_template('xmr/node_detail.html', pagination=pagination, nodeInfo=nodeInfo,
                           **context)  # **context


@xmr_bp.route('/xmr/supernode_detail/<string:address>/<string:port>')
def xmr_supernode_detail(address, port):  # 暂定是根据地址进行索引
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, nodeInfo , supernodeInf = get_xmr_supernodes_detail(address, port, start, perpage)

    pagination = Pagination(bs_version=4, page=page, total=3322, per_page=perpage, record_name='node')
    return render_template('xmr/supernode_detail.html', pagination=pagination, nodeInfo=nodeInfo,supernodeInf = supernodeInf,
                           **context)  # **context
@xmr_bp.route('/xmr/node/search', methods=['GET', 'POST'])  # 需要继续完善
def xmr_node_search():
    rule = request.values['sortname']
    starttime = request.values['starttime'][:10]
    endtime = request.values['endtime'][:10]
    print("rule: ", rule, "\nstarttime: ", starttime, "\nendtime: ",endtime)
    log.info("The sorting rule is" + str(rule))
    log.info("++++++++++++++++++++++++++++++++++++++++")
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    nodes, context = get_xmr_search_node("data_monero", perpage, start, rule, starttime, endtime)

    pagination = Pagination(bs_version=4, page=page, total=64536, per_page=perPage, record_name='supernodes')#这里的total暂时先写的是总节点信息数量
    return render_template('xmr/xmr_supernodes.html', nodes=nodes, pagination=pagination, **context)



@xmr_bp.route('/xmr/block_detail/<string:hash>')
def xmr_block_detail(hash):
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage

    context, blocktrans = xmrreturn.blockdetail_return(hash, start, perpage, True)
    # print(blocktrans[0]['_source'])
    total = context["total"]
    log.info("Total transaction volume is" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('xmr/block_detail.html', pagination=pagination, blocktrans=blocktrans,
                           **context)  # **context


@xmr_bp.route('/xmr/block/search', methods=['GET', 'POST'])  # 需要继续完善
def xmr_block_search():
    rule = request.values['sortname']
    starttime = request.values['starttime']
    endtime = request.values['endtime']
    log.info("The sorting rule is" + str(rule))
    log.info("++++++++++++++++++++++++++++++++++++++++")
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    blocks, context = xmrreturn.block_search(perPage, start, rule, starttime, endtime)  # pagination默认perPage20
    total = context['block_total']
    log.info("The total number of block information is" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='blocks')
    return render_template('xmr/xmr_block.html', blocks=blocks, pagination=pagination, **context)


# qpr交易标签
@xmr_bp.route('/xmr/transaction')
def xmr_transaction():
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, latestTransList = xmr_transactionreturn.trans_return(perpage, start)
    total = context["trans_total"]
    log.info("The total transaction information is" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('xmr/transaction.html', latestTransList=latestTransList, pagination=pagination, **context)


# 门罗币交易详情页
@xmr_bp.route('/xmr/tsc_detail/<string:hash>')  ##后端数据已经准备完毕，前端页面还未处理！
def xmr_tsc_detail(hash):
    tsc_info, context = xmr_transactionreturn.trans_detail_return(hash)
    log.info("The transaction details are:")
    log.info("Return Page tsc_detail")
    return render_template('xmr/tsc_detail.html', tsc_info=tsc_info, **context)


@xmr_bp.route('/xmr/query_trans')
def xmr_query_test():
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, latestTransList = xmr_transactionreturn.trans_return(perpage, start)
    total = context["trans_total"]
    log.info("The total transaction information is" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('xmr/query_trans.html', latestTransList=latestTransList, pagination=pagination, **context)


@xmr_bp.route('/xmr/transaction/search_tx', methods=['GET', 'POST'])
def xmr_transaction_search_tx():
    rule = request.values['sortname']
    starttime = request.values['starttime']
    endtime = request.values['endtime']
    minvalue = request.values['minvalue']
    maxvalue = request.values['maxvalue']
    valuetype = 'XMR'
    log.info("The sorting rule is:" + str(rule))
    log.info("The currency type is:" + str(valuetype))
    log.info("++++++++++++++++++++++++++++++++++++++++")
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, result = xmr_transactionreturn.trans_ajax_tx(rule, starttime, endtime, minvalue, maxvalue, valuetype,
                                                          perpage, start)
    log.info("The query result is" + str(len(result)))
    total = context["trans_total"]
    log.info("The total number of block information is" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('xmr/transaction.html', latestTransList=result, pagination=pagination, **context)


# QPR search功能的实现，查询对应的区块高度，交易hash的详细信息，或者地址信息。
@xmr_bp.route('/xmr/search', methods=['GET', 'POST'])
def xmr_search():
    text = request.values['search_text']
    perpage = perPage
    rull = r"^(1|3)[a-zA-Z\d]{24,33}$"
    if len(text) > 2 and text[0] == '0' and text[1] == 'x':
        rule = "^0x(.*)"
        text = re.findall(rule, text)[0]
    if text.isdigit():  # 由高度找区块信息
        log.info("The input information is:" + str(text))
        hash = xmrblock.block_reverse(int(text))  # 从高度找到区块哈希值
        if hash:
            page = request.args.get(get_page_parameter(), type=int, default=1)
            start = (page - 1) * perpage
            context, blocktrans = xmrreturn.blockdetail_return(hash, start, perpage, True)  # 返回区块信息blockInfo和交易信息
            total = context["total"]
            log.info("Total transaction volume is:" + str(total))
            pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
            return render_template('xmr/block_detail.html', pagination=pagination, blocktrans=blocktrans, **context)
        else:
            return render_template('search_error_message.html')
    elif len(text) == 64:  ##交易hash
        result = datainterchange.xmr_get_block(text)
        tx_result = datainterchange.xmr_get_transaction(text)
        if result:
            page = request.args.get(get_page_parameter(), type=int, default=1)
            start = (page - 1) * perpage
            context, blocktrans = xmrreturn.blockdetail_return(text, start, perpage, True)
            total = context["total"]
            log.info("Total transaction volume is:" + str(total))
            pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
            return render_template('xmr/block_detail.html', pagination=pagination, blocktrans=blocktrans, **context)
        elif tx_result:
            tsc_info, context = xmr_transactionreturn.trans_detail_return(text)
            log.info("Transaction details are:")
            log.info("Return Page tsc_detail")
            return render_template('xmr/tsc_detail.html', tsc_info=tsc_info, **context)
        else:
            return render_template('search_error_message.html')

    else:
        return render_template('search_error_message.html')


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
