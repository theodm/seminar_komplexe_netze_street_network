import math

import osmnx.plot
from bottle import Bottle, run, request, response, static_file, route, get
import osmnx as ox
import networkx as nx
from networkx.classes.reportviews import NodeView

from graph.mdig_to_graph import mdig_to_graph
import matplotlib.pyplot as plt
import io
import base64

from src.server.colormap.colormap import colormap_for_range
from src.server.colormap.colormap import colormap_for_float_range_fn
from src.server.graph.redo_geometry import redo_geometry


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



# @get("/api/color_edge_betweenness_centrality")
# def color_relative_betweenness():
#     global graph_cache
#
#     graphkey = request.query.graphkey
#
#     if graphkey not in graph_cache:
#         raise Exception("Graph not found")
#
#     graph = graph_cache[graphkey]
#
#     edge_betweenness_centrality = nx.edge_betweenness_centrality(graph)

@get("/api/degree_histogram")
def degree_histogram():
    global graph_cache

    graphkey = request.query.graphkey

    if graphkey not in graph_cache:
        raise Exception("Graph not found")

    graph = graph_cache[graphkey]

    plt.clf()
    degrees = [d for n, d in graph.degree()]
    plt.hist(degrees, bins=range(min(degrees), max(degrees) + 1, 1))

    response.content_type = 'image/png'

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf.read()

def get_graph_type_as_str(graph):
    if isinstance(graph, nx.Graph):
        return "Graph"
    elif isinstance(graph, nx.MultiGraph):
        return "MultiGraph"
    elif isinstance(graph, nx.DiGraph):
        return "DiGraph"
    elif isinstance(graph, nx.MultiDiGraph):
        return "MultiDiGraph"
    else:
        raise Exception("Invalid graph type")

@get("/api/load_node_data")
def load_node_data():
    global graph_cache

    data_type = request.query.data_type
    graphkey = request.query.graphkey

    if graphkey not in graph_cache:
        raise Exception("Graph not found")

    graph = graph_cache[graphkey]

    if data_type == "relative_betweenness":
        # ToDo: relative betweenness with travel time?
        relative_betweenness_centrality = nx.betweenness_centrality(graph)

        # Wir passen jeden Wert der relativen Betweenness Centrality für die
        # Farbdarstellung logarithmisch an. Damit werden auch mittelmäßig wichtige
        # Knoten noch farblich unterschieden von unbedeutenden.
        def logify(x):
            # log(x+1)
            return math.log(100 * x + 1)
        color_fn = colormap_for_float_range_fn([logify(rbc) for rbc in relative_betweenness_centrality.values()], "inferno")


        result = { nodeId: {
            "relative_betweenness_centrality": rbc,
            "rbcColor": color_fn(logify(rbc))
        } for nodeId, rbc in relative_betweenness_centrality.items() }

        return {
            "graphkey": graphkey,
            "dataType": data_type,
            "graphType": get_graph_type_as_str(graph),
            "data": result
        }
    else:
        raise Exception("Invalid data type")


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
    # only if graph instance of mMltiDiGraph or DiGraph
    dead_ends = []
    if isinstance(graph, nx.MultiDiGraph) or isinstance(graph, nx.DiGraph):
        dead_ends = get_dead_ends(graph)

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
        "no_path_to_all_nodes": [int(node) for node in dead_ends],
        "graphType": get_graph_type_as_str(graph),
        "average_shortest_path_length": average_shortest_path_length,
        "diameter": diameter,
    }

def adjust_graph_edges_geometry(graph):
    # osmnx vereinfacht die Daten aus OSM, dort gibt es auch für ein Straßensegment
    # eigentlich mehrere Knoten. osmnx speichert bei der Vereinfachung aber die Koordinaten
    # für alle vorher bestehenden Punkte um das Straßensegement beim Zeichnen nachzeichnen zu können.
    # Das Attribut geometry gibt es jedoch nur bei Kanten, bei denen auch tatsächlich eine Vereinfachung
    # stattgefunden hat.
    # Wir vereinheitlichen und machen das auch überall dort, wo keine Vereinfachung notwendig war.
    for edge in graph.edges:
        edge_data = graph.edges[edge]

        if not "geometry" in edge_data:
            edge_data["geometry"] = [(graph.nodes[edge[0]]['x'], graph.nodes[edge[0]]['y']), (graph.nodes[edge[1]]['x'], graph.nodes[edge[1]]['y'])]


    for edge in graph.edges:
        edge_data = graph.edges[edge]

        if "done" in edge_data:
            continue

        if (edge[1], edge[0], edge[2]) in graph.edges:
            other = graph.edges[(edge[1], edge[0], edge[2])]

            geometry = edge_data["geometry"] if isinstance(edge_data["geometry"], list) else list(edge_data["geometry"].coords)
            geometry = redo_geometry(geometry, 0.00001)
            edge_data["geometry"] = geometry
            edge_data["done"] = True

            geometry_other = other["geometry"] if isinstance(other["geometry"], list) else list(other["geometry"].coords)
            geometry_other = redo_geometry(geometry_other, 0.00001)
            other["geometry"] = geometry_other
            other["done"] = True

    return

@get('/api/graph')
def graph():
    global graph_cache

    north = request.query.north
    east = request.query.east
    south = request.query.south
    west = request.query.west
    _filter_dead_ends = request.query.filter_dead_ends == "true"
    _redo_geometry = request.query.redo_geometry == "true"

    oxg = ox.graph_from_bbox(north, south, east, west, network_type='drive')

    # request type can be Graph or MultiDiGraph
    graph_type = request.query.type

    if (graph_type == "DiGraph" or graph_type == "MultiDiGraph") and _redo_geometry:
        adjust_graph_edges_geometry(oxg)

    if graph_type == "Graph":
        oxg = mdig_to_graph(oxg)
    elif graph_type == "DiGraph":
        oxg = ox.utils_graph.get_digraph(oxg)
    elif graph_type == "MultiGraph":
        oxg = ox.utils_graph.get_undirected(oxg)
    elif graph_type == "MultiDiGraph":
        pass
    else:
        raise Exception("Invalid request type")


    nodes = {}

    if _filter_dead_ends and (isinstance(oxg, nx.MultiDiGraph) or isinstance(oxg, nx.DiGraph)):
        dead_ends = get_dead_ends(oxg)
        print("Filtering dead ends" + str(dead_ends))
        oxg.remove_nodes_from(get_dead_ends(oxg))

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
        elif graph_type == "DiGraph":
            str_edge_id = "[" + str(edge_id[0]) + "," + str(edge_id[1]) + "]"
        elif graph_type == "MultiGraph":
            str_edge_id = "[" + str(edge_id[0]) + "," + str(edge_id[1]) + "," + str(edge_id[2]) + "]"
        elif graph_type == "MultiDiGraph":
            str_edge_id = "[" + str(edge_id[0]) + "," + str(edge_id[1]) + "," + str(edge_id[2]) + "]"
        else:
            raise Exception("Invalid request type")

        obj = {}

        for key, value in oxedge.items():
            # bei adjust_graph_edges_geometry() wird geometry zum Teil zu einer Liste
            if key == "geometry" and not isinstance(value, list):
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

    # damit wir die Knoten nach Knotengrad einfärben können
    # hier mit dem matplotlib colormap "inferno"
    colors_for_degree = colormap_for_range(max(dict(oxg.degree()).values()) + 1, "inferno")

    degrees = oxg.degree()
    if graph_type == "DiGraph" or graph_type == "MultiDiGraph":
        out_degrees = oxg.out_degree()
        in_degrees = oxg.in_degree()

    # Alle Knoten bekommen ein Attribut "degree" mit der Anzahl der Kanten (Knotengrad)
    for node_id in oxg.nodes:
        nodes[node_id]["degree"] = degrees[node_id]
        nodes[node_id]["degree_color"] = colors_for_degree[degrees[node_id]]

        if graph_type == "DiGraph" or graph_type == "MultiDiGraph":
            nodes[node_id]["out_degree"] = out_degrees[node_id]
            nodes[node_id]["in_degree"] = in_degrees[node_id]

    # Außerdem ein paar Grad-Statistiken für den Graphen
    max_degree = max(dict(degrees).values())
    avg_degree = sum(dict(degrees).values()) / num_nodes
    min_degree = min(dict(degrees).values())

    if graph_type == "DiGraph" or graph_type == "MultiDiGraph":
        max_degree = f"{max_degree} (out: {max(dict(out_degrees).values())}, in: {max(dict(in_degrees).values())})"
        avg_degree = f"{avg_degree} (out: {sum(dict(out_degrees).values()) / num_nodes}, in: {sum(dict(in_degrees).values()) / num_nodes})"
        min_degree = f"{min_degree} (out: {min(dict(out_degrees).values())}, in: {min(dict(in_degrees).values())})"

    global_cluster_coefficient_avg = '<multi graph>'
    if graph_type == "Graph" or graph_type == "DiGraph":
        # Alle Knoten bekommen ein Attribut "local_cluster_coefficient" mit dem lokalen Cluster-Koeffizienten
        # (Anzahl der Kanten zwischen den Nachbarn eines Knotens / Anzahl der möglichen Kanten zwischen den Nachbarn eines Knotens)
        for node_id in oxg.nodes:
            nodes[node_id]["local_cluster_coefficient"] = nx.clustering(oxg, node_id)

        global_cluster_coefficient_avg = nx.average_clustering(oxg)

    # Wir speichern einen Graph_Key für diesen Graphen
    # damit dieser vom Client erneut referenziert werden kann
    # und dann nicht neu berechnet werden muss.
    # Potzentiell unsicher und ineffizient: Diese Anwendung sollte nur lokal verwendet
    # werden, niemals über das Internet verfügbar sein. (DDOS, etc.)
    graphkey = "graph" + north + "_" + east + "_" + south + "_" + west + "_" + graph_type + "_" + str(_filter_dead_ends) + "_" + str(_redo_geometry)
    graph_cache[graphkey] = oxg


    return {
        "graphkey": graphkey,
        "filter_dead_ends": bool(_filter_dead_ends),
        "redo_geometry": bool(_redo_geometry),
        "graphType": graph_type,
        "nodes": nodes,
        "edges": edges,
        "graphInfo": {
            "numNodes": num_nodes,
            "numEdges": num_edges,
            "maxDegree": max_degree,
            "avgDegree": avg_degree,
            "minDegree": min_degree,
            "globalClusterCoefficientAvg": global_cluster_coefficient_avg
        }
    }



run(host='localhost', port=8080, debug=True)
