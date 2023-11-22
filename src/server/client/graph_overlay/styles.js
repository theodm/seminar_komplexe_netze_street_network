
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

const edgeColorNormal = '#64748b';
const edgeColorHovered = '#f59e0b';

const edgeColorHighlightSource = '#f59e0b';
const edgeColorHighlightTarget = '#1e293b';
const edgeColorHighlightBoth = '#dc2626';

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
export function styleExpression() {

    const ifEdgeExpression = (expr, defaultValue) => {
        return ['match', ['get', 'type'], 'edge', expr, defaultValue]
    }

    const ifNodeExpression = (expr, defaultValue) => {
        return ['match', ['get', 'type'], 'node', expr, defaultValue]
    }

    const edgeColorExpression = [
        'match',
        ['get', 'edgeStatus'], 
        'normal', edgeColorNormal,
        'edgeIsHovered', edgeColorHovered,
        'nodeIsHovered_EdgeNeighbor', ['match', ['get', 'neighborHoveredEdgeColor'], 'source', edgeColorHighlightSource, 'target', edgeColorHighlightTarget, edgeColorHighlightBoth],            
        '#FF0000'
    ]

    const nodeColorExpression = [
        'match',
        ['get', 'nodeStatus'], 
        'normal', nodeColorNormal,
        'nodeIsHovered', nodeColorHover,
        // ToDo: Das ist unschön aber mit dem palette-Operator hat es nicht funktioniert.
    
        'nodeIsHovered_NodeNeighbor', ['match', ['get', 'neighborHoveredNodeColor'], 
            '0', _colorsForNeighbourNodes[0], 
            '1', _colorsForNeighbourNodes[1], 
            '2', _colorsForNeighbourNodes[2], 
            '3', _colorsForNeighbourNodes[3], 
            '4', _colorsForNeighbourNodes[4], 
            '5', _colorsForNeighbourNodes[5], 
            '6', _colorsForNeighbourNodes[6],
            '7', _colorsForNeighbourNodes[7],
            '8', _colorsForNeighbourNodes[8],
            "#ffffff"
        ],
        'edgeIsHovered_NodeNeighbor', nodeColorHover,
        '#00000000'
    ]

    const styleExpression = {
        'stroke-color': ifEdgeExpression(edgeColorExpression, "#00000000"),
        'stroke-width': 3,
        'fill-color': '#ffffff19',

        'circle-radius': 6,
        'circle-color': '#00000066',
        'circle-stroke-color': ifNodeExpression(nodeColorExpression, "#00000000"),
        'circle-stroke-width': 1.25,
    }

    console.log(JSON.stringify(styleExpression, null, 2))

    return styleExpression;
}

