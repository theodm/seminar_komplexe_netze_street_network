import { createNodeStyleHover } from './styles.js';
import { createNodeStyleNormal } from './styles.js';
import { createEdgeStyleHover } from './styles.js';
import { createEdgeStyleNormal } from './styles.js';
import { createNodeNeighborStyleHover } from './styles.js';
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

    // Unser Tooltip im HTML
    const info = document.getElementById('info');

    // Diese Variablen geben die aktuell gehoverten Knoten und Kanten an.
    // Diese wurden im Style verändert und müssen nach dem Hover wieder zurückgesetzt werden.
    let hoveredNodes = [];
    let hoveredEdges = []

    /**
     * Zurücksetzen der Styles nach Hover-Ende.
     */
    function resetStylesForHoveredElements() {
        for (let nodeId of hoveredNodes) {
            nodes2feature[nodeId].setStyle(createNodeStyleNormal());
        }

        for (let edgeId of hoveredEdges) {
            edges2feature[edgeId].setStyle(createEdgeStyleNormal());
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

            if (isNode(obj)) {
                let node = obj;
                let nodeId = node.id

                // Highlight base Node
                nodes2feature[nodeId].setStyle(createNodeStyleHover());
                hoveredNodes.push(nodeId);

                // Highligh neighbors
                const neighbors = node.neighbors;
                for (let i = 0; i < neighbors.length; i++) {
                    const neighborId = neighbors[i].id;
                    nodes2feature[neighborId].setStyle(createNodeNeighborStyleHover(i));
                    hoveredNodes.push(neighborId);
                }


                // Highlight Edges
                const edgesToColor = findEdgeIdsForNodeWithType(graph, nodeId);

                // iterate key, value in edgesToColor
                for (const [edgeId, type] of Object.entries(edgesToColor)) {
                    hoveredEdges.push(edgeId);

                    edges2feature[edgeId].setStyle(createEdgeStyleHover(type));
                }
            } else {
                const edge = obj;
                const edgeId = obj.id;

                // highlight edge
                edges2feature[edgeId].setStyle(createEdgeStyleHover(edge.oneway ? "source" : "both"));
                hoveredEdges.push(edgeId);

                // highlight source and target node
                nodes2feature[obj.source.id].setStyle(createNodeStyleHover());
                nodes2feature[obj.target.id].setStyle(createNodeNeighborStyleHover(0));

                hoveredNodes.push(obj.source.id);
                hoveredNodes.push(obj.target.id);
            }
        },

        function (evt, feature) {
            resetStylesForHoveredElements();

            info.style.visibility = 'hidden';
        }
    );

    return () => {
        removeHoverOverFeatures(map, callbacks);
    }
}

