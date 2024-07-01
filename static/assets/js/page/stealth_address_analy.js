$(function () {

   // 参考 https://echarts.baidu.com/examples/editor.html?c=mix-zoom-on-value
var dom = document.getElementById("active_stealth_bar");
var myChart = echarts.init(dom,'dark_one');
var app = {};
option = null;
myChart.showLoading();

$.get('/btc/stealth_address_trans', function (obama_budget_2012) {
    myChart.hideLoading();
    name=[1,2,3,4];
    option = {
        tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow',
                label: {
                    show: true,
                    color:'#000'
                }
            }
        },
        toolbox: {
            feature: {
                mark: {show: true},
//                dataView: {show: true, readOnly: false},
                magicType: {show: true, type: ['line', 'bar']},
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        calculable : true,
        grid: {
            top: '10%',
            left: '3%',
            right: '3%',
            containLabel: true
        },
        xAxis: [
            {
                type : 'category',
                data : obama_budget_2012.end_date
            }
        ],
        yAxis: [
            {
                type : 'value',
                name : 'Stealth Address 日交易笔数',
                data : obama_budget_2012.trans_num
            }
        ],
        dataZoom: [
            {
                show: true,
                start: 94,
                end: 100
            },
            {
                type: 'inside',
                start: 94,
                end: 100
            }
        ],
        series : [
            {
                name: '交易数',
                type: 'bar',
                data: obama_budget_2012.trans_num
            }
//            {
//                name: '交易金额',
//                type: 'bar',
//                data: obama_budget_2012.trans_sum
//            }
        ]
    };

    myChart.setOption(option);

});
if (option && typeof option === "object") {
    myChart.setOption(option, true);
};
});

//---------------------------------------------------------------
