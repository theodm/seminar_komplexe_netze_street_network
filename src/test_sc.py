import networkx as nx
from joblib import Memory
from street_continuity.all import *


memory = Memory("cachedir", verbose=0)

@memory.cache
def cached_graph_from_place(place, network_type):
    return ox.graph_from_place(place, network_type=network_type)
# load the primal graph from osmnx
oxg = cached_graph_from_place("Darmstadt, Germany", network_type="drive")


# @memory.cache
# def cached_graph_from_bbox(north, south, east, west, network_type):
#     return ox.graph_from_bbox(north, south, east, west, network_type=network_type)
#
# oxg = cached_graph_from_bbox(50.2977, 49.8367, 8.9628, 8.0516, network_type="drive")


def dual_graph_to_nxgraph(d_graph: DualGraph):
    nxgraph = nx.Graph()

    for _, node in d_graph.node_dictionary.items():
        nxgraph.add_node(node.did, original_edges=node.edges, names=node.names)

    for _, edge in d_graph.edge_dictionary.items():
        nxgraph.add_edge(edge[0], edge[1])

    return nxgraph

def plot_with_degree(oxg: nx.MultiDiGraph, min_angle: int = 90, min_degree: int = 0):
    # Calculate primal graph
    p_graph = from_osmnx(oxg=oxg, use_label=True)

    # Calculate dual graph
    d_graph = dual_mapper(primal_graph=p_graph, min_angle=min_angle)

    # Convert dual graph to networkx
    nxgraph = dual_graph_to_nxgraph(d_graph)

    # Calculate degree of nodes in dual graph (Anzahl Kreuzungen des Straßenzuges)
    nodes_to_degree = nxgraph.degree()

    # Nun setzen wir im originalen Graphen
    # in den Kanten die Anzahl der Kreuzungen (Knotengrad im dualen Graph)
    # dann können wir die Kanten entsprechend kolorieren

    # default value for all edges
    for edge in oxg.edges:
        oxg.edges[edge]["degree"] = 0

    selected_nodes = [n for n, d in nxgraph.degree() if d >= min_degree]
    
    # Für alle Straßenzüge (die im dualen Graphen als Knoten gespeichert sind)
    for n in selected_nodes:
        # Für jede Kante des Straßenzuges im originalen Graphen
        for e in nxgraph.nodes[n]["original_edges"]:
            
            # Workaround: Im originalen Graphen kann es Mehrfachverbindungen geben.
            # wir geben allen Kanten die entsprechenden Eigenschaften.
            for i in range(100):
                if oxg.has_edge(e[0], e[1], i):
                    edge = oxg.edges[e[0], e[1], i]
                    edge["degree"] = nodes_to_degree[n]

                if oxg.has_edge(e[1], e[0], i):
                    edge = oxg.edges[e[1], e[0], i]
                    edge["degree"] = nodes_to_degree[n]
    
    # Nun können wir die Kanten entsprechend kolorieren
    ec = ox.plot.get_edge_colors_by_attr(oxg, "degree", cmap="inferno")

    # und anzeigen
    fig, ax = ox.plot_graph(
        oxg, edge_color=ec, edge_linewidth=2, node_size=0, dpi=5000, figsize=(30, 30))

def plot_with_colors(oxg: nx.MultiDiGraph, min_angle: int = 90, min_degree: int = 0):
    # Calculate primal graph
    p_graph = from_osmnx(oxg=oxg, use_label=True)

    # Calculate dual graph
    d_graph = dual_mapper(primal_graph=p_graph, min_angle=90)

    # Convert dual graph to networkx
    nxgraph = dual_graph_to_nxgraph(d_graph)

    # use greedy coloring to color the nodes
    colors = nx.greedy_color(nxgraph, strategy="largest_first")
    max_color = max(colors.values()) + 1

    # ToDo: Das sollten wirklich unterschiedliche Farben sein, eine ColorMap geht nicht,
    # da ähnliche Werte auch gleiche Farben hervorbringen
    colormap = ox.plot.get_colors(n=max_color, cmap="Paired", alpha=1.0, return_hex=True)

    selected_nodes = [n for n, d in nxgraph.degree() if d >= min_degree]

    # Für alle Straßenzüge (die im dualen Graphen als Knoten gespeichert sind)
    for n in selected_nodes:
        # Eine Farbe für jeden Straßenzug
        color_num = colors[n]

        # Für jede Kante des Straßenzuges im originalen Graphen
        for e in nxgraph.nodes[n]["original_edges"]:

            # Workaround: Im originalen Graphen kann es Mehrfachverbindungen geben.
            # wir geben allen Kanten die entsprechenden Eigenschaften.
            for i in range(100):
                if oxg.has_edge(e[0], e[1], i):
                    edge = oxg.edges[e[0], e[1], i]
                    edge["color"] = colormap[color_num]

                if oxg.has_edge(e[1], e[0], i):
                    edge = oxg.edges[e[1], e[0], i]
                    edge["color"] = colormap[color_num]

    # Nun können wir die Kanten entsprechend kolorieren
    ec = []

    for edge in oxg.edges:
        if not "color" in oxg.edges[edge]:
            oxg.edges[edge]["color"] = "#ffffff"

        ec.append(oxg.edges[edge]["color"])

    # und anzeigen
    fig, ax = ox.plot_graph(
        oxg, edge_color=ec, edge_linewidth=2, node_size=0, dpi=5000, figsize=(30, 30))

plot_with_degree(oxg)