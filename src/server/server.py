from bottle import Bottle, run, request, response, static_file, route, get
import osmnx as ox
import networkx as nx
from networkx.classes.reportviews import NodeView

from graph.mdig_to_graph import mdig_to_graph


# Mit diesen Anweisungen werden alle Dateien im Ordner ./client
# unter der URL /** zur Verfügung gestellt. index.html wird zusätzlich
# unter dem Root-Pfad / bereitgestellt.

@route('/')
def server_static():
    return static_file('index.html', root='./client')
    
@route('/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./client')

graph_cache = {

}

# @get("/api/node_info_")
# def node_info():
#     global graph_cache
#
#     graphkey = request.query.graphkey
#
#     if graphkey not in graph_cache:
#         raise Exception("Graph not found")
#
#     graph = graph_cache[graphkey]
#
#     return {
#         "cluster_coefficient": ox.clustering(graph)
#     }

def get_dead_ends(graph):
    '''
    Gibt für einen Graphen alle Knoten zurück, die nicht in der größten
    starken Zusammenhangskomponente enthalten sind. Das sind die Knoten,
    die keinen Pfad zu allen anderen Knoten haben oder die von denen man nicht
    von der größten Komponente zurück kommt.

    Bei uns kommt das öfters vor, wenn wir nur einen Ausschnitt des Graphen
    anzeigen oder wegen des Reduktionsschritts von osmnx bzw. fehlerhaften
    Daten.
    '''
    components = list(nx.strongly_connected_components(graph))

    # Die Knoten der größten Komponente gehören nicht zu unserem Ergebnis
    largest_component = max(components, key=len)
    components.remove(largest_component)

    return [node for component in components for node in component]


@get("/api/shortest_path_info")
def shortest_path_info():
    global graph_cache

    graphkey = request.query.graphkey

    if graphkey not in graph_cache:
        raise Exception("Graph not found")

    graph = graph_cache[graphkey]

    # ToDo: Bei allen Requests die Fehler im JS / HTML
    # auslesen und als Modal ausgeben, damit der Benutzer
    # weiß was schief gelaufen ist.
    nodes_without_shortest_path = get_dead_ends(graph)

    try:
        average_shortest_path_length = nx.average_shortest_path_length(graph)
    except nx.NetworkXError:
        average_shortest_path_length = "<not connected>"

    try:
        diameter = nx.diameter(graph)
    except nx.NetworkXError:
        diameter = "<not connected>"

    return {
        "graphkey": graphkey,
        "no_path_to_all_nodes": [int(node) for node in nodes_without_shortest_path],
        "graphType": "Graph" if graph is nx.Graph else "MultiDiGraph",
        "average_shortest_path_length": average_shortest_path_length,
        "diameter": diameter,
    }


# get route /api/graph with query parameter north, east, south...
# which returns a json structure with properties nodes and edges
# calculates route with osmnx and returns nodes and edges
@get('/api/graph')
def graph():
    global graph_cache

    north = request.query.north
    east = request.query.east
    south = request.query.south
    west = request.query.west
    filter_dead_ends = request.query.get_dead_ends == "true"

    oxg = ox.graph_from_bbox(north, south, east, west, network_type='drive')

    # request type can be Graph or MultiDiGraph
    graph_type = request.query.type
    if graph_type == "Graph":
        oxg = mdig_to_graph(oxg)
    elif graph_type == "MultiDiGraph":
        pass
    else:
        raise Exception("Invalid request type")

    nodes = {}

    def node_view_to_node_json(nid: int, node: NodeView, recursive: bool):
        obj = {
            "lat": node["y"],
            "lon": node["x"],
            "id": nid
        }

        for key, value in node.items():
            obj[key] = value

        if recursive:
            obj["neighbors"] = []

            for neighbor_id in oxg.neighbors(nid):
                obj["neighbors"].append(node_view_to_node_json(neighbor_id, oxg.nodes[neighbor_id], False))

        return obj

    for node_id in oxg.nodes:
        oxnode: NodeView = oxg.nodes[node_id]

        nodes[node_id] = node_view_to_node_json(node_id, oxnode, True)

    edges = {}

    for edge_id in oxg.edges:
        oxedge = oxg.edges[edge_id]

        if graph_type == "Graph":
            str_edge_id = "[" + str(edge_id[0]) + "," + str(edge_id[1]) + "]"
        elif graph_type == "MultiDiGraph":
            str_edge_id = "[" + str(edge_id[0]) + "," + str(edge_id[1]) + "," + str(edge_id[2]) + "]"
        else:
            raise Exception("Invalid request type")

        obj = {}

        for key, value in oxedge.items():
            # convert LINESTRING to list of coordinates
            if key == "geometry":
                obj[key] = list(value.coords)
            else:
                obj[key] = value

        obj["id"] = str_edge_id
        obj["source"] = node_view_to_node_json(edge_id[0], oxg.nodes[edge_id[0]], True)
        obj["target"] = node_view_to_node_json(edge_id[1], oxg.nodes[edge_id[1]], True)

        edges[str_edge_id] = obj

    # calculate num_nodes, num_edges, max_degree, avg_degree, min_degree
    num_nodes = oxg.number_of_nodes()
    num_edges = oxg.number_of_edges()

    degrees = oxg.degree()

    # Alle Knoten bekommen ein Attribut "degree" mit der Anzahl der Kanten (Knotengrad)
    for node_id in oxg.nodes:
        nodes[node_id]["degree"] = degrees[node_id]

    # Außerdem ein paar Grad-Statistiken für den Graphen
    max_degree = max(dict(degrees).values())
    avg_degree = sum(dict(degrees).values()) / num_nodes
    min_degree = min(dict(degrees).values())

    # Wir speichern einen Graph_Key für diesen Graphen
    # damit dieser vom Client erneut referenziert werden kann
    # und dann nicht neu berechnet werden muss.
    # Potzentiell unsicher und ineffizient: Diese Anwendung sollte nur lokal verwendet
    # werden, niemals über das Internet verfügbar sein. (DDOS, etc.)
    graphkey = "graph" + north + "_" + east + "_" + south + "_" + west + "_" + graph_type + "_" + str(filter_dead_ends)
    graph_cache[graphkey] = oxg

    if filter_dead_ends:
        oxg.remove_nodes_from(filter_dead_ends(oxg))

    return {
        "graphkey": graphkey,
        "filter_dead_ends": bool(filter_dead_ends),
        "graphType": graph_type,
        "nodes": nodes,
        "edges": edges,
        "graphInfo": {
            "numNodes": num_nodes,
            "numEdges": num_edges,
            "maxDegree": max_degree,
            "avgDegree": avg_degree,
            "minDegree": min_degree
        }
    }



run(host='localhost', port=8080, debug=True)
