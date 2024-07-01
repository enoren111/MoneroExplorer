from loguru import logger

from utils import ts2t, today,time_quantum
import datetime
# from app import es


# es.tryagain_instance()
# es = es.instance


def get_balance(address):
    from web3.auto import w3
    from web3 import Web3
    w3 = Web3(Web3.IPCProvider("/Users/whitechen/Desktop/大四/graduate_design/go-ethereum/data/geth.ipc"))
    address = w3.toChecksumAddress(address.lower())
    balance = w3.eth.getBalance(address)/(10 ** 18)
    # balance= w3.eth.getBalance("0x407d73d8a49eeb85d32cf465507dd71d507100c1")
    return balance


def get_day(timestamp):
    import datetime
    the_datetime = datetime.datetime.fromtimestamp(timestamp)
    the_day = the_datetime.strftime('%Y-%m-%d')
    day = datetime.datetime.strptime(the_day + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
    return day


def get_month(timestamp):  # 返回日期当月起始datetime对象
    import datetime
    the_datetime = datetime.datetime.fromtimestamp(timestamp)
    the_month = the_datetime.strftime('%Y-%m')
    month = datetime.datetime.strptime(the_month + '-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    return month


def calu_heatmap_data(active_day,dates):


    active_day.reverse()
    dates.reverse()
    # active_day = [0, 0, 0, 0, 0, 0, 0, 0, 273, 67, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    day_object = datetime.datetime.strptime(today(), "%Y-%m-%d")
    weekday = day_object.weekday()  # 比真正日期小1

    heatmap_data = []
    blank_month_count = 1
    weeks = 53
    idx = 0

    # if day-weekday-1<=0:
    #     month = day_object.month
    # else:
    #     month = ' '*blank_month_count
    #     blank_month_count+=1
    #
    # for i in range(weekday+1)[::-1]:   # 0 1 2 3 4
    #     item = {}
    #     item['weekday'] = i
    #     item['weeks']=weeks
    #     item['value']= active_day[idx]
    #     item['month']=month
    #     idx += 1
    #     heatmap_data.append(item)
    #
    # day_object = day_object-datetime.timedelta(days=(weekday+1))

    # weeks-=1

    for i in range(weeks)[::-1]:
        if day_object.day - weekday - 1 <= 0:  # 当前周里有1号日期，则显示月份label
            month = day_object.month
        else:
            month = ' ' * blank_month_count
            blank_month_count += 1
        for j in range(weekday + 1)[::-1]:
            item = {}
            item['weekday'] = j + 1
            item['weeks'] = i + 1
            item['value'] = active_day[idx]
            # logger.info(active_day[idx]['value'])
            item['date'] = dates[idx]
            item['month'] = month
            idx += 1
            heatmap_data.append(item)
        day_object = day_object - datetime.timedelta(days=(weekday + 1))
        weekday = day_object.weekday()
        # print(day_object)
        # print(weekday)
    heatmap_data.reverse()
    return heatmap_data


def get_info(address):
    import time
    import datetime
    from dateutil.relativedelta import relativedelta
    from dateutil import rrule
    from elasticsearch import Elasticsearch

    tx_index = 'eth_transaction'
    tx_doc_type = '_doc'
    blk_index = 'eth_block'
    blk_doc_type = '_doc'

    # 获取地址余额
    # balance=get_balance(address)
    balance=0
    # logger.info(balance)


    # 获取该地址第一次发现时间、最后一次活跃时间、交易总次数、平均交易金额、最大交易金额、最小交易金额
    body = {
        "track_total_hits": True,
        "query": {
            "bool": {
                "should": [
                    {
                        "term": {"from.keyword": address}
                    },
                    {
                        "term": {"to.keyword": address}
                    }
                ]
            }
        },
        "aggs": {
            "min_time": {
                "min": {"field": "time"}
            },
            "max_time": {
                "max": {"field": "time"}
            },
            "avg_volume": {
                "avg": {"field": "value"}
            },
            "max_volume": {
                "max": {"field": "value"}
            },
            "min_volume": {
                "min": {"field": "value"}
            }
        },
        "size":0
    }
    result = es.search(index=tx_index, doc_type=tx_doc_type, body=body)
    # print(result)
    # logger.info(result)
    # logger.info(address)
    print(result)
    ftime = int(result['aggregations']['min_time']['value'])
    ltime = int(result['aggregations']['max_time']['value'])
    count = result['hits']['total']
    # avg_volume = result['aggregations']['avg_volume']['value']
    # max_volume = result['aggregations']['max_volume']['value']
    # logger.info(result['aggregations'])
    # min_volume = result['aggregations']['min_volume']['value']
    avg_volume=0
    max_volume=0
    min_volume=0
    # 获取该地址总转出交易次数、总转出交易金额、总转入交易金额、总转入交易次数
    body = {
        "size": 0,
        "track_total_hits": True,
        "query": {
            "term": {"from.keyword": address}
        },
        "aggs": {
            "volume": {
                "sum": {"field": "value"}
            }
        }
    }
    result = es.search(index=tx_index, doc_type=tx_doc_type, body=body)
    total_out = result['hits']['total']['value']
    total_out_volume = result['aggregations']['volume']['value']

    body = {
        "size": 0,
        "track_total_hits": True,
        "query": {
            "term": {"to.keyword": address}
        },
        "aggs": {
            "volume": {
                "sum": {"field": "value"}
            }
        }
    }
    result = es.search(index=tx_index, doc_type=tx_doc_type, body=body)
    total_in = result['hits']['total']['value']
    total_in_volume = result['aggregations']['volume']['value']

    # # 获取最大交易哈希
    # body = {
    #     "size": 0,
    #     "track_total_hits": True,
    #     "query": {
    #         "term": {"to": address}
    #     },
    #     "aggs": {
    #         "volume": {
    #             "sum": {"field": "value"}
    #         }
    #     }
    # }
    # result = es.search(index=tx_index, doc_type=tx_doc_type, body=body)




    # 获取该地址爆块数
    body = {
        "size": 0,
        "track_total_hits": True,
        "query": {
            "term": {
                "miner": address
            }
        }
    }
    result = es.search(index=blk_index, doc_type=blk_doc_type, body=body)
    blk_count = result['hits']['total']


    # 四个时间：查询开始 查询结束 地址创建 最后活跃
    # 获取该地址最近一年每日交易次数列表
    end = int(time.time())
    # start = end - 365 * 24 * 3600
    start = end - 371 * 24 * 3600   # 年日期范围拓展  距start 371天以前的起始时间戳 ，包含start共372天

    start_day = get_day(start)
    start_ts = int(time.mktime(start_day.timetuple()))

    end_day = get_day(end)
    end_ts = int(time.mktime(end_day.timetuple()))
    # end_ts1 = int(time.mktime(end_day.timetuple()))

    ftime_day = get_day(ftime)
    ftime_ts = int(time.mktime(ftime_day.timetuple()))

    ltime_day = get_day(ltime)
    ltime_ts = int(time.mktime(ltime_day.timetuple()))

    active_day = []

    if start_ts < ftime_ts:
        for i in range(start_ts, ftime_ts, 24 * 3600):  # 没有包括ftime_ts
            active_day.append(0)
            # active_day.append({datetime.datetime.fromtimestamp(i): 0})

    # start_ts = ftime_ts

    # if end_ts > ltime_ts:
    #     end_ts1 = ltime_ts  # ts裁剪用于查询

    for i in range(ftime_ts, ltime_ts+24*3600, 24 * 3600):  # 从ftime_ts起始，包括进ltime_ts
        body = {
            "size": 0,
            "track_total_hits": True,
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "time": {
                                    "gte": i,
                                    "lt": i + 24 * 3600
                                }
                            }
                        },
                        {
                            "bool": {
                                "should": [
                                    {
                                        "term": {"from.keyword": address}
                                    },
                                    {
                                        "term": {"to.keyword": address}
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
        result = es.search(index=tx_index, doc_type=tx_doc_type, body=body)
        volume = result['hits']['total']
        # active_day.append({datetime.datetime.fromtimestamp(i): volume})
        active_day.append(volume['value'])

    if end_ts > ltime_ts:  # 最后活跃时间的下一天
        for i in range(ltime_ts+24*3600, end_ts+24*3600, 24 * 3600):  # 边界不严谨，但active_day总数是对的
            active_day.append(0)
            # active_day.append({datetime.datetime.fromtimestamp(i): 0})
    print(active_day)

    # 获取该地址每月交易次数
    active_month_value = []
    active_month_date = []


    ftime_month = get_month(ftime)   # 起始月份时间戳
    ltime_month = get_day(ltime)
    monthes = rrule.rrule(rrule.MONTHLY, dtstart=ftime_month, until=ltime_month).count()

    for i in range(0, monthes):
        start = ftime_month + relativedelta(months=i)
        start_ts = int(time.mktime(start.timetuple()))
        end = ftime_month + relativedelta(months=i + 1)
        end_ts = int(time.mktime(end.timetuple()))
        body = {
            "size": 0,
            "track_total_hits": True,
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "time": {
                                    "gte": start_ts,
                                    "lt": end_ts
                                }
                            }
                        },
                        {
                            "bool": {
                                "should": [
                                    {
                                        "term": {"from.keyword": address}
                                    },
                                    {
                                        "term": {"to.keyword": address}
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
        result = es.search(index=tx_index, doc_type=tx_doc_type, body=body)
        volume = result['hits']['total']
        # active_month.append({start: volume})
        active_month_value.append(volume)     # [['2017-08', 259]...]
        active_month_date.append(start.strftime("%Y-%m"))

    heatmap_data = calu_heatmap_data(active_day, time_quantum(today(), 372))
    # return [ftime, ltime, count, avg_volume, max_volume, min_volume, total_in, total_in_volume, total_out, blk_count, active_day, active_month]
    return {"balance": balance, "create_time": ts2t(int(ftime)), "last_active_time": ts2t(int(ltime)), "trans_num": count['value'],
            "avg_volume": avg_volume, "max_volume": max_volume, "min_volume": min_volume, "total_in": total_in,
            "total_in_volume": total_in_volume, "total_out": total_out, "total_out_volume": total_out_volume,
            "blk_count": blk_count, "active_day": active_day, "active_month": {"date":active_month_date,"value":active_month_value},"heatmap_data":heatmap_data}



if __name__ == '__main__':
    address = '0x027f9F8575821365a70f3812Ea5F565946e7aC0d'
    # address = '0x444bD2354623367bBA518176158f8b32Fe749F00'
    # balance = get_balance(address)
    infos = get_info(address)

    # heatmap data
    # active_day = infos['active_day']
    # print(balance)
    # print(infos)
