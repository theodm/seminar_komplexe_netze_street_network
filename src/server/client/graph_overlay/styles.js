
export const colorsForNeighbourNodes = [
    "#e11d48",
    "#22c55e",
    "#c026d3",
    "#a3e635",
    "#6d28d9",
    "#38bdf8",
    "#ea580c",
    "#f9a8d4",
    "#f59e0b"
];
// map to ol colors

const nodeColorNormal = '#64748b';
const nodeColorHover = '#f59e0b';
const nodeColorNoPathToAllOther = '#000000';

const edgeColorNormal = '#64748b';
const edgeColorHovered = '#f59e0b';
const edgeColorHide = '#000000';

const edgeColorHighlightSource = '#f59e0b';
const edgeColorHighlightTarget = '#1e293b';
const edgeColorHighlightBoth = '#dc2626';

export function update() {

}

export function nodeColorFunction(nodeFeature) {
    switch (nodeFeature.get("nodeStatus")) {
        case 'normal':
            switch (nodeFeature.get("colorOverlay")) {
                case 'none':
                    return nodeColorNormal;
                case 'degree':
                    return nodeFeature.get("degreeColor");
                case 'relativeBetweenness':
                    return nodeFeature.get("rbcColor");
            }
            return nodeColorNormal;
        case 'nodeIsHovered':
            return nodeColorHover;
        case 'nodeIsHovered_NodeNeighbor':
            return colorsForNeighbourNodes[nodeFeature.get("neighborHoveredNodeColor")];
        case 'edgeIsHovered_NodeNeighbor':
            return nodeColorHover;

        case 'noPathToAllOther':
            return nodeColorNoPathToAllOther;
    }

    throw new Error("nodeStatus " + nodeFeature.get("nodeStatus") + "not found");
}

export function edgeColorFunction(edgeFeature) {

    switch (edgeFeature.get("edgeStatus")) {
        case 'normal':
            switch (edgeFeature.get("colorOverlay")) {
                case 'none':
                    return edgeColorNormal;
                case 'degree':
                    return edgeFeature.get("degreeColor");
                case 'relativeBetweennessEdge':
                    return edgeFeature.get("rbcEdgeColor");
                    
                case 'dualNodeDegree': {
                    const edgeDegreeInRange = edgeFeature.get("dual_node_neighbors") && edgeFeature.get("dual_node_neighbors").length >= edgeFeature.get("show_min") && edgeFeature.get("dual_node_neighbors").length <= edgeFeature.get("show_max");
                    // Nur farblich hervorheben, wenn die Anzahl der Nachbarn im festgelegten Bereich liegt
                    return edgeDegreeInRange ? edgeFeature.get("dualNodeDegreeColor") : edgeColorHide;
                }
                case 'dualNodeColor': {
                    const edgeDegreeInRange = edgeFeature.get("dual_node_neighbors") && edgeFeature.get("dual_node_neighbors").length >= edgeFeature.get("show_min") && edgeFeature.get("dual_node_neighbors").length <= edgeFeature.get("show_max");
                    // Nur farblich hervorheben, wenn die Anzahl der Nachbarn im festgelegten Bereich liegt
                    return edgeDegreeInRange ? edgeFeature.get("dual_node_color") : edgeColorHide;
                }
            }
            return edgeColorNormal;
        case 'dualNodeIsHovered_DualNodeNeighbor':
            return colorsForNeighbourNodes[edgeFeature.get("neighborHoveredDualNodeColor")];
        case 'edgeIsHovered':
            return edgeColorHovered;
        case 'nodeIsHovered_EdgeNeighbor':
            switch (edgeFeature.get("neighborHoveredEdgeColor")) {
                case 'source':
                    return edgeColorHighlightSource;
                case 'target':
                    return edgeColorHighlightTarget;
                case 'both':
                    return edgeColorHighlightBoth;
            }

    }

    throw new Error("edgeStatus not found");
}

export function updateFeature(feature) {
    if (feature.get("type") === "node")
        feature.set("nodeColor", nodeColorFunction(feature));
    else
        feature.set("edgeColor", edgeColorFunction(feature));
}

/**
 * Wir verwenden hier Style-Expressions, da diese von allen verwendeten 
 * Renderern unterstützt wird. Das ist eine spezielle Art von Programmiersprache,
 * die bei openlayers verwendet wird, um die Styles von Features dynamisch nach
 * Attributwerten zu definieren.
 * 
 * siehe auch: 
 * https://github.com/openlayers/openlayers/blob/28c4728b620d0a44bd61a33fc28f726b2efdf650/src/ol/expr/expression.js
 * https://github.com/openlayers/openlayers/blob/main/src/ol/style/webgl.js
 */
export function styleExpression(nodeSize = 5) {

    const ifEdgeExpression = (expr, defaultValue) => {
        return ['match', ['get', 'type'], 'edge', expr, defaultValue]
    }

    const ifNodeExpression = (expr, defaultValue) => {
        return ['match', ['get', 'type'], 'node', expr, defaultValue]
    }

    const edgeColorExpression = [
        'get',
        'edgeColor'
    ]

    const nodeColorExpression = [
        'get',
        'nodeColor'
    ]

    const styleExpression = {
        'stroke-color': ifEdgeExpression(edgeColorExpression, "#00000000"),
        'stroke-width': 3,
        'fill-color': '#ffffff19',

        'circle-radius': nodeSize,
        'circle-fill-color': nodeSize === 0 ? "#00000000" : ifNodeExpression(nodeColorExpression, "#00000000"),
        'circle-stroke-color': nodeSize === 0 ? "#00000000" : ifNodeExpression(nodeColorExpression, "#00000000"),
        'circle-stroke-width': 1.25,
    }

    console.log(JSON.stringify(styleExpression, null, 2))

    return styleExpression;
}

