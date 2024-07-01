from Model import dataValidation
import json
from Serives.bitcoinmessage import is_carry_tx
from config import config
from log import log
from bee_var import VALUE_ACC
from utils import ts2t
log = log.init_logger(config.log_filepath)
from dao import datainterchange
import time


class BlockDetail():  # 区块交易查询命令
    def __init__(self,size=10,start=0,block_id=7000000):
        self.size = size
        self.start = start
        self.block_id = block_id

    def sbody(self):
        # 查询区块全部交易或按分页查询
        body = {
            "query":{
                "term":{
                    "blockheight":self.block_id
                }
            },
            "from": self.start,
            "track_total_hits": True
        }
        return body

        # 按分页查
    def deal_results(self,hit_data):
        # print(json.dumps(hit_data))
        return hit_data


class ZcashAllTranses():
    def __init__(self,size=20,start=0,order="desc"):   # asc
        self.size = size
        self.start = start
        self.order = order

    def sbody(self):
            return {
                "query": {
                    "match_all": {}
                },
                "size": self.size,
                "from": self.start,
                "sort": {"height": {"order": self.order}},
                "track_total_hits": True
                # "sort": {"time": {"order": order}}  # 性能问题
            }

    def deal_results(self, hit_data):
        return hit_data


def zcash_get_transaction(s_class):  # 处理返回的交易数据量
    body = s_class.sbody()
    result = dataValidation.Zcash_DataValidation_transaction(body)
    took = result['took']
    total = result['hits']['total']['value']
    log.info("查询时间为" + str(took))
    log.info("总交易量为" + str(total))
    if s_class.size!=None:
        result = s_class.deal_results(result['hits']['hits'][0:s_class.size])
    else:
        result = s_class.deal_results(result['hits']['hits'])
    return {"took":took,"total":total,"result":result}


def zcash_get_transaction_byhash(hash):  ##获取交易详情
    result = datainterchange.zcash_get_transaction(hash)
    log.info("交易信息")
    log.info("查询交易信息成功"+str(hash))
    vin = []      ##处理交易信息的输入和输出保存为[{"address":"value"},]
    vout = []
    vin_times = len(result["_source"]["vin"])  ##交易的输入个数
    vout_times = len(result["_source"]["vout"]) ##交易的输出个数
    result["vin_times"] = vin_times
    result["vout_times"] = vout_times
    result["value_shield"] = 0;
    value = 0
    pub_new=0
    pub_old=0
    for i in result["_source"]["vout"]:
        value+=i["value"]
    if vin_times ==0:

        result['inputvalue'] = 'shielded'
        address_in="SHIELDED"
        vin.append([address_in, '?'])
        if vout_times==0:
            result['trans_type'] = 'z-to-z'
            address_out = "SHIELDED"
            result['outputvalue'] = 'shielded'
            for i in result['_source']["vjoinsplit"]:
                pub_new += i["vpub_new"]
            for i in result['_source']["vjoinsplit"]:
                pub_old += i["vpub_old"]
            result['fee'] = '{:.8f}'.format(pub_new-pub_old)
            vout.append([address_out, '?'])
        else:
            for i in result['_source']["vjoinsplit"]:
                pub_new+=i["vpub_new"]
            result['fee'] = '{:.8f}'.format(pub_new - value)
            result['outputvalue'] = value
            result['trans_type'] = 'z-to-t'
            for item in result['_source']['vout']:
                address_out = item['scriptPubKey']['addresses'][0]
                asm = item["scriptPubKey"]["asm"]
                vout.append([address_out, item['value'], asm])
    elif "coinbase" in result["_source"]["vin"][0].keys():
        result['trans_type'] = 'Coinbase'
        result['inputvalue'] =  'miner reward'
        result['fee']=0
        address = "COINBASE"
        asm = result['_source']['vin'][0]['coinbase']
        vin.append([address, value, asm])
        if vout_times==0:
            address_out = "SHIELDED"
            result['outputvalue'] = 'shielded'
            vout.append([address_out, '?'])
        else:
            result['outputvalue'] = value
            for item in result['_source']['vout']:
                address_out = item['scriptPubKey']['addresses'][0]
                asm=item["scriptPubKey"]["asm"]
                vout.append([address_out, item['value'],asm])
    elif vout_times==0:
        for i in result["_source"]["vin"]:
            value += i["value"]
        result['inputvalue']=value
        result['outputvalue'] = 'shielded'
        result['trans_type'] = 't-to-z'
        address_out="SHIELDED"
        for i in result['_source']["vjoinsplit"]:
            pub_old += i["vpub_old"]
        result['fee'] = '{:.8f}'.format(result['inputvalue'] - pub_old)
        vout.append([address_out, '?'])
        for item in result['_source']['vin']:
            if "address" in item.keys():
                address_in = item['address'][0]
            else:
                address_in='unkonwn_for_now'
            vin.append([address_in, item['value']])
    else:
        result['trans_type'] = 'Transparent Transfer'
        result['outputvalue'] = value
        value=0
        for i in result["_source"]["vin"]:
            value += i["value"]
        result['inputvalue'] = value
        result['fee']='{:.8f}'.format(result['inputvalue']-result['outputvalue'])
        for item in result['_source']['vout']:
            address_out = item['scriptPubKey']['addresses'][0]
            asm = item["scriptPubKey"]["asm"]
            vout.append([address_out, '{:.8f}'.format(item['value']),asm])
        for item in result['_source']['vin']:
            address_in = item['address'][0]
            vin.append([address_in, item['value']])
    result["_time"] = ts2t(result["_source"]["blocktime"])
    # for item in result["_source"]["vin"]:
    #     if "coinbase" in item.keys():
    #         address = "COINBASE"
    #         value=result["_source"]['outputvalue'] / (10 ** 8)
    #         asm=item["coinbase"]
    #     else:
    #         address = item["addresses"]
    #         value = item["value"] / (10 ** 8)
    #         asm=item["scriptSig"]["asm"]
    #     vin.append([address,value,asm])
    # for item in result["_source"]["vout"]:
    #     value = item["value"]
    #     address = item["scriptPubKey"]["addresses"]
    #     asm=item["scriptPubKey"]["asm"]
    #     type=item["scriptPubKey"]["type"]
    #     vout.append([address,value,asm,type])
    result["vin"] = vin
    result["vout"] = vout
    # result["status"] = "成功"

    # 判断交易是否是夹带信息
    Flag,Carry_part=is_carry_tx(hash)
    if Flag==True:
        result["iscarry"]=True
        result["carrypart"]=Carry_part
    else:
        result["iscarry"] = False
        result["carrypart"] = Carry_part
    return result


def transaction_ajax(body):
    log.info("++++++++++++++++++开始交易查询+++++++++++++++++")
    result = dataValidation.DataValidation_transaction(body)
    if result:
        total = result["hits"]["total"]['value']
        log.info("符合条件的交易为"+str(total))
        if total==0:
            return {}
        took = result['took']
        result = result['hits']['hits']
        for item in result:
            vin_times = len(item["_source"]["vin"])  ##交易的输入个数
            vout_times = len(item["_source"]["vout"])  ##交易的输出个数
            item["vin_times"] = vin_times
            item["vout_times"] = vout_times
            if item["_source"]["inputvalue"]==0:
                item["value"] = item["_source"]["outputvalue"]
            else:
                item["value"] = item["_source"]["inputvalue"]
            if "dayprice" in item["_source"].keys():
                item["usdvalue"] = round(item["value"] * item["_source"]["dayprice"] / 100000000, 6)
            else:
                item["usdvalue"] = 0
            item["value"]=round(item["value"] / 100000000, 6)
        return {"took":took,"total":total,"result":result}
    else:
        return {}