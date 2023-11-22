

/**
 * Installiert einen Hover-Handler für Features auf der Karte. Zur Erinnerung
 * Features sind z.B. Knoten oder Kanten (bzw. alle Objekte auf der Karte, die wir definiert haben).
 * 
 * @param {function} onHover Wird immer aufgerufen, wenn sich der Mauszeiger über einem Feature befindet.
 * @param {function} onHoverEnter Wird aufgerufen, wenn der Mauszeiger erstmalig über einem Feature ist. (nur einmal)
 * @param {function} onHoverLeave Wird aufgerufen, wenn der Mauszeiger das Feature verlässt. (nur einmal)
 */
export function registerFeatureHover(map, onHover, onHoverEnter, onHoverLeave, featureSelector = (features) => features[0]) {
    let currentFeature = undefined;

    let pointerMoveCallback = (evt) => {
        if (evt.dragging) {
            return;
        }

        // var pixel = map.getEventPixel(evt.originalEvent);

        const features = []
        map.forEachFeatureAtPixel(evt.pixel,
            function (feature) {
                features.push(feature);
            }, {
            hitTolerance: 5
        }
        );

        const hit = features.length > 0;
        map.getTargetElement().style.cursor = hit ? 'pointer' : '';
        if (hit) {
            console.log('featuers ', features)
            const feature = featureSelector(features);
            console.log('feature ', feature)


            onHover(evt, feature);

            if (feature !== currentFeature) {
                onHoverEnter(evt, feature);
                currentFeature = feature;
            }
        } else {
            onHoverLeave(evt, currentFeature);
            currentFeature = undefined;
        }
    };
    map.on('pointermove', pointerMoveCallback);

    let pointerLeaveCallback = (evt) => {
        onHoverLeave(evt, currentFeature);
        currentFeature = undefined;
    };
    map.getTargetElement().addEventListener('pointerleave', pointerLeaveCallback);

    return [pointerMoveCallback, pointerLeaveCallback];
}

export function removeHoverOverFeatures(map, removeArray) {
    map.un('pointermove', removeArray[0]);
    map.getTargetElement().removeEventListener('pointerleave', removeArray[1]);
}