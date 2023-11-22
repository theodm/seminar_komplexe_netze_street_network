from bottle import Bottle, run, request, response, static_file, route, get
import osmnx as ox
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



# get route /api/graph with query parameter north, east, south...
# which returns a json structure with properties nodes and edges
# calculates route with osmnx and returns nodes and edges
@get('/api/graph')
def graph():
    north = request.query.north
    east = request.query.east
    south = request.query.south
    west = request.query.west

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

    max_degree = max(dict(degrees).values())
    avg_degree = sum(dict(degrees).values()) / num_nodes
    min_degree = min(dict(degrees).values())

    return {
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
