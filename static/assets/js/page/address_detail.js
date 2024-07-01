$(function () {
    $('#chart-group').slick({
        dots:true,
        slidesToShow: 1,
        slidesToScroll: 1,
        // infinite: true,
        arrows:false,

        autoplay:false,
        autoplaySpeed: 2000



    });


        /// select
    $('#balance-select').on('change', function () {

        // 余额换算
        var unit =  $(this).children('option:selected').index();

        $(this).prev().text(unit)
    });

    // echart
    var theme = 'dark_one';

        setTimeout(function () {
            window.onresize = function () {
                myChart1.resize();
                myChart2.resize();
            }
        }, 200);


        $('ul[data-toggle="tabs"]').on('shown.bs.tab', function (e) {
            myChart1.resize();
            myChart2.resize();

        });



        var dom = document.getElementById("inout");
        var myChart1 = echarts.init(dom,theme);
        var app = {};
        option1 = null;


        option1 = {

            tooltip: {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%)"
            },
            legend: {
                // orient: 'vertical',
                // top: 'middle',
                bottom: 10,
                left: 'center',
                data: ['转入交易笔数', '转出交易笔数']
            },
            series: [
                {
                    type: 'pie',
                    radius: ['40%', '70%'],
                    center: ['50%', '50%'],
                    selectedMode: 'single',
                    color: ['#91ca8c', '#f49f42'],
                    labelLine: {
                        normal: {
                            show: false
                        }
                    },
                    label: {
                        normal: {
                            show: false,
                            position: 'center'
                        }
                    },
                    data: [

                        {value: total_in, name: '转入交易笔数'},
                        {value: total_out, name: '转出交易笔数'}
                    ],
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
        ;


        if (option1 && typeof option1 === "object") {
            myChart1.setOption(option1, true);
        }

   // 参考 https://echarts.baidu.com/examples/editor.html?c=mix-zoom-on-value



option2 = null;
// myChart.showLoading();
    // myChart.hideLoading();

    option2= {
        title:{
          text:'地址每月活跃情况一览'
        },
        tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow',
                label: {
                    show: true,
                    textStyle:{

                        color:'#000'
                    }
                }
            }
        },
        calculable : true,
        grid: {
            // top: '10%',
            left: '3%',
            right: '3%',
            // bottom:'2%',
            containLabel: true
        },

        xAxis: [
            {
                type : 'category',
                data : active_month.date
            }
        ],
        yAxis: [
            {
                type : 'value',
                name : '月交易笔数'
            }
        ],
        series : [
            {
                name: '交易数',
                type: 'bar',
                data: active_month.value
            }
        ]
    };

    if (active_month.date.length>10){  // 动态隐藏/显示dataZoom
        $('#active_month_bar').height(300)
        option2['dataZoom'] = [
            {
                show: true
                // start: 40,
                // end: 90
            },
            {
                type: 'inside',
                // start: 40,
                // end: 90
            }
        ]
    }else{
        option2['grid']['bottom'] = '2%'
    }
var dom = document.getElementById("active_month_bar");
var myChart2 = echarts.init(dom,theme);
var app = {};

if (option2 && typeof option2 === "object") {
    myChart2.setOption(option2, true);
}


});