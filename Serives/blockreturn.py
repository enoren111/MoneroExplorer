from datetime import datetime, timedelta

import requests

import mysql_dealer
from Serives import btcblock
from Serives import  transactionreturn, btcblock, zcash_blockreturn
from Serives import btctransaction
from flask import request
from flask import current_app
import math

from Serives.btcaddrtag import get_my_tags
from Serives.transactionreturn import  btc_home_trans_return
from blueprint.btc import news_return
from dao.mybtc import cluster
from utils import ts2t
import json
from config import config
from log import log
import time

log = log.init_logger(config.log_filepath)

###code by tiancy-----------
def btc_home_show():
    r = requests.get("https://api.blockchair.com/bitcoin/stats")
    re = json.loads(r.text)
    result = btcblock.btc_home_get_blocks(5,0)
    blocks = result['blocks']
    # ans = btctransaction.get_transaction(btctransaction.AllTranses(5, 0, order='desc'))
    context2, latestTransList = btc_home_trans_return(5, 0)
    count, list = get_my_tags(0, 5)
    addr_list, single_list, repeat_list = cluster(list, 'addr')
    news=news_return()
    context={
        "blocks":blocks,
        "trans_sum":re['data']['transactions'],
        "marketCap":re['data']['market_cap_usd'],
        "difficulty": re['data']['difficulty'],
        "tags":single_list,
        "news":news
    }
    return latestTransList,context
###code by tiancy--------------
def block_return(perpage,start):
    dateMap = {

        "0": "今天",
        "1": "本周",
        "2": "本月",
        "3": "今年",
        "4": "全部"
    }

    order_rule = ''
    order = request.args.get('order', default='0')  # 默认值为今天
    order_rule = dateMap[order]
    del dateMap[order]
    result = btcblock.get_blocks(perpage,start)
    total = result['total']
    blocks = result['blocks']
    took = result['took']
    start = time.time()
    log.info("区块总数为"+str(total))
    end = time.time()
    print(end-start)
    pages = math.ceil(float(total) / perpage)
    context = {
        "order_rule": order_rule,
        "date_map": dateMap,
        "pages": pages,
        "block_total": total,
        "took": took,
        "page_title": '区块'
    }
    return blocks, context


def block_search(perpage,start,rule,starttime,endtime):
    result = btcblock.get_searchblock(perpage,start,rule,starttime,endtime)
    total = result['total']
    blocks = result['blocks']
    took = result['took']
    start = time.time()
    log.info("区块总数为"+str(total))
    end = time.time()
    print(end-start)
    pages = math.ceil(float(total) / perpage)
    context = {
        "pages": pages,
        "block_total": total,
        "took": took,
        "page_title": '区块'
    }
    return blocks, context


def blockdetail_return(hash,start,size,block_flag=False):
    block_total = btcblock.get_block_total()  ##区块总数
    blockdetail = btcblock.get_block_detail(hash,0,block_flag)
    blocktrans = btcblock.get_detail(hash,start,size)
    if blockdetail:
        blockdetail['time1'] = datetime.utcfromtimestamp(blockdetail['time'])
        blockdetail['time_bj'] = blockdetail['time1'] + timedelta(hours=8)
        # blockdetail['time'] = ts2t(blockdetail['time'])
        blockheight = blockdetail["height"]
        blockdetail['confirm_num'] = block_total - 1 - blockheight
        log.info("区块总数:"+str(block_total))
        context = {
            "blockInfo": blockdetail,
            "col_names": current_app.config['BLOCK_DETAIL_TB_COL_NAME'],
            "page_id": str(blockheight),
            "total": blockdetail["trans_num"],
            "page_title": '区块'
        }
        return context,blocktrans
    return {},blocktrans