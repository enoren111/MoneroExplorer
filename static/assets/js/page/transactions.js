// echart


$(function () {

    // banner
    $('#trans-statistical-info').slick({
        dots:true,
        slidesToShow: 1,
        slidesToScroll: 1,
        // infinite: true,
        arrows:false,

        autoplay:true,
        autoplaySpeed: 2000
    });



    // 过滤module组
    var cur = "今天";   // 全局，日期过滤开关
    var pdo = "今天";  // 前一个日期过滤选项
    var update_pages = transes_pages;
    // var jump_flag = false;  // 无效


    setTimeout(function () {
        window.onresize = function () {
            // myChart.resize();
            // myChart1.resize();
            // myChart2.resize();
        }
    }, 200);

    function get_trans_f_args() {

        var order;
        if ($("#switch").hasClass("switched")) {
            order = 'asc';
        } else {
            order = 'desc';
        }

        var page;
        if (optionlist.indexOf(cur) < optionlist.indexOf(pdo)) {
            page = 1
            $('.bee-pagination .jump-ipt').val(1);
        } else {
            page = $('.bee-pagination .jump-ipt').val();
        }

        return {"order": order, "page": page, "tr_op": optionlist.indexOf(cur)}
    }

    function update_trans(data) {  // 表格+图表
        var transes = data.transes;
        var columns = data.cols;
        // console.log(columns)
        $("#transes-table tbody tr").remove();
        for (var i = 0; i < transes.length; i++) {
            var row = "<tr>";
            for (var j = 0; j < columns.length; j++) {

                var tdv = cutstr(transes[i][columns[j]], 23);
                row += "<td>" + tdv + "</td>";
            }
            row += "</tr>"

            $("#transes-table tbody:last").append(row);
        }


        // 隐藏行字段
        var $table = $("#transes-table")
        var tharr = $table.find('th');
        for (var i=0;i<tharr.length;i++){
            if (tharr[i].hasAttribute('hidden')){
                $table.find('tr').find('td:eq(' + i + ')').attr({"hidden":"hidden"});
            }
        }

        // 处理第0列，添加超链接
        for (var i = 0; i < transes.length; i++) {
            var tdv = cutstr(transes[i][columns[0]], 20);
            var td = "<a href='/eth/tsc_detail?hash=" + transes[i][columns[0]] + "'>" + tdv + "</a>"
            $('#transes-table tbody tr:eq(' + i + ') td:eq(0)').html(td)
        }

        // 处理第1列，添加超链接
        for (var i = 0; i < transes.length; i++) {
            var tdv = cutstr(transes[i][columns[1]], 20);
            var td = "<a href='/eth/block_detail/" + transes[i][columns[1]] + "'>" + tdv + "</a>"
            $('#transes-table tbody tr:eq(' + i + ') td:eq(1)').html(td)
        }

        // 处理第3列，添加超链接
        for (var i = 0; i < transes.length; i++) {
            var tdv = cutstr(transes[i][columns[3]], 20);
            var td = "<a href='/eth/address/detail/" + transes[i][columns[3]] + "'>" + tdv + "</a>"
            $('#transes-table tbody tr:eq(' + i + ') td:eq(3)').html(td)
        }


        // 处理第4列，添加超链接
        for (var i = 0; i < transes.length; i++) {
            var tdv = cutstr(transes[i][columns[4]], 20);
            // if transes[i][columns[4]]!=null
            var td = "<a href='/eth/address/detail/" + transes[i][columns[4]] + "'>" + tdv + "</a>"
            if (transes[i]['to_type']) td+='<span><i class="fa fa-cogs"></i></span>'
            $('#transes-table tbody tr:eq(' + i + ') td:eq(4)').html(td)
        }

    }

    function ru_trans(jump_flag = false) {  // request update 交易表格
        filter_args = get_trans_f_args();

        if (filter_args != null) {
            $.ajax({
                type: 'POST',
                url: '/ajax/transactions/filter',
                data: JSON.stringify(filter_args),
                contentType: 'application/json;charset=UTF-8',
                success: function (data) {
                    json_data = jQuery.parseJSON(data);
                    update_pages = json_data.pages;

                    $('.transes_total').text(json_data.total);

                    update_trans(json_data);

                    if (update_pages != transes_pages||jump_flag) {
                        transes_pages = update_pages;
                        $('.transes_pages').text(update_pages); // 上下翻页情况下值不变
                        $('.pagination').empty();
                        $('.pagination').pagination({ // 曲线救国，待优化
                            pageCount: transes_pages,
                            current: json_data.page,
                            // jump: true,
                            callback: function (api) {
                                var data = {
                                    page: api.getCurrent(),
                                    name: 'mss',
                                    say: 'oh'
                                };
                                //  可在此处发送ajax请求
                                // api.setPageCount(update_pages);
                                // console.log('d')
                                $('.bee-pagination .jump-ipt').val(api.getCurrent);

                                ru_trans();
                            }
                        }, function (api) {
                            // api.setPageCount(update_pages); // test
                        });
                    }


                }
            });
        }
    }

    // order checkbox
    $("#switch").on('click', function () {
        if ($("#switch").hasClass("switched")) {
            $("#switch").removeClass("switched"); // 降序 左
            ru_trans();

        }
        else {
            $("#switch").addClass("switched");
            //  升序 右
            ru_trans();

        }
    });

    // 按时间筛选
    var $tf = $('#time-filter');
    $tf.next().children('.dropdown-item').on('click', function () {

        var cid = optionlist.indexOf(cur);
        $tf.html("按" + $(this).text() + "筛选 <span class='oi oi-elevator'></span>");
        cur = $(this).text();

        ru_trans();  // 内部比较cur与pdo采取不同策略
        pdo = cur;
    });

    // 选择字段
    $('#fields-filter').next().children('.dropdown-item').on('click', function (e) {
        if ($(this).hasClass('item-checked')) {
            $(this).removeClass('item-checked');
            $(this).find('i').removeClass('fa-check-square-o');
            $(this).find('i').addClass('fa-square-o');

            $('#transes-table tr').find('td:eq(' + $(this).index() + ')').removeAttr("hidden");
            $('#transes-table tr').find('th:eq(' + $(this).index() + ')').removeAttr("hidden");

        //     $('#transes-table tr').find('td:eq(' + $(this).index() + ')').show();
        //     $('#transes-table tr').find('th:eq(' + $(this).index() + ')').show();
        } else {
            $(this).addClass('item-checked');
            $(this).find('i').removeClass('fa-square-o');
            $(this).find('i').addClass('fa-check-square-o');


            $('#transes-table tr').find('td:eq(' + $(this).index() + ')').attr({"hidden":"hidden"});
            $('#transes-table tr').find('th:eq(' + $(this).index() + ')').attr({"hidden":"hidden"});

            // $('#transes-table tr').find('td:eq(' + $(this).index() + ')').hide();
            // $('#transes-table tr').find('th:eq(' + $(this).index() + ')').hide();
        }
        e.stopPropagation();
    });

    // pagination.js  翻页
    $('.pagination').pagination({  // 总页数改变后， at  147
        pageCount: transes_pages,
        callback: function (api) {
            var data = {
                page: api.getCurrent(),
                name: 'mss',
                say: 'oh'
            };
            //  可在此处发送ajax请求
            $('.bee-pagination .jump-ipt').val(api.getCurrent())
            ru_trans();
        }
    }, function (api) {
        // api.setPageCount(update_pages); // test
    });

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
        // 自带页码更新属性
        // alert($(this).val());
        if (e.which == 13) {
            ru_trans(jump_flag = true);
        }

    });


});


var theme = 'dark_one';

// big-deal echarts
// 参考https://echarts.baidu.com/examples/editor.html?c=confidence-band
var dom = document.getElementById("big-deal");
var myChart = echarts.init(dom, theme);
option = {
    title: {
        text: '每日大额交易数(金额≥1000 ETH)',
        // subtext: '数据来自西安兰特水电测控技术有限公司',
        x: 'center',
        // align: 'right',
    },
    xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
            formatter: function (value, idx) {
                var date = new Date(value);
                // return idx === 0 ? value : [date.getMonth() + 1, date.getDate()].join('-');
                return idx === 0 ? value : date.getMonth() === 0 && date.getDate() === 1 ? value : [date.getMonth() + 1, date.getDate()].join('-');
            }
        },
        splitLine: {
            show: false
        },
        boundaryGap: false
    },
    grid: {
        left: '3%',
        right: '3%',
        bottom: '3%',
        containLabel: true
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross',
            animation: false,
            label: {
                backgroundColor: '#ccc',
                borderColor: '#aaa',
                borderWidth: 1,
                shadowBlur: 0,
                shadowOffsetX: 0,
                shadowOffsetY: 0,
                textStyle: {
                    color: '#222'
                }
            }
        },
        // formatter: function (params) {
        //     return params[0].value + '<br />' + params[0].name;
        // }
    },
    yAxis: {
        type: 'value',
        axisLabel: {}
    },
    series:
        [{
            data: values1,
            type: 'line',
            // smooth: true,
            // showSymbol: false
        }]
}
;
if (option && typeof option === "object") {
    myChart.setOption(option, true);
}

// daily_trans_sum
var dom = document.getElementById("daily_trans_sum");
var myChart1 = echarts.init(dom, theme);
option1 = {
    title: {
        text: '每日交易金额 (ETH)',
        x: 'center'
    },
    xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
            formatter: function (value, idx) {
                var date = new Date(value);


                // return idx === 0 ? value : [date.getMonth() + 1, date.getDate()].join('-');
                return idx === 0 ? value : date.getMonth() === 0 && date.getDate() === 1 ? value : [date.getMonth() + 1, date.getDate()].join('-');
            },
            // interval: 0

        },
        boundaryGap: false
    },
    grid: {
        left: '3%',
        right: '3%',
        bottom: '3%',
        containLabel: true
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross',
            animation: false,
            label: {
                backgroundColor: '#ccc',
                borderColor: '#aaa',
                borderWidth: 1,
                shadowBlur: 0,
                shadowOffsetX: 0,
                shadowOffsetY: 0,
                textStyle: {
                    color: '#222'
                }
            }
        },
        formatter: function (params) {
            return params[0].name + '<br />' + params[0].value;
        }
    },
    yAxis: {
        type: 'value',
        axisLabel: {}

    },
    series:
        [{
            data: values2,
            type: 'line',
            // smooth: true,
            // showSymbol: false
        }]
}
;
if (option1 && typeof option1 === "object") {
    myChart1.setOption(option1, true);
}


// daily_trans_num
var dom = document.getElementById("daily_trans_num");
var myChart2 = echarts.init(dom, theme);
option2 = {
    title: {
        text: '每日交易笔数',
        x: 'center'
    },
    xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
            formatter: function (value, idx) {
                var date = new Date(value);


                // return idx === 0 ? value : [date.getMonth() + 1, date.getDate()].join('-');
                return idx === 0 ? value : date.getMonth() === 0 && date.getDate() === 1 ? value : [date.getMonth() + 1, date.getDate()].join('-');
            },
            // interval: 0
        },
        boundaryGap: false
    },
    grid: {
        left: '3%',
        right: '3%',
        bottom: '3%',
        containLabel: true
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross',
            animation: false,
            label: {
                backgroundColor: '#ccc',
                borderColor: '#aaa',
                borderWidth: 1,
                shadowBlur: 0,
                shadowOffsetX: 0,
                shadowOffsetY: 0,
                textStyle: {
                    color: '#222'
                }
            }
        },
        formatter: function (params) {
            return params[0].name + '<br />' + params[0].value;
        }
    },
    yAxis: {
        type: 'value',
        axisLabel: {}

    },
    series:
        [{
            data: values3,
            type: 'line',
            // smooth: true,
            // showSymbol: false
        }]
}
;
if (option2 && typeof option2 === "object") {
    myChart2.setOption(option2, true);
}

//ec daily_trans_type
var dom = document.getElementById("daily_trans_type");
var myChart3 = echarts.init(dom, theme);
// var app = {};
option = {
    title: {
        text: '交易类型统计',
        left: 'center'
    },
    tooltip: {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c} ({d}%)"
    },
    legend: {
        // orient: 'vertical',
        // top: 'middle',
        bottom: 10,
        left: 'center',
        data: ['合约创建', '合约调用', '普通交易']
    },
    series: [
        {
            name: '交易类型',
            type: 'pie',
            radius: '65%',
            center: ['50%', '50%'],
            selectedMode: 'single',
            data: [

                {value: values8[2], name: '合约创建'},
                {value: values8[1], name: '合约调用'},
                {value: values8[0], name: '普通交易'}
            ],
            labelLine: {
                normal: {
                    show: false
                }
            },
            label: {
                normal: {
                    formatter: '{c}',
                    position: 'inside'
                }
            },
            itemStyle: {
                emphasis: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }
    ]
};


if (option && typeof option === "object") {
    myChart3.setOption(option, true);
}