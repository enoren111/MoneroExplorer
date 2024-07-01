from elasticsearch import Elasticsearch
from config import config

es_ip = config.es_ip
# es_ip="192.168.126.176"
index = 'zcash_tx'
doc_type = 'raw'
es_port = 9200
es = Elasticsearch("%s:%d" % (es_ip, es_port))
def zcash_getAddressTX(final_address,page):
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
                        "vin.address.keyword": {
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
    result = es.search(index=index, body=body)
    return result
def zcash_getAddressSent(address):
    source1='''
                        double total=0;
                        String address="'''+address+'''";
                        for(int i=0;i<doc["vin.value"].length;i++)
                        {
                          if(doc["vin.address.keyword"][i].equals(address))
                          {
                            total+=doc["vin.value"][i];

                          }
                        }
                        return total;
                        '''
    index1='zcash_tx'
    body={
        "size": 0,
        "query": {
            "nested": {
                "path": "vin",
                "query": {
                    "term": {
                        "vin.address.keyword": address
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
    result = es.search(index=index1, body=body)
    return result
def zcash_getAddressRecv(address):
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
    index1 = 'zcash_tx'
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
    result = es.search(index=index1,body=body)
    return result
