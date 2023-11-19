from bottle import Bottle, run, request, response, static_file, route, get
import osmnx as ox
from networkx.classes.reportviews import NodeView


@route('/')
def server_static():
    return static_file('index.html', root='.')

# get route /graph with query parameter north, east, south...
# which returns a json structure with properties nodes and edges
# calculates route with osmnx and returns nodes and edges
@get('/graph')
def graph():
    north = request.query.north
    east = request.query.east
    south = request.query.south
    west = request.query.west

    # calculate graph with osmnx
    oxg = ox.graph_from_bbox(north, south, east, west, network_type='drive')

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

        str_edge_id = "[" + str(edge_id[0]) + "," + str(edge_id[1]) + "," + str(edge_id[2]) + "]"

        obj = {}

        for key, value in oxedge.items():
            # convert LINESTRING to list of coordinates
            if key == "geometry":
                obj[key] = list(value.coords)
            else:
                obj[key] = value

        edges[str_edge_id] = obj

    return {
        "nodes": nodes,
        "edges": edges
    }



run(host='localhost', port=8080, debug=True)

