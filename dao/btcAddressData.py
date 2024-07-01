from elasticsearch import Elasticsearch
from config import config

es_ip = config.es_ip
index = 'btc_tx_new'
doc_type = 'raw'
es_port = config.es_port
# from app import es

# es = Elasticsearch("%s:%d" % (es_ip, es_port))
es = Elasticsearch(hosts=es_ip,port=es_port,request_timeout=600)
# es = Elasticsearch(hosts=es_ip,port=es_port,request_timeout=600)

def getAddressTX(final_address,page):
    page_size=10
    body = {
        "query":
          {
            "bool": {
              "should": [
                {
                  "nested": {
                    "path": "vin",
                    "query": {
                      "term": {
                        "vin.addresses.keyword": {
                          "value": final_address
                        }
                      }
                    }
                  }
                },
                {
                  "nested": {
                    "path": "vout",
                    "query": {
                      "term": {
                        "vout.scriptPubKey.addresses.keyword": {
                          "value": final_address
                        }
                      }
                    }
                  }
                }
              ]
            }
        },
        "from": (page - 1) * page_size,
        "size": page_size,
        "sort": [
          {
            "blocktime": {
              "order": "asc"
            }
          }
        ]
    }
    result = es.search(index=index, body=body,request_timeout=600)
    return result
def getAddressSent(address):
    source1='''
                        long total=0;
                        String address="'''+address+'''";
                        for(int i=0;i<doc["vin.value"].length;i++)
                        {
                          if(doc["vin.addresses.keyword"][i].equals(address))
                          {
                            total+=doc["vin.value"][i];

                          }
                        }
                        return total;
                        '''
    index1='btc_tx_new'
    body={
        "size": 0,
        "query": {
            "nested": {
                "path": "vin",
                "query": {
                    "term": {
                        "vin.addresses.keyword": address
                    }
                }
            }
        },
        "aggs": {
            "sum": {
                "nested": {
                    "path": "vin"
                },
                "aggs": {

                    "value_count": {
                        "sum": {
                            "script": {
                                "lang": "painless",
                                "source": source1
                            }
                        }
                    }
                }
            }

        }
        }
    result = es.search(index=index1, body=body,request_timeout=600)
    return result
def getAddressRecv(address):
    source1 = '''
                        double total=0;
                        String address="'''+address+'''";
                        for(int i=0;i<doc["vout.value"].length;i++)
                        {
                          if(doc["vout.scriptPubKey.addresses.keyword"][i].equals(address))
                          {
                            total+=doc["vout.value"][i];

                          }
                        }
                        return total;
                        '''
    index1 = 'btc_tx_new'
    body={
        "size": 0,
        "query": {
            "nested": {
                "path": "vout",
                "query": {
                    "term": {
                        "vout.scriptPubKey.addresses.keyword": address
                    }
                }
            }
        },
        "aggs": {
            "sum": {
                "nested": {
                    "path": "vout"
                },
                "aggs": {

                    "value_count": {
                        "sum": {
                            "script": {
                                "lang": "painless",
                                "source": source1
                            }
                        }
                    }
                }
            }

        }
    }
    result = es.search(index=index1,body=body,request_timeout=600)
    return result
