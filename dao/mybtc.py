from elasticsearch import Elasticsearch

from Serives.btcaddrtag import get_address_mytags
from bee_var import mybtctag_index, btctagseed_index
from config import config

es_ip = config.es_ip
es_port = 9200


def get_tag_info(final_address):
    es = Elasticsearch("%s:%d" % (es_ip, es_port))
    label_clash=0
    try:
        body = {
            "query": {
                "terms": {
                    "_id": [
                        final_address
                    ]
                }
            }
        }
        res = es.search(index = btctagseed_index,body = body)
    except Exception as e:
        return None
    if (res['hits']['total']['value'] == 0):
        return None
    return res


def get_trans_info(hash):
    index = 'my_btc_trans'
    es = Elasticsearch("%s:%d" % (es_ip, es_port))
    try:
        result = es.get(index=index, doc_type="_doc", id=hash)
    except Exception as e:
        return None
    return result


# cluster the same address
def cluster(list, attr):
    address = ""
    addr_list = []
    single_list = []
    repeat_list = []

    for l in list:
        if address != l[attr]:
            address = l[attr]
            single_list.append(l)
        else:
            addr_list.append(l[attr])
            repeat_list.append(l)

    return addr_list, single_list, repeat_list
