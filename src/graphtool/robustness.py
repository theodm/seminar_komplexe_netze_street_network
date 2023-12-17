from random import random

import matplotlib
#https://stackoverflow.com/questions/75769820/how-to-prevent-matplotlib-to-be-shown-in-popup-window
matplotlib.use('Agg')

import math
import os
import graph_tool.all as gt

import osm2geojson
import overpass

from joblib import Parallel, delayed

import osmnx as ox
import networkx as nx
import pyintergraph
from osmnx import graph_from_polygon

from src.server.graph.mdig_to_graph import mdig_to_graph

import geopandas as gpd
from shapely.geometry import Polygon

from src.server.graph.nx_to_dual_graph import osmnx_to_dual_graph

import matplotlib.pyplot as plt


def graph_from_geocode(place):
    return ox.graph_from_place(place, network_type="drive")


def calculate_graph_path_metrics(_G, weight=None):
    shortest_distance_matrix = gt.shortest_distance(_G, weights=_G.edge_properties[weight] if weight else None)



    avg_path_length = sum([sum(i) for i in shortest_distance_matrix]) / (_G.num_vertices() ** 2 - _G.num_vertices())
    diameter = max([max(i) for i in shortest_distance_matrix])

    return avg_path_length, diameter

def convert_graph_to_graphtool(G):
    for e in G.edges:
        G.edges[e]["_edge_label"] = str(e)

    for n in G.nodes:
        G.nodes[n]["_node_label"] = str(n)

    graph_tool_graph = pyintergraph.nx2gt(G, "node_label")
    return graph_tool_graph


def save_edge_plot_with_attribute(G, attribute_name, filepath):
    MDG = nx.MultiDiGraph(G)

    ec = ox.plot.get_edge_colors_by_attr(
        MDG, attribute_name, cmap="inferno")

    fig, ax = ox.plot_graph(
        MDG, edge_color=ec, edge_linewidth=2, node_size=0, dpi=50, figsize=(30, 30), filepath=filepath, save=True)

def map_dual_node_attribute_to_primal_edges_attribute(G, DG, attribute_name):
    for e in G.edges:
        edge = G.edges[e]

        edge[attribute_name] = 0

    for n in DG.nodes:
        node_in_dual = DG.nodes[n]

        # Für jede Kante des Straßenzuges im originalen Graphen
        for e in node_in_dual["original_edges"]:
            if not G.has_edge(e[0], e[1]):
                raise ValueError("Edge not found in original graph")

            edge = G.edges[(e[0], e[1])]

            edge[attribute_name] = node_in_dual[attribute_name]



def relative_betweenness_centrality(G, _G,  weight=None):
    vb, eb = gt.betweenness(_G, weight=_G.edge_properties[weight] if weight else None)

    node_betweenness_centrality = {}

    for v in _G.vertices():
        node = eval(_G.vertex_properties["_node_label"][v])

        node_betweenness_centrality[node] = vb[v]

    edge_betweenness_centrality = {}

    for e in _G.edges():
        edge = eval(_G.edge_properties["_edge_label"][e])

        edge_betweenness_centrality[edge] = eb[e]

    # Set the resulting values in all edges and nodes

    def modify_v(x):
        # log(x+1)
        return math.log(100 * x + 1)

    node_betweenness_centrality = {k: modify_v(v) for k, v in node_betweenness_centrality.items()}

    for node in G.nodes:
        if node not in node_betweenness_centrality.keys():
            node_betweenness_centrality[node] = 0

    nx.set_node_attributes(
        G, node_betweenness_centrality, "node_betweenness_centrality")

    edge_betweenness_centrality = {k: modify_v(v) for k, v in edge_betweenness_centrality.items()}

    # Es werden nicht alle Kanten von edge_betweenness_centrality zurückgegeben,
    # wir suchen die fehlenden Kanten und fügen sie mit dem Wert 0 hinzu
    for edge in G.edges:
        if edge not in edge_betweenness_centrality.keys():
            edge_betweenness_centrality[edge] = 0

    nx.set_edge_attributes(
        G, edge_betweenness_centrality, "edge_betweenness_centrality")


stadt_name = "Wiesbaden, Hessen, Deutschland"

print(f"Analysiere nun: {stadt_name}")

stadt_file_name = (stadt_name
                   .replace(", ", "_")
                   .replace(" ", "_")
                   .replace("(", "_")
                   .replace(")", "_")
                   .replace("/", "_")
                   .replace("\\", "_"))

MDG = graph_from_geocode(stadt_name)

# add travel_time attribute to edges
ox.add_edge_speeds(MDG)
ox.add_edge_travel_times(MDG)

G = mdig_to_graph(MDG)

# remove self loops
G.remove_edges_from(nx.selfloop_edges(G))

_G = convert_graph_to_graphtool(G)

i = 0
while True:
    # select random edge
    edges = _G.get_edges()

    random_edge = edges[int(random() * len(edges))]

    print(f"random_edge: {random_edge}")

    _G.remove_edge(list(random_edge))

    avg_path_length, diameter = calculate_graph_path_metrics(_G)

    print(f"avg_path_length: {avg_path_length}")
    print(f"diameter: {diameter}")
    print(f"num_edges: {_G.num_edges()}")

    # get number of connected components
    component_labels, hist = gt.label_components(_G)

    print(f"num_connected_components: {hist}")

    # relative_betweenness_centrality(G, _G)
    # save_edge_plot_with_attribute(G, "edge_betweenness_centrality", filepath=f"robustness/{stadt_file_name}_rb_{i}.png")

    i += 1

#
# avg_path_length, diameter  = calculate_graph_path_metrics(_G)
# avg_path_length_tt, diameter_tt  = calculate_graph_path_metrics(_G, weight="travel_time")
# avg_path_length_lgt, diameter_lgt  = calculate_graph_path_metrics(_G, weight="length")
#
# # Dualer Graph
# DG = osmnx_to_dual_graph(G)
#
# # nodes of dual graph
# num_nodes_dual = DG.number_of_nodes()
# # edges of dual graph
# num_edges_dual = DG.number_of_edges()
#
# # degrees of dual graph
# degrees_dual = DG.degree()
# degrees_values_dual = dict(degrees_dual).values()
# # avg degree of dual graph
# avg_degree_dual = sum(degrees_values_dual) / num_nodes_dual
# # min degree of dual graph
# min_degree_dual = min(degrees_values_dual)
# # max degree of dual graph
# max_degree_dual = max(degrees_values_dual)
