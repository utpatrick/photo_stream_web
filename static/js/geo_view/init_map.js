function initMap() {

    var mapOptions = {
        center: new google.maps.LatLng(0, 0),
        zoom: 1,
        minZoom: 1
    };

    var map = new google.maps.Map(document.getElementById('map'), mapOptions);

    var allowedBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(85, -180),	// top left corner of map
        new google.maps.LatLng(-85, 180)	// bottom right corner
    );

    var k = 5.0;
    var n = allowedBounds.getNorthEast().lat() - k;
    var e = allowedBounds.getNorthEast().lng() - k;
    var s = allowedBounds.getSouthWest().lat() + k;
    var w = allowedBounds.getSouthWest().lng() + k;
    var neNew = new google.maps.LatLng(n, e);
    var swNew = new google.maps.LatLng(s, w);
    boundsNew = new google.maps.LatLngBounds(swNew, neNew);
    map.fitBounds(boundsNew);

    // loading photo through customized json file
    var geo_photo = JSON.parse($("#geo_photo").attr("data-name"));

    var size = geo_photo.length;
    var markers = [];
    var marker, i = 0;

    for(i = 0; i < size; i++){

        var this_photo_date = new Date(geo_photo[i].last_update);
        var lower_bar = new Date($( "#slider-range" ).slider( "values", 0 )*1000);
        var upper_bar = new Date($( "#slider-range" ).slider( "values", 1 )*1000);

        if(this_photo_date >= lower_bar && this_photo_date <= upper_bar){
            var id = 'photo_' + i;
            var lat = parseFloat(geo_photo[i].geo_info[0]);
            var lon = parseFloat(geo_photo[i].geo_info[1]);
            var gps = {};
            gps["lat"] = lat;
            gps["lng"] = lon;

            var parsed_url = '/image?img_id=' + geo_photo[i].key_url;

            marker = new google.maps.Marker({
                position: gps,
                temp_url: parsed_url,
                icon: '/static/images/marker.png',
                id: id,
                zIndex:100
            });

            google.maps.event.addListener(marker, 'mouseover', function() {
                var icon = {
                    url: this.temp_url,
                    scaledSize: new google.maps.Size(100, 100)
                };
                this.setIcon(icon);
            });

            google.maps.event.addListener(marker, 'mouseout', function() {
                this.setIcon('/static/images/marker.png');
            });

            markers.push(marker);
        }
    }
    var markerCluster = new MarkerClusterer(map, markers, {imagePath: '/static/images/label/m'});
}