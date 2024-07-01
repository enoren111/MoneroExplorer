from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from config.config import *
rpc_connection = AuthServiceProxy('http://%s:%s@%s:%d' % (RPC_USER, RPC_PASSWD, RPC_IP, RPC_PORT))
def getTxDetail(tx_hash):
    tx = rpc_connection.getrawtransaction(tx_hash, True)
    vin=[]
    vout=[]
    if 'coinbase' not in tx["vin"][0]:
        for item in tx["vin"]:
            n=item["vout"]
            the_tx=rpc_connection.getrawtransaction(item["txid"], True)
            for out in the_tx["vout"]:
                if out['n'] == n:
                    try:
                        address = out['scriptPubKey']['addresses'][0]
                        value= out["value"]
                        single_vin={
                            "address":address,
                            "value":value
                        }
                        vin.append(single_vin)
                    except Exception as e:
                        pass
    for item in tx['vout']:
        try:
            address = item['scriptPubKey']['addresses'][0]
            value= item["value"]
            single_vout={
                "address":address,
                "value":value
            }
            vout.append(single_vout)
        except Exception as e:
            pass

    return {
        "vin":vin,
        "vout":vout
    }