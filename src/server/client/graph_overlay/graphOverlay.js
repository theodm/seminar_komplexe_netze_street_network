import {styleExpression, updateFeature} from './styles.js';
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
            "colorOverlay": document.getElementById('node-highlight').value,
            "degreeColor": node['degree_color'],

            "rbc_color": '#000000',

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
            "colorOverlay": document.getElementById('edge-highlight').value,

            props: edge
        });

        vectorSource.addFeature(feature);
        edges2feature[edge.id] = feature;
    }

    for (const feature of vectorSource.getFeatures()) {
        updateFeature(feature);
    }

    const rendererSetting = document.getElementById('renderer').value;

    const style = styleExpression(parseInt(document.getElementById('node-size').value));

    if (rendererSetting === 'webgl') {
        let webGlVectorLayer = new ol.layer.Layer({
            source: vectorSource,
            style: style
        });

        webGlVectorLayer.createRenderer = function () {
            let webglVectorLayer = new ol.renderer.webgl.VectorLayer(this, {
                source: vectorSource,
                style: style
            });

            return webglVectorLayer;
        }


        map.addLayer(webGlVectorLayer);
    } else if (rendererSetting === 'vector') {
        let vectorLayer = new ol.layer.Vector({
            source: vectorSource,
            style: style
        });
        map.addLayer(vectorLayer);
    } else if (rendererSetting === 'vectorImage') {
        let vectorImageLayer = new ol.layer.VectorImage({
            source: vectorSource,
            style: style
        });

        map.addLayer(vectorImageLayer);
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

        // none, degree, relative_betweenness
        setNodeColorOverlay(type) {
            for (const nodeId in nodes) {
                nodes2feature[nodeId].set('colorOverlay', type);
                updateFeature(nodes2feature[nodeId]);
            }
        },

        setEdgeColorOverlay(type) {
            for (const edgeId in edges) {
                edges2feature[edgeId].set('colorOverlay', type);
                updateFeature(edges2feature[edgeId]);
            }
        },

        setNodeSize(size) {
            // if vectorLayer has property setStyle then use it else not
            if (vectorLayer.setStyle) {
                vectorLayer.setStyle(styleExpression(size));
            } else {
                alert("cannot dynamically change size of webgl :(")
            }

        },

        /**
         * Hier können den Knoten und Kanten beliebige Properties hinzugefügt werden,
         * diese werden sowohl dem Feature als auch den props hinzugefügt.
         * @param nodeData Map von NodeId zu Properties oder undefined
         * @param edgeData Map von NodeId zu Properties oder undefined
         */
        updateData(nodeData, edgeData) {
            if (!nodeData) {
                nodeData = {};
            }

            if (!edgeData) {
                edgeData = {};
            }

            for (const nodeId in nodeData) {
                const feature = nodes2feature[nodeId];

                for (const key in nodeData[nodeId]) {
                    feature.get('props')[key] = nodeData[nodeId][key];
                    feature.set(key, nodeData[nodeId][key]);
                    updateFeature(feature)
                }
            }

            for (const edgeId in edgeData) {
                const feature = edges2feature[edgeId];

                for (const key in edgeData[edgeId]) {
                    feature.get('props')[key] = edgeData[edgeId][key];
                    feature.set(key, edgeData[edgeId][key]);
                    updateFeature(feature)
                }
            }
        },


        /**
         * Hier können die Nodes (=IDs) übergeben werden, die nicht zu allen Knoten
         * einen Weg haben. Von denen aus also nicht alle anderen Knoten erreicht werden
         * können.
         */
        setNodesNoPathToAllNodes(nodesNoPathToAllNodes) {
            for (const nodeId of nodesNoPathToAllNodes) {
                nodes2feature[nodeId].set('nodeHighlight', 'noPathToAllOther');
                updateFeature(nodes2feature[nodeId]);
            }
        }

    }
}