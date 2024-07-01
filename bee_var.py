from elasticsearch import Elasticsearch
from config import config
from log import log

log = log.init_logger(config.log_filepath)

#Syc btctag
mybtctag_index = 'my_btc_tag_new2,my_btc_tag_cluster'
btctagclu_index = 'my_btc_tag_cluster'
btctagseed_index = 'btc_tag2'
btctagall_index = 'addr_cluster_test'

api_url="http://10.112.60.13/getcluster"
#Syc BtcMix
mybtcmix_index = 'btc_mix_tx'
#SYC Btc Big Transactions
mybtctrans_index = 'my_btc_trans'
#Syc Total Addr
total_addr_index='addr_cluster_test'
#Syc cluster_info
cluster_info_index = 'clusters'
perPage_10=10
perPage = 10 ##分页一页显示的数量
block_offline_file = "btc_blocks_sample.json"
trans_offline_flie = "btc_transactions_sample.json"
btc_tag = "btc_tag.json"
block_num_offline = 619140
block_fields = {'0': '高度', '1': '哈希值', '2': '矿工', '3': '出块时间', '4': '交易数', '5': '区块大小(字节)', '6': '叔块', '7': '出块奖励(ETH)',
                '8': '总交易额'}
trans_type={'0': '普通交易', '1': '合约交易', '2': '创建合约'}
btcblock_index= "bitcoin_block1"
btctransaction_index = 'btc_tx_new'
block_raw = 'raw'
transaction_raw ='raw'
btctag_index = 'my_btc_tag_new2'
# 更新后的新索引名称
btcblock_newindex='btc_blk_new'

btc_tag_cluster='my_btc_tag_cluster'
#cluster_search
btc_cluster_search = 'addr_cluster_test'

btctransaction_newindex='btc_tx_new'

darknet_clash = 'darknet_btc_crush'

#最新集群信息标签
my_cluster_info = 'my_clusters3'

# 夹带信息的索引信息
btc_carrymessage_index='bitcoin_information'
carrymessage_type='raw'
# btc_carrymessage_index='newdecode'
# carrymessage_type='_doc'


BTC_FIELDS = ['交易哈希', '所在区块', '时间', '发送方', '接收方','交易额(BTC)']
VALUE_ACC = 9  # 交易value精度

class ESManager(object): ###类的名字大写
    instance =None
    es_ip = None
    es_port=None
    time_out=600

    def __init__(self,ip,port,timeout):
        self.time_out=timeout
        self.es_ip=ip
        self.es_port=port

    def get_instance(self):
        try:
            es = Elasticsearch(host=self.es_ip,port=self.es_port,timeout=self.time_out)
        except Exception as e:
            log.error(e)
            return 0
        else:
            log.info("es创建成功")

            self.instance = es
            return 1

    def tryagain_instance(self): ##保证创建es对象成功，失败次数超过五次则创建失败
        count =0
        while count < 5:
            # print("es yes")
            flag = self.get_instance()
            if flag:
                log.info("es对象创建成功")
                break
            else:
                count = count+1
        if count>=5:
            # print("es no")

            log.info("es对象创建失败")
            return 0
        return 1


