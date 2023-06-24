var chart;

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */
function requestData() {
    $.ajax({
        url: '/live-data',
        success: function(point) {
            console.log(point)
            var series = chart.series[0],
                shift = series.data.length > 600; // series가 n개가 넘으면
                                                 // shift를 하는 역할

            // Point를 추가적으로 그려주는 역할
            chart.series[0].addPoint(point, true, false);

            // 1초마다 재귀호출
            setTimeout(requestData, 50);
        },
        cache: false
    });
}

$(document).ready(function() {
    chart = new Highcharts.Chart({
        chart: {
            height: 200,
            renderTo: 'data-container',
            defaultSeriesType: 'spline',
            events: {
                load: requestData
            }
        },
        title: {
            text: 'Real-time Score'
        },
        xAxis: {
            type: 'datetime',
            tickPixelInterval: 150,
            maxZoom: 20 * 1000
        },
        yAxis: {
            minPadding: 0.2,
            maxPadding: 0.2,
            min : 0,
            max : 100,
            tickInterval : 20,
            title: {
                text: 'Score',
                margin: 80
            }
        },
        series: [{
            name: 'Random data',
            data: []
        }]
    });
});
