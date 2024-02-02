from nx_to_dual_graph import osmnx_to_dual_graph2
import osmnx as ox

from src.server.graph.mdig_to_graph import mdig_to_graph


def test_osmnx_to_dual_graph2():
    # load bbox in osmnx: north: 51.376829999808535 east: 7.493830372772883 south: 51.37415594084297 west: 7.487587956101059

    # load graph from osmnx
    G = ox.graph_from_bbox(51.376829999808535, 51.37415594084297, 7.493830372772883, 7.487587956101059, network_type="drive")
    G = mdig_to_graph(G)

    assert len(G.nodes) == 6
    assert len(G.edges) == 5

    osmnx_to_dual_graph2(G)

    # print all edges and the info dl_label
    for edge in G.edges:
        print(f"{edge} {G.edges[edge]['dl_label'] if 'dl_label' in G.edges[edge] else ''}")

    print("\n")
    for edge in G.edges:
        print(f"{edge} {G.edges[edge]['dual_original_edges'] if 'dual_original_edges' in G.edges[edge] else ''}")

def test_osmnx_to_dual_graph2_2():
    # load bbox in osmnx: north: 51.376829999808535 east: 7.493830372772883 south: 51.37415594084297 west: 7.487587956101059

    # load graph from osmnx
    G = ox.graph_from_bbox(50.08672000001033, 50.081520027080586, 8.241499342430098, 8.228008174205963, network_type="drive")
    G = mdig_to_graph(G)

    osmnx_to_dual_graph2(G)

    # print all edges and the info dl_label
    for edge in G.edges:
        print(f"{edge} {G.edges[edge]['dl_label'] if 'dl_label' in G.edges[edge] else ''}")

    print("\n")
    for edge in G.edges:
        print(f"{edge} {G.edges[edge]['dual_original_edges'] if 'dual_original_edges' in G.edges[edge] else ''}")


def test_osmnx_to_dual_graph2_3():
    # load graph from osmnx
    G = ox.graph_from_bbox(50.08521902848318, 50.08277356729431, 8.246034303382197, 8.239689646680192,
                           network_type="drive")
    G = mdig_to_graph(G)

    osmnx_to_dual_graph2(G)

    # print all edges and the info dl_label
    for edge in G.edges:
        print(f"{edge} {G.edges[edge]['dl_label'] if 'dl_label' in G.edges[edge] else ''}")

    print("\n")
    for edge in G.edges:
        print(f"{edge} {G.edges[edge]['dual_original_edges'] if 'dual_original_edges' in G.edges[edge] else ''}")
