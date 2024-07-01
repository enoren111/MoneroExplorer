import re
import time

from elasticsearch import Elasticsearch
from log import log
from config import config
from log import log
from bee_var import perPage, perPage_10
from mysql_dealer import mysql_dealer

log = log.init_logger(config.log_filepath)
rule = "查询字段及格式：" \
       "交易时间 blocktime:2020-12-25T19:24:08," \
       "交易金额(BTC) inputvalue:double," \
       "手续费(聪)fee:int " \
       "输入地址 inputaddr:String," \
       "输出地址 outputaddr:String，" \
       "输入地址类别 type:(P2SH,P2SKH,NEW)," \
       "发送方地址个数 inputaddrnum:int," \
       "接收方地址个数outputaddrnum:int," \
       "费率feerate:double"


def buildQueryBody(text, start, page):
    flagor = False
    flagand = False
    str_input_num = ''
    str_minvin=''
    str_maxvin=''
    str_output_num = ''
    str_minvout=''
    str_maxvout=''
    str_height=''
    str_minheight = ''
    str_maxheight = ''
    str_value=''
    str_minvalue = ''
    str_maxvalue = ''
    str_date=''
    str_before = ''
    str_after = '{"range": {"blocktime": {"gte": "' + "2003-01-01T00:00:00" + '"}}}'
    str_input=''
    str_output=''
    str_maxfee=''
    str_minfee = ''
    str_fee = ''
    str_coinbase=''
    str_USD=''
    str_USDMin=''
    str_USDMax=''
    str_existprice=''
    str_inputValue  =''
    str_outputValue=''
    str_outputValueMin=''
    str_outputValueMax=''
    str_inputValueMax=''
    str_inputValueMin=''
    if not re.findall('and', text):
        text=text+' and'
    if re.findall('and', text):
        flagand = True
    # if re.findall('or', text):
    #     flagor = True
    if flagand and not flagor:
        # text = text.replace("(","")
        # text = text.replace(")", "")
        result = text.split("and")
        log.error(result)
        for item in result:
            item = item.strip()
            if re.findall("=", item):
                node1 = item.split("=")[0]
                node2 = item.split("=")[1]
                # log.error(node1, node2)
                if node1 == "vin_num":
                    str_input_num = ',{"term": {"vin_size":"' + str(node2) + '"}}'
                if node1 == "vout_num":
                    str_output_num = ',{"term": {"vout_size":"' + str(node2) + '" }}'
                if node1 == "height":
                    str_height = ',{"term": {"blockheight": "' + str(node2) + '"}}'
                if node1 == 'TotalValueBTC':
                    node2 = float(node2) * 100000000
                    str_value = ',{"term": {"inputvalue":'+ str(node2) + '}}'
                if node1 == 'date':  # =
                    node2 = time.mktime(time.strptime(node2, '%Y-%m-%d %H:%M:%S'))
                    node2 = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(node2 - 28800.0))
                    str_date = ',{"term": {"blocktime": {"' + str(node2) + '"}}}'
                if node1 == 'InputValueBTC':
                    node2 = float(node2) * 100000000
                    str_inputValue=',{"nested": {"path": "vin","query": {"term": {"vin.value": {"value": "'+str(node2)+'"} }}}}'
                if node1 == 'OutputValueBTC':
                    node2 = float(node2)
                    str_outputValue=',{"nested": {"path": "vout","query": {"term": {"vout.value": {"value": "'+str(node2)+'"} }}}}'
                if node1 == 'inputaddress':
                    node2=".*" + node2 + ".*"
                    str_input = ',{"nested": {"path": "vin","query": {"regexp": {"vin.addresses.keyword": {"value": "' + node2 + '" }}}}} '
                if node1 == 'outputaddress':
                    node2 = ".*" + node2 + ".*"
                    str_output = ',{"nested": {"path": "vout","query": {"regexp": {"vout.scriptPubKey.addresses.keyword": {"value": "' + node2 + '"  }}}}}'
                if node1 =='fee':
                    node2 = float(node2) * 100000000
                    str_fee = ' ,{"term": {"fee":"' + str(node2) + '" }}'
                if node1=='isCoinbase':
                    str_coinbase = ',{"term": {"iscoinbase": ' + node2 + '}}'
                if node1=='TotalValueUSD':
                    node2 = float(node2) * 100000000
                    str_existprice = ',{"exists": {"field": "dayprice"}}'
                    str_USD = """,{ "script": {"script": "doc['inputvalue'].value*doc['dayprice'].value ==""" + str(
                        node2) + """"}} """

                elif node1 == "feerate":
                    strr = """{ "script": {"script": {"inline": "doc['fee'].value/doc['size'].value>=""" + node2 + ""","lang": "painless"}}}"""
                    continue
            if re.findall(">", item):
                node1 = item.split(">")[0]
                node2 = item.split(">")[1]
                # log.error(node1, node2)
                if node1 == "height":
                    str_minheight = ',{"range": {"blockheight":{"gte": "' + str(node2) + '"}}}'
                if node1 == "vin_num":
                    str_minvin = ',{"range": {"vin_size":{"gte": "' + str(node2) + '"}}}'
                if node1 == "vout_num":
                    str_minvout = ',{"range": {"vout_size":{"gte": "' + str(node2) + '"}}}'
                if node1 == 'TotalValueBTC':
                    node2 = float(node2) * 100000000
                    str_minvalue = ',{"range": {"inputvalue":{"gte": ' + str(node2) + '}}}'
                if node1=='InputValueBTC':
                    node2 = float(node2) * 100000000
                    str_inputValueMin = ',{"nested": {"path": "vin","query": { "range": {"vin.value": {"gte": "'+str(node2)+'"}}}}}'
                if node1=='OutputValueBTC':
                    node2 = float(node2)
                    str_outputValueMin = ',{"nested": {"path": "vout","query": { "range": {"vout.value": {"gte": "'+str(node2)+'"}}}}}'
                if node1 == 'date':  # >
                    node2 = time.mktime(time.strptime(node2, '%Y-%m-%d %H:%M:%S'))
                    node2 = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(node2 - 28800.0))
                    str_after = '{"range": {"blocktime": {"gte": "' + str(node2) + '"}}}'
                if node1 =='fee':
                    node2 = float(node2) * 100000000
                    str_minfee=',{"range": {"fee":{"gte": "' + str(node2) + '"}}}'
                if node1 == 'TotalValueUSD':
                        node2 = float(node2) * 100000000
                        str_existprice=',{"exists": {"field": "dayprice"}}'
                        str_USDMin = """,{ "script": {"script": "doc['inputvalue'].value*doc['dayprice'].value >=""" + str(node2) + """"}} """
                elif node1 == "feerate":
                    strr = """{ "script": {"script": {"inline": "doc['fee'].value/doc['size'].value>=""" + node2 + ""","lang": "painless"}}}"""
                    continue
            if re.findall("<", item):
                node1 = item.split("<")[0]
                node2 = item.split("<")[1]
                # log.error(node1, node2)
                if node1 == "height":
                    str_maxheight = ',{"range": {"blockheight":{' + '"lte": "' + str(node2) + '"}}}'
                if node1 == "vin_num":
                    str_maxvin = ',{"range": {"vin_size":{' + '"lte": "' + str(node2) + '"}}}'
                if node1 == "vout_num":
                    str_maxvout = ',{"range": {"vout_size":{' + '"lte": "' + str(node2) + '"}}}'
                if node1 == 'TotalValueBTC':
                    node2 = float(node2) * 100000000
                    str_maxvalue = ',{"range": {"inputvalue":{' + '"lte": ' + str(node2) + '}}}'
                if node1 == 'date':  # <
                    node2 = time.mktime(time.strptime(node2, '%Y-%m-%d %H:%M:%S'))
                    node2 = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(node2 - 28800.0))
                    str_before = ',{"range": {"blocktime": {' + '"lte": "' + str(node2) + '"}}}'
                if node1 == 'fee':
                    node2 = float(node2) * 100000000
                    str_maxfee = ',{"range": {"fee":{' + '"lte": "' + str(node2) + '"}}}'
                if node1=='InputValueBTC':
                    node2 = float(node2) * 100000000
                    str_inputValueMax = ',{"nested": {"path": "vin","query": { "range": {"vin.value": {"lte": "'+str(node2)+'"}}}}}'
                if node1=='OutputValueBTC':
                    node2 = float(node2)
                    str_outputValueMax = ',{"nested": {"path": "vout","query": { "range": {"vout.value": {"lte": "'+str(node2)+'"}}}}}'
                if node1 == 'TotalValueUSD':
                        node2 = float(node2) * 100000000
                        str_existprice = ',{"exists": {"field": "dayprice"}}'
                        str_USDMax = """,{ "script": {"script": "doc['inputvalue'].value*doc['dayprice'].value <=""" + str(
                            node2) + """"}} """
                elif node1 == "feerate":
                    strr = """{ "script": {"script": {"inline": "doc['fee'].value/doc['size'].value<=""" + node2 + ""","lang": "painless"}}}"""
                    continue
    body = """{
                "query":
                    {
                        "bool": {
                            "must":[ 
                            """ + str(str_after).replace("'", "") + """
                                    """ + str(str_input_num).replace("'", "") + """ 
                                    """ + str(str_minvin).replace("'", "") + """ 
                                    """ + str(str_minvout).replace("'", "") + """ 
                                    """ + str(str_maxvin).replace("'", "") + """ 
                                    """ + str(str_maxvout).replace("'", "") + """ 
                                    """ + str(str_output_num).replace("'", "") + """
                                     """ + str(str_height).replace("'", "") + """
                                    """ + str(str_minheight).replace("'", "") + """
                                    """ + str(str_maxheight).replace("'", "") + """
                                     """ + str(str_coinbase).replace("'", "") + """
                                     """ + str(str_minvalue).replace("'", "") + """
                                     """ + str(str_value).replace("'", "") + """
                                      """ + str(str_maxvalue).replace("'", "") + """
                                       """ + str(str_before).replace("'", "") + """
                                        """ + str(str_date).replace("'", "") + """
                                       """ + str(str_input).replace("'", "") + """
                                       """ + str(str_output).replace("'", "") + """
                                       """ + str(str_maxfee).replace("'", "") + """
                                       """ + str(str_minfee).replace("'", "") + """
                                        """ + str(str_fee).replace("'", "") + """
                                        """ + str(str_inputValue).replace("'", "") + """
                                        """ + str(str_inputValueMax).replace("'", "") + """
                                        """ + str(str_inputValueMin).replace("'", "") + """
                                        """ + str(str_existprice).replace("'", "") + """
                                        """ + str(str_outputValue).replace("'", "") + """
                                        """ + str(str_outputValueMax).replace("'", "") + """
                                        """ + str(str_outputValueMin).replace("'", "") + """
                                        """+str(str_USD) + """
                                        """+str(str_USDMin) + """
                                        """+str(str_USDMax) + """
                                        
                                    ]}},
                  "from": """ + str(start) + """,
                "size": """ + str(page) + """,
                "sort": {"blockheight": {"order": "desc"}},           
                "track_total_hits": true
            }"""
    log.error(body)
    return body

# text = "blocktime=2020-12-26T04:31:32 and fee>=1880"
# body = buildQueryBody(text,10,20)
# # body ={
# #             "query":
# #                 {
# #                     "bool": {
# #                         "must":[ {"term": {"blocktime":"2020-12-26T04:31:32"}}]  }},
# #               "from": 10,
# #             "size": 20,
# #             "sort": {"blockheight": {"order": "desc"}},
# #             "track_total_hits": True
# #         }
# body =str(body)
# # print(body)
# es = Elasticsearch("10.112.38.18:9200")
# result = es.search(index="btc_tx_new",body=body)
# print(result)
