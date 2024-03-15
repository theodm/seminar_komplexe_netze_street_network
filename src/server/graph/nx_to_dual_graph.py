from dataclasses import dataclass
from math import isclose

import networkx as nx
from joblib import Memory
from street_continuity.all import *
from street_continuity.util import *

from src.server.colormap.colormap import colormap_for_range


def _dual_graph_to_nxgraph(d_graph: DualGraph):
    nxgraph = nx.Graph()

    for _, node in d_graph.node_dictionary.items():
        nxgraph.add_node(node.did, original_edges=node.edges, names=node.names)

    for _, edge in d_graph.edge_dictionary.items():
        nxgraph.add_edge(edge[0], edge[1])

    return nxgraph

def edge_equal(edge1, edge2):
    if (edge1[0] == edge2[0] and edge1[1] == edge2[1]) or (edge1[0] == edge2[1] and edge1[1] == edge2[0]):
        return True

def get_edge_geometry_latest_to_target(edge, edge_data, source_node, source_node_data, target_node, target_node_data):
    if not "geometry" in edge_data:
        return (source_node_data["x"], source_node_data["y"])

    # ziemlich blöd programmiert, das geht einfacher :/
    end_point = (edge_data["geometry"].coords[-1][0], edge_data["geometry"].coords[-1][1])
    one_before_end_point = (edge_data["geometry"].coords[-2][0], edge_data["geometry"].coords[-2][1])

    start_point = (edge_data["geometry"].coords[0][0], edge_data["geometry"].coords[0][1])
    one_after_start_point = (edge_data["geometry"].coords[1][0], edge_data["geometry"].coords[1][1])

    if isclose(end_point[0], target_node_data["x"]) and isclose(end_point[1], target_node_data["y"]):
        return one_before_end_point
    elif isclose(start_point[0], target_node_data["x"]) and isclose(start_point[1], target_node_data["y"]):
        return one_after_start_point

    raise ValueError("Target node not found in edge geometry")



def osmnx_to_dual_graph2(oxg: nx.Graph, use_label: bool = True):
    for node in oxg.nodes:
        node_data = oxg.nodes[node]
        node_coords = (node_data["x"], node_data["y"])

        edges_tested = {

        }

        for edge in oxg.edges(node):
            edge_data = oxg.edges[edge]

            edge_source = edge[0] if edge[0] != node else edge[1]
            edge_source_data = oxg.nodes[edge_source]
            edge_source_coords = get_edge_geometry_latest_to_target(edge, edge_data, edge_source, edge_source_data, node, node_data)
            edge_target = node

            assert edge_source != edge_target
            assert edge_target == (edge[1] if edge[0] != node else edge[0])

            for edge2 in oxg.edges(node):
                if edge == edge2:
                    continue

                if (edge, edge2) in edges_tested or (edge2, edge) in edges_tested:
                    continue

                edge2_data = oxg.edges[edge2]

                edge2_source = edge2[0] if edge2[0] != node else edge2[1]
                edge2_source_data = oxg.nodes[edge2_source]
                edge2_source_coords = get_edge_geometry_latest_to_target(edge2, edge2_data, edge2_source, edge2_source_data, node, node_data)
                edge2_target = node

                assert edge2_source != edge2_target
                assert edge2_target == (edge2[1] if edge2[0] != node else edge2[0])

                angle = compute_angle(edge_source_coords, node_coords, edge2_source_coords)

                edges_tested[(edge, edge2)] = angle

        # sort edges by angle descending
        edges_tested = sorted(edges_tested.items(), key=lambda x: x[1], reverse=True)

        edges_to_ignore = []

        oxg.nodes[node]["dl_label_to_edge"] = {}

        label_number = 0
        for edges, angle in edges_tested:
            edgeA = edges[0]
            edgeB = edges[1]

            if edgeA in edges_to_ignore or edgeB in edges_to_ignore:
                continue

            edgeA_data = oxg.edges[edgeA]
            edgeB_data = oxg.edges[edgeB]

            def is_compatible_highway(a, b):
                # if a is a string convert to list
                if isinstance(a, str):
                    a = [a]

                if isinstance(b, str):
                    b = [b]

                for _l in a:
                    for _r in b:
                        if _l == _r:
                            return True

                return a == b

            def is_compatible(edgeA_data, edgeB_data):
                if not use_label:
                    return True

                if is_compatible_highway(edgeA_data["highway"], edgeB_data["highway"]):
                    return True

                return False

            if not is_compatible(edgeA_data, edgeB_data):
                continue

            if not "dl_label" in oxg.edges[edgeA]:
                oxg.edges[edgeA]["dl_label"] = []

            oxg.edges[edgeA]["dl_label"].append((node, label_number))

            if not "dl_label" in oxg.edges[edgeB]:
                oxg.edges[edgeB]["dl_label"] = []

            oxg.edges[edgeB]["dl_label"].append((node, label_number))

            edges_to_ignore.append(edgeA)
            edges_to_ignore.append(edgeB)

            oxg.nodes[node]["dl_label_to_edge"][label_number] = [edgeA, edgeB]

            label_number += 1



    @dataclass
    class DualNode():
        did: int
        edges: list
        names: list
        refs: list

    dual_nodes = []
    edges_to_dual_node = {}

    processed_edges = {}

    def gather_edges(edge):
        if edge in processed_edges:
            return []

        processed_edges[edge] = True
        processed_edges[(edge[1], edge[0])] = True

        edge_data = oxg.edges[edge]

        if not "dl_label" in edge_data:
            return [edge]

        # left
        left_node = edge_data["dl_label"][0]
        left_label = left_node[1]

        left_edges = list(
            filter(
                lambda x: not edge_equal(x, edge),
                oxg.nodes[left_node[0]]["dl_label_to_edge"][left_label]
            )
        )

        left_edges = gather_edges(left_edges[0])

        # right
        right_edges = []
        if len(edge_data["dl_label"]) == 2:
            right_node = edge_data["dl_label"][1]
            right_label = right_node[1]

            right_edges = list(
                filter(
                lambda x: not edge_equal(x, edge),
                    oxg.nodes[right_node[0]]["dl_label_to_edge"][right_label]
                )
            )

            right_edges = gather_edges(right_edges[0])

        return left_edges + [edge] + right_edges

    for edge in oxg.edges:
        if edge in processed_edges:
            continue

        edges = gather_edges(edge)
        dual_node = DualNode(did=len(dual_nodes), edges=edges, names=[oxg.edges[e]["name"] if "name" in oxg.edges[e] else "" for e in edges], refs=[oxg.edges[e]["ref"] if "ref" in oxg.edges[e] else "" for e in edges])
        dual_nodes.append(dual_node)

        for edge in edges:
            edges_to_dual_node[edge] = dual_node
            edges_to_dual_node[(edge[1], edge[0])] = dual_node

    dual_edges = []

    for node in oxg.nodes:
        dual_nodes_in_node = []

        for edge in oxg.edges(node):
            dual_node = edges_to_dual_node[edge]

            if dual_node in dual_nodes_in_node:
                continue

            dual_nodes_in_node.append(dual_node)

        processed = []
        for dn1 in dual_nodes_in_node:
            for dn2 in dual_nodes_in_node:
                if dn1 == dn2 or (dn1, dn2) in processed or (dn2, dn1) in processed:
                    continue

                processed.append((dn1, dn2))

                dual_edges.append((dn1.did, dn2.did))

    nxgraph = nx.Graph()

    for dual_node in dual_nodes:
        nxgraph.add_node(dual_node.did, original_edges=dual_node.edges, names=str(dual_node.names), refs=str(dual_node.refs))

    for dual_edge in dual_edges:
        nxgraph.add_edge(dual_edge[0], dual_edge[1])

    def enrich_graph(oxg: nx.Graph, nxgraph: nx.Graph):
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

    enrich_graph(oxg, nxgraph)

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
