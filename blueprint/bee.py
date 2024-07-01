from flask import redirect, url_for
from flask_login import logout_user
from flask import Blueprint, render_template, request
from flask import render_template, url_for
from flask_paginate import get_page_parameter, Pagination

from Serives import blockreturn
from Serives.zcash_addrtag import get_query_history, get_trans_query_history
from bee_var import perPage_10

bee_bp = Blueprint('bee',__name__)


@bee_bp.route('/', methods=['GET', 'POST'])
def index():
    latestTransList, context = blockreturn.btc_home_show()
    return render_template('btc/btc_home.html', latestTransList=latestTransList, **context)
@bee_bp.route('/i2p_senior_query', methods=['GET', 'POST'])
def i2p_senior_query():
    perpage = 50  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    count, list = get_query_history(start, perpage)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='history')
    return render_template('btc/i2p_senior_query.html', list=list, pagination=pagination)
@bee_bp.route('/i2p_query_history', methods=['GET', 'POST'])
def i2p_query_history():
    perpage = 50  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    count, list = get_query_history(start, perpage)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='history')
    return render_template('btc/i2p_query_hisory.html', list=list, pagination=pagination)
@bee_bp.route('/trans_senior_query', methods=['GET', 'POST'])
def trans_senior_query():
    perpage = 50  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    count, list = get_trans_query_history(start, perpage)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='history')
    return render_template('btc/trans_senior_query.html',list=list, pagination=pagination)

@bee_bp.route('/query_history', methods=['GET', 'POST'])
def query_history():
    perpage = 50  # pagination默认
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * perpage
    count, list = get_trans_query_history(start, perpage)
    pagination = Pagination(bs_version=4, page=page, total=count, per_page=perpage, record_name='history')
    return render_template('btc/query_history.html',list=list, pagination=pagination)

