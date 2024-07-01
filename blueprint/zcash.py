import requests
import os
import json
import math
from flask import Blueprint, current_app, render_template, request, jsonify
from flask_paginate import Pagination, get_page_parameter
from Serives import blockreturn, transactionreturn, btcblock, zcash_blockreturn, zcashblock, \
    zcash_transactionreturn
from Serives.ZcashAddressDetail import zcash_handleAddressTx
from Serives.bitcoinmessage import get_by_newsearch,get_by_newsearch_new
from Serives.btcAddressDetail import handleAddressTx
from Serives.zcash_addrtag import zcash_get_rtt, zcash_get_rtt_by_differ, get_i2ps
from dao.bitcoin_node import get_btc_node, get_btc_node_analyse, get_max_height, get_btc_node_byIP
from utils import validation_address, get_dict_key_value
from dao import datainterchange
from flask_login import login_required

import re
zcash_bp = Blueprint('zcash', __name__)
from config import config
from log import log
from bee_var import perPage, perPage_10
from mysql_dealer import mysql_dealer
import time
from app import es
from Serives.btcaddrtag import get_address_tags_with_address,get_address_tags_with_service,get_address_tags_with_two,get_pure_address_tags,updateAddressTag,get_tags,get_address_tags,get_special_addr,updateSpecialAddr,get_special_addrs
log = log.init_logger(config.log_filepath)

es.tryagain_instance()
es = es.instance



@zcash_bp.route('/test')
def zcash_test():
    print("Yes!")

#
#ZcashPage by tiancy
#
@zcash_bp.route('/zcash')
def zcash_home():
    #blocks, context = zcash_blockreturn.zcash_block_return(5, 0)
    #return render_template('zcash/zcash_home.html',blocks=blocks, **context)
    zcash_latestTransList,context= zcash_blockreturn.zcash_home_show()
    return render_template('zcash/zcash_home.html',latestTransList=zcash_latestTransList, **context)

@zcash_bp.route('/zcash/block')
def zcash_block():
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    blocks, context = zcash_blockreturn.zcash_block_return(perpage, start)  # pagination默认perPage20查询实现
    total = context['block_total']
    log.info("Zcash区块信息总数为" + str(total))#打印日志
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='blocks')
    return render_template('zcash/zcash_block.html', blocks=blocks, pagination=pagination, **context)
@zcash_bp.route('/zcash/zcash_block_detail/<string:hash>')
def zcash_block_detail(hash):
    perpage = perPage
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start=(page - 1) * perpage
    context,blocktrans= zcash_blockreturn.zcash_blockdetail_return(hash,start,perpage,True)
    total =context["total"]
    log.info("交易总量为"+str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('zcash/zcash_block_detail.html', pagination=pagination,blocktrans=blocktrans,**context)  # **context

@zcash_bp.route('/zcash/transaction')
def zcash_transaction():
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, latestTransList = zcash_transactionreturn.zcash_trans_return(perpage, start)
    total = context["trans_total"]
    log.info("zcash交易信息总数为" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('zcash/zcash_transaction.html',latestTransList=latestTransList, pagination=pagination, **context)

@zcash_bp.route('/zcash/trans_detail/<string:hash>')     ##详细交易信息展示
def zcash_tsc_detail(hash):
    tsc_info,context = zcash_transactionreturn.zcash_trans_detail_return(hash)
    log.info("交易详细信息为：")
    log.info("返回页面tsc_detail")
    return render_template('zcash/zcash_tsc_detail.html',  tsc_info=tsc_info,**context)
@zcash_bp.route('/zcash/vision_test/<string:hash>')     ##详细交易信息展示
def vision_test(hash):
    tsc_info,context = zcash_transactionreturn.zcash_trans_detail_return(hash)
    log.info("交易详细信息为：")
    log.info("返回页面tsc_detail")
    return render_template('zcash/vision_test.html',  tsc_info=tsc_info,**context)
@zcash_bp.route('/zcash/address')
def zcash_address():
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    context, latestTransList = transactionreturn.trans_return(perpage, start)
    total = context["trans_total"]
    log.info("zcash交易信息总数为" + str(total))
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    return render_template('zcash/zcash_address.html',latestTransList=latestTransList, pagination=pagination, **context)

@zcash_bp.route('/zcash/address/<string:address>')
def zcash_address_detail(address):
    page_size=10
    final_address=address
    page=int(request.args.get("page","1"))
    tx_list,total,first_seen,recv,sent,recv_num,sent_num,balance=zcash_handleAddressTx(final_address,page)
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=page_size)
    return render_template('zcash/zcash_address_detail.html',txs=tx_list,pagination=pagination,address=final_address,recv=recv,sent=sent,balance=balance,first_seen=first_seen,recv_num=recv_num,sent_num=sent_num)
@zcash_bp.route('/zcash/address_static')
def zcash_address_static():
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

    #fields, content = get_daily_eth_a_info()
    chart_data = []
    # for id,item in enumerate(content['date']):
    #     data = {}
    #     data['date'] = item
    #     data['new_address'] = content['new_address'][id]
    #     data['active_address'] = content['active_address'][id]
    #     chart_data.append(data)
    content={}
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


@zcash_bp.route('/zcash/transaction_static')
def zcash_transction_static():
    return render_template('zcash/transaction_static.html')

@zcash_bp.route('/zcash/search',methods=['GET', 'POST'])
def zcash_search():
    text = request.values['search_text']
    perpage = perPage
    rull = r"^(1|3)[a-zA-Z\d]{24,33}$"
    if len(text) > 2 and text[0] == '0' and text[1] == 'x':
        rule = "^0x(.*)"
        text = re.findall(rule,text)[0]
    if text.isdigit():
        log.info("输入信息为："+str(text))
        hash = zcashblock.zcash_block_reverse(int(text))
        if hash:
            page = request.args.get(get_page_parameter(), type=int, default=1)
            start = (page - 1) * perpage
            context, blocktrans = zcash_blockreturn.zcash_blockdetail_return(hash, start, perpage, True)
            total = context["total"]
            log.info("交易总量为" + str(total))
            pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
            return render_template('zcash/zcash_block_detail.html', pagination=pagination, blocktrans=blocktrans,**context)
        else:
            return render_template('search_error_message.html')
    elif len(text) == 64: ##hash值
        result=datainterchange.zcash_get_block(text)
        tx_result = datainterchange.zcash_get_transaction(text)
        if result:
            page = request.args.get(get_page_parameter(), type=int, default=1)
            start = (page - 1) * perpage
            context, blocktrans = zcash_blockreturn.zcash_blockdetail_return(text, start, perpage, True)
            total = context["total"]
            log.info("交易总量为" + str(total))
            pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
            return render_template('zcash/zcash_block_detail.html', pagination=pagination, blocktrans=blocktrans, **context)
        elif tx_result:
            tsc_info, context = zcash_transactionreturn.zcash_trans_detail_return(text)
            log.info("交易详细信息为：")
            log.info("返回页面tsc_detail")
            return render_template('zcash/zcash_tsc_detail.html', tsc_info=tsc_info, **context)
        else:
            return render_template('search_error_message.html')
    elif re.findall(rull,text) and validation_address("btc",text):   #最后一个为地址
        page_size = 10
        final_address = text
        page = int(request.args.get("page", "1"))
        tx_list, total, first_seen, recv, sent, recv_num, sent_num, balance = handleAddressTx(final_address, page)
        pagination = Pagination(bs_version=4, page=page, total=total, per_page=page_size)
        return render_template('btc/address_detail.html', txs=tx_list, pagination=pagination, address=final_address,
                               recv=recv, sent=sent, balance=balance, first_seen=first_seen, recv_num=recv_num,
                               sent_num=sent_num)
    else:
        page = request.args.get(get_page_parameter(), type=int, default=1)
        start = (page - 1) * perpage
        context,latestTranList=transactionreturn.trans_search_return(start,perpage,text)
        if context:
            total = context["trans_total"]
            log.info("交易信息总数为" + str(total))
            pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
            return render_template('btc/transaction.html', latestTransList=latestTranList, pagination=pagination,
                                   **context)
        else:

            return render_template('btc/../templates/search_error_message.html')


@zcash_bp.route('/i2p_view',methods=['GET', 'POST'])
def i2p_view():
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t=time.time()
    usetime = round(time.time() - t, 3)
    count, list = get_i2ps(start, perpage)
    content = {
        "page_title": 'i2p_addr',
        "count": count,
        "address": None,
        "servicename": None,
        "usetime":usetime
    }
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='i2p_addr')
    return render_template('btc/i2p_addr_all.html', list=list, pagination=pagination, **content)
@zcash_bp.route('/zcash/rtt_txs',methods=['GET', 'POST'])
def zcash_rtt_txs():
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t=time.time()
    count, list = zcash_get_rtt(start, perpage)
    usetime=round(time.time()-t,3)
    content = {
        "page_title": 'rtt_txs',
        "count": count,
        "address": None,
        "servicename": None,
        "usetime":usetime
    }
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='rtt')
    return render_template('zcash/zcash_rtt_txs.html', list=list, pagination=pagination,**content)
@zcash_bp.route('/zcash/search_rtt_txs',methods=['GET', 'POST'])
def zcash_search_rtt_txs():
    text = request.values['differ_text']
    perpage = perPage_10  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    t=time.time()
    if text =='':
        count, list = zcash_get_rtt(start, perpage)
    else:
        count, list = zcash_get_rtt_by_differ(text,start, perpage)
    usetime=round(time.time()-t,3)
    content = {
        "page_title": 'rtt_txs',
        "count": count,
        "address": None,
        "servicename": None,
        "usetime":usetime
    }
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='rtt')
    return render_template('zcash/zcash_rtt_txs.html', list=list, pagination=pagination,**content)
