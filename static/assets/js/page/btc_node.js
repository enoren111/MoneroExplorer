
$(function () {
    // pagination.js  翻页
    $('.pagination').pagination({  // 总页数改变后， at  147
        pageCount: pages,
        callback: function (api) {
            var data = {
                page: api.getCurrent()
            };
            //  可在此处发送ajax请求
            $('.bee-pagination .jump-ipt').val(api.getCurrent())
            ru_table();
        }
    }, function (api) {
        // api.setPageCount(update_pages); // test
    });
    

    function get_ru_args() {  // 获取请求更新参数

        var page = $('.bee-pagination .jump-ipt').val();;

        return {"st":'search_text',"page":page}

    }

    function ru_table(jump_flag=false) {  // request update big deal table;jump_flag为页面跳转标记
        args = get_ru_args()
        // console.log(args)
        if (args!=null){
            $.ajax({
                type: 'POST',
                url: '/ajax/node',
                data: JSON.stringify(args),
                contentType: 'application/json;charset=UTF-8',
                success: function (data) {
                    // 比较table_pages 和 update_pages大小
                    var json_data = jQuery.parseJSON(data);
                    var update_pages = json_data.pages;
                    $('#table_item_total').text(json_data.total); // 更新表格项总数
                    update_table(json_data);
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

                                ru_table();
                            }
                        }, function (api) {
                            // api.setPageCount(update_pages); // test
                        });


                    }


                }
            });

        }
    }


    function update_table(data) {  // 表格+图表
        var new_data = data.update_data;
        var columns = data.key_list;
        // console.log(columns)
        var $table = $('#node-table')
        // $("#big-transes-table tbody tr").remove();
        $table.find("tbody tr").remove();
        for (var i = 0; i < new_data.length; i++) {
            var row = "<tr>";
            for (var j = 0; j < columns.length; j++) {

                var tdv = truncate_str(get_dict_key_value(new_data[i],columns[j]), 23);
                row += "<td>" + tdv + "</td>";
            }
            row += "</tr>"
            // $("#big-transes-table tbody:last").append(row);
            $table.children("tbody:last").append(row);
        }
        // 隐藏行字段
        var tharr = $table.find('th');
        for (var i=0;i<tharr.length;i++){
            if (tharr[i].hasAttribute('hidden')){
                $table.find('tr').find('td:eq(' + i + ')').attr({"hidden":"hidden"});
            }
        }

        var cid;
         // 处理第1列，添加超链接
        cid = 0;
        for (var i = 0; i < new_data.length; i++) {
            var tdv = truncate_str(get_dict_key_value(new_data[i],columns[cid]), 20);
            var td = "<a href='/eth/node/" + new_data[i][columns[cid]] + "'>" + tdv + "</a>"
            $table.find('tbody tr:eq(' + i + ') td:eq('+cid+')').html(td)
        }
    }


    // 0111 翻页 bee-pagination 不可用
    $('.bee-pagination .prev').on('click', function () {
        $('.pagination .prev').click();
        // $('.pagination .page-item:first-child .page-link').click();
    });

    $('.bee-pagination .next').on('click', function () {
        $('.pagination .next').click();
        // $('.pagination .page-item:last-child .page-link').click();

    });

    $('.bee-pagination .jump-ipt').keypress(function (e) { // 跳转
        if (e.which == 13) {
            ru_table(jump_flag = true);
        }

    });


    // 0111 选择字段
    // args #fields-filter #node-table fields 怎么才能写成插件？
    $('#fields-filter').next().children('.dropdown-item').on('click', function (e) {
        if ($(this).hasClass('item-checked')) {
            $(this).removeClass('item-checked');
            $(this).find('i').removeClass('fa-check-square-o');
            $(this).find('i').addClass('fa-square-o');

            $('#node-table tr').find('td:eq(' + $(this).index() + ')').removeAttr("hidden");
            $('#node-table tr').find('th:eq(' + $(this).index() + ')').removeAttr("hidden");

            // $('#node-table tr').find('td:eq(' + $(this).index() + ')').show();
            // $('#node-table tr').find('th:eq(' + $(this).index() + ')').show();
        } else {
            $(this).addClass('item-checked');
            $(this).find('i').removeClass('fa-square-o');
            $(this).find('i').addClass('fa-check-square-o');

            $('#node-table tr').find('td:eq(' + $(this).index() + ')').attr({"hidden":"hidden"});
            $('#node-table tr').find('th:eq(' + $(this).index() + ')').attr({"hidden":"hidden"});

            // $('#node-table tr').find('td:eq(' + $(this).index() + ')').hide();
            // $('#node-table tr').find('th:eq(' + $(this).index() + ')').hide();
        }
        e.stopPropagation();
    });
});




$(function () {
   setTimeout(function () {
            window.onresize = function () {
                // myChart.resize();
                myChart1.resize();
            }
        }, 200);

    // 轮播
    $('#node-banner').slick({
        dots:true,
        slidesToShow: 1,
        slidesToScroll: 1,
        // infinite: true,
        arrows:false,

        autoplay:true,
        autoplaySpeed: 5000

    });


// var series1 = []
// var series2 = []
// var series3 = []
// var series4 = []
//
//     for (var i=0;i<30;i++){
//         series1.push(cv_series[i])
//         series2.push(ct_series[i])
//         series3.push(asn_series[i])
//         series4.push(co_series[i])
//     }



var test_dist=[["a",85934,"70.00%"],["b",40004,"30.00%"]]

var theme = 'dark_one';
// 客户端分布饼图
// 客户端版本
var dom = document.getElementById("version-pie");
var myChart1 = echarts.init(dom,theme);
var app = {};
option1 = null;
app.title = '环形图';

option1 = {
    title:{
        text:'客户端版本分布',
        x:'center'
    },
    tooltip: {
        trigger: 'item',
        // formatter: "{a} <br/>{b}: {c} ({d}%)"
        formatter:function (param) {
            return param.name+" <br/>"+param.value+": "+param.data['p']
        }
    },
    // legend: {
    //     orient: 'vertical',
    //     x: 'left',
    //     data:['直接访问','邮件营销','联盟广告','视频广告','搜索引擎']
    // },
    series: [
        {
            name:'客户端版本',
            type:'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: {
                normal: {
                    show: false,
                    position: 'center'
                }
                // ,emphasis: {
                //     show: true,
                //     textStyle: {
                //         fontSize: '30',
                //         fontWeight: 'bold'
                //     }
                // }
            },
            labelLine: {
                normal: {
                    show: false
                }
            },
            // data:test_dist
            data:btc_cv_series
        }
    ]
};
;
if (option1 && typeof option1 === "object") {
    myChart1.setOption(option1, true);
}

// 国家分布
var dom = document.getElementById("country-pie");
var myChart2 = echarts.init(dom,theme);

option2 = {
    title:{
        text:'节点国家分布',
        x:'center'
    },
    tooltip: {
        trigger: 'item',
        // formatter: "{a} <br/>{b}: {c} ({d}%)"
        formatter:function (param) {
            return param.name+" <br/>"+param.value+": "+param.data['p']
        }
    },
    // legend: {
    //     orient: 'vertical',
    //     x: 'left',
    //     data:['直接访问','邮件营销','联盟广告','视频广告','搜索引擎']
    // },
    series: [
        {
            name:'访问来源',
            type:'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: {
                normal: {
                    show: false,
                    position: 'center'
                }
                ,emphasis: {
                    show: true,
                    textStyle: {
                        fontSize: '30',
                        fontWeight: 'bold'
                    }
                }
            },
            labelLine: {
                normal: {
                    show: false
                }
            },
            data:btc_ct_series
        }
    ]
};
;
if (option2 && typeof option2 === "object") {
    myChart2.setOption(option2, true);
}


var dom = document.getElementById("asn-pie");
var myChart3 = echarts.init(dom,theme);
option3 = {
    title:{
        text:'节点网络分布',
        x:'center'
    },
    tooltip: {
        trigger: 'item',
        // formatter: "{a} <br/>{b}: {c} ({d}%)"
        formatter:function (param) {
            return param.name+" <br/>"+param.value+": "+param.data['p']
        }
    },
    // legend: {
    //     orient: 'vertical',
    //     x: 'left',
    //     data:['直接访问','邮件营销','联盟广告','视频广告','搜索引擎']
    // },
    series: [
        {
            name:'访问来源',
            type:'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: {
                normal: {
                    show: false,
                    position: 'center'
                }
                ,emphasis: {
                    show: true,
                    textStyle: {
                        fontSize: '30',
                        fontWeight: 'bold'
                    }
                }
            },
            labelLine: {
                normal: {
                    show: false
                }
            },
            data:btc_asn_series
        }
    ]
};
;
if (option3 && typeof option3 === "object") {
    myChart3.setOption(option3, true);
}

var dom = document.getElementById("os-pie");
var myChart4 = echarts.init(dom,theme);
option4 = {
    title:{
        text:'节点协议版本分布',
        x:'center'
    },
    tooltip: {
        trigger: 'item',
        // formatter: "{a} <br/>{b}: {c} ({d}%)"
        formatter:function (param) {
            return param.name+" <br/>"+param.value+": "+param.data['p']
        }
    },
    // legend: {
    //     orient: 'vertical',
    //     x: 'left',
    //     data:['直接访问','邮件营销','联盟广告','视频广告','搜索引擎']
    // },
    series: [
        {
            name:'访问来源',
            type:'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: {
                normal: {
                    show: false,
                    position: 'center'
                }
                ,emphasis: {
                    show: true,
                    textStyle: {
                        fontSize: '30',
                        fontWeight: 'bold'
                    }
                }
            },
            labelLine: {
                normal: {
                    show: false
                }
            },
            data:btc_co_series
        }
    ]
};
;
if (option4 && typeof option4 === "object") {
    myChart4.setOption(option4, true);
}
});


$(function () {

});