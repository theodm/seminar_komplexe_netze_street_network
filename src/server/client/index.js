import { getCookieOrDefault } from './util/cookie.js';
import { createGraphOverlay } from './graph_overlay/graphOverlay.js';

document.addEventListener('DOMContentLoaded', function () {

    var center = getCookieOrDefault('last_saved_center_position', "[8.239761, 50.078218]");
    var zoom = getCookieOrDefault('last_saved_zoom_level', 12);

    // Die Checkbox, die angibt ob der Tooltip fixiert werden soll oder nicht.
    const fixedTooltip = getCookieOrDefault('fixed_tooltip', false);
    document.getElementById('fixed-tooltip').checked = fixedTooltip;

    document.getElementById('fixed-tooltip').addEventListener('change', function () {
        Cookies.set('fixed_tooltip', this.checked);
    });

    var map = new ol.Map({
        renderer: 'webgl',
        target: 'map',
        layers: [
            new ol.layer.WebGLTile({
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

    let removeGraphOverlayFn = undefined

    // on graph load, request to server /graph
    // with bbox as query parameter (keys: north, east, ...) in axios returns
    // json object with object nodes and edges
    document.getElementById('load-graph-button').addEventListener('click', function () {
        var extent = getExtent();

        // <select id="graph-type" name="graph-type">
        //                 <option value="MultiDiGraph">default (MultiDiGraph)</option>
        //                 <option value="Graph">simple (Graph)</option>
        //             </select>
        // get graphType from select element
        const graphType = document.getElementById('graph-type').value;

        console.log('graphType: ' + graphType)

        var url = '/api/graph?north=' + extent[0] + '&east=' + extent[1] + '&south=' + extent[2] + '&west=' + extent[3] + '&type=' + graphType;

        axios.get(url)
            .then(function (response) {
                if (removeGraphOverlayFn) {
                    console.log('remove graph overlay')
                    // remove old graph overlay
                    removeGraphOverlayFn();
                }

                const graph = response.data;

                const localNumberOfNodes = Object.keys(graph.nodes).length;
                const localNumberOfEdges = Object.keys(graph.edges).length;

                document.getElementById('num_nodes').innerHTML = graph.graphInfo.numNodes + " (" + localNumberOfNodes + ")";
                document.getElementById('num_edges').innerHTML = graph.graphInfo.numEdges + " (" + localNumberOfEdges + ")";
                document.getElementById('max_degree').innerHTML = graph.graphInfo.maxDegree;
                document.getElementById('avg_degree').innerHTML = graph.graphInfo.avgDegree;
                document.getElementById('min_degree').innerHTML = graph.graphInfo.minDegree;

                removeGraphOverlayFn = createGraphOverlay(map, graph);
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