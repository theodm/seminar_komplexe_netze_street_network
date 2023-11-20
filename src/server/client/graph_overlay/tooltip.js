import { isNode } from "../graph/graph.js";
import { colorsForNeighbourNodes } from "./styles.js";

/**
 * Beim Hovern über Knoten und Kanten soll ein Tooltip 
 * ausgegeben werden. Hier ist der Inhalt definiert. 
 */
export function getContentsOfTooltip(feature) {
    const obj = feature.get('props');

    if (isNode(feature.get('props'))) {
        // feature is node
        const { id, lat, lon, neighbors, ...otherProps } = feature.get('props');

        // create html for neighbors with color
        const neighborHtml = neighbors.map((neighbor, i) =>
            `<span style="color: ${colorsForNeighbourNodes(i)}">
                ${neighbor.id}
            </span>`
        ).join('');

        return `
            <div>
                <p>type: node</p>
                <p>id: ${id}</p>
                <p>lat: ${lat}</p>
                <p>lon: ${lon}</p>
                <p></p>
                ${Object.entries(otherProps)
                    .map(([key, value]) => `<p>${key}: ${value}</p>`)
                    .join('')}
                <p>neighbours: ${neighborHtml}</p>
            </div>
        `;
    }

    // feature is edge
    return `
        <div>
            <p>type: edge</p>
            <p>id: ${obj.id}</p>
            <p>source: ${obj.source.id}</p>
            <p>target: ${obj.target.id}</p>
            ${Object.entries(obj)
                .filter(([key]) => !['id', 'source', 'target', 'geometry'].includes(key))
                .map(([key, value]) => `<p>${key}: ${value}</p>`)
                .join('')}
        </div>
    `;

}