$(document).ready(function () {
    $(".item-content").each(function () {
        $(this).click(function () {
            locationId = $(this).attr('id')
            geoId = locationId.replace("location", "geo")
            console.log(geoId)
            // Lấy lat, log
            geo = $('#' + geoId).text();
            geo = geo.split(',')
            goLocation(geo[0], geo[1])
        })
    })
})

/**
 * Created by thangld on 18/03/2017.
 */
function initMap() {
    var uluru = {lat: 21.007663, lng: 105.842799};
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: uluru
    });
    var marker = new google.maps.Marker({
        position: uluru,
        map: map
    });
    marker.setMap(map)
}

function goLocation(lat, lng) {
    console.log(lat)
    console.log(lng)
    var uluru = {lat: parseInt(lat), lng: parseInt(lng)};
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 6,
        center: uluru
    });
    var marker = new google.maps.Marker({
        position: uluru,
        map: map
    });
}
