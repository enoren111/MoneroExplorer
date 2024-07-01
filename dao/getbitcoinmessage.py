# coding:utf-8
from bee_var import btc_carrymessage_index, carrymessage_type
from log import log
from config import config
# from app import es
from log import log
from config import config
from elasticsearch import Elasticsearch
log = log.init_logger(config.log_filepath)
# es.tryagain_instance()
# es = es.instance
# 比特币夹带信息方面的配置

# 本地es配置

# es = Elasticsearch(host='192.168.126.176', port=9200)
# index='bitcoin_message'
# doc_type='raw'


def get_transaction_detail(tx_hash):
    try:
        result = es.get(index=btc_carrymessage_index, id=tx_hash, doc_type=carrymessage_type)
    except Exception as e:
        log.error("es错误"+str(e))
        result ={}
    return result

# 通过搜索hash的方式获得夹带信息
def get_by_hash(tx_hash):
    try:
        result = es.get(index=btc_carrymessage_index, id=tx_hash, doc_type=carrymessage_type)
    except Exception as e:
        # log.error("es错误"+str(e))
        result ={"found": False}
    return result


# 查询  长字符串
def get_long_btcmessage(perPage,start,string,order):
    body=body_get_long_str_btcmessage_by_page(perPage,start,string,order)
    try:
        result = es.search(index=btc_carrymessage_index, doc_type=carrymessage_type,body=body)
    except Exception as e:
        log.error("es错误"+str(e))
        result ={}
    return result
#
# 查询 短字符串
def get_short_btcmessage(perPage,start,string,order):
    body=body_get_short_str_btcmessage_by_page(perPage,start,string,order)
    try:
        result = es.search(index=btc_carrymessage_index, doc_type=carrymessage_type, body=body)
    except Exception as e:
        log.error("es错误"+str(e))
        result ={}
    return result



# 分页的body:

# 长字符串
def body_get_long_str_btcmessage_by_page(size,start,string,order):
    body={
        "query": {
            "multi_match": {
                "query": string,
                "fields": ["input.string", "output.string"],
                "fuzziness": "AUTO"
            }
        },
        "highlight": {
            "fields": {"*": {}},
            "pre_tags": ["<span style=\"color: red\">"],
            "post_tags": ["</span>"]
        },
        "size": size,
        "from": start,
        "sort":{
            "height":{
                "order":order
            }
        }
    }
    return body

#
def body_get_short_str_btcmessage_by_page(size,start,string,order):
    body = {
        "query": {
            "multi_match": {
                "query": string,
                "fields": ["input.string", "output.string"]
            }
        },
        "highlight": {
            "fields": {"*": {}},
            "pre_tags": ["<span style=\"color: red\">"],
            "post_tags": ["</span>"]
        },
        "size": size,
        "from": start,
        "sort":{
            "height":{
                "order":order
            }
        }
    }
    return body
# 输入单词匹配相关信息
def body_get_btcmessage_by_str(string):
    body = {
        "query": {
            "multi_match": {
                "query": string,
                "fields": ["input.string", "output.string"],
                "fuzziness": "AUTO"
            }
        },
        "highlight": {
            "fields": {"*": {}},
            "pre_tags": ["<span style=\"color: red\">"],
            "post_tags": ["</span>"]
        }
    }
    return body

def get_btcmessgae_by_search(string):
    body=body_get_btcmessage_by_str(string)
    try:
        result = es.search(index=btc_carrymessage_index, doc_type=carrymessage_type, body=body)
    except Exception as e:
        log.error("es错误"+str(e))
        result ={}
    return result

def body_get_blocktime(height):
    body={
        "query": {
            "term": {
                "height": height
            }
        }
    }
    return body

def get_blocktime(height):
    body=body_get_blocktime(height)
    try:
        result = es.search(index="bitcoin_block", doc_type=carrymessage_type, body=body)
    except Exception as e:
        log.error("es错误"+str(e))
        result ={}
    return result


def get_maxmin_height(starttime,endtime):
    body = {
        "query": {"range": {"time": {
            "gte": starttime,
            "lte": endtime
        }}},
        "aggs": {
            "max_height": {"max": {"field": "height"}},
            "min_height": {"min": {"field": "height"}}
        }
    }
    try:
        result = es.search(index="bitcoin_block", doc_type=carrymessage_type, body=body)
    except Exception as e:
        log.error("es错误"+str(e))
        result ={}
    return result


def get_long_btcmessage_new(perPage, start, string, order,startheight,endheight,lanuage):
    body={
        "query": {
            "bool": {
                "must": [
                    {"multi_match": {
                        "query": string,
                        "fields": ["input.string", "output.string"],
                        "fuzziness": "AUTO"}},
                    {"bool": {
                        "should": [
                            {"term": {
                                "input.language": {
                                    "value": lanuage
                                }
                            }},
                            {"term": {
                                "output.language": {
                                    "value": lanuage
                                }
                            }}
                        ]
                    }}
                ],
                "filter": {"range": {"height": {"gte": startheight,"lte": endheight}}}}},
        "highlight": {"fields": {"input.string": {}, "output.string": {}},
                      "pre_tags": ["<span style=\"color: red\">"],
                      "post_tags": ["</span>"]
                      },
        "size": perPage,
        "from": start,
        "sort": [{"height": {"order": order}}]
    }
    try:
        result = es.search(index=btc_carrymessage_index, doc_type=carrymessage_type, body=body)
    except Exception as e:
        log.error("es错误"+str(e))
        result ={}
    return result


def get_short_btcmessage_new(perPage, start, string, order,startheight,endheight,lanuage):
    body={
        "query": {
            "bool": {
                "must": [
                    {"multi_match": {
                        "query": string,
                        "fields": ["input.string", "output.string"]
                        }},
                    {"bool": {
                        "should": [
                            {"term": {
                                "input.language": {
                                    "value": lanuage
                                }
                            }},
                            {"term": {
                                "output.language": {
                                    "value": lanuage
                                }
                            }}
                        ]
                    }}
                ],
                "filter": {"range": {"height": {"gte": startheight,"lte": endheight}}}}},
        "highlight": {"fields": {"input.string": {}, "output.string": {}},
                      "pre_tags": ["<span style=\"color: red\">"],
                      "post_tags": ["</span>"]
                      },
        "size": perPage,
        "from": start,
        "sort": [{"height": {"order": order}}]
    }
    try:
        result = es.search(index=btc_carrymessage_index, doc_type=carrymessage_type, body=body)
    except Exception as e:
        log.error("es错误"+str(e))
        result ={}
    return result
