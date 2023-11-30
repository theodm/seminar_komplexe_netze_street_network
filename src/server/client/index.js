import {getCookieOrDefault} from './util/cookie.js';
import {createGraphOverlay} from './graph_overlay/graphOverlay.js';

document.addEventListener('DOMContentLoaded', function () {

    var center = getCookieOrDefault('last_saved_center_position', "[8.239761, 50.078218]");
    var zoom = getCookieOrDefault('last_saved_zoom_level', 12);

    // renderer wird in cookies gespeichert (ist select elemtn) und wird daraus geladen
    const renderer = getCookieOrDefault('renderer', 'webgl');
    document.getElementById('renderer').value = renderer;

    document.getElementById('renderer').addEventListener('change', function () {
        Cookies.set('renderer', this.value);
    });

    // Die Checkbox, die angibt ob der Tooltip fixiert werden soll oder nicht.
    const fixedTooltip = getCookieOrDefault('fixed_tooltip', false);
    document.getElementById('fixed-tooltip').checked = fixedTooltip;

    document.getElementById('fixed-tooltip').addEventListener('change', function () {
        Cookies.set('fixed_tooltip', this.checked);
    });

    // Die Select-Box, die den Graph-Typ angibt.
    const graphType = getCookieOrDefault('graph_type', 'MultiDiGraph');

    document.getElementById('graph-type').value = graphType;

    document.getElementById('graph-type').addEventListener('change', function () {
        Cookies.set('graph_type', this.value);
    });

    // Die Checkbox, die angibt ob tote Knoten, von denen aus nicht alle anderen Knoten
    // erreicht werden können, angezeigt werden sollen.
    const filterDeadEnds = getCookieOrDefault('filter_dead_ends', false);
    document.getElementById('filter-dead-ends').checked = filterDeadEnds;

    document.getElementById('filter-dead-ends').addEventListener('change', function () {
        Cookies.set('filter_dead_ends', this.checked);
    });

    // Wie sollen Nodes koloriert sein?
    const nodeHighlight = getCookieOrDefault('node_highlight', 'none');
    document.getElementById('node-highlight').value = nodeHighlight;

    document.getElementById('node-highlight').addEventListener('change', function () {
        Cookies.set('node_highlight', this.value);
    });

    // Wie sollen Edges koloriert sein?
    const edgeHighlight = getCookieOrDefault('edge_highlight', 'none');
    document.getElementById('edge-highlight').value = edgeHighlight;

    document.getElementById('edge-highlight').addEventListener('change', function () {
        Cookies.set('edge_highlight', this.value);
    });

    // Geometry der Kanten verbessern (Beide Kantenrichtungen anzeigen)?
    const redoGeometry = getCookieOrDefault('redo_geometry', false);
    document.getElementById('redo-geometry').checked = redoGeometry;

    document.getElementById('redo-geometry').addEventListener('change', function () {
        Cookies.set('redo_geometry', this.checked);
    });

    // Größe der Knoten
    const nodeSize = getCookieOrDefault('node_size', 6);
    document.getElementById('node-size').value = nodeSize;

    document.getElementById('node-size').addEventListener('change', function () {
        Cookies.set('node_size', this.value);
    });

    // Minimale Anzahl an Nachbarn, die ein Knoten haben muss, damit die Kante farblich hervorgehoben wird.
    const dual_min = getCookieOrDefault('dual_min', 0);

    document.getElementById('dual_min').value = dual_min;

    document.getElementById('dual_min').addEventListener('change', function () {
        Cookies.set('dual_min', this.value);
    });

    // Maximale Anzahl an Nachbarn, die ein Knoten haben muss, damit die Kante farblich hervorgehoben wird.
    const dual_max = getCookieOrDefault('dual_max', 9999);

    document.getElementById('dual_max').value = dual_max;

    document.getElementById('dual_max').addEventListener('change', function () {
        Cookies.set('dual_max', this.value);
    });

    // Welches Bild in der Bildansicht anzeigen?
    const image_selector = getCookieOrDefault('image_selector', 'degree_histogram');

    document.getElementById('image-selector').value = image_selector;

    document.getElementById('image-selector').addEventListener('change', function () {
        Cookies.set('image_selector', this.value);
    });

    // Welcher Hover-Modus soll verwendet werden?
    const hover_mode = getCookieOrDefault('hover_mode', 'node_edge');

    document.getElementById('hover-mode').value = hover_mode;

    document.getElementById('hover-mode').addEventListener('change', function () {
        Cookies.set('hover_mode', this.value);
    });


    var map = new ol.Map({
        renderer: 'webgl',
        target: 'map',
        layers: [
            new ol.layer.WebGLTile({
                // apiKey ist in localhost nicht erforderlich
                source: new ol.source.StadiaMaps({
                    layer: 'alidade_smooth_dark',
                    retina: true,
                    // apiKey: 'OPTIONAL'
                  })
                // Wir verwenden hier StadiaMaps statt OSM, da StadiaMaps
                // hier einen dunkleren Hintergrund hat, der Knoten und Kanten
                // mit ihren grellen Farben sichtbarer macht.
                    //new ol.source.OSM()
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


    let currentGraph = undefined;
    let currentGraphOverlayAccess = undefined;

    // Das akutell angezeigte Bild aktualisieren (z.B. Knotengrad-Histogramm,)
    function updateImage() {
        if (!currentGraph) {
            document.getElementById('image-container').innerHTML = 'no graph loaded'
        }

        const type = document.getElementById('image-selector').value;

        document.getElementById('image-container').innerHTML = ""
        document.getElementById('image-container').innerHTML = '<img src="/api/' + type + '?graphkey=' + currentGraph.graphkey + '" alt="Degree Histogram" />'
    }

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

        let filterDeadEnds = document.getElementById('filter-dead-ends').checked;
        let redoGeometry = document.getElementById('redo-geometry').checked;
        const url = '/api/graph?north=' + extent[0] + '&east=' + extent[1] + '&south=' + extent[2] + '&west=' + extent[3] + '&type=' + graphType + '&filter_dead_ends=' + filterDeadEnds + '&redo_geometry=' + redoGeometry;

        axios.get(url)
            .then(function (response) {
                currentGraph = response.data;

                if (currentGraphOverlayAccess) {
                    console.log('remove graph overlay')
                    // remove old graph overlay
                    currentGraphOverlayAccess.remove();
                }

                const graph = response.data;

                const localNumberOfNodes = Object.keys(graph.nodes).length;
                const localNumberOfEdges = Object.keys(graph.edges).length;

                document.getElementById('num_nodes').innerHTML = graph.graphInfo.numNodes + " (" + localNumberOfNodes + ")";
                document.getElementById('num_edges').innerHTML = graph.graphInfo.numEdges + " (" + localNumberOfEdges + ")";
                document.getElementById('max_degree').innerHTML = graph.graphInfo.maxDegree;
                document.getElementById('avg_degree').innerHTML = graph.graphInfo.avgDegree;
                document.getElementById('min_degree').innerHTML = graph.graphInfo.minDegree;
                document.getElementById('global_cluster_officient_avg').innerText = graph.graphInfo.globalClusterCoefficientAvg

                currentGraphOverlayAccess = createGraphOverlay(map, graph);

                updateImage();
            })
            .catch(function (error) {
                console.log(error);
                alert('Error loading graph');
            });
    });


    document.getElementById('load-shortest-path-info-button').addEventListener('click', function () {
        if (!currentGraph) {
            alert('No graph loaded');
            return;
        }
        const graphkey = currentGraph.graphkey

        var url = '/api/shortest_path_info?graphkey=' + graphkey;

        axios.get(url)
            .then(function (response) {
                const data = response.data;

                document.getElementById('average_shortest_path_length').innerText = data.average_shortest_path_length;
                document.getElementById('diameter').innerText = data.diameter;

                if (currentGraphOverlayAccess) {
                    currentGraphOverlayAccess.setNodesNoPathToAllNodes(data.no_path_to_all_nodes);
                } else {
                    alert('No graph overlay loaded');
                }

            })
            .catch(function (error) {
                console.log(error);
                alert('Error loading shortest path info');
            });

    });

    document.getElementById('load-additional-data').addEventListener('change', function () {
        if (document.getElementById('load-additional-data').value === 'none') {
            return;
        }

        if (!currentGraph) {
            alert('No graph loaded');
            return;
        }

        const graphkey = currentGraph.graphkey

        var url = '/api/load_additional_data?graphkey=' + graphkey + '&data_type=' + document.getElementById('load-additional-data').value

        // reset select box
        document.getElementById('load-additional-data').value = 'none';

        axios.get(url)
            .then(function (response) {
                const data = response.data;

                const nodeData = data.node_data;
                const edgeData = data.edge_data;
                const additional_text_data = data.additional_text_data;

                if (additional_text_data) {
                    document.getElementById('dual_numNodes').innerText = additional_text_data.dual_numNodes ? additional_text_data.dual_numNodes : "";
                    document.getElementById('dual_numEdges').innerText = additional_text_data.dual_numEdges ? additional_text_data.dual_numEdges : "";
                    document.getElementById('dual_maxDegree').innerText = additional_text_data.dual_maxDegree ? additional_text_data.dual_maxDegree : "";
                    document.getElementById('dual_avgDegree').innerText = additional_text_data.dual_avgDegree ? additional_text_data.dual_avgDegree : "";
                    document.getElementById('dual_minDegree').innerText = additional_text_data.dual_minDegree ? additional_text_data.dual_minDegree : "";
                    document.getElementById('dual_globalClusterCoefficientAvg').innerText = additional_text_data.dual_globalClusterCoefficientAvg ? additional_text_data.dual_globalClusterCoefficientAvg : "";
                }

                currentGraphOverlayAccess.updateData(nodeData, edgeData)

                updateImage();
            })
            .catch(function (error) {
                console.log(error);
                alert('Error loading additional data');
            });
    });

    document.getElementById('clear-cookies-button').addEventListener('click', function () {
        Cookies.remove('last_saved_center_position');
        Cookies.remove('last_saved_zoom_level');
        Cookies.remove('renderer');
        Cookies.remove('fixed_tooltip');
        Cookies.remove('filter_dead_ends');
        Cookies.remove('node_highlight');
        Cookies.remove('graph_type');
        Cookies.remove('redo_geometry');
        Cookies.remove('edge_highlight');
        Cookies.remove('node_size');
        Cookies.remove('dual_min');
        Cookies.remove('dual_max');
        Cookies.remove('image_selector');
    });

    document.getElementById('node-size').addEventListener('change', function () {
        if (currentGraphOverlayAccess) {
            currentGraphOverlayAccess.setNodeSize(parseInt(this.value));
        }
    });

    document.getElementById('node-highlight').addEventListener('change', function () {
        if (currentGraphOverlayAccess) {
            currentGraphOverlayAccess.setNodeColorOverlay(this.value);
        }
    });

    document.getElementById('edge-highlight').addEventListener('change', function () {
        if (currentGraphOverlayAccess) {
            currentGraphOverlayAccess.setEdgeColorOverlay(this.value);
        }
    });

    document.getElementById('dual_min').addEventListener('change', function () {
        if (currentGraphOverlayAccess) {
            currentGraphOverlayAccess.setDualMin(parseInt(this.value));
        }
    });

    document.getElementById('dual_max').addEventListener('change', function () {
        if (currentGraphOverlayAccess) {
            currentGraphOverlayAccess.setDualMax(parseInt(this.value));
        }
    });

    document.getElementById('image-selector').addEventListener('change', function () {
        updateImage();
    });


}, false);