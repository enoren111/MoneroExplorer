'''
Author: @Jinhao Liu
Date: 2023-03-27 15:09:12
Copyright (c) 2023 by @Jinhao Liu, All Rights Reserved.
'''
'''
Author: @Jinhao Liu
Date: 2023-03-27 15:09:12
Copyright (c) 2023 by @Jinhao Liu, All Rights Reserved. 
'''
'''
Author: @Jinhao Liu
Date: 2023-03-27 15:09:12
Copyright (c) 2023 by @Jinhao Liu, All Rights Reserved. 
'''
from flask import Flask
# from bee_var import ESManager
from config import config
from log import log
import os
from flask_moment import Moment

log = log.init_logger(config.log_filepath)
# app = Flask(__name__,template_folder='../templates')
from bee_var import ESManager
es = ESManager(config.es_ip,config.es_port,config.time_out)

from settings import BaseConfig
from blueprint.bee import bee_bp
from blueprint.eth import eth_bp
from blueprint.btc import btc_bp
from blueprint.zcash import zcash_bp
from blueprint.xmr import xmr_bp
# 如果这个文件不是当做一个模块被导入时，就会执行这个里面的代码
if __name__ == '__main__':
    app = Flask(__name__)  # 创建 Flask 应用

    config_name = os.getenv('FLASK_ENV', 'development')
    # print(config_name)
    app.config.from_object(BaseConfig)
    app.register_blueprint(bee_bp)
    app.register_blueprint(eth_bp)
    app.register_blueprint(btc_bp)
    app.register_blueprint(zcash_bp)
    app.register_blueprint(xmr_bp)
    moment = Moment(app)
    # moment.init_app()
  # 设置用户登录视图函数 endpoin

    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


    flag = es.tryagain_instance()  ##标记es对象是否创建成功，如果失败，则不启动项目
    if flag:
        log.info("es对象创建成功")
        log.info("项目启动成功，开始打印日志")
        # app.run(debug=True)
    else:
        log.debug("es对象创建失败,请检查错误")
    app.run( debug=True)

