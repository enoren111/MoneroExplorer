import math

import pymysql
import datetime
from utils import cut_date, visit_mode_check
from data import sample as sd
import json
from flask import request
from config import config


class mysql_dealer():
    ip = config.mysql_ip
    user = 'ljh15029793506'
    psw = '13009160543ljhXT'
    port = config.mysql_port

    db = None
    cursor = None

    def __init__(self, database):
        try:
            self.db = pymysql.connect(host=self.ip, user=self.user, password=self.psw, port=self.port,
                                      database=database)
            self.cursor = self.db.cursor()
        except Exception as e:
            print("MySQL连接失败1" + str(e))

    def __del__(self):
        try:
            self.cursor.close()
            self.db.close()
        except:
            print("MySQL连接失败2")

    def get_cursor_exe_result(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def group(self, table, field, order="desc"):
        # sql = "select "+field+",count(*) as nums from "+table+" group by "+field+" order by nums "+order
        sql = "select t1." + field + ", t1.nums,concat(round(t1.nums/t2.total*100,2),'%') from (select " + field + ",count(*) as nums from " + table + " group by " + field + " order by nums desc ) t1,(select count(*) as total from passive_nodes) t2"
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
    db = pymysql.connect(host=config.mysql_ip, user="ljh15029793506", password="13009160543ljhXT", database=database, port=config.mysql_port)

    return db


def get_xmr_tag_info(perpage, start):
    dateMap = {

        "0": "今天",
        "1": "本周",
        "2": "本月",
        "3": "今年",
        "4": "全部"
    }
    order_rule = ''
    order = request.args.get('order', default='0')  # 默认值为今天
    order_rule = dateMap[order]
    del dateMap[order]
    rings = []
    fields = []
    try:
        db = startDb("rm-2zeu3aj13g5xmy515")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM testnet_rings_info LIMIT {},{};".format(start, perpage))
        print("db:______________________________________\n", db)

        results = cursor.fetchall()
        # field: 0-time 1-block 2-txhash 3-keyimg 4-pubk 5-out_6-index 7-ringct 8-coinbase 9-amount  10-matched 11-matched_flood 12-0mix_closet_flood
        for id, field in enumerate(cursor.description):
            # print("field", field[0])
            fields.append(field[0])
        for row in results:
            ring = {}
            for id in range(len(fields)):

                if id == 0:
                    ring[fields[id]] = row[id]
                    # print("row0: ", ring[fields[id]])
                else:
                    ring[fields[id]] = row[id]
                    # print("row: ", ring[fields[id]])
            rings.append(ring)
        print("=======================================我是content分割线===============================================")
        print(rings)
    except Exception as e:
        print("MySQL连接失败3" + str(e))
    context = {
        "order_rule": order_rule,
        "date_map": dateMap,
        "page_title": '区块'
    }
    return rings

# 获取时间范围数据sql
def get_time_range(order="0"):
    if order=='0':
        return  ' where to_days(createtime) = to_days(now());'
    elif order=='1':
        return ' where DATE_SUB(CURDATE(), INTERVAL 7 DAY) <= date(createtime);'
    elif order=='2':
        return  ' where DATE_SUB(CURDATE(), INTERVAL 30 DAY) <= date(createtime);'
    elif order=='3':
        return 'where YEAR(create_date)=YEAR(NOW());'


# 获取地址分布
def get_addr_num(order='0',v=None,perpage=10,strt=0):

    sql= 'SELECT count(*) as res  from monero'#主地址
    sql1='SELECT count(*) as res  from monerosub'#子地址
    ranged=';'
    if order!='4':
        ranged=get_time_range(order)
        sql=sql+ranged
        sql1=sql1+ranged
    else:
        sql+=ranged
        sql1+=ranged
    if not v:
        sql='select * from monerosub'+ranged[:-1]+' union all select * from monero '+ranged
        # ''.replace()
        sql1=sql[:-1]+f" ORDER BY createtime DESC limit {strt},{perpage};"
        sql=f'select count(*) from ({sql[:-1]}) as t1' 
        datas = []
        total=0
        print(sql,sql1)
        try:
            db = startDb("addrs_syc")
            cursor = db.cursor()
            cursor.execute(sql1)
            datas = cursor.fetchall()
            db.commit()
            cursor.execute(sql)
            res1=cursor.fetchall()
            total=res1[0][0]
            

            
        except Exception as e:
            print("MySQL连接失败3" + str(e))

        return datas,total
        
    else:
    
        datas = []
        
        try:
            db = startDb("addrs_syc")
            cursor = db.cursor()
            cursor.execute(sql)
            res = cursor.fetchall()
            datas.append(res[0][0])
            db.commit()
            cursor.execute(sql1)
            res1=cursor.fetchall()
            datas.append(res1[0][0])
            print("db:______________________________________\n", db)

            
        except Exception as e:
            print("MySQL连接失败3" + str(e))

        return datas,1


def get_xmr_spent_info(perpage, start):
    dateMap = {

        "0": "今天",
        "1": "本周",
        "2": "本月",
        "3": "今年",
        "4": "全部"
    }
    order_rule = ''
    order = request.args.get('order', default='0')  # 默认值为今天
    order_rule = dateMap[order]
    del dateMap[order]
    spents = []
    fields = []
    try:
        db = startDb("xmr_info")
        cursor = db.cursor()
        cursor.execute(
            "select * from testnet_rings_info where matched='real' or matched_flood='real' or 0mix_closet_flood='real' LIMIT {},{};".format(
                start, perpage))
        results = cursor.fetchall()
        # field: 0-time 1-block 2-txhash 3-keyimg 4-pubk 5-out_6-index 7-ringct 8-coinbase 9-amount  10-matched 11-matched_flood 12-0mix_closet_flood
        for id, field in enumerate(cursor.description):
            fields.append(field[0])
        for row in results:
            spent = {}
            for id in range(len(fields)):

                if id == 0:
                    spent[fields[id]] = cut_date(row[id])
                else:
                    spent[fields[id]] = row[id]
            spents.append(spent)
        print(spents)
    except Exception as e:
        print("MySQL连接失败4" + str(e))
    total = 207488  # 这里在数据库是查好了写上去的，如果有需要要重算重写
    pages = math.ceil(float(total) / perpage)
    context = {
        "order_rule": order_rule,
        "date_map": dateMap,
        "pages": pages,
        "block_total": total,
        "page_title": '环'
    }
    return spents, context


def get_xmr_nodes_info(tablename, perpage, start):
    dateMap = {

        "0": "今天",
        "1": "本周",
        "2": "本月",
        "3": "今年",
        "4": "全部"
    }
    order_rule = ''
    order = request.args.get('order', default='0')  # 默认值为今天
    order_rule = dateMap[order]
    del dateMap[order]
    nodes = []
    fields = []
    try:
        db = startDb("xmr_info")
        cursor = db.cursor()

        cursor.execute(
            "select * from {} LIMIT {},{};".format(tablename, start, perpage))

        results = cursor.fetchall()

        for id, field in enumerate(cursor.description):
            fields.append(field[0])
        for row in results:
            node = {}
            print("row: ", row)

            for id in range(len(fields)):
                node[fields[id]] = row[id]
            nodes.append(node)
    except Exception as e:
        print("MySQL连接失败5" + str(e))
    total = 3322  # 这里在数据库是查好了写上去的，如果有需要要重算重写
    pages = math.ceil(float(total) / perpage)
    context = {
        "order_rule": order_rule,
        "date_map": dateMap,
        "pages": pages,
        "block_total": total,
        "page_title": '节点'
    }
    return nodes, context


def get_xmr_search_node(tablename, perpage, start, rule, starttime, endtime):
    dateMap = {

        "0": "今天",
        "1": "本周",
        "2": "本月",
        "3": "今年",
        "4": "全部"
    }
    order_rule = ''
    order = request.args.get('order', default='0')  # 默认值为今天
    order_rule = dateMap[order]
    del dateMap[order]
    nodes = []
    fields = []
    try:
        db = startDb("xmr_info")
        cursor = db.cursor()
        search_words = "select * from {} where DATE_FORMAT( last_seen,  '%Y-%m-%d' )> '{}' AND DATE_FORMAT( last_seen,  '%Y-%m-%d' )< '{}' ORDER BY DATE_FORMAT( last_seen,  '%Y-%m-%d' ) {} LIMIT {},{};".format(tablename,starttime,endtime,rule,start, perpage)
        print(search_words)
        cursor.execute(search_words)
        results = cursor.fetchall()
        print("_____________________ search result __________________________")
        print(results)
        print("________________ ______ result end ___________________________")

        for id, field in enumerate(cursor.description):
            fields.append(field[0])
        for row in results:
            node = {}
            print("row: ", row)

            for id in range(len(fields)):
                node[fields[id]] = row[id]
            nodes.append(node)
    except Exception as e:
        print("MySQL连接失败6" + str(e))
    total = 3322  # 这里在数据库是查好了写上去的，如果有需要要重算重写
    pages = math.ceil(float(total) / perpage)
    context = {
        "order_rule": order_rule,
        "date_map": dateMap,
        "pages": pages,
        "block_total": total,
        "page_title": '节点'
    }
    return nodes, context


def get_xmr_nodes_detail(address, perpage, start):
    nodes = {}
    fields = []
    try:
        db = startDb("xmr_info")
        cursor = db.cursor()
        cursor.execute(
            "select * from data_monero where address='{}';".format(address))
        results = cursor.fetchall()
        for id, field in enumerate(cursor.description):
            fields.append(field[0])
        if results[0]:
            for id in range(len(fields)):
                nodes[fields[id]] = results[0][id]
        print(nodes)
    except Exception as e:
        print("MySQL连接失败" + str(e))
    return {}, nodes


def get_xmr_supernodes_detail(address, port, perpage, start):
    supernodes = []
    fields = []
    node1 = {}
    try:
        db = startDb("xmr_info")
        cursor = db.cursor()
        cursor.execute(
            "select * from supernode_monero_mainnet where address='{}' and port='{}';".format(address, port))
        results = cursor.fetchall()
        for id, field in enumerate(cursor.description):
            fields.append(field[0])
        for row in results:
            supernode = {}
            print("row: ", row)
            for id in range(len(fields)):
                supernode[fields[id]] = row[id]
            supernodes.append(supernode)
        print("================================================")
        print(supernodes)
        if results[0]:
            for id in range(len(fields)):
                node1[fields[id]] = results[0][id]
        print("=============================node1============================")

        print(node1)
    except Exception as e:
        print("MySQL连接失败7" + str(e))
    return {}, node1, supernodes


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
        cursor.close()
        db.close()
    except:
        # sd.get_daily_eth_a_info()
        fields, content = sd.get_daily_eth_a_info1()

        print("MySQL error8")

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


def get_node_detail_info(node_id):  # despatch
    md_test = mysql_dealer("ethnodes")
    fields = md_test.get_table_fields("passive_nodes")
    row = md_test.get_table_items("passive_nodes", "node_id", node_id)
    dict = {}
    if len(row) == 1:
        for id, field in enumerate(fields):
            dict[field] = row[0][id]  # 节点详情转字典
    else:
        for id, field in enumerate(fields):
            dict[field] = 'null-s'
        # print('未在mysql内查询到节点',node_id)
    return dict


def get_node_distribution():  # 节点分布详情
    md_test = mysql_dealer("ethnodes")

    def foo():
        mysql_result = {}
        mysql_result['ct_dist'] = (md_test.group("passive_nodes", 'country'))
        mysql_result['cv_dist'] = (md_test.group("passive_nodes", 'client_version'))  # client_version
        mysql_result['co_dist'] = (md_test.group("passive_nodes", 'client_os'))  # client_os
        mysql_result['asn_dist'] = (md_test.group("passive_nodes", 'asn'))
        return mysql_result
    mysql_result = visit_mode_check(foo, "eth_nodes_dstb_sample.json")

    node_dist = {}
    for key in mysql_result:
        node_dist[key] = []
    for key in mysql_result:
        for item in mysql_result[key]:
            node_dist[key].append({"value": item[1], "name": item[0], "p": item[2]})

    return node_dist

