$(function () {

    $('#statistical-info').slick({
        dots:true,
        slidesToShow: 1,
        slidesToScroll: 1,
        // infinite: true,
        arrows:false,

        autoplay:false,
        autoplaySpeed: 2000
    });


    setTimeout(function () {
        window.onresize = function () {
            myChart.resize();
            myChart2.resize();
            myChart3.resize();
            myChart4.resize();
            myChart5.resize();
            myChart6.resize();
        }
    }, 200);


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
        splitLine:{
            show:false
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
var myChart2 = echarts.init(dom, theme);
var app = {};
// option = null;
option2 = {
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
if (option2 && typeof option2 === "object") {
    myChart2.setOption(option2, true);
}


// daily_trans_num
var dom = document.getElementById("daily_trans_num");
var myChart3 = echarts.init(dom, theme);
var app = {};
// option = null;
option3 = {
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
if (option3 && typeof option3 === "object") {
    myChart3.setOption(option3, true);
}

//ec daily_trans_type
var dom = document.getElementById("daily_trans_type");
var myChart4 = echarts.init(dom, theme);
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
            name:'交易类型',
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
    myChart4.setOption(option, true);
}

//
var dom = document.getElementById("daily_new_contract");
var myChart5 = echarts.init(dom, theme);
option = {
    color: ['#3398DB'],
    title: {
        text: '每日新发布合约数',
        x: 'center'
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {            // 坐标轴指示器，坐标轴触发有效
            type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
        }
    },
    grid: {
        left: '3%',
        right: '3%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: [
        {
            type: 'category',
            data: dates,
            axisTick: {
                alignWithLabel: true
            },
            axisLabel: {
                formatter: function (value, idx) {
                    var date = new Date(value);


                    // return idx === 0 ? value : [date.getMonth() + 1, date.getDate()].join('-');
                    return idx === 0 ? value : date.getMonth() === 0 && date.getDate() === 1 ? value : [date.getMonth() + 1, date.getDate()].join('-');
                },
                // interval: 0

            },
        }
    ],
    yAxis: [
        {
            type: 'value',
            axisLabel: {}
        }
    ],
    series: [
        {
            name: '新发布合约',
            type: 'bar',
            barWidth: '60%',
            data: values4
        }
    ]
};

if (option && typeof option === "object") {
    myChart5.setOption(option, true);
}


var dom = document.getElementById("daily_address");
var myChart6 = echarts.init(dom, theme);
option = {
    title: {
        text: '每日活跃地址与新增地址数',
        x: 'center',
        // align: 'right',

    },
    grid: {
        left: '3%',
        right: '3%',
        bottom: '3%',
        containLabel: true
    },
    tooltip: {
        trigger: 'axis'
    },
    legend: {
        x: 'left',
        orient: 'vertical',
        data: ['活跃地址', '新增地址'],

    },
    calculable: true,
    xAxis: [
        {
            type: 'category',
            data: dates,

            axisLabel: {
                formatter: function (value, idx) {
                    var date = new Date(value);


                    // return idx === 0 ? value : [date.getMonth() + 1, date.getDate()].join('-');
                    return idx === 0 ? value : date.getMonth() === 0 && date.getDate() === 1 ? value : [date.getMonth() + 1, date.getDate()].join('-');
                },
                // interval: 0

            }
        }
    ],
    yAxis: [
        {
            type: 'value',
            axisLabel: {}
        }
    ],
    series: [
        {
            name: '活跃地址',
            type: 'line',
            data: values6,

        },
        {
            name: '新增地址',
            type: 'line',
            data: values7,

        }
    ]
};
if (option && typeof option === "object") {
    myChart6.setOption(option, true);
}