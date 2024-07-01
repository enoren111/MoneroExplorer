import mysql_dealer
from bee_var import btcblock_index, btctransaction_index, block_raw, btctransaction_newindex, btctag_index, \
    mybtctag_index, mybtcmix_index, mybtctrans_index, btc_tag_cluster, darknet_clash, btc_cluster_search, \
    btctagclu_index, btctagseed_index, btctagall_index
# from app import es
from log import log
from config import config

log = log.init_logger(config.log_filepath)
from bee_var import ESManager
es = ESManager(config.es_ip,config.es_port,config.time_out)
es.tryagain_instance()
es = es.instance
# print("es.info::::::::::::::",es.info)

def get_block(idid):  ##get区块信息
    try:
        result = es.get(index=btcblock_index, doc_type=block_raw, id=idid)
    except Exception as e:
        log.error(e)
        result = {}
    return result


def zcash_get_block(idid):  ##get区块信息
    try:
        result = es.get(index="zcash_block", doc_type=block_raw, id=idid)
    except Exception as e:
        log.error(e)
        result = {}
    return result

def xmr_get_block(idid):  ##get区块信息
    try:
        result = es.get(index="monero_block", doc_type=block_raw, id=idid)
    except Exception as e:
        log.error(e)
        result = {}
    return result

def search_block(body):  ##search查询区块信息
    try:
        result = es.search(index=btcblock_index, body=body)
    except Exception as e:
        log.error(e)
        result = {}
    return result


# code by tiancy-----
def zcash_search_block(body):
    try:
        result = es.search(index="zcash_block", body=body)
    except Exception as e:
        log.error(e)
        result = {}
    return result


def xmr_search_block(body):
    try:
        result = es.search(index="monero_block", body=body)
    except Exception as e:
        log.error(e)
        result = {}
    return result




def zcash_search_block_trans_num(body):
    try:
        result = es.search(index="zcash_block", body=body)['hits']['hits'][0]['_source']['tx']
    except Exception as e:
        log.error(e)
        result = {}
    return result


# code by tiancy------

def getTxbyHash(hash):
    body = {
        "query": {
            "term": {
                "txid": {
                    "value": hash
                }
            }
        }
    }
    result = es.search(index="btc_tx_new", body=body)
    res = result['hits']['hits'][0]['_source']
    return res


def search_transaction(body):  ##查询交易信息
    try:
        result = es.search(index=btctransaction_index, body=body, request_timeout=600)
    except Exception as e:
        log.error(e)
        result = {}
    return result


def zcash_search_transaction(body):  ##查询交易信息
    try:
        result = es.search(index="zcash_tx", body=body, request_timeout=600)
    except Exception as e:
        log.error(e)
        result = {}
    return result




def xmr_search_transaction(body):  ##查询交易信息
    try:
        result = es.search(index="monero_tx", body=body, request_timeout=600)
        # print(result)
    except Exception as e:
        log.error(e)
        result = {}
    return result

def get_transaction(idid):  ##查询交易信息
    try:
        result = es.get(index=btctransaction_index, doc_type=block_raw, id=idid)
        # result = es.get(index=btctransaction_newindex, doc_type='_doc', id=idid)

        print("btc transaction result:  ",result)
    except Exception as e:
        log.error(e)
        result = {}
    return result


def zcash_get_transaction(idid):  ##查询交易信息
    try:
        result = es.get(index="zcash_tx", id=idid, request_timeout=600)
        # result = es.get(index=btctransaction_newindex, doc_type='_doc', id=idid)
    except Exception as e:
        log.error(e)
        result = {}
    return result

def xmr_get_transaction(idid):  ##查询交易信息

    try:
        result = es.get(index="monero_tx",doc_type=block_raw, id=idid, request_timeout=600)
        print("monero result ________________________________{r}".format(r=result))

    except Exception as e:

        log.error(e)
        result = {}
    return result

def search_tag(body):  ##查询标签信息
    try:
        result = es.search(index=btctag_index, body=body, request_timeout=600)
    except Exception as e:
        log.error(e)
        result = {}
    return result


# syc--------------------

# Syc Search tag
def search_my_tag(body, flag):
    result = dict()
    try:
        if (flag == ''):
            result = es.search(index=mybtctag_index, body=body)
        if (flag == 'seed'):
            result = es.search(index=btctagseed_index, body=body)
        if (flag == 'clu'):
            result = es.search(index=btctagclu_index, body=body)
        if (flag == 'all'):
            result = es.search(index=btctagall_index, body=body)
    except Exception as e:
        log.error(e)
        result = {}
    return result


# SYC tag cluster
def search_new_tags(body):
    try:
        result = es.search(index=btc_tag_cluster, body=body)
    except Exception as e:
        log.error(e)
        result = {}
    return result


# SYC cluster search
def search_tag_cluster(body):
    try:
        result = es.search(index=btc_cluster_search, body=body)
    except Exception as e:
        log.error(e)
        result = {}
    return result


# SYC darknet clash
def search_darknet_clash(body):
    try:
        result = es.search(index=darknet_clash, body=body)
    except Exception as e:
        log.error(e)
        result = {}
    return result


# Syc Search Mix
def search_my_mix(body):
    try:
        result = es.search(index=mybtcmix_index, body=body)
    except Exception as e:
        log.error(e)
        result = {}
    return result


# mybtc search transactions
def search_my_trans(body):
    try:
        result = es.search(index=mybtctrans_index, body=body)
    except Exception as e:
        log.error(e)
        result = {}
    return result
