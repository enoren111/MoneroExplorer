import os
import json
import math
import time
from datetime import datetime
import requests
from flask import Blueprint, current_app, render_template, request, jsonify,url_for
from flask_paginate import Pagination, get_page_parameter

from Serives import zcash_blockreturn
from utils import ts2t, time_quantum, DateEncoder, today, day_stamp, get_dict_key_value, visit_mode_check
from mysql_dealer import get_daily_eth_a_info, get_node_detail_info, get_node_distribution, mysql_dealer
from data.local_data_dealer import get_node_kbuckets_data,get_node_kbuckets_data2
from es1 import get_blocks, get_trans_in_block, get_block_byid, get_latest_trans, get_trans_at_address, \
    get_contract_list, block_byminer, get_transaction_byhash, get_all_trans, get_contract_code, trans_info_per_day, \
    get_node_list, judge_trans_type, get_transes, get_nodes, get_node, get_trans_total, get_block_total, search_node, \
    block_search, trans_ajax, eth_home_show
from es3 import get_transes_v2,get_transes_v3,BigDealTranses,get_block_detail,AllTranses,BlockDetail,get_transaction
from data.getinfo import get_info
from bee_var import *
from loguru import logger



eth_bp = Blueprint('eth', __name__)
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

'''
json.dumps 需要由jQuery.parseJSON解析
jsonify不需要解析，可以直接使用
'''

@eth_bp.route('/eth')
def eth_home():
    eth_latestTransList, context = eth_home_show()
    return render_template('eth/eth_home.html', latestTransList=eth_latestTransList, **context)


@eth_bp.route('/eth/historyRate/', methods=['POST', 'GET'])
def EthHistoryRate():
    global results_all
    try:
        page = int(request.args.get("page", 1))
    except:
        page = 1
    page_size = 10
    sql = "select * from ETH_PriceRate order by priceTime {0} limit {1},{2}".format('desc', (page - 1) * page_size,
                                                                                page_size)
    sql_all = "select * from ETH_PriceRate order by priceTime {} ".format('desc')
    count_sql = "select count(1) from ETH_PriceRate"
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
    return render_template('eth/ethRatehistory.html', pagination=pagination, result=result_list,
                           results_all=result_list_all)
# BLOCK
@eth_bp.route('/eth/block')
def eth_block():
    # blocks = read_from_txt('block-table.txt')
    # default_size = 20
    perPage = 20  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perPage
    # end = start + perPage

    dateMap = {

        "0": "今天",
        "1": "本周",
        "2": "本月",
        "3": "今年",
        "4": "全部"
    }

    order_rule = ''
    order = request.args.get('order', default='0')  # 默认值为今天
    # if order != None:
    order_rule = dateMap[order]
    del dateMap[order]

    result = get_blocks(perPage, start)
    # logger.info(result)
    # logger.info(start)

    total = result['total']['value']

    blocks = result['blocks']
    took = result['took']
    # logger.info(total)
    # logger.info(page)
    # logger.info(perPage)
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='blocks')
    pages = math.ceil(float(total) / perPage)
    context = {
        "order_rule": order_rule,
        "date_map": dateMap,
        "pages": pages,
        "block_fields": block_fields,
        "block_total": total,
        "took": took,
        "page_title": '区块'
    }
    logger.info(blocks)
    return render_template('eth/eth_block.html', blocks=blocks, pagination=pagination, **context)


@eth_bp.route('/eth/block_detail/<int:blockNumber>')
def eth_block_detail(blockNumber):
    logger.info(blockNumber)

    ## blockInfo
    block_total = get_block_total()
    # logger.info(block_total['value'])
    # blockInfo = get_block_byid(blockNumber)

    blockInfo = get_block_detail(blockNumber, True)
    # logger.info(blockInfo)
    logger.info(blockInfo)
    blockInfo['time'] = ts2t(blockInfo['timestamp'])

    # logger.info(blockInfo['time'])
    blockInfo['confirm_num'] = block_total['value'] - 1 - int(blockNumber)
    # logger.info(block_total)
    # logger.info(blockInfo)
    ## transactions of block
    # transes_info = get_transes_v2(blockNum=blockNumber, detail=True)  # True 统计普通交易和合约交易个数() 已融合于get_block_detail

    context = {
        "blockInfo": blockInfo,
        "col_names": current_app.config['BLOCK_DETAIL_TB_COL_NAME'],
        "page_id": str(blockNumber),
        "page_title": '区块'
    }
    # context.update(transes_info)
    return render_template('eth/block_detail.html', **context)  # **context


@eth_bp.route('/eth/block/search', methods=['GET', 'POST'])
def eth_block_search():
    rule = request.values['sortname']
    starttime = request.values['starttime']
    endtime = request.values['endtime']
    logger.info("排序规则为" + str(rule))
    logger.info("++++++++++++++++++++++++++++++++++++++++")
    perpage = perPage * 2  # pagination默认
    # logger.info(perPage)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    dateMap = {

        "0": "今天",
        "1": "本周",
        "2": "本月",
        "3": "今年",
        "4": "全部"
    }

    order_rule = ''
    order = request.args.get('order', default='0')  # 默认值为今天
    # if order != None:
    order_rule = dateMap[order]
    del dateMap[order]
    result = block_search(perpage, start, rule, starttime, endtime)  # pagination默认perPage20
    total = result['total']['value']
    # logger.info(total)
    blocks = result['blocks']
    took = result['took']
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perpage, record_name='blocks')
    pages = math.ceil(float(total) / perpage)
    context = {
        "order_rule": order_rule,
        "date_map": dateMap,
        "pages": pages,
        "block_fields": block_fields,
        "block_total": total,
        "took": took,
        "page_title": '区块'
    }

    return render_template('eth/eth_block.html', blocks=blocks, pagination=pagination, **context)


# TRANSACTION
@eth_bp.route('/eth/transactions')
def eth_transactions():
    perPage = current_app.config['TABLE_ITEMS_PER_PAGE']  # pagination默认
    perPage = perPage * 2
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perPage
    # end = start + perPage
    # total, latestTransList = get_all_trans(perPage, start)  # 返回页面展示所需的数据 start>10000会报错
    # total, latestTransList = get_latest_trans(perPage, start)
    # total = 0;latestTransList = []
    # tv2_result = get_transes_v2(size=perPage, start=start, time_rang_id=0)  # 默认降序 despatch

    ans = get_transaction(perPage, start)
    # logger.info(perPage)
    print(ans)
    total = ans['total']['value']

    latestTransList = ans['result']
    # logger.info(latestTransList)
    # logger.info(ans['result'])
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='blocks')

    pages = math.ceil(float(total) / perPage)

    context = {
        "labels": ['1', '2', '3', '4', '5', '6', '7'],
        "dataset3": [20, 40, 30, 85, 10, -20, 60],
        "trans_total": total,
        "trans_fields": current_app.config['TRANS_FIELDS'],
        "pages": pages,
        "tr_option_list": current_app.config['TIME_RANGE_OPTIONS'],
        "columns": current_app.config['TRANS_TB_KEYS'],
        "page_title": '交易',
        "took": ans['took']

    }

    # for daily chart
    # fields, content = get_daily_eth_a_info()
    # for field in fields:
    #     context[field] = content[field]
    # context['trans_type'] = [content['normal_trans_num'][-1], content['call_trans_num'][-1],
    #                          content['contract_trans_num'][-1]]
    # return render_template('eth/transactions.html', latestTransList=latestTransList, pagination=pagination)

    return render_template('eth/transactions.html', latestTransList=latestTransList, pagination=pagination, **context)


@eth_bp.route('/eth/transaction/search', methods=['GET', 'POST'])
def eth_transaction_search():
    rule = request.values['sortname']
    logger.info("排序规则为" + str(rule))
    starttime = request.values['starttime']
    logger.info(starttime)
    endtime = request.values['endtime']
    logger.info(endtime)
    minvalue = request.values['minvalue']
    logger.info(minvalue)
    maxvalue = request.values['maxvalue']
    logger.info(maxvalue)
    # valuetype = request.values['servicename']

    # logger.info("货币类型为：" + str(valuetype))
    logger.info("++++++++++++++++++++++++++++++++++++++++")
    perpage = perPage  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    ans = trans_ajax(rule, starttime, endtime, minvalue, maxvalue, perpage, start)
    logger.info(ans)
    total = ans['total']['value']

    latestTransList = ans['result']
    # logger.info(latestTransList)
    # logger.info(ans['result'])
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='blocks')

    pages = math.ceil(float(total) / perPage)

    context = {
        "labels": ['1', '2', '3', '4', '5', '6', '7'],
        "dataset3": [20, 40, 30, 85, 10, -20, 60],
        "trans_total": total,
        "trans_fields": current_app.config['TRANS_FIELDS'],
        "pages": pages,
        "tr_option_list": current_app.config['TIME_RANGE_OPTIONS'],
        "columns": current_app.config['TRANS_TB_KEYS'],
        "page_title": '交易',
        "took": ans['took']

    }


    return render_template('eth/transactions.html', latestTransList=latestTransList, pagination=pagination, **context)


@eth_bp.route('/eth/tsc_detail')
def eth_tsc_detail():
    tsc_hash = request.args.get('hash')
    tsc_info = get_transaction_byhash(tsc_hash)
    # tsc_info['hash'] = tsc_hash
    context = {
        "page_title": '交易',
        "page_id": str(tsc_hash)
    }
    return render_template('eth/tsc_detail.html', tsc_info=tsc_info, **context)


@eth_bp.route('/eth/trans/big_deal')
def eth_big_deal():

    ## 折线图
    fields, datas = get_daily_eth_a_info()

    ## 大额交易表格
    perPage = current_app.config['TABLE_ITEMS_PER_PAGE']  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perPage
    '''
    tv2_result = get_transes_v2(start=start,size=perPage,big_deal=True)
    total = tv2_result['total']
    bigTransesList = tv2_result['result']
    '''

    ans = get_transes_v3(BigDealTranses(size=perPage, start=start))
    total = ans['total']
    bigTransesList = ans['result']

    # total=0;bigTransesList=[]
    pages = math.ceil(float(total) / perPage)
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='blocks')
    context = {
        "total":total,
        "bigTransesList":bigTransesList,
        "pages":pages,
        "exception_trans":datas['exception_trans'],
        "date_list":datas['date'],
        "tr_options":current_app.config['TIME_RANGE_OPTIONS'],
        "unit_list":current_app.config['UNITS'],
        "page_title":'大额交易'
    }


    return render_template('eth/big_deal.html',**context,pagination=pagination)


# ADDRESS
@eth_bp.route('/eth/address')
def eth_address():
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

    def foo():
        return get_transes_v2(size=0, address=item['address'])['total']

    for item in richList:
        item['trans_num'] = visit_mode_check(foo(), data=100)

    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(bs_version=4, page=page, total=20, per_page=10, record_name='rich')

    content = get_daily_eth_a_info()
    logger.info(content)
    chart_data = []
    # for id,item in enumerate(content['date']):
    #     data = {}
    #     data['date'] = item
    #     data['new_address'] = content['new_address'][id]
    #     data['active_address'] = content['active_address'][id]
    #     chart_data.append(data)
    content['active_address'] = "active_address"
    content['new_address'] = "new_address"
    content['date'] = "2020"

    context = {
        'active_address': content['active_address'],
        'new_address': content['new_address'],
        'date': content['date'],
        "page_title": '地址',
        "pages": 2
        # chart_data:chart_data
    }

    return render_template('eth/address.html', richList=richList, pagination=pagination, **context)


@eth_bp.route('/eth/address/detail/<addr>')
def eth_address_detail(addr):
    # 交易列表 ajax
    # 爆块 ajax
    # 统计 unfinished

    context = {
        "address": addr,
        "tr_options": current_app.config['TIME_RANGE_OPTIONS']
    }
    type = judge_trans_type(addr)

    # 判断地址类型
    def foo():
        return get_info(addr)

    logger.info(addr)
    if type == trans_type['0']:  # 普通地址
        # total1, atrans = get_trans_at_address(addr)  # 废弃
        # context['trans_num'] = total1

        ## 地址统计信息
        # transes_info = get_transes_v2(address=addr, detail=True)  # timeout warning   弃用

        transes_info = visit_mode_check(foo(), "eth_address_detail_sample.json")
        # total2, eblocks = block_byminer(addr,size=0)  # 爆块数
        # context['eb_num'] = total2
        context.update(transes_info)
        # logger.info(context)
        context["page_title"] = '地址'
        context["page_id"] = addr
        return render_template('eth/address_detail.html', **context)
    elif type == trans_type['1']:  # 合约地址
        # total, ctrans = get_trans_at_address(addr, 20, 0)
        c_code = get_contract_code(addr)
        context = {
            "address": addr,
            "total": 0,
            "c_code": c_code,
            "page_title": '合约',
            "page_id": addr,

        }

        return render_template('eth/contract_detail.html', **context)
        # eth_contract_detail()
    else:
        print("not deal exception!")

## NODE
# send_update_node()
@eth_bp.route('/eth/node')
def eth_node():


    ## node分布 国家，版本，网络，操作系统
    node_dist = get_node_distribution()

    pie_series = {}  # 饼图数据
    interval = 30

    for key in node_dist:
        sum_nums = sum(item['value'] for item in node_dist[key][:])
        others_nums = sum(item['value'] for item in node_dist[key][interval:])
        pie_series[key] = node_dist[key][0:interval]
        pie_series[key].append({"value":(sum(item['value'] for item in node_dist[key][interval:])),"name":"others","p":str(round(others_nums/sum_nums*100,2))+'%'})
        # pie_series[key].append({"value":(sum(item['value'] for item in node_dist[key][interval:])),"name":"others","p":str(round(sum(item['pv'] for item in node_dist[key][interval:])*100,2)) +'%' })





    ## 表格&分页
    perPage = 20  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perPage
    node_result = get_node_list(perPage, start)
    total = node_result['total']
    node_list = node_result['result']
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='node_list')
    pages = math.ceil(float(total) / perPage)




    context = {
        "node_total":total,
        "table_fields":current_app.config['NODE_TB_COL_NAME'],  # 选择字段
        "pages":pages,
        "height":get_block_total(),
        "page_title":'节点',
        "took":node_result['took'],
        "node_dist":node_dist,
        "pie_series":pie_series
    }
    # context.update(node_dist)

    return render_template('eth/node.html', node_list=node_list, pagination=pagination,**context)


@eth_bp.route('/eth/node/<node_id>')
def eth_node_detail(node_id):
    node = get_node(node_id)
    # mysql_node_info = get_node_detail_info(node_id)
    # node['country'] = mysql_node_info['country']
    context = {
        "page_id": node_id,
        "page_title":'节点'
    }
    return render_template('eth/node_detail.html', node=node,**context)


# POOL
@eth_bp.route('/eth/pool')
def eth_pool():
    context={
        "page_title": '矿池'
    }
    return render_template('eth/pool.html',**context)


# CONTRACT
@eth_bp.route('/eth/contract')
def eth_contract():

    # table
    page_size = current_app.config['TABLE_ITEMS_PER_PAGE']  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * page_size
    # end = start + perPage
    total, contractList = get_contract_list(page_size,start)
    # total = 0;latestTransList = []
    pagination = Pagination(bs_version=4, page=page, total=total, per_page=page_size, record_name='cl')
    pages = math.ceil(float(total) / page_size)
    ## 每日新发布合约数
    # date_list = time_quantum('2019-03-02', 30)
    # for date in date_list:
    #     pass
    fields, content = get_daily_eth_a_info()

    context = {
        # "address": addr,
        "total": total,
        "new_contract":content['new_contract'],
        "date_list":content['date'],
        "table_fields":current_app.config['CONTRACT_TB_FIELDS'],
        "pages":pages,
        "page_title":"合约"


    }
    return render_template('eth/contract.html', contractList=contractList, pagination=pagination,**context)


@eth_bp.route('/eth/contract_detail')
def eth_contract_detail():  # 废弃
    caddress = request.args.get('caddress')
    # print(caddress)
    # total, ctrans = get_trans_at_address(caddress, 20, 0)  # despatch
    # return render_template('eth/contract.html', contractList=contractList, pagination=pagination)

    c_code = get_contract_code(caddress)

    context = {
        "address": caddress,
        "total": 0,   # total由datatable赋值 /data/address_trans?
        "c_code": c_code,
        "page_title":"合约"

    }

    return render_template('eth/contract_detail.html', **context)


# DATATABLE DATA
## node kbuckets
@eth_bp.route('/data/kbuckets')  # methods=['POST']
def send_node_kbuckets_data():
    draw = request.args.get('draw', 1, type=int)
    # length = request.args.get('length', type=int)
    # start = request.args.get('start', type=int)
    nodeid = request.args.get('nid')
    # total = 1
    # data_list = [
    #     {'rname':'0(0)','c0': {'id':'123',"port":'321'}, 'c1': '1', 'c2': '1', 'c3': '0', 'c4': '0', 'c5': '0', 'c6': '0', 'c7': '0', 'c8': '0','c9':'0','c10':'0','c11':'0','c12':'0','c13':'0','c14':'0','c15':'0'},
    #     {'rname':'1(2)','c0': {'id':'123',"port":'322'}, 'c1': '1', 'c2': '1', 'c3': '0', 'c4': '0', 'c5': '0', 'c6': '0', 'c7': '0', 'c8': '0','c9':'0','c10':'0','c11':'0','c12':'0','c13':'0','c14':'0','c15':'0'}]

    # data_list = get_node_kbuckets_data2(nodeid)
    data_list = get_node_kbuckets_data()  # local data
    total=len(data_list)
    return json.dumps({"draw": draw, "recordsTotal": total, "recordsFiltered": total,
                       "data": data_list}, ensure_ascii=False)


@eth_bp.route('/data/translist')  # 为block_detail datatable 返回地址交易列表
def send_translist():
    draw = request.args.get('draw', 1, type=int)
    length = request.args.get('length', type=int)
    start = request.args.get('start', type=int)
    blockNumber = request.args.get('bnum', type=int)
    # tr_op = request.args.get('tr_op', type=int)

    # order = request.args.get('order[0][dir]')  # 排序规则：ase/desc
    # print(request.args.get('order[0][column]'))  # 排序字段索引
    # total, transList = get_trans_in_block(blockNumber, length, start)  # despatch transList in block
    # ans = get_transes_v3(BlockDetail(block_id=blockNumber))   # 不适用
    total, transList = get_transes(size=length, start=start, order='asc', blockNum=blockNumber)  # 无序
    # logger.info(transList[0:length])
    # logger.info(len(transList))
    # logger.info(transList[0]['trans_type'])
    # transList[0]['trans_type']="普通"

    # logger.info(total)
    # logger.info(draw)
    # tlToJson = json.dumps(transList)
    return json.dumps(
        {"draw": draw, "recordsTotal": total['value'], "recordsFiltered": total['value'], "data": transList[0:length]})


@eth_bp.route('/data/explode_block')
@eth_bp.route('/data/explode_block')
def send_explode_block():  # 返回地址爆块
    # perPage = 20
    draw = request.args.get('draw', 1, type=int)
    length = request.args.get('length', type=int)
    start = request.args.get('start', type=int)
    miner = request.args.get('address')
    # print('miner='+str(miner)+";start="+str(start))
    total, eblocks = block_byminer(miner, length, start)  # transList in block
    return json.dumps({"draw": draw, "recordsTotal": total, "recordsFiltered": total,
                       "data": eblocks}, ensure_ascii=False)


@eth_bp.route('/data/address_trans')
def send_address_trans():  # 返回地址交易
    # perPage = 20
    draw = request.args.get('draw', 1, type=int)
    length = request.args.get('length', type=int)
    start = request.args.get('start', type=int)
    address = request.args.get('address')
    tr_op = request.args.get('tr_op', type=int)
    # request.args.get('search[value]')  # 搜索字段
    # print(request.args.get('order[0][column]'))  # 排序字段索引
    # print(request.args.get('order[0][dir]'))  # 排序规则：ase/desc
    # total, atrans = get_trans_at_address(address, length, start)   # 可由get_transes_v3替代
    ans = get_transes_v3(
        BigDealTranses(size=length, start=start, args={"tropId": tr_op, "value": 0, "address": address, "unitId": 0}))
    total = ans['total']['value']
    atrans = ans['result']
    # logger.info(total)
    # logger.info(atrans)
    return json.dumps({"draw": draw, "recordsTotal": total, "recordsFiltered": total,
                       "data": atrans}, ensure_ascii=False)



# TEST
@eth_bp.route('/statistics_chart')
def statistics_chart():
    fields, content = get_daily_eth_a_info()
    context = {}
    context.update(content)
    context['trans_type'] = [content['normal_trans_num'][-1], content['call_trans_num'][-1],
                             content['contract_trans_num'][-1]]

    return render_template('eth/statistics_chart.html',**context)

# AJAX
@eth_bp.route('/ajax/check_node', methods=['POST'])
def check_node():
    # print(request.args.get('ip'))



    # ip = request.values['ip']
    # port = request.values['port']
    node_ip = '67.203.1.170'
    node_port = '30303'
    url ='http://192.168.126.52:5600/?addr='+node_ip+':'+node_port
    try:


        r = requests.get(url)
        response_dict = r.json()
    except:
        response_dict={ "result": 0, "ret": "error" }
    status = get_dict_key_value(response_dict,['result']);
    # status = 0
    node_info={
        'node_ip':node_ip,
        'node_port':node_port
    }
    if status == 1:
        node_info['status']='online'
        # node_info = search_node(node_ip)
    else:
        node_info['status'] = 'offline'


    return jsonify(node_info)


@eth_bp.route('/ajax/qrcode')
def get_address_qrcode():
    return jsonify(message='qrcode there')







## node table

@eth_bp.route('/ajax/node', methods=['POST'])
def send_update_node():
    args = request.get_json()

    page = int(args['page'])

    perPage = current_app.config['TABLE_ITEMS_PER_PAGE']  # pagination默认
    start = (page - 1) * perPage
    node_result = get_node_list(perPage, start)
    total = node_result['total']
    node_list = node_result['result']

    pages = math.ceil(float(total) / perPage)
    keys = current_app.config['NODE_TB_KEYS']


    return json.dumps({"pages":pages,"page":page,"total":total,"update_data":node_list,"key_list":keys})



## bid_deal_table
@eth_bp.route('/ajax/trans/big_deal', methods=['POST'])
def send_update_bigDeal():
    args = request.get_json()

    print(args)
    page = int(args['page'])

    # 参数验证
    # if args['value']!='':
    #     print(args['value'])

    ## 大额交易表格
    page_size = current_app.config['TABLE_ITEMS_PER_PAGE']  # pagination默认
    start = (page - 1) * page_size

    bdt = BigDealTranses(size=page_size,start=start,args=args)
    tv3_result = get_transes_v3(bdt)
    total = tv3_result['total']
    bigTransList = tv3_result['result']
    '''
    tv2_result = get_transes_v2(start=start, size=perPage, big_deal=True)
    total = tv2_result['total']
    bigTransList = tv2_result['result']
    '''
    pages = math.ceil(float(total) / page_size)
    keys = current_app.config['BIG_DEAL_TB_KEYS']

    # return total
    return json.dumps({"pages":pages,"page":page,"total":total,"update_data":bigTransList,"key_list":keys})



## block table filter
@eth_bp.route('/ajax/block/filter', methods=['POST'])
def send_filter_block():
    # page = int(request.values['page'])
    # order = request.values['order']
    data = request.get_json()  # 需要在ajax请求中设置 contentType: 'application/json;charset=UTF-8',
    perPage = current_app.config['TABLE_ITEMS_PER_PAGE']

    # if data is None or data['search_text'].strip() == '':  # 错误处理
    if data is None:  # 错误处理
        return jsonify(message='请选择过滤条件'), 400
    page = int(data['page'])
    order = data['order']
    time_range_id = data['time']

    start = (page - 1) * perPage
    result = get_blocks(perPage, start, order, time_range_id)
    total = result['total']
    blocks_filtered = result['blocks']
    took = result['took']
    pages = math.ceil(float(total) / perPage)
    # return jsonify(message=data['search_text'])

    keys = current_app.config['BLOCK_TB_KEYS']
    return json.dumps(
        {"blocks": blocks_filtered, "took":took,"message": data['search_text'], "pages": pages, "total": total, "page": page,"key_list":keys},
        cls=DateEncoder)


## transactions_table_filter
@eth_bp.route('/ajax/transactions/filter', methods=['POST'])
def send_f_transactions():
    data = request.get_json()
    tr_op = data['tr_op']
    order = data['order']
    page = int(data['page'])

    perPage = current_app.config['TABLE_ITEMS_PER_PAGE']
    start = (page - 1) * perPage

    date_list = time_quantum('2019-1-10', 30)  # test
    total, transes = get_transes(size=perPage,order=order,start=start,time_rang_id=tr_op)
    pages = math.ceil(float(total) / perPage)
    columns = current_app.config['TRANS_TB_KEYS']

    # print(data['time_option']+1)
    return json.dumps({"message": '', "cols":columns,"transes":transes, "date_list": date_list, "pages": pages,"none_test":['1',None], "total": total, "page": page})


# TEST
@eth_bp.route('/data/example3')
def get_data():
    data = os.path.join(os.path.join(basedir, 'data'), 'table.txt')
    vardata = []
    draw = request.args.get('draw', 1, type=int)
    length = request.args.get('length', type=int)
    start = request.args.get('start', type=int)

    lines = open(data, 'r', encoding='utf-8').read().split('\n')
    filtered = len(lines)
    if start + length > filtered:
        end = filtered
    else:
        end = start + length
    for line in lines:
        tds = line.split(',')
        vardata.append(tds)
    return json.dumps(
        {"draw": draw, "recordsTotal": len(vardata), "recordsFiltered": filtered, "data": vardata[start:end]},
        ensure_ascii=False)
    # return json.dumps(vardata, ensure_ascii=False)


def read_from_txt(filename):
    data_path = os.path.join(os.path.join(basedir, 'data'), filename)
    lines = open(data_path, 'r', encoding='utf-8').read().split('\n')
    split_lines = []
    for line in lines:
        split_lines.append(line.split(','))
    return split_lines


def template():  # 不可调用
    perPage = 20  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perPage
    # end = start + perPage
    # total, transOfA = get_trans_at_address(addr, perPage, start)
    # total = 0;latestTransList = []
    # pagination = Pagination(bs_version=4, page=page, total=total, per_page=perPage, record_name='ad')
    context = {
        # "address": addr,
        # "total": total
    }
