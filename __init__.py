import os
import json
import math
import sys
sys.path.append('..')

from flask import Flask, render_template, request, jsonify
from blueprint.bee import bee_bp
from blueprint.eth import eth_bp
from blueprint.btc import btc_bp
from blueprint.zcash import zcash_bp
from blueprint.xmr import xmr_bp

from settings import BaseConfig
from extensions import moment
from flask import redirect, url_for
from flask_login import logout_user
from flask import Blueprint, render_template, request
from flask import render_template, url_for
from flask_login import current_user, login_required,LoginManager,login_user
from mysql_dealer import mysql_dealer
from log import log
from config import config
from flask_login import UserMixin  # 引入用户基类

app = Flask(__name__)  # 创建 Flask 应用

config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(BaseConfig)
app.register_blueprint(bee_bp)
app.register_blueprint(eth_bp)
app.register_blueprint(btc_bp)
app.register_blueprint(zcash_bp)
app.register_blueprint(xmr_bp)

moment.init_app(app)

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)
    register_blueprints(app)
    register_extensions(app)
    return app


def register_blueprints(app):
    app.register_blueprint(bee_bp)
    app.register_blueprint(eth_bp)
    app.register_blueprint(btc_bp)
    app.register_blueprint(zcash_bp)


def register_extensions(app):
    moment.init_app(app)

