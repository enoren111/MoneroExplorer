am4core.ready(function () {

// Themes begin
am4core.useTheme(am4themes_dark);
am4core.useTheme(am4themes_animated);
// Themes end




var chart = am4core.create("heatmap", am4charts.XYChart);
chart.maskBullets = false;


var bgColor = new am4core.InterfaceColorSet().getFor("background");

var xAxis = chart.xAxes.push(new am4charts.CategoryAxis());
var xAxis2 = chart.xAxes.push(new am4charts.CategoryAxis());
var yAxis = chart.yAxes.push(new am4charts.CategoryAxis());

xAxis.dataFields.category = "weeks";
xAxis2.dataFields.category = "month";

yAxis.dataFields.category = "weekday";

xAxis.renderer.grid.template.disabled = true;
xAxis.renderer.minGridDistance = 40;
// xAxis.renderer.labels.template.fill = am4core.color("#000");
// xAxis.renderer.opposite = true;
// xAxis.renderer.labels.template.disabled = true;
xAxis.renderer.labels.template.fontSize = 0;

xAxis2.renderer.minGridDistance = 10;  // 决定月份坐标是否能够完全显示
xAxis2.renderer.opposite = true;
// xAxis2.renderer.labels.template.disabled = true;

yAxis.renderer.grid.template.disabled = true;
yAxis.renderer.inversed = true;
yAxis.renderer.minGridDistance = 30;

var series = chart.series.push(new am4charts.ColumnSeries());
series.dataFields.categoryX = "weeks";
series.dataFields.categoryY = "weekday";
series.dataFields.value = "value";
series.sequencedInterpolation = true;
series.defaultState.transitionDuration = 3000;



var columnTemplate = series.columns.template;
columnTemplate.strokeWidth = 1;
columnTemplate.strokeOpacity = 0.2;
columnTemplate.stroke = bgColor;
// columnTemplate.tooltipText = "{weeks}, {weekday}: {value.workingValue.formatNumber('#.')}";
columnTemplate.tooltipText = "{date},{value.workingValue.formatNumber('#.')}笔交易";
columnTemplate.width = am4core.percent(90);
columnTemplate.height = am4core.percent(90);

series.heatRules.push({
  target: columnTemplate,
  property: "fill",
  min: am4core.color('#fff'),   // bgColor
  max: chart.colors.getIndex(0)
});

// heat legend
var heatLegend = chart.bottomAxesContainer.createChild(am4charts.HeatLegend);
heatLegend.width = am4core.percent(100);
heatLegend.series = series;
heatLegend.minColor = am4core.color("#fff");
heatLegend.valueAxis.renderer.labels.template.fontSize = 9;
// heatLegend.valueAxis.renderer.labels.template.fill = am4core.color("#A0CA92");
heatLegend.valueAxis.renderer.minGridDistance = 30;



// heat legend behavior
series.columns.template.events.on("over", (event) => {
  handleHover(event.target);
})

series.columns.template.events.on("hit", (event) => {
  handleHover(event.target);
})

function handleHover(column) {
  if (!isNaN(column.dataItem.value)) {
    heatLegend.valueAxis.showTooltipAt(column.dataItem.value)
  }
  else {
    heatLegend.valueAxis.hideTooltip();
  }
}

series.columns.template.events.on("out", (event) => {
  heatLegend.valueAxis.hideTooltip();
})






// chart.data = datas;
chart.data = heatmap_data;

});
