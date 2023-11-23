import {styleExpression} from './styles.js';
import {edgeGetGeometry, isNode} from '../graph/graph.js';
import {createHoverLogicForGraphOverlay} from './hoverLogic.js';


class WebGLLayer extends ol.layer.Layer {
    createRenderer() {
        return new ol.renderer.webgl.VectorLayer(this, {
            style
        });
    }
}

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

    // use WebGLVectorLayerRenderer for better performance
    // https://openlayers.org/en/latest/examples/webgl-layer.html

    const vectorSource = new ol.source.Vector({
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

            // Die Änderungen werden von den Style-Expressions ausgewertet
            "type": "node",
            "nodeStatus": "normal",

            props: node,

        });

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

            // Die Änderungen werden von den Style-Expressions ausgewertet
            "type": "edge",
            "edgeStatus": "normal",

            props: edge
        });

        vectorSource.addFeature(feature);
        edges2feature[edge.id] = feature;
    }

    const rendererSetting = document.getElementById('renderer').value;

    if (rendererSetting === 'webgl') {
        let webGlVectorLayer = new ol.layer.Layer({
            source: vectorSource,
            style: styleExpression()
        });

        webGlVectorLayer.createRenderer = function () {
            return new ol.renderer.webgl.VectorLayer(this, {
                source: vectorSource,
                style: styleExpression()
            });
        }

        map.addLayer(webGlVectorLayer);
    } else if (rendererSetting === 'vector') {
        map.addLayer(new ol.layer.Vector({
            source: vectorSource,
            style: styleExpression()
        }));
    } else if (rendererSetting === 'vectorImage') {
        map.addLayer(new ol.layer.VectorImage({
            source: vectorSource,
            style: styleExpression()
        }));
    } else {
        throw new Error('renderer not found');
    }

    const vectorLayer = map.getLayers().getArray().slice(-1)[0];

    const removeHoverLogicFn = createHoverLogicForGraphOverlay(map, graph, nodes2feature, edges2feature);

    return {
        remove: () => {
            removeHoverLogicFn();
            map.removeLayer(vectorLayer);
        },

        /**
         * Hier können die Nodes (=IDs) übergeben werden, die nicht zu allen Knoten
         * einen Weg haben. Von denen aus also nicht alle anderen Knoten erreicht werden
         * können.
         */
        setNodesNoPathToAllNodes(nodesNoPathToAllNodes) {
            for (const nodeId of nodesNoPathToAllNodes) {
                nodes2feature[nodeId].set('nodeHighlight', 'noPathToAllOther');
            }
        }

    }
}