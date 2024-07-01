$(function () {
    var ENTER_KEY = 13
    var unit = 'ETH';
    var cur = "今天";   // 全局，日期过滤开关
    var pdo = "今天";  // 前一个日期过滤选项

    var flag = false;  // 金额或地址更新flag
    // var pages = 0;  //table_pages
    // optionlist


    function get_ru_args() {  // 获取请求更新参数
        // tr 金额 单位 地址监测 page
        var value = $('.bee-filter #value').val()  //可能为空
        var address = $('.bee-filter #address').val()
        var tropId = tr_option_list.indexOf(cur)
        var unitId = unit_list.indexOf(unit);
        var page;
        if (tr_option_list.indexOf(cur) < tr_option_list.indexOf(pdo)) {
            page = 1
            $('.bee-pagination .jump-ipt').val(1);
        } else {
            if (flag){
                flag = false
                page = 1
                $('.bee-pagination .jump-ipt').val(1);
            }else{
                page = $('.bee-pagination .jump-ipt').val();
            }

        }
        return {"value":value,"address":address,"tropId":tropId,"unitId":unitId,"page":page}

    }

    function ru_bdt(jump_flag=false) {  // request update big deal table;jump_flag为页面跳转标记
        args = get_ru_args()
        // console.log(args)
        if (args!=null){
            $.ajax({
                type: 'POST',
                url: '/ajax/trans/big_deal',
                data: JSON.stringify(args),
                contentType: 'application/json;charset=UTF-8',
                success: function (data) {
                    // 比较table_pages 和 update_pages大小
                    var json_data = jQuery.parseJSON(data);
                    var update_pages = json_data.pages;
                    $('#table_item_total').text(json_data.total); // 更新表格项总数
                    update_bdt(json_data);
                    if (update_pages != pages||jump_flag) {
                        // 更新翻页组件
                        pages = update_pages;
                        $('.pages').text(pages);
                        $('.pagination').empty();
                        $('.pagination').pagination({ // 曲线救国，待优化
                            pageCount: pages,
                            current: json_data.page,
                            // jump: true,
                            callback: function (api) {
                                var data = {
                                    page: api.getCurrent()
                                };

                                $('.bee-pagination .jump-ipt').val(api.getCurrent);

                                ru_bdt();
                            }
                        }, function (api) {
                            // api.setPageCount(update_pages); // test
                        });


                    }


                }
            });

        }
    }

    function update_bdt(data) {  // 表格+图表
        var new_data = data.update_data;
        var columns = data.key_list;
        // console.log(columns)
        var $table = $('#big-transes-table')
        // $("#big-transes-table tbody tr").remove();
        $table.find("tbody tr").remove();
        for (var i = 0; i < new_data.length; i++) {
            var row = "<tr>";
            for (var j = 0; j < columns.length; j++) {

                var tdv = cutstr(new_data[i][columns[j]], 23);
                row += "<td>" + tdv + "</td>";
            }
            row += "</tr>"
            // $("#big-transes-table tbody:last").append(row);
            $table.children("tbody:last").append(row);
        }

        // 处理第0列，添加超链接
        var cid;
        cid=0;
        for (var i = 0; i < new_data.length; i++) {
            var tdv = truncate_str(new_data[i][columns[cid]], 20);
            var td = "<a href='/eth/tsc_detail?hash=" + new_data[i][columns[cid]] + "'>" + tdv + "</a>"
            $table.find('tbody tr:eq(' + i + ') td:eq('+cid+')').html(td)
        }

        // 处理第1列，添加超链接
        cid = 1;
        for (var i = 0; i < new_data.length; i++) {
            var tdv = truncate_str(new_data[i][columns[cid]], 20);
            var td = "<a href='/eth/block_detail/" + new_data[i][columns[cid]] + "'>" + tdv + "</a>"
            $table.find('tbody tr:eq(' + i + ') td:eq('+cid+')').html(td)
        }

        // 处理第3列，添加超链接
        cid = 3;
        for (var i = 0; i < new_data.length; i++) {
            var tdv = truncate_str(new_data[i][columns[cid]], 20);
            var td = "<a href='/eth/address/detail/" + new_data[i][columns[cid]] + "'>" + tdv + "</a>"
            $table.find('tbody tr:eq(' + i + ') td:eq('+cid+')').html(td)
        }


        // 处理第4列，添加超链接
        cid = 4;
        for (var i = 0; i < new_data.length; i++) {
            var tdv = truncate_str(new_data[i][columns[cid]], 20);
            // if transes[i][columns[4]]!=null
            var td = "<a href='/eth/address/detail/" + new_data[i][columns[cid]] + "'>" + tdv + "</a>"
            if (new_data[i]['to_type']) td+='<span><i class="fa fa-cogs"></i></span>'
            $table.find('tbody tr:eq(' + i + ') td:eq('+cid+')').html(td)
        }
    }


    // 单位换算
    var $unit = $('#unit');
    $unit.next().children('.dropdown-item').on('click', function () {

        // var cid = unit_list.indexOf(cur);
        $unit.html($(this).text()+" <i class=\"fa fa-caret-down\"></i>");
        unit = $(this).text()
        ru_bdt();  // 内部比较cur与pdo采取不同策略

    });


    // 按时间筛选
    var $tf = $('#trf-button');
    $tf.next().children('.dropdown-item').on('click', function () {

        var cid = tr_option_list.indexOf(cur);
        $tf.html("按" + $(this).text() + "筛选 <i class=\"fa fa-caret-down\"></i>");
        cur = $(this).text();

        ru_bdt();  // 内部比较cur与pdo采取不同策略
        pdo = cur;
    });

    // 地址检测&金额input
    $('.bee-filter #address').keypress(function (e) { // 跳转

        if (e.which == ENTER_KEY) {
            flag = true;
            ru_bdt();
        }

    });

    $('.bee-filter #value').keypress(function (e) { // 跳转

        if (e.which == ENTER_KEY) {
            flag = true;
            ru_bdt();
        }

    });
    // 页面跳转

     // 翻页 bee-pagination
    $('.bee-pagination .prev').on('click', function () {
        $('.pagination .prev').click();
        // $('.bee-pagination .jump-ipt').val($('.pagination').find('span').text()) // 回调函数里已经

    });

    $('.bee-pagination .next').on('click', function () {
        $('.pagination .next').click();
        // $('.bee-pagination .jump-ipt').val($('.pagination .active').text())

    });

    $('.bee-pagination .jump-ipt').keypress(function (e) { // 跳转
        if (e.which == 13) {
            ru_bdt(jump_flag = true);
        }

    });

     // pagination.js  翻页
    $('.pagination').pagination({  // 总页数改变后， at  147
        pageCount: pages,
        callback: function (api) {
            var data = {
                page: api.getCurrent()
            };
            //  可在此处发送ajax请求
            $('.bee-pagination .jump-ipt').val(api.getCurrent())
            ru_bdt();
        }
    }, function (api) {
        // api.setPageCount(update_pages); // test
    });
    
});


$(function () {

});

// 参考:https://echarts.baidu.com/examples/editor.html?c=line-aqi
var dom = document.getElementById("big-deal");
var myChart = echarts.init(dom,'dark_one');
var app = {};
option = null;


// $.get('/static/data/aqi-beijing.json', function (data) {
    myChart.setOption(option = {

        visualMap: {
            show: false,
            min: 100,
            max: 600,
            dimension: 1,
            inRange: {
                color: ['yellow','red','purple']      //'#ddd','#FAB6B6'
            }
        },
        title: {
            text: '大额交易'
        },
        tooltip: {
            trigger: 'axis',
            // formatter:function (params) {
            //     // return
            // }

        },
        xAxis: {
            // data: data.map(function (item) {
            //     return item[0];
            // }),
            data:dates,
            splitLine: {
                show: false
            }
        },
        yAxis: {

        },
        dataZoom: [{
            startValue: '2014-06-01'
        }, {
            type: 'inside'
        }],
        series: {
            // itemStyle:{
            //     label:{
            //         show:false // 无效
            //     },
            //     normal:{
            //         // color:'#2ec7c9',
            //         lineStyle:{
            //
            //             color:new echarts.graphic.LinearGradient(0, 1, 0, 0,  // 左 下 右 上
            //                 [
            //                     {offset: 0, color: '#00FF00'},
            //                     {offset: 0.5, color: '#3A8EE6'},
            //                     {offset: 0.8, color: '#FAB6B6'},
            //                     {offset: 1, color: '#ddd'}
            //                 ]
            //             )
            //         }
            //     }
            // },
            showSymbol:false,
            name: '交易笔数',
            type: 'line',
            data:exception_trans,
            // data: data.map(function (item) {
            //     return item[1];
            // }),
            // markLine: {
            //     silent: true,
            //     itemStyle: {
            //         normal: { lineStyle: { type: 'solid', color: ['#fff'] }, label: { show: true, position: 'end' } },
            //     },
            //     data: [{
            //         // itemStyle:{
            //         //     normal:{
            //         //         color:'#fff'  // markLine颜色
            //         //     }
            //         // },
            //         yAxis: 50,
            //     }, {
            //         yAxis: 100,
            //     },  {
            //         yAxis: 200
            //     }, {
            //         yAxis: 300
            //     }]
            // }
        }
    });
// });;  // 匹配 getjson
if (option && typeof option === "object") {
    myChart.setOption(option, true);
}