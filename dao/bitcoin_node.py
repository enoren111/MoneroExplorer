import pymysql
import datetime
from log import log
# from app import es
from config import config
from bee_var import btcblock_newindex, block_raw, btcblock_index
from utils import cut_date,visit_mode_check
from data import sample as sd
import json

log = log.init_logger(config.log_filepath)
# es.tryagain_instance()
# es = es.instance

#idid="39.99.132.128"
#useruser='root'
#pswpsw='bupt_2019'
idid="192.168.1.6"
useruser='bupt'
pswpsw='bupt2021'

class btc_node_mysql_dealer():
    id = idid
    user = useruser
    psw = pswpsw

    db=None
    cursor=None

    def __init__(self, database):
        try:
            self.db = pymysql.connect(self.id, self.user, self.psw, database)
            self.cursor = self.db.cursor()
        except Exception as e:
            print("MySQL连接失败"+str(e))

    def __del__(self):
        try:
            self.cursor.close()
            self.db.close()
        except:
            print("MySQL连接失败")

    def get_cursor_exe_result(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def group(self, table, field, order="desc"):
        # sql = "select "+field+",count(*) as nums from "+table+" group by "+field+" order by nums "+order
        sql = "select t1."+field+", t1.nums,concat(round(t1.nums/t2.total*100,2),'%') from (select "+field+",count(*) as nums from "+table+" group by "+field+" order by nums desc ) t1,(select count(*) as total from node_peer) t2"
        # sql = "select t1." + field + ", t1.nums,round(t1.nums/t2.total,4) from (select " + field + ",count(*) as nums from " + table + " group by " + field + " order by nums desc ) t1,(select count(*) as total from passive_nodes) t2"

        return self.get_cursor_exe_result(sql)

    def get_table_items(self, table, key=None, value=None):  # 表格查询
        if key:
            sql = "select * from " + table + " where " + key + " = '" + value + "'"
            # print(sql)
        else:
            sql = "select * from " + table  # 查询全部
        return self.get_cursor_exe_result(sql)

    def get_table_fields(self, table):
        sql = "desc " + table
        results = self.get_cursor_exe_result(sql)
        fields = []
        for item in results:
            fields.append(item[0])
        return fields


def startDb(database):
    id = idid
    user = useruser
    psw = pswpsw
    db = pymysql.connect(id, user, psw, database)
    return db


def get_daily_eth_a_info():  # 获取ETH日统计信息
    # content = []
    content = {}
    fields = []
    try:
        db = startDb("ethnodes")
        cursor = db.cursor()
        # cursor.execute("select * from daily_eth where date > %s limit 30", "2019-04-17")
        cursor.execute("SELECT * FROM (select * from daily_eth order by date desc limit 30) aa ORDER BY date")
        results = cursor.fetchall()

        for id, field in enumerate(cursor.description):
            content[field[0]] = []
            fields.append(field[0])

        for row in results:
            # list = []
            for id in range(len(fields)):
                if id == 0:
                    content[fields[id]].append(cut_date(row[id]))
                else:
                    content[fields[id]].append(row[id])
            # item['date'] = cut_date(row[0])
            # item['exception_trans'] = row[1]
            # item['trans_num'] = row[2]
            # item['trans_sum'] = row[3]
            # item['normal_trans_num'] = row[4]
            # item['call_trans_num'] = row[5]
            # item['contract_trans_num'] = row[6]
            # item['active_address'] = row[7]
            # item['new_address'] = row[8]
            # item['new_contract'] = row[9]
            # print(cut_date(row[0]))

        cursor.close()
        db.close()
    except:
        # sd.get_daily_eth_a_info()
        fields, content = sd.get_daily_eth_a_info1()

        print("MySQL error")


    return fields, content  # 返回 字段列表 {'key':[]} key为字段名，[]为数据列表


def get_eth_node():  # despatch
    try:
        db = startDb("ethnodes")
        cursor = db.cursor()
        # cursor.execute("select * from daily_eth where date > %s", "2019-04-17")
        cursor.execute(
            "select * from passive_nodes where node_id='ec7e331550fb023db624b49b55c6ae3b93ec81565535f8e4ec54bcf5ff4794f2543a525828617f66168f5bd5617d3cb9c98e43c7058688d9f3d9935bcea8b633' ")
        results = cursor.fetchall()
        print(results)
        for row in results:
            print(row)
            pass
        for id, field in enumerate(cursor.description):
            print(field)
    except:
        ("Error: unable to fecth data")

    db.close()


# print(get_daily_eth_a_info())

def get_btc_node(perpage, start):
    count = 0
    result_list = []
    try:
        sql_dealer = btc_node_mysql_dealer("bitnodes")

        sql="select * from node_peer limit {0},{1}".format(start,perpage)

        sql_count = "select count(1) from node_peer"
        result=sql_dealer.get_cursor_exe_result(sql)
        count = int(sql_dealer.get_cursor_exe_result(sql_count)[0][0])

    except:
        ("Error: unable to sql data")
        result={}
        count=0
    else:
        result_list = []
        for result in result:
            single = dict()
            (
                single['id'], single['ip'], single['port'], single['height'],
                single['fftime'], single['lftime'], single['service'], single['user_agent'],
                single['protocol_version'], single['city'], single['country'],
                single['asn'],single['lat'], single['lng']) = (result)
            result_list.append(single)
    return result_list,count

def get_btc_node_analyse():
    # 国家、服务端、协议版本、asn

    md_test = btc_node_mysql_dealer("bitnodes")

    mysql_result={}
    mysql_result['ct_dist'] = (md_test.group("node_peer", 'country'))
    mysql_result['cv_dist'] = (md_test.group("node_peer", 'user_agent'))  # client_version
    mysql_result['co_dist'] = (md_test.group("node_peer", 'protocol_version'))  # client_os
    mysql_result['asn_dist'] = (md_test.group("node_peer", 'asn'))

    node_dist = {}
    for key in mysql_result:
        node_dist[key] = []
    for key in mysql_result:
        for item in mysql_result[key]:
            node_dist[key].append({"value": item[1], "name": item[0], "p": item[2]})

    return node_dist

def get_max_height():
    body = {
        "query": {"match_all": {}},
        "aggs": {
            "max_height": {"max": {"field": "height"}}
        }
    }
    try:
        result = es.search(index=btcblock_index, doc_type=block_raw, body=body)
        maxheight = int(result['aggregations']['max_height']['value'])
    except Exception as e:
        log.error("es search max block height wrong "+str(e))
        maxheight=9999999
    return maxheight

def get_btc_node_byIP(ip):
    try:
        sql_dealer = btc_node_mysql_dealer("bitnodes")
        sql="select DISTINCT * from node_peer where ip=\"{}\"".format(ip)
        print(sql)
        result=sql_dealer.get_cursor_exe_result(sql)
        print(result)
    except Exception as e:
        print("Error: unable to sql data"+str(e))
        result_list = []
    else:
        result_list = []
        for result in result:
            single = dict()
            (
                single['id'], single['ip'], single['port'], single['height'],
                single['fftime'], single['lftime'], single['service'], single['user_agent'],
                single['protocol_version'], single['city'], single['country'],
                single['asn'], single['lat'], single['lng']) = (result)
            result_list.append(single)
    return result_list
