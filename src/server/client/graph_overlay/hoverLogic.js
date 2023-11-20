import { createNodeStyleHover } from './styles.js';
import { createNodeStyleNormal } from './styles.js';
import { createEdgeStyleHover } from './styles.js';
import { createEdgeStyleNormal } from './styles.js';
import { findEdgeIdsForNodeWithType } from '../graph/graph.js';
import { isNode } from '../graph/graph.js';
import { getContentsOfTooltip } from './tooltip.js';
import { registerFeatureHover } from './hover.js';

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

    registerFeatureHover(
        map,
        function (evt, feature) {
            // Der Tooltip soll immer am Mauszeiger sein.
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

            if (isNode(feature)) {
                let node = feature.get('props');
                let nodeId = node.id

                hoveredNodes.push(nodeId);
                hoveredEdges = findEdgeIdsForNodeWithType(nodeId);

                for (let nodeId of hoveredNodes) {
                    nodes2feature[nodeId].setStyle(createNodeStyleHover());
                }

                for (let edgeId of hoveredEdges) {
                    edges2feature[edgeId].setStyle(createEdgeStyleHover());
                }

            }
        },

        function (evt, feature) {
            resetStylesForHoveredElements();

            info.style.visibility = 'hidden';
        }
    );
}

