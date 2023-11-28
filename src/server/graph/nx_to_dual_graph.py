import networkx as nx
from joblib import Memory
from street_continuity.all import *

from src.server.colormap.colormap import colormap_for_range


def _dual_graph_to_nxgraph(d_graph: DualGraph):
    nxgraph = nx.Graph()

    for _, node in d_graph.node_dictionary.items():
        nxgraph.add_node(node.did, original_edges=node.edges, names=node.names)

    for _, edge in d_graph.edge_dictionary.items():
        nxgraph.add_edge(edge[0], edge[1])

    return nxgraph

def osmnx_to_dual_graph(oxg: nx.Graph, min_angle: int = 0, use_label: bool = True):
    '''
    Konvertiert den Graphen extrahiert aus osmnx in den dualen Graphen
    und gibt diesen als eigenen NetworkX-Graph, zur weiteren Analyse
    zurück. Außerdem wird der originale Graph mit weiteren Attributen
    zum dualen Graph versehen.
    '''

    # Nur für den einfachen Graph
    if not isinstance(oxg, nx.Graph):
        raise ValueError("osmnx_to_dual_graph() requires a Graph")

    # Calculate primal graph
    p_graph = from_osmnx(oxg=oxg, use_label=use_label)

    # Calculate dual graph
    d_graph = dual_mapper(primal_graph=p_graph, min_angle=min_angle)

    # Convert dual graph to networkx
    nxgraph = _dual_graph_to_nxgraph(d_graph)

    # Wir speichern direkt die Knotengrade (nun natürlich in den Kanten, denn eine Menge von Kanten im Originalgraphen ist ja ein Knoten des dualen Graphens)
    nodes_to_degree = nxgraph.degree()

    # damit wir die Knoten nach Knotengrad einfärben können
    # hier mit dem matplotlib colormap "inferno"
    colors_for_degree = colormap_for_range(max(dict(nodes_to_degree).values()) + 1, "inferno")

    # Für alle Straßenzüge (die im dualen Graphen als Knoten gespeichert sind)
    for n in nxgraph.nodes:
        node_in_dual = nxgraph.nodes[n]

        # Wir suchen gleich auch die Nachbarn der Knoten im dualen Graphen
        # und dann speichern wir alle orginalen Kanten als jeden Nachbarn
        #
        # z.B. [[(5, 4), (3, 7), (9, 6)], [(2, 0), (10, 9)]]
        # Der Knoten hat zwei Nachbarn, der erste Nachbar hat drei Kanten im Originalgraphen, der zweite Nachbar hat zwei Kanten im Originalgraphen.
        node_neighbors = []

        for neighbor in nxgraph.neighbors(n):
            node_neighbors.append(nxgraph.nodes[neighbor]["original_edges"])

        # Für jede Kante des Straßenzuges im originalen Graphen
        for e in node_in_dual["original_edges"]:
            if not oxg.has_edge(e[0], e[1]):
                raise ValueError("Edge not found in original graph")

            edge = oxg.edges[(e[0], e[1])]

            edge["dual_node_degree"] = nodes_to_degree[n]
            edge["dual_node_degree_color"] = colors_for_degree[nodes_to_degree[n]]
            edge["dual_original_edges"] = node_in_dual["original_edges"]
            edge["dual_original_names"] = node_in_dual["names"]
            edge["dual_node_neighbors"] = node_neighbors

    return nxgraph


