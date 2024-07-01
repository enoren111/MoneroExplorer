import requests

from Serives import btcblock, zcashblock, transactionreturn, zcash_transactionreturn
from Serives import btctransaction
from flask import request
from flask import current_app
import math
from utils import ts2t
import json
from config import config
from log import log
import time

log = log.init_logger(config.log_filepath)


def zcash_home_show():
    r = requests.get("https://api.blockchair.com/zcash/stats")
    re = json.loads(r.text)
    result = zcashblock.zcash_home_get_blocks(5,0)
    blocks = result['blocks']
    context2, zcash_latestTransList = zcash_transactionreturn.zcash_home_trans_return(5, 0)
    context={
        "blocks":blocks,
        "marketCap": re['data']['market_cap_usd'],
        "trans_sum": re['data']['transactions'],
        "difficulty":re['data']['difficulty']
    }
    return zcash_latestTransList,context
def zcash_block_return(perpage,start):
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
    result = zcashblock.zcash_get_blocks(perpage,start)
    total = result['total']
    blocks = result['blocks']
    took = result['took']
    start = time.time()
    log.info("zcash区块总数为"+str(total))
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


def zcash_blockdetail_return(hash,start,size,block_flag=False):
    block_total = zcashblock.zcash_get_block_total()  ##区块总数
    blockdetail = zcashblock.zcash_get_block_detail(hash,0,block_flag)
    blocktrans = zcashblock.zcash_get_detail(hash,start,size)
    if blockdetail:
        blockdetail['time'] = ts2t(blockdetail['time'])
        blockdetail['confirm_num'] = blockdetail["confirmations"]
        log.info("区块总数:"+str(block_total))
        context = {
            "blockInfo": blockdetail,
            "col_names": current_app.config['BLOCK_DETAIL_TB_COL_NAME'],
            "page_id": str(blockdetail["hash"]),
            "total": blockdetail["trans_num"],
            "page_title": '区块'
        }
        return context,blocktrans
    return {},blocktrans