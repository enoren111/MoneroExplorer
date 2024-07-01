import os


class BaseConfig():
    TABLE_ITEMS_PER_PAGE = 10
    TRANS_FIELDS = ['交易哈希', '所在区块', '时间', '发送方', '接收方', '类型', '手续费(ETH)', '交易额(ETH)']
    BTC_FIELDS = ['交易哈希', '所在区块', '时间', '发送方', '接收方','交易额(BTC)']
    TIME_RANGE_OPTIONS = ['今天', '本周', '本月', '今年', '全部']
    NODE_TB_COL_NAME = ['ID','IP地址','端口','最后在线','客户端','版本','操作系统','地理位置','网络','高度']
    BLOCK_DETAIL_TB_COL_NAME = ['交易哈希','所在区块','时间','发送方','接收方','类型','手续费','交易额(ETH)']
    UNITS = ['ETH','USD','RMB']
    VALUE_ACC = 9  # 交易value精度
    CONTRACT_TB_FIELDS = ['合约地址','合约名字','编译器版本','账户余额','交易总数','编译器参数','已验证','验证日期']  # 合约表格字段
    TRANS_TB_KEYS = ['hash', 'blockNumber', 'time', 'from', 'to', 'trans_type', 'trans_fee', 'value']  # 更新table用
    BLOCK_TB_KEYS = ['height', 'hash', 'miner', 'time', 'trans_num', 'size', 'uncles', ['cost','block_reward'], ['cost','total_value']]
    BIG_DEAL_TB_KEYS = ['hash','blockNumber','time','from', 'to','value']
    ADDRESS_TB_KEYS = ['rank','address','trans_num','value', 'value']
    NODE_TB_KEYS = ['nodeID','nodeIP','nodePort','lastOnline', 'client','clientVersion','os','country','asnum','height']
    MAX_TR_ID = 4
    SAMPLE_DATA_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))+'/darkbee/static/data/sample'  # 根目录
    ONLINE_MODE = True

class OnlineConfig(BaseConfig):
    ONLINE_MODE = False
class OfflineConfig(BaseConfig):
    ONLINE_MODE = True

config = {
    'development': BaseConfig,
    'online':OnlineConfig,
    'offline':OfflineConfig
}
