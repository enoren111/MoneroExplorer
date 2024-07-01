import re
import time
import datetime
import json
import coinaddr
from Validation import Validation
import random
import smtplib
from email.mime.text import MIMEText


def send_email(sender,receivers,title,content):
    mail_host = 'smtp.qq.com'
    mail_user = 'qinpengrui@foxmail.com'
    mail_pass = 'egjffkgfucanbfgd'
    message = MIMEText(content,'plain','utf-8')
    message['Subject'] = title
    message['From'] = sender
    message['To'] = receivers
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host,25)
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(
        sender,receivers,message.as_string())
        smtpObj.quit()
        print('success')
    except smtplib.SMTPException as e:
        print('error',e)


def validation_address(type,address): ##type支持BTC/BCH/ETH/ZEC/LTC/XMR/DASH的地址有效性验证
    ##type 的输入为btc,bch,ltc,eth,dash,XMR,zec
    coinlist = ['btc','bch','ltc','eth','dash']
    if type in coinlist:
        result = coinaddr.validate(type,address)
        return result.valid
    else:
        result = Validation.is_address(type,address)
        return result

def my_validation_address(address):
    pattern = r'\b(bc(0([ac-hj-np-z02-9]{39}|[ac-hj-np-z02-9]{59})|1[ac-hj-np-z02-9]{8,87})|[13][a-km-zA-HJ-NP-Z1-9]{25,35})\b'
    regex = re.compile(pattern)
    res = regex.findall(address)
    if(res!=[]):
        return 1
    else:
        return 0


def ts2t(ts):  # 时间戳转为时间
    # timeStamp = ts
    timeArray = time.localtime(ts)
    # print(timeArray)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


def t2ts(t):
    timeArray = time.strptime(t, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


# print (ts2t(1551662526))


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


def calu_dates_interval():
    date1 = '2019-05-20 07:21:32'
    date2 = '2019-05-20 07:21:29'
    # date2 = '16/Nov/2018:08:44:34'
    date1_ts = t2ts(date1)
    date2_ts = t2ts(date2)

    # 定义的日期格式需与当前时间格式一致
    d1 = datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')
    # d2 = datetime.datetime.strptime(date2, '%d/%b/%Y:%H:%M:%S')

    d = d1 - d2
    print(date1_ts - date2_ts)
    print('相差的天数：{}'.format(d.days))
    print('相差的秒数：{}'.format(d.seconds))


# calu_dates_interval()

def cut_date(fdate):   # 舍去小时
    date_stamp = datetime.datetime.strptime(str(fdate), "%Y-%m-%d %H:%M:%S")  # 将字符串转化为时间
    # short_date = time.strftime("%Y-%m-%d", date_stamp)
    return date_stamp.strftime('%Y-%m-%d')


# cut_date('2019-05-17 00:00:00')


def getEveryDay(begin_date, end_date):  # 返回两个日期内的日期列表
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list


# print(getEveryDay('2016-01-01', '2017-05-11'))
def today():
    timeArray = time.localtime(time.time())
    # print(timeArray)
    ftime = time.strftime("%Y-%m-%d", timeArray)
    return ftime





def time_quantum(moment, days):  # 返回当前日期之前若干天的日期列表 despatch args:%Y-%m-%d today()
    moment_object = datetime.datetime.strptime(moment, "%Y-%m-%d")
    # print(moment_object)
    date_list = []
    while days > 0:
        fmoment = moment_object.strftime("%Y-%m-%d")
        date_list.append(fmoment)
        moment_object -= datetime.timedelta(days=1)
        days = days - 1
    # print(date_list)
    date_list.reverse()
    return date_list


# time_quantum(today(), 1)   #


def calu_date(moment, days):  # 返回距今天days以前的日期
    moment_object = datetime.datetime.strptime(moment, "%Y-%m-%d")
    moment_object -= datetime.timedelta(days=days)
    return moment_object.strftime("%Y-%m-%d")


# print(today())
# time_quantum('2016-01-01', 3)
# print(time_quantum(today(), 3))


def day_stamp(fdate1, fdate2=None):  # args: 格式化日期%Y-%m-%d
    # 返回每日或时间段内起始和终止的时间戳
    if fdate2 == None:  # 当日
        start = datetime.datetime.strptime(fdate1, "%Y-%m-%d")
        end = start + datetime.timedelta(days=1)
        # print(end)
        # 转为时间数组
        timeArray = time.strptime(str(start), "%Y-%m-%d %H:%M:%S")
        timeArray2 = time.strptime(str(end), "%Y-%m-%d %H:%M:%S")
        # 转为时间戳
        start_stamp = int(time.mktime(timeArray))
        end_stamp = int(time.mktime(timeArray2))
        return start_stamp, end_stamp
    else:
        start = datetime.datetime.strptime(fdate1, "%Y-%m-%d")
        end = datetime.datetime.strptime(fdate2, "%Y-%m-%d") + datetime.timedelta(days=1)
        # 转为时间数组
        timeArray = time.strptime(str(start), "%Y-%m-%d %H:%M:%S")
        timeArray2 = time.strptime(str(end), "%Y-%m-%d %H:%M:%S")
        # 转为时间戳
        start_stamp = int(time.mktime(timeArray))
        end_stamp = int(time.mktime(timeArray2))
        return start_stamp, end_stamp


# print(day_stamp(today()))


def judge_tr_endpoint(tr_id):  # 根据id判别时间范围的起始日期 time range
    if tr_id == 4:  # 查询全部
        print("unexpected args at judge_tr_endpoint ")
        return 1, 2  # fake
    else:
        date_object = datetime.datetime.strptime(today(), "%Y-%m-%d")
        year = date_object.year
        month = date_object.month
        weekday = date_object.weekday()
        if tr_id == 0:  # 当天
            return day_stamp(today())
        elif tr_id == 1:  # 本周
            start = calu_date(today(), weekday)
            return day_stamp(start, today())
        elif tr_id == 2: # 本月
            return day_stamp(datetime.datetime(year, month, 1, 0, 0, 0).strftime("%Y-%m-%d"), today())
        elif tr_id == 3:  # 一年
            return day_stamp(datetime.datetime(year, 1, 1, 0, 0, 0).strftime("%Y-%m-%d"), today())


def judge_node_online(lastReachTs):
    if int(time.time()) - lastReachTs > 3600 * 24:
        return '0'
    else:
        return '1'


# print(judge_tr_endpoint(4))


def get_dict_key_value(data, prop_list=[]):
    if prop_list != []:
        for key in prop_list:
            if key in data:
                data = data[key]
            else:
                return ''
    return data  # 返回目标数据

## TEST
# print(day_stamp(today()))
# print(int(time.time()))

# print(ts2t(1548125049))

# 装饰器 检查在线/离线模式，es状态
def visit_mode_check(func,sample=None,data=None):
    from functools import wraps
    from flask import current_app
    from data.sample import get_local_data
    @wraps(func)
    def warpTheFunction():
        try:
            if current_app.config['ONLINE_MODE']:
                return func
            else:
                if sample!=None:
                    return get_local_data(sample)
                elif data!=None:
                    return data
                else:
                    return {}
        except:
            if sample != None:
                return get_local_data(sample)
            elif data != None:
                return data
            else:
                return {}
    return warpTheFunction()



def generate_verification_code(len=6):
    code_list = []
    for i in range(10):
        code_list.append(str(i))
    myslice = random.sample(code_list, len) # 从list中随机获取6个元素，作为一个片断返回
    verification_code = ''.join(myslice) # list to string
    return verification_code


