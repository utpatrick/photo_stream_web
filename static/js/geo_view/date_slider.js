$( function() {

    var min = new Date($("#a_year_before").attr("data-name")).getTime() / 1000;
    var max = new Date($("#current_date").attr("data-name")).getTime() / 1000;

    $( "#slider-range" ).slider({
        range: true,
        min: min,
        max: max,
        step: 86400,
        values: [min, max],
        slide: function( event, ui ) {
            $( "#amount" ).val( (new Date(ui.values[ 0 ] *1000).toLocaleDateString() )
            + " - "
            + (new Date(ui.values[ 1 ] *1000)).toLocaleDateString() );
        },
        change: function( event, ui ) {
            initMap();
        }
    });

    $( "#amount" ).val( (new Date($( "#slider-range" ).slider( "values", 0 )*1000).toLocaleDateString()) +
        " - " + (new Date($( "#slider-range" ).slider( "values", 1 )*1000)).toLocaleDateString());
});