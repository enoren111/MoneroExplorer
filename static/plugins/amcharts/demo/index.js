
// 参考：https://www.amcharts.com/demos/range-area-chart/


am4core.ready(function () {
    am4core.useTheme(am4themes_dark);
am4core.useTheme(am4themes_animated);

var chart = am4core.create("chartdiv", am4charts.XYChart);
// chart.colors.step = 2;

var data = [];
var n_a = 100;
var a_a = 250;
$.get('/btc/day_address', function (address_datas) {
	end_date=address_datas.end_date;
	for (var i=0;i<end_date.length;i++)
	{
		//alert(end_date[i]);
		data.push({ date: end_date[i], n_a: address_datas.new_address[i], a_a: address_datas.active_address[i] });
	}

chart.data = data;




/* dateAxis */
var dateAxis = chart.xAxes.push(new am4charts.DateAxis());  //new am4charts.CategoryAxis()
dateAxis.renderer.grid.template.location = 0;

dateAxis.dateFormats.setKey("day", "MM-dd");  // "MMMM dt"
dateAxis.periodChangeDateFormats.setKey("day", "MM-dd");
dateAxis.periodChangeDateFormats.setKey("month", "[bold]yyyy-MM-dd[/]");

var dateAxis2 = chart.xAxes.push(new am4charts.DateAxis());
dateAxis2.renderer.labels.template.disabled = true;
dateAxis2.dateFormats.setKey("day", "yyyy-MM-dd");  // "MMMM dt"
dateAxis2.periodChangeDateFormats.setKey("day", "yyyy-MM-dd");


/* valueAxis */

var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
valueAxis.tooltip.disabled = true;



/* series */

var series = chart.series.push(new am4charts.LineSeries());
series.name = "新增地址";

// series.dataFields.valueX = "date";
series.dataFields.dateX = "date";
series.dataFields.openValueY = "a_a";
series.dataFields.valueY = "n_a";

series.tooltipText = "新增地址: {valueY.value}";
var s1_bullets = series.bullets.push(new am4charts.CircleBullet());
// s1_bullets.circle.stroke = am4core.color("#000");
s1_bullets.circle.strokeWidth = 0;
s1_bullets.circle.radius = 2;
// s1_bullets.circle.fill = am4core.color("#000");

// series.tooltipText = "open: {openValueY.value} close: {valueY.value}";
// series.strokeWidth = 2;  // 线宽
// series.sequencedInterpolation = true;
// series.fillOpacity = 0.3;


var series2 = chart.series.push(new am4charts.LineSeries());
series2.name = "活跃地址";
series2.dataFields.dateX = "date";
// series2.dataFields.valueX = "date";
series2.dataFields.valueY = "a_a";
series2.xAxis = dateAxis2;
// series2.sequencedInterpolation = true;
series2.stroke = chart.colors.getIndex(6);
// series2.tensionX = 0.8;   // 平滑
series2.tooltipText = "活跃地址: {valueY.value}";
var bullet = series2.bullets.push(new am4charts.Bullet());
bullet.width = 4;
bullet.height = 4;
bullet.horizontalCenter = "middle";
bullet.verticalCenter = "middle";

var rectangle = bullet.createChild(am4core.Rectangle);
// rectangle.stroke = interfaceColors.getFor("background");
rectangle.strokeWidth = 0;
rectangle.width = 4;
rectangle.height = 4;
rectangle.fill = chart.colors.getIndex(6) //series2.stroke





/* 给scrollbarX用 */
var series3 = chart.series.push(new am4charts.LineSeries());
// series.dataFields.valueX = "date";
series3.dataFields.dateX = "date";
series3.dataFields.valueY = "n_a";


var series4 = chart.series.push(new am4charts.LineSeries());
series4.dataFields.dateX = "date";
series4.dataFields.valueY = "a_a";

series3.hiddenInLegend = true;
series4.hiddenInLegend = true;
series3.defaultState.properties.visible = false;
series4.defaultState.properties.visible = false;




chart.cursor = new am4charts.XYCursor();
chart.cursor.xAxis = dateAxis;

/* dateAxis2 tooltip样式 */
dateAxis2.adapter.add("getTooltipText", (text) => {
 // return ">>> [bold]" + text + "[/] <<<";
    return text
});



// chart.scrollbarX = new am4core.Scrollbar();
chart.scrollbarX = new am4charts.XYChartScrollbar();
chart.scrollbarX.series.push(series3);
chart.scrollbarX.series.push(series4);
chart.scrollbarX.parent = chart.bottomAxesContainer;  // scrollbar位置

// legend
chart.legend = new am4charts.Legend();
chart.legend.parent = chart.plotContainer;
chart.legend.zIndex = 100;

});
});
