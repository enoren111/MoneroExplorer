from dao.ZcashAddressData import zcash_getAddressTX, zcash_getAddressRecv, zcash_getAddressSent
from utils import ts2t


def zcash_handleAddressTx(address,page):
    result=zcash_getAddressTX(address,page)
    try:
        result2=zcash_getAddressRecv(address)
        recv='{:.8f}'.format(result2['aggregations']['sum']['value_count']['value'])
        recv_num=result2['hits']['total']['value']
    except Exception as e:
        print(e.args)
        recv="error"
        recv_num="error"
    try:
        result3=zcash_getAddressSent(address)
        sent = '{:.8f}'.format(result3['aggregations']['sum']['value_count']['value'])
        sent_num=result3['hits']['total']['value']
    except Exception as e:
        print(e.args)
        sent="error"
        sent_num="error"
    if recv=="error" or sent=="error":
        balance="error"
    else:
        balance='{:.8f}'.format(result2['aggregations']['sum']['value_count']['value']-result3['aggregations']['sum']['value_count']['value'])
    txs = result['hits']['hits']
    total = int(result['hits']['total']['value'])
    tx_list = []
    if len(txs)>0:
        first_seen=ts2t(txs[0]['_source']['blocktime'])
    else:
        first_seen=""
    for tx in txs:
        single_tx = dict()
        tx_source = tx['_source']
        vin = []  ##处理交易信息的输入和输出保存为[{"address":"value"},]
        vout = []
        vin_times = len(tx_source["vin"])  ##交易的输入个数
        vout_times = len(tx_source["vout"])  ##交易的输出个数
        single_tx["vin_times"] = vin_times
        single_tx["vout_times"] = vout_times
        single_tx["value_shield"] = 0
        value = 0
        pub_new = 0
        pub_old = 0
        for i in tx_source["vout"]:
            value += i["value"]
        if vin_times == 0:
            single_tx['inputvalue'] = 'shielded'
            address_in = "SHIELDED"
            vin.append([address_in, '?'])
            if vout_times == 0:
                address_out = "SHIELDED"
                single_tx['outputvalue'] = 'shielded'
                for i in tx_source["vjoinsplit"]:
                    pub_new += i["vpub_new"]
                for i in tx_source["vjoinsplit"]:
                    pub_old += i["vpub_old"]
                single_tx['fee'] = '{:.8f}'.format(pub_new - pub_old)
                vout.append([address_out, '?'])
            else:
                for i in tx_source["vjoinsplit"]:
                    pub_new += i["vpub_new"]
                single_tx['fee'] = '{:.8f}'.format(pub_new - value)
                single_tx['outputvalue'] = value
                for item in tx_source['vout']:
                    address_out = item['scriptPubKey']['addresses'][0]
                    asm = item["scriptPubKey"]["asm"]
                    vout.append([address_out, item['value'], asm])
        elif "coinbase" in tx_source["vin"][0].keys():
            single_tx['trans_type'] = 'Coinbase'
            single_tx['inputvalue'] = 'miner reward'
            single_tx['fee'] = 0
            address = "COINBASE"
            asm = tx_source['vin'][0]['coinbase']
            vin.append([address, value, asm])
            if vout_times == 0:
                address_out = "SHIELDED"
                single_tx['outputvalue'] = 'shielded'
                vout.append([address_out, '?'])
            else:
                single_tx['outputvalue'] = value
                for item in tx_source['vout']:
                    address_out = item['scriptPubKey']['addresses'][0]
                    asm = item["scriptPubKey"]["asm"]
                    vout.append([address_out, item['value'], asm])
        elif vout_times == 0:
            single_tx['trans_type'] = 'Shielded Transfer'
            for i in tx_source["vin"]:
                value += i["value"]
            single_tx['inputvalue'] = value
            single_tx['outputvalue'] = 'shielded'
            address_out = "SHIELDED"
            for i in tx_source["vjoinsplit"]:
                pub_old += i["vpub_old"]
            single_tx['fee'] = '{:.8f}'.format(single_tx['inputvalue'] - pub_old)
            vout.append([address_out, '?'])
            for item in tx_source['vin']:
                address_in = item['address']
                vin.append([address_in, item['value']])
        else:
            single_tx['trans_type'] = 'Transparent Transfer'
            single_tx['outputvalue'] = value
            value = 0
            for i in tx_source["vin"]:
                value += i["value"]
            single_tx['inputvalue'] = value
            single_tx['fee'] = '{:.8f}'.format(single_tx['inputvalue'] - single_tx['outputvalue'])
            for item in tx_source['vout']:
                address_out = item['scriptPubKey']['addresses'][0]
                asm = item["scriptPubKey"]["asm"]
                vout.append([address_out, '{:.8f}'.format(item['value']), asm])
            for item in tx_source['vin']:
                address_in = item['address']
                vin.append([address_in, item['value']])
        # single_tx['inputvalue']=tx_source['inputvalue']/10**8
        # single_tx['outputvalue'] = tx_source['outputvalue'] / 10 ** 8
        # single_tx['fee'] = tx_source['fee'] / 10 ** 8
        # single_tx['hash'] = tx_source['hash']
        single_tx["txid"]=tx_source["txid"]
        single_tx['blocktime'] = ts2t(tx_source['blocktime'])
        # txin_list = []
        # txout_list = []
        # vin = tx_source['vin']
        # vout = tx_source['vout']
        # for single_vin in vin:
        #     address = single_vin['address']
        #     value = single_vin['value']
        #     single_vin_info = {
        #         "address": address,
        #         "value": '{:.8f}'.format(value)
        #     }
        #     txin_list.append(single_vin_info)
        # for single_vout in vout:
        #     value = single_vout['value']
        #     address = single_vout['scriptPubKey']['addresses']
        #     single_vout_info = {
        #         "address": address,
        #         "value": '{:.8f}'.format(value)
        #     }
        #     txout_list.append(single_vout_info)
        single_tx['vin'] = vin
        single_tx['vout'] = vout
        tx_list.append(single_tx)
    return tx_list,total,first_seen,recv,sent,recv_num,sent_num,balance
