import { getCookieOrDefault } from './util/cookie.js';
import { createGraphOverlay } from './graph_overlay/graphOverlay.js';

document.addEventListener('DOMContentLoaded', function () {

    var center = getCookieOrDefault('last_saved_center_position', "[8.239761, 50.078218]");
    var zoom = getCookieOrDefault('last_saved_zoom_level', 12);

    var map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            })
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat(JSON.parse(center)),
            zoom: JSON.parse(zoom)
        })
    });

    function getCenter() {
        var center = ol.proj.toLonLat(map.getView().getCenter());
        return [center[0], center[1]];
    }

    function getExtent() {
        var extent = map.getView().calculateExtent(map.getSize());

        var bottomLeft = ol.proj.toLonLat(ol.extent.getBottomLeft(extent));
        var topRight = ol.proj.toLonLat(ol.extent.getTopRight(extent));

        return [
            topRight[1],
            topRight[0],
            bottomLeft[1],
            bottomLeft[0]
        ]
    }

    // ol on view moved event
    map.getView().on('change:center', function () {
        var center = getCenter();

        document.getElementById('lat').value = center[1];
        document.getElementById('lon').value = center[0];

        // save center point in cookies with js-cookie
        Cookies.set('last_saved_center_position', JSON.stringify(center));
        Cookies.set('last_saved_zoom_level', JSON.stringify(map.getView().getZoom()));

        var extent = getExtent();

        document.getElementById('north').value = extent[0];
        document.getElementById('east').value = extent[1];
        document.getElementById('south').value = extent[2];
        document.getElementById('west').value = extent[3];
    });

    // On GeoSearch Button Click
    document.getElementById('geosearch-button').addEventListener('click', function () {

    });

    // on graph load, request to server /graph
    // with bbox as query parameter (keys: north, east, ...) in axios returns
    // json object with object nodes and edges
    document.getElementById('load-graph-button').addEventListener('click', function () {
        var extent = getExtent();

        var url = '/api/graph?north=' + extent[0] + '&east=' + extent[1] + '&south=' + extent[2] + '&west=' + extent[3];

        axios.get(url)
            .then(function (response) {
                createGraphOverlay(map, response.data);
            })
            .catch(function (error) {
                console.log(error);
                alert('Error loading graph');
            });
    });

    document.getElementById('clear-cookies-button').addEventListener('click', function () {
        Cookies.remove('last_saved_center_position');
        Cookies.remove('last_saved_zoom_level');
    });


}, false);