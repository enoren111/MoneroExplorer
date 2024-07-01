from Model import dataValidation
from Serives import btcblock, zcashblock
from Serives import btctransaction
from flask import request
from flask import current_app
import math
from utils import ts2t
import json
from config import config
from log import log
import time

log = log.init_logger(config.log_filepath)


def zcash_get_trans_num(height):
    body={
        {
            "query": {
                "term": {"height": height}
            }
        }
    }
    #result=[]
    result = dataValidation.Zcash_DataValidation_block(body)
    return result
zcash_get_trans_num(100)