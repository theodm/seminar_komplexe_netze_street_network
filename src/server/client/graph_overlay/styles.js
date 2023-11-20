
export function colorsForNeighbourNodes(index) {
    return [
        "#e11d48",
        "#22c55e",
        "#c026d3",
        "#a3e635",
        "#6d28d9",
        "#38bdf8",
        "#ea580c",
        "#f9a8d4",
        "#f59e0b"
    ][index % 9];
}

function createNodeStyleWithParams(color, highlight=false) {
    let fillColor = highlight ? (color + "99") : 'rgba(255,255,255,0.4)';

    return new ol.style.Style({
        image: new ol.style.Circle({
            radius: 6,
            fill: new ol.style.Fill({
                color: fillColor
            }),
            stroke: new ol.style.Stroke({
                color: color,
                width: 1.25
            })
        })
    });
}

function createEdgeStyleWithParams(color) {
    return new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: color,
            width: 3
        }),
        fill: new ol.style.Fill({
            color: 'rgba(255,255,255,0.1)'
        })
    });
}

// Farbe des Knotens, wenn nicht über ihn gehovert wird.
export function createNodeStyleNormal() {
    return createNodeStyleWithParams('#64748b');
}

// Farbe des Knotens, wenn über ihn gehovert wird.
export function createNodeStyleHover() {
    return createNodeStyleWithParams('#f59e0b', true);
}

// Farbe der Nachbarknoten, wenn über den Base-Knoten gehovert wird.
export function createNodeNeighborStyleHover(index) {
    return createNodeStyleWithParams(colorsForNeighbourNodes(index), true);
}




// Farbe der Kante, wenn nicht über sie gehovert ist.
export function createEdgeStyleNormal() {
    return createEdgeStyleWithParams('#64748b');
}

// Farbe der Kante, wenn über einen Knoten gehovert wird.
export function createEdgeStyleHover(type) {
    // Farbe der ausgehenden Kante, wenn ein Knoten
    // ausgewählt ist. (Wenn also der Knoten Quelle einer Kante ist.)
    const edgeColorHighlightSource = '#f59e0b';

    // Farbe der eingehenden Kante, wenn ein Knoten 
    // ausgewählt ist. (Wenn also der Knoten Ziel einer Kante ist.)
    const edgeColorHighlightTarget = '#1e293b';

    // Farbe einer Kante, wenn ein Knoten ausgewählt ist und
    // die Kante sowohl eingehende als auch ausgehende Kante ist.
    const edgeColorHighlightBoth = '#dc2626';

    let color = type === "both" ? edgeColorHighlightBoth : type === "source" ? edgeColorHighlightSource : edgeColorHighlightTarget;

    return createEdgeStyleWithParams(color);
}