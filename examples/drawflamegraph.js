//Kudos to: https://www.stefaanlippens.net/jupyter-custom-d3-visualization.html

require.undef('drawflamegraph');
define('drawflamegraph', ['d3','flamegraph'], function (d3,flamegraph) {
    
    function draw(container, data, width, height) {
            
            var svg = d3.select(container).append("svg")
                .attr('width', width)
                .attr('height', height)
                .append("g");
        
            /* 
            //Example of adding a simple circle to the SVG to test rendering
            svg.append('circle')
                .attr("cx", 100)
                .attr("cy", 100)
                .attr("r", 50)
                .style("fill", "#1f77b4")
                .style("opacity", 0.7);
            */
            
            var fg = flamegraph();
            fg.minFrameSize(3);
            fg.inverted(true);
            fg.getName(function(d) {
                    return d.data.SpanName;
                });
            fg.label(function(d) {
                    return "TraceId: " + d.data.TraceID + ", Duration: "+d.data.value+"ms";
                });

            svg 
                .datum(data)
                .call(fg);
    
}
return draw;
});

