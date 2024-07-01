from dao import datainterchange
from utils import visit_mode_check
import json
from config import config
from log import log
from bee_var import block_num_offline, block_offline_file, trans_offline_flie, btc_tag

log = log.init_logger(config.log_filepath)


def DataValidation_block(body):  ##验证不同的模式返回不同的数据  development，online offline
    result = datainterchange.search_block(body)
    log.info("search block data:" + json.dumps(len(result)))
    result = visit_mode_check(result, block_offline_file)
    return result





def XMR_DataValidation_block(body):  ##验证不同的模式返回不同的数据  development，online offline
    # print("...........", datainterchange.xmr_search_block(body))

    result = datainterchange.xmr_search_block(body)
    log.info("search block data:" + json.dumps(len(result)))
    result = visit_mode_check(result, block_offline_file)
    return result


# code by tiancy for zcash test-----
def Zcash_DataValidation_block(body):
    result = datainterchange.zcash_search_block(body)
    log.info("search block data:" + json.dumps(len(result)))
    result = visit_mode_check(result, block_offline_file)
    return result


def Zcash_DataValidation_block_Trans_num(body):
    result = datainterchange.zcash_search_block_trans_num(body)
    log.info("search block data:" + json.dumps(len(result)))
    result = visit_mode_check(result, block_offline_file)
    return result


# code by tiancy------


def DataValidation_transaction(body):  ##验证不同的模式返回不同的数据  development，online offline
    result = datainterchange.search_transaction(body)
    log.info("search transaction data:" + json.dumps(len(result)))
    result = visit_mode_check(result, trans_offline_flie)
    return result


def Zcash_DataValidation_transaction(body):  ##验证不同的模式返回不同的数据  development，online offline
    result = datainterchange.zcash_search_transaction(body)
    log.info("search transaction data:" + json.dumps(len(result)))
    result = visit_mode_check(result, trans_offline_flie)
    return result


def xmr_DataValidation_transaction(body):  ##验证不同的模式返回不同的数据  development，online offline
    result = datainterchange.xmr_search_transaction(body)
    log.info("search transaction data:" + json.dumps(len(result)))
    result = visit_mode_check(result, trans_offline_flie)
    return result


def DataValidation_blocknums(body):  ##验证不同的模式返回不同的数据  development，online offline
    result = datainterchange.search_block(body)["hits"]["total"]['value']
    log.info("search block data:" + str(result))
    result = visit_mode_check(result, block_num_offline)
    return result


def Zcash_DataValidation_blocknums(body):  ##验证不同的模式返回不同的数据  development，online offline
    result = datainterchange.zcash_search_block(body)["hits"]["total"]['value']
    log.info("search block data:" + str(result))
    result = visit_mode_check(result, block_num_offline)
    return result


def xmr_DataValidation_blocknums(body):
    result = datainterchange.xmr_search_block(body)["hits"]["total"]['value']
    log.info("search block data:" + str(result))
    result = visit_mode_check(result, block_num_offline)
    return result


def DataValidation_transactionnums(body):
    result = datainterchange.search_transaction(body)["hits"]["total"]['value']
    log.info("search block_transaction data:" + str(result))
    result = visit_mode_check(result, block_num_offline)
    return result


def DataValidation_btctag(body):
    result = datainterchange.search_tag(body)
    log.info("search block_transaction data:" + str(result))
    result = visit_mode_check(result, btc_tag)
    return result


# syc------------------------


# syc Search Tag
def DataValidation_mybtctag(body, flag):
    result = datainterchange.search_my_tag(body, flag)
    log.info("search my_btc_tag data:" + str(result))
    result = visit_mode_check(result, btc_tag)
    return result


# syc tag cluster
def DataValidation_tag_cluster(body):
    result = datainterchange.search_new_tags(body)
    log.info("search cluster_tag data:" + str(result))
    result = visit_mode_check(result, btc_tag)
    return result


# syc darknet_clash
def DataValidation_darknet_clash(body):
    result = datainterchange.search_darknet_clash(body)
    log.info("search darknet_clash data:" + str(result))
    result = visit_mode_check(result, btc_tag)
    return result


# Syc cluster_search
def DataValidation_cluster_search(body):
    result = datainterchange.search_tag_cluster(body)
    log.info("search my_btc_tag data:" + str(result))
    result = visit_mode_check(result, btc_tag)
    return result


# Syc Search Mix
def DataValidation_btcmix(body):
    result = datainterchange.search_my_mix(body)
    log.info("search btc_mixing data:" + str(result))
    result = visit_mode_check(result, btc_tag)
    return result


# SYC Big Transactions
def DataValidation_mybtctrans(body):
    result = datainterchange.search_my_trans(body)
    log.info("search my_btc_transaction data:" + str(result))
    result = visit_mode_check(result, trans_offline_flie)
    return result
