import {colorsForNeighbourNodes, updateFeature} from './styles.js';
import { findEdgeIdsForNodeWithType } from '../graph/graph.js';
import { isNode } from '../graph/graph.js';
import { getContentsOfTooltip } from './tooltip.js';
import { registerFeatureHover } from '../map/hover.js';
import { removeHoverOverFeatures } from '../map/hover.js';

export function createHoverLogicForGraphOverlay(
    map,
    graph,
    nodes2feature,
    edges2feature
) {
    const nodes = graph.nodes;
    const edges = graph.edges;

    const redoGeometry = graph.redo_geometry

    // Unser Tooltip im HTML
    const info = document.getElementById('info');

    // Diese Variablen geben die aktuell gehoverten Knoten und Kanten an.
    // Diese wurden im Style verändert und müssen nach dem Hover wieder zurückgesetzt werden.
    let hoveredNodes = [];
    let hoveredEdges = []

    let currentHoverMode = document.getElementById('hover-mode').value;

    document.getElementById('hover-mode').addEventListener('change', function () {
        currentHoverMode = document.getElementById('hover-mode').value;
    });

    /**
     * Zurücksetzen der Styles nach Hover-Ende.
     */
    function resetStylesForHoveredElements() {
        for (let nodeId of hoveredNodes) {
            nodes2feature[nodeId].set('nodeStatus', 'normal');
            updateFeature(nodes2feature[nodeId])
        }

        for (let edgeId of hoveredEdges) {
            edges2feature[edgeId].set('edgeStatus', 'normal');
            updateFeature(edges2feature[edgeId])
        }

        hoveredNodes = [];
        hoveredEdges = [];
    }

    const callbacks = registerFeatureHover(
        map,
        function (evt, feature) {

            // Der Tooltip soll immer am Mauszeiger sein. Es sei denn,
            // die Einstellung fixed-tooltip ist aktiviert.
            if (document.getElementById('fixed-tooltip').checked) {
                info.style.left = "10px";
                info.style.top = '75px';
                return;
            }

            info.style.left = evt.pixel[0] + 'px';
            info.style.top = evt.pixel[1] + 'px';
        },

        function (evt, feature) {
            // Tooltip anzeigen und Inhalt setzen.
            info.style.visibility = 'visible';
            info.innerHTML = getContentsOfTooltip(feature);

            // Zurücksetzen der Styles, falls vorher gehovert wurde und aus irgendeinem
            // Grund nicht zurückgesetzt.
            resetStylesForHoveredElements();

            const obj = feature.get('props');

            if (currentHoverMode === 'node_edge') {
                if (isNode(obj)) {
                    let node = obj;
                    let nodeId = node.id

                    // Highlight base Node
                    hoveredNodes.push(nodeId);
                    nodes2feature[nodeId].set('nodeStatus', 'nodeIsHovered');
                    updateFeature(nodes2feature[nodeId])

                    // Highlight neighbors 
                    const neighbors = node.neighbors;
                    for (let i = 0; i < neighbors.length; i++) {
                        const neighborId = neighbors[i].id;
                        nodes2feature[neighborId].set('nodeStatus', 'nodeIsHovered_NodeNeighbor');
                        nodes2feature[neighborId].set('neighborHoveredNodeColor', ( i % colorsForNeighbourNodes.length ) + "");
                        updateFeature(nodes2feature[neighborId])

                        hoveredNodes.push(neighborId);
                    }

                    // Highlight Edges
                    const edgesToColor = findEdgeIdsForNodeWithType(graph, nodeId, redoGeometry);

                    // iterate key, value in edgesToColor
                    for (const [edgeId, type] of Object.entries(edgesToColor)) {
                        hoveredEdges.push(edgeId);

                        edges2feature[edgeId].set('edgeStatus', 'nodeIsHovered_EdgeNeighbor');
                        edges2feature[edgeId].set('neighborHoveredEdgeColor', type);
                        updateFeature(edges2feature[edgeId])
                    }
                } else {
                    const edge = obj;
                    const edgeId = obj.id;

                    // highlight edge
                    edges2feature[edgeId].set('edgeStatus', 'edgeIsHovered');
                    hoveredEdges.push(edgeId);
                    updateFeature(edges2feature[edgeId])

                    // highlight source and target node
                    nodes2feature[obj.source.id].set('nodeStatus', 'edgeIsHovered_NodeNeighbor');
                    nodes2feature[obj.target.id].set('nodeStatus', 'edgeIsHovered_NodeNeighbor');

                    updateFeature(nodes2feature[obj.source.id])
                    updateFeature(nodes2feature[obj.target.id])

                    hoveredNodes.push(obj.source.id);
                    hoveredNodes.push(obj.target.id);
                }
            } else if (currentHoverMode === 'dual_node' || currentHoverMode === 'dual_node_no_neigbors') {
                if (!isNode(obj)) {
                    // Alle Kanten, auf die sich der Knoten bezieht, hervorheben.
                    feature.get('dual_original_edges').forEach(edgeId => {
                        edges2feature[edgeId].set('edgeStatus', 'edgeIsHovered');
                        hoveredEdges.push(edgeId);

                        updateFeature(edges2feature[edgeId])
                    });

                    if (currentHoverMode === 'dual_node') {
                        // Alle Nachbarknoten (=mehrere Kanten) hervorheben
                        feature.get('dual_node_neighbors').forEach((edgesInNode, i) => {
                            for (const edgeId of edgesInNode) {
                                edges2feature[edgeId].set('edgeStatus', 'dualNodeIsHovered_DualNodeNeighbor');
                                edges2feature[edgeId].set('neighborHoveredDualNodeColor', ( i % colorsForNeighbourNodes.length ) + "");
                                hoveredEdges.push(edgeId);

                                updateFeature(edges2feature[edgeId])
                            }
                        });
                    }
                }


            } else {
                throw new Error('hover mode ' + currentHoverMode + ' not found');
            }
        },

        function (evt, feature) {
            resetStylesForHoveredElements();

            info.style.visibility = 'hidden';
        },

        /**
         * Diese Funktion gibt an, welches Feature priorisiert werden soll, 
         * wenn der Benutzer mit seinem Mauszeiger über mehrere Features hovert. Dabei wird
         * eine Hit-Toleranz berücksichtigt, für große Finger. 
         */
        function (features) {
            // Node priorisieren wir beim Hover vor Edges, da Edges
            // sowieso einfacher zu hovern sind.
            const nodeFeatures = features.filter(f => isNode(f.get('props')));

            return nodeFeatures.length > 0 ? nodeFeatures[0] : features[0];
        }
    );

    return () => {
        removeHoverOverFeatures(map, callbacks);
    }
}

