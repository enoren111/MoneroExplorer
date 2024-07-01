<!--
 * @Author: @Jinhao Liu
 * @Date: 2023-04-02 19:26:41
 * Copyright (c) 2023 by @Jinhao Liu, All Rights Reserved. 
-->
# Function Documentation 功能文档
## Transaction Details List Page 交易详情列表页
- url:/xmr/num_money
- function:num_money
- views flie:blueprint/xmr.py
- api params:
  - p:page(页码) int defult 1
  - t:time range selection(时间范围选择) defult day
  - d:download symbol(下载标志) when defult None == true, Download query results(下载查询结果)excel
- return
  - d=='true' 
    - call stack(调用堆栈)
      - xmrreturn.block_return_new
        - xmr_trans_return
          - sb_for_block
            - return query(返回查询)body
          - xmr_search_transaction
            - return result(返回结果)
    - return download object(返回下载对象)
  - d!="true"
    - The call stack is similar, but the query body is different(调用堆栈类似 查询body不同)
    - Return pagination object and other information(返回分页对象以及其他信息)
- template:xmr/num_money.html

## Transaction classification visualization page 交易分类可视化页
- url:/xmr/class_stat
- function:class_stat
- views flie:blueprint/xmr.py
- api params:
  - t:time range selection(时间范围选择) defult day
  - block_trade:The difference between the amount of the bulk transaction(大宗交易区别金额) 
- return
  - call stack(调用堆栈)
    - xmr_trans_class  /Serives/xmr_transactionreturn.py
      - sb_for_block /Serives/xmr_transactionreturn.py
      - xmr_search_transaction /dao/datainterchange.py
    - return query result(返回查询结果)
- template:xmr/class_stat.html

## Transaction Address Statistics 交易地址统计
- url:/xmr/use_stat
- function:use_stat
- views flie:blueprint/xmr.py
- api params:
  - t:time range selection(时间范围选择) defult day
- return
  - call stack(调用堆栈)
    - get_addr_num mysql_dealer.py
      - get_time_range mysql_dealer.py
      - startDb mysql_dealer.py
    - return query result(返回查询结果)
- template:xmr/use_stat.html