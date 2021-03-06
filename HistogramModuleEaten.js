// HistogramModule.js
var HistogramModule = function(bins, canvas_width, canvas_height) {
    // Create the elements

    // Create the tag:
    var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
    canvas_tag += "style='border:1px dotted'></canvas>";
    // Append it to body:
    var canvas = $(canvas_tag)[0];
    $("#elements").append(canvas);
    // Create the context and the drawing controller:
    var context = canvas.getContext("2d");

    // Prep the chart properties and series:
    var datasets = [{
        label: "Distance of directly eaten food from nearest safe spot.",
        fillColor: "rgba(0,127,255,0.5)",
        strokeColor: "rgba(0,127,255,0.8)",
        highlightFill: "rgba(0,127,255,0.75)",
        highlightStroke: "rgba(0,127,255,1)",
        data: []
    }];

    // Add a zero value for each bin
    for (var i in bins)
        datasets[0].data.push(0);

    var data = {
        labels: bins,
        datasets: datasets
    };

    var options = {
        scaleBeginsAtZero: true
    };

    // Create the chart object
    var chart = new Chart(context,{'type': 'bar', 'data': data, 'options': options});

    // Now what?
    this.render = function(data) {
        for (var i in data)
            chart.data.datasets[0].data[i] = data[i];
        chart.update();
    };

    this.reset = function() {
        chart.destroy();
        chart = new Chart(context,{'type': 'bar', 'data': data, 'options': options});
    };
};