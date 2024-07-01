'''
Author: @xiaonancheng
Date: 2023-03-27 15:09:12
https://www.cnblogs.com/xiaonancheng
Copyright (c) 2023 by @xiaonancheng, All Rights Reserved. 
'''

from flask import current_app
from loguru import logger

from data.local_data_dealer import json_dealer
import json
import os


def get_daily_eth_a_info1():   # despatch -> get_local_data
    dir = current_app.config['SAMPLE_DATA_DIR']

    f = open(os.path.join(dir, 'btc_tag.json'))

    data_dict = json.loads(f.read())
    logger.info(data_dict)
    return data_dict

def get_local_data(file):
    dir = current_app.config['SAMPLE_DATA_DIR']
    data = json_dealer.read(dir, file)
    # print(data)
    return data