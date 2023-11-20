
function createNodeStyleWithParams(color) {
    return new ol.style.Style({
        image: new ol.style.Circle({
            radius: 6,
            fill: new ol.style.Fill({
                color: 'rgba(255,255,255,0.4)'
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
    return createNodeStyleWithParams('#4338ca');
}

// Farbe des Knotens, wenn über ihn gehovert wird.
export function createNodeStyleHover() {
    return createNodeStyleWithParams('#D44D5C');
}


// Farbe der Kante, wenn nicht über sie gehovert ist.
export function createEdgeStyleNormal() {
    return createEdgeStyleWithParams('#4338ca');
}

// Farbe der Kante, wenn über einen Knoten gehovert wird.
export function createEdgeStyleHover(type) {
    // Farbe der ausgehenden Kante, wenn ein Knoten
    // ausgewählt ist. (Wenn also der Knoten Quelle einer Kante ist.)
    const edgeColorHighlightSource = '#773344AA';

    // Farbe der eingehenden Kante, wenn ein Knoten 
    // ausgewählt ist. (Wenn also der Knoten Ziel einer Kante ist.)
    const edgeColorHighlightTarget = '#77334466';

    // Farbe einer Kante, wenn ein Knoten ausgewählt ist und
    // die Kante sowohl eingehende als auch ausgehende Kante ist.
    const edgeColorHighlightBoth = '#773344FF';

    let color = type === "both" ? edgeColorHighlightBoth : type === "source" ? edgeColorHighlightSource : edgeColorHighlightTarget;

    return createEdgeStyleWithParams(color);
}