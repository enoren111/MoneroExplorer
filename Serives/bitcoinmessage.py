# coding:utf-8
import re
from config import config
import math
import time
from config.config import log_filepath
from dao.getbitcoinmessage import get_btcmessgae_by_search, get_long_btcmessage, get_short_btcmessage, \
    get_transaction_detail, get_blocktime, get_maxmin_height, get_long_btcmessage_new, get_short_btcmessage_new, \
    get_by_hash
from log import log


log = log.init_logger(config.log_filepath)


def get_by_newsearch(perPage, start,string,order):

    # 当长度较短时使用直接查询 可以返回与长查询同样的数据结构
    if len(string)>2:
        result=get_long_btcmessage(perPage,start,string,order)
    else:
        result=get_short_btcmessage(perPage,start,string,order)
    try:
        took_time =result['took']
        list = result['hits']['hits']
        total = result['hits']['total']['value']
        # total = result['hits']['total']['value']

        pages = math.ceil(float(total) / perPage)
        context = {
            "total_num": total,
            "page_num": pages,
            "target_str": string,
            "time":took_time,
            "page_title": "夹带信息"
        }
        for tx in list:
            height=tx['_source']['height']
            tx_time,blockhash=get_trans_time(height)
            # 时间
            tx.update(tx_time=tx_time)

            # 区块对应hash
            tx.update(blockhash=blockhash)

            # 语言列表
            lanuagelist=init_lanuage(tx)
            tx.update(lanuagelist=lanuagelist)
    except Exception as e:
        # result有问题，则返回空数据
        log.error("es错误"+str(e))
        list={}
        total=0
        pages=0
        context={
            "total_num": total,
            "page_num": pages,
            "target_str": string,
            "page_title": "夹带信息"
        }
    return list,context


def get_by_newsearch_new(perPage, start, string,order,starttime,endtime,lanuage):
    # 首先将时间字符串转变为高度范围：
    if starttime:
        realstarttime = time.mktime(time.strptime(starttime, '%Y-%m-%d %H:%M:%S'))
    else:
        realstarttime = 1230998400 ##比特币诞生的时间
    if endtime:
        realendtime = time.mktime(time.strptime(endtime,'%Y-%m-%d %H:%M:%S'))
    else:
        realendtime = time.time()

    startheight,endheight=trans_time_to_height(realstarttime,realendtime)

    # 更改语言
    if lanuage:
        if lanuage=="english" :
            lan="en"
        else:
            lan="zh"
    else:
        lan="en"



    # 当长度较短时使用直接查询 可以返回与长查询同样的数据结构
    if len(string) > 2:
        result = get_long_btcmessage_new(perPage, start, string, order,startheight,endheight,lan)
    else:
        result = get_short_btcmessage_new(perPage, start, string, order,startheight,endheight,lan)
    try:
        took_time = result['took']
        list = result['hits']['hits']
        total = result['hits']['total']['value']
        # total = result['hits']['total']['value']
        pages = math.ceil(float(total) / perPage)
        context = {
            "total_num": total,
            "page_num": pages,
            "target_str": string,
            "time": took_time,
            "lanuage":lanuage,
            "starttime":starttime,
            "endtime":endtime,
            "sorttype":order,
            "page_title": "夹带信息"
        }
        for tx in list:
            height = tx['_source']['height']
            tx_time,blockhash=get_trans_time(height)
            # 时间
            tx.update(tx_time=tx_time)
            # 区块对应hash
            tx.update(blockhash=blockhash)
            # 语言列表
            lanuagelist = init_lanuage(tx)
            tx.update(lanuagelist=lanuagelist)
    except Exception as e:
        # result有问题，则返回空数据
        log.error("es错误" + str(e))
        list = {}
        total = 0
        pages = 0
        context = {
            "total_num": total,
            "page_num": pages,
            "target_str": string,
            "page_title": "夹带信息"
        }
    return list, context

# 获得交易所在区块的高度
def get_trans_height(tx_hash):
    result=get_transaction_detail(tx_hash)
    if len(result)!=0:
        height=result['_source']['blockheight']
    else:
        height=0
    return height

#获得交易的时间戳
def get_trans_time(height):
#     先获取高度 再通过高度获取区块的时间戳
    result=get_blocktime(height)

    temptime=result['hits']['hits'][0]['_source']['time']
    timeArray = time.localtime(int(temptime))
    otherStyleTime = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)

    hash=result['hits']['hits'][0]['_id']
    return otherStyleTime,hash

def init_lanuage(tx):
    # 先获得语言列表 在转化为中文列表 在去重
    lanuagelist=[]
    if "input" in tx['_source']:
        for input in tx['_source']['input']:
            lanuagelist.append(input["language"])

    if "output" in tx['_source']:
        for output in tx['_source']['output']:
            lanuagelist.append(output["language"])
    temp_list=[]
    for temp in lanuagelist:
        if temp in LANUAGE_ZH:
            last= LANUAGE_ZH[temp]
        else:
            last="其他语言"
        temp_list.append(last)

    last_list = []
    for id in temp_list:
        if id not in last_list:
            last_list.append(id)
    return last_list

# 语言对照表
LANUAGE_ZH={
    "zh":"中文",
    "en":"英文",
    "ja":"日文",
    "de":"德文",
    "fr":"法文"
}
# 将时间范围转化为高度范围
def trans_time_to_height(starttime,endtime):
    result=get_maxmin_height(starttime,endtime)
    try:
        maxheight = int(result['aggregations']['max_height']['value'])
        minheight = int(result['aggregations']['min_height']['value'])

    except Exception as e:
        log.error("get max min height worng "+str(e))
        maxheight=1000000
        minheight=0
    return minheight,maxheight


# 判断一个交易是否是夹带信息交易

def is_carry_tx(hash):
    result=get_by_hash(hash)
    if result['found']==False:
        return False,result
    else:
        return True,result['_source']



