
/**
 * GraphResponse is of type
 *
 * interface Graph {
 *     // nid = node id
 *     nodes: { [nid: number]: Node };
 *     // eid = [sourceId,targetId,index]
 *     edges: { [eid: string]: Edge }};
 *     // graphType= "MultiDiGraph" | "Graph"
 *     graphType: "MultiDiGraph" | "Graph";
 *     graphInfo: {
 *         numNodes: number;
 *         numEdges: number;
 *         maxDegree: number;
 *         avgDegree: number;
 *         minDegree: number;
 *     };
 * }
 * 
 * interface Node {
 *    id: number;
 *    lat: number;
 *    lon: number;
 *    // optional, könnte leer sein, falls nicht geladen
 *    // für einen Knoten wird nur eine Rekursionsstufe an
 *    // Nachbarn geladen, um es dem Client einfacher zu machen.
 *    neighbors: Node[] | undefined;
 *    
 *    // dynamisch: alle weiteren Attribute des Knoten (z.B. street_count)
 *    properties: { [key: string]: string };
 * }
 * 
 * interface Edge {
 *     id: string;
 *     osmid: number;
 *     // Hier befindet sich der Verlauf der Straße
 *     // welcher von osmnx herausgefiltert wurde,
 *     // aber weiterhin gespeichert wird.
 *     geometry?: [number,number][];
 *     
 *     // Source- und Target-NodeId
 *     source: Node;
 *     target: Node;
 * 
 *    // dynamisch: alle weiteren Attribute der Kante (z.B. highway, oneway, ...)
 *    properties: { [key: string]: string };
 * }
 */

/**
 * Gibt die Koordinaten-Folge der Kante zurück. (Verlauf der Straße)
 * Kann mehrere Koordinaten umfassen, da osmnx ZwischenKnoten filtert, 
 * aber den Straßenverlauf erhält.
 * 
 * @param {Edge} edge Kante
 * @returns {number[][]} Koordinaten-Folge der Kante
 */
export function edgeGetGeometry(edge) {
    let geometry = edge.geometry;
    
    if (!geometry) {
        // Wenn die Kante keine Geometrie hat, dann wird die Geometrie
        // aus den Koordinaten der Knoten berechnet. (Das wird von osmnx so geliefert.)
        // ToDo: Evtll wäre es schöner das schon auf dem Server zu berechnen ?!
        geometry = [[edge.source.lon, edge.source.lat], [edge.target.lon, edge.target.lat]];
    }

    return geometry;
}

/**
 * Gibt an, ob das vorliegende Objekt ein Knoten ist oder eine Kante
 **/
export function isNode(obj) {
    return obj.lat !== undefined;
}


/**
 * Gibt alle Kanten mit ihrer Id zurück, die in den Knoten
 * mit der Node-ID nodeId hinein oder hinausgehen. Dabei wird
 * der Typ source / target / both zurückgegeben, je nachdem
 * ob die Kante in den Knoten hinein oder hinausgeht oder
 * in beide Richtungen geht.
 *
 * @param {Graph} graph
 * @param {number} nodeId 
 * @returns 
 */
export function findEdgeIdsForNodeWithType(graph, nodeId) {
    const nodes = graph.nodes;
    const edges = graph.edges;

    const result = {}

    for (const eid in edges) {
        var edge = edges[eid];
        if (edge.source.id === nodeId) {
            if (graph.graphType === "Graph") {
                // Bei einem einfachen Graphen (Graph) ist die Richtung egal
                result[eid] = "both";
                continue;
            }
            // Ausgehende Kante
            result[eid] = "source";
            if (!edge.oneway) {
                result[eid] = "both";
            }

        } else if (edge.target.id === nodeId) {
            if (graph.graphType === "Graph") {
                // Bei einem einfachen Graphen (Graph) ist die Richtung egal
                result[eid] = "both";
                continue;
            }

            // Eingehende Kante
            result[eid] = "target";
            if (!edge.oneway) {
                result[eid] = "both";
            }
        }
    }


    return result;
}