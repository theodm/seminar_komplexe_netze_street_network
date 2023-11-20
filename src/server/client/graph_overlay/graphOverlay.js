import {createNodeStyleNormal} from './styles.js';
import {createEdgeStyleNormal} from './styles.js';
import { edgeGetGeometry } from '../graph/graph.js';
import { createHoverLogicForGraphOverlay } from './hoverLogic.js';

/**
 * Erstellt einen Overlay für openlayers, welches die Knoten und Kanten
 * des osmnx-Graphen anzeigt. openlayers arbeitet mit sogenannten Layern.
 * 
 * @param {Graph} graph 
 */
export function createGraphOverlay(
    map,
    graph
) {
    const nodes = graph.nodes;
    const edges = graph.edges;

    var vectorSource = new ol.source.Vector({
        features: []
    });

    // Ein Feature in openlayers ist ein Objekt, welches auf der Karte angezeigt wird
    // (z.B. ein Punkt, eine Linie, ein Polygon, ein Kreis, ein Text, ...)

    // Map von NodeId zu Feature
    const nodes2feature = {};
    // Map von EdgeId zu Feature
    const edges2feature = {};

    // Alle Knoten als Features (Punkte) hinzufügen
    for (const nodeId in nodes) {
        const node = nodes[nodeId];

        var feature = new ol.Feature({
            geometry: new ol.geom.Point(ol.proj.fromLonLat([node.lon, node.lat])),
            props: node
        });

        // Initiales Aussehen des Punktes setzen
        feature.setStyle(createNodeStyleNormal());

        vectorSource.addFeature(feature);
        nodes2feature[node.id] = feature;
    }

    // Alle Kanten als Features (Linien) hinzufügen
    for (const edgeId in edges) {
        const edge = edges[edgeId];

        const geometry = edgeGetGeometry(edge);

        const pointsToConnect = [];
        for (const point of geometry) {
            pointsToConnect.push(ol.proj.fromLonLat(point));
        }

        // Eine Kante besteht sichtbar aus mehreren Linien,
        // da osmnx ZwischenKnoten filtert, aber den Straßenverlauf erhält.
        var feature = new ol.Feature({
            "geometry": new ol.geom.LineString(pointsToConnect),
            props: edge
        });

        // Initiales Aussehen der Linien setzen
        feature.setStyle(createEdgeStyleNormal());

        vectorSource.addFeature(feature);
        edges2feature[edge.id] = feature;
    }

    map.addLayer(new ol.layer.Vector({
        source: vectorSource
    }));

    // get last added layer (vector layer)
    const vectorLayer = map.getLayers().getArray().slice(-1)[0];

    // var select = new ol.interaction.Select({
    //     layers: [vectorLayer]
    // });

    // map.addInteraction(select);

    // // on select show message
    // select.on('select', function (e) {
    //     if (!e.target.getFeatures() || e.target.getFeatures().getLength() === 0) {
    //         return;
    //     }

    //     var selectedFeatures = e.target.getFeatures();
    //     var coordinates = selectedFeatures.item(0).getGeometry().getCoordinates();
    //     var lonLat = ol.proj.toLonLat(coordinates);

    //     var props = selectedFeatures.item(0).getProperties().props;

    //     alert('You clicked on ' + lonLat[0] + ', ' + lonLat[1] + ' with props ' + JSON.stringify(props));
    // });

    const removeHoverLogicFn = createHoverLogicForGraphOverlay(map, graph, nodes2feature, edges2feature);

    return () => {
        removeHoverLogicFn();
        map.removeLayer(vectorLayer);
    }
}