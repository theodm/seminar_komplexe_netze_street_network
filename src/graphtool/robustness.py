from random import random

import joblib
import matplotlib
import numpy as np
#https://stackoverflow.com/questions/75769820/how-to-prevent-matplotlib-to-be-shown-in-popup-window
matplotlib.use('Agg')

import math
import os
import graph_tool.all as gt

import osm2geojson
import overpass

from collections import Counter

from joblib import Parallel, delayed, Memory

import osmnx as ox
import networkx as nx
import pyintergraph
from osmnx import graph_from_polygon

from src.server.graph.mdig_to_graph import mdig_to_graph

import geopandas as gpd
from shapely.geometry import Polygon

from src.server.graph.nx_to_dual_graph import osmnx_to_dual_graph

import matplotlib.pyplot as plt


def graph_from_geojson(geojson):
    gdf = gpd.GeoDataFrame.from_features(geojson)

    polygon = gdf["geometry"].unary_union

    # create graph using this polygon(s) geometry
    G = graph_from_polygon(
        polygon,
        network_type="drive"
    )

    return G

def graph_from_geocode(place):
    return ox.graph_from_place(place, network_type="drive")

def get_all_nodes_from_largest_component(_G, component_labels, most_frequent_component_label):
    res = []

    for v in _G.vertices():
        if component_labels[v] == most_frequent_component_label:
            res.append(v)

    return res

# Gibt alle Knoten zurück, die nicht in der größten Komponente sind.
def get_all_nodes_from_non_largest_component(_G, component_labels, most_frequent_component_label):
    res = []

    for v in _G.vertices():
        if component_labels[v] != most_frequent_component_label:
            res.append(v)

    return res


def calculate_graph_path_metrics(_G, ignore_nodes=[],  weight=None):
    __G = _G.copy()
    __G.remove_vertex(ignore_nodes)

    shortest_distance_matrix = gt.shortest_distance(__G, weights=__G.edge_properties[weight] if weight else None)
            
    avg_path_length = sum([sum(i) for i in shortest_distance_matrix]) / (__G.num_vertices() ** 2 - __G.num_vertices())
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


def removal_causes_multiple_components(_G, edge_to_remove):
    # Nur benutzbar, falls es vorher nur eine Komponente gab.
    __G = _G.copy()

    __G.remove_edge(list(edge_to_remove))

    component_labels, hist = gt.label_components(__G)

    return len([h for h in hist if h > 1]) > 1


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
    
    return node_betweenness_centrality, edge_betweenness_centrality, vb, eb


def analyze_stadt(stadt, strategy, normalized_steps, avoid_multiple_components=False):

    matplotlib.use('Agg')

    if isinstance(stadt, dict):
        stadt_name = stadt["stadt_name_gvad"]
    else:
        stadt_name = stadt

    print(f"Analysiere nun: {stadt_name}, {strategy}, {normalized_steps}, {avoid_multiple_components}")

    stadt_file_name = (stadt_name
                    .replace(", ", "_")
                    .replace(" ", "_")
                    .replace("(", "_")
                    .replace(")", "_")
                    .replace("/", "_")
                    .replace("\\", "_"))

    if isinstance(stadt, dict):
        MDG = graph_from_geojson(stadt["geojson"])
    else:
        MDG = graph_from_geocode(stadt)

    # add travel_time attribute to edges
    ox.add_edge_speeds(MDG)
    ox.add_edge_travel_times(MDG)

    G = mdig_to_graph(MDG)

    # remove self loops
    G.remove_edges_from(nx.selfloop_edges(G))

    _G = convert_graph_to_graphtool(G)

    if strategy == "random":
        pass
    elif strategy == "betweenness" or strategy == "betweenness_with_recomputation":
        nc, ec, ncr, ecr = relative_betweenness_centrality(G, _G)
    elif strategy == "betweenness_tt" or strategy == "betweenness_with_recomputation_tt":
        nc, ec, ncr, ecr = relative_betweenness_centrality(G, _G, weight="travel_time")

    start_avg_path_length, start_diameter = calculate_graph_path_metrics(_G, ignore_nodes=[])
    start_avg_path_length_tt, start_diameter_tt = calculate_graph_path_metrics(_G, ignore_nodes=[], weight="travel_time")

    start_num_edges = _G.num_edges()

    step_results = []

    step_results.append({
        "step": 0,
        "normalized_step": 0,

        "num_components": 1,

        "largest_component_num_nodes": int(_G.num_vertices()),
        "largest_component_num_edges": int(_G.num_edges()),

        "largest_component_avg_path_length": float(start_avg_path_length),
        "largest_component_diameter": float(start_diameter),

        "largest_component_avg_path_length_tt": float(start_avg_path_length_tt),
        "largest_component_diameter_tt": float(start_diameter_tt),

        "normalized_largest_component_avg_path_length": float(start_avg_path_length / start_avg_path_length),
        "normalized_largest_component_diameter": float(start_diameter / start_diameter),

        "normalized_largest_component_avg_path_length_tt": float(start_avg_path_length_tt / start_avg_path_length_tt),
        "normalized_largest_component_diameter_tt": float(start_diameter_tt / start_diameter_tt),

        "num_edges": int(start_num_edges),
        "num_nodes": int(_G.num_vertices()),
    })

    print(f"real steps to do: {normalized_steps * start_num_edges}")

    i = 0

    edges_from_largest_component = _G.get_edges()

    while True:
        try:
            edges = edges_from_largest_component

            if strategy == "betweenness_with_recomputation" or strategy == "betweenness_with_recomputation_tt":
                nc, ec, ncr, ecr = relative_betweenness_centrality(G, _G, weight="travel_time" if strategy == "betweenness_with_recomputation_tt" else None)

                #save_edge_plot_with_attribute(G, "edge_betweenness_centrality", f"./robustness/{stadt_file_name}_{strategy}_{normalized_steps}_{avoid_multiple_components}_{i}.png")

            edge_to_remove = None
            if strategy == "random":
                # Auswahl: Welche Kante soll entfernt werden?
                # hier: zufällige Kante
                while True:
                    edge_to_remove = edges[int(random() * len(edges))]

                    if avoid_multiple_components and removal_causes_multiple_components(_G, edge_to_remove):
                        continue

                    break

            elif strategy == "betweenness" or strategy == "betweenness_tt" or strategy == "betweenness_with_recomputation" or strategy == "betweenness_with_recomputation_tt":
                _max = 0

                for e in edges:
                    if ecr[e] > _max and (not avoid_multiple_components or not removal_causes_multiple_components(_G, e)):
                        _max = ecr[e]
                        edge_to_remove = e
            else:
                raise ValueError(f"Unknown strategy {strategy}")

            #print(f"Remove edge: {edge_to_remove}")

            edge_label = eval(_G.edge_properties["_edge_label"][edge_to_remove])
            G.remove_edge(edge_label[0], edge_label[1])
            _G.remove_edge(list(edge_to_remove))
            i += 1

            # Auswertung: Wie hat sich das Netzwerk entwickelt?

            # https://graph-tool.skewed.de/static/doc/autosummary/graph_tool.topology.label_components.html
            component_labels, hist = gt.label_components(_G)

            # Welchen Wert gibt es in largest_component am häufigsten. Hier: Was ist die größte Komponente
            # und welche Knoten gehören zu ihr?
            # https://stackoverflow.com/questions/6252280/find-the-most-frequent-number-in-a-numpy-vector
            most_frequent_component_label = Counter(list(component_labels)).most_common(1)[0][0]

            # Gibt alle Kanten zurück, die in der größten Komponente sind.
            def get_edges_from_largest_component():
                edges = _G.get_edges()

                edges_from_largest_component = []

                for e in edges:
                    # get nodes of edge
                    v1 = e[0]
                    v2 = e[1]

                    if component_labels[v1] != most_frequent_component_label or component_labels[v2] != most_frequent_component_label:
                        continue

                    edges_from_largest_component.append(e)

                return edges_from_largest_component

            edges_from_largest_component = get_edges_from_largest_component()

            avg_path_length, diameter = calculate_graph_path_metrics(_G, ignore_nodes=get_all_nodes_from_non_largest_component(_G, component_labels, most_frequent_component_label))
            avg_path_length_tt, diameter_tt = calculate_graph_path_metrics(_G, ignore_nodes=get_all_nodes_from_non_largest_component(_G, component_labels, most_frequent_component_label), weight="travel_time")

            step_results.append({
                "step": i,
                "normalized_step": float(i / start_num_edges),


                "num_components": len(hist),

                "largest_component_num_nodes": int(hist[most_frequent_component_label]),
                "largest_component_num_edges": len(edges_from_largest_component),

                "largest_component_avg_path_length": float(avg_path_length),
                "largest_component_diameter": float(diameter),

                "largest_component_avg_path_length_tt": float(avg_path_length_tt),
                "largest_component_diameter_tt": float(diameter_tt),

                "normalized_largest_component_avg_path_length": float(avg_path_length / start_avg_path_length),
                "normalized_largest_component_diameter": float(diameter / start_diameter),

                "normalized_largest_component_avg_path_length_tt": float(avg_path_length_tt / start_avg_path_length_tt),
                "normalized_largest_component_diameter_tt": float(diameter_tt / start_diameter_tt),

                "num_edges": int(_G.num_edges()),
                "num_nodes": int(_G.num_vertices()),
            })

            if float(i / start_num_edges) >= normalized_steps:
                break

        except Exception as e:
            print(e)
            break

    return {
        "stadt_name": stadt_name,
        "strategy": strategy,
        "avoid_multiple_components": avoid_multiple_components,

        "normalized_steps": normalized_steps,
        "real_normalized_steps": float(i / start_num_edges),
        "real_real_steps": i,
        "results": step_results,
        **{k: v for k, v in stadt.items() if k != "geojson"}
    } 

# staedte = [
#     "Frauenstein, Hessen, Deutschland",
#     #"Wiesbaden, Hessen, Deutschland",
# ]

import json

staedte = json.load(open("result.json", "r"))

# sort by area descending
staedte.sort(key=lambda x: x["flaeche"], reverse=True)

# only retain 100 largest cities
staedte = staedte[:100]

# reverse
staedte = staedte[::-1]

to_analyze = []

for stadt in staedte:
    for strategy in [
        "random",
        "betweenness",
        "betweenness_with_recomputation",
        "betweenness_tt",
        "betweenness_with_recomputation_tt"
    ]:
        to_analyze.append({
            "stadt": stadt,
            "strategy": strategy,
            "normalized_steps": 0.015,
            "avoid_multiple_components": True
        })

        to_analyze.append({
            "stadt": stadt,
            "strategy": strategy,
            "normalized_steps": 0.015,
            "avoid_multiple_components": False
        })

memory = Memory("cachedir", verbose=0)
@memory.cache
def cached_analyze_stadt(stadt, strategy, normalized_steps, avoid_multiple_components=False):
    result = analyze_stadt(stadt, strategy, normalized_steps, avoid_multiple_components)
    return result

results = Parallel(n_jobs=-1)(delayed(cached_analyze_stadt)(d["stadt"], d["strategy"], d["normalized_steps"], d["avoid_multiple_components"]) for d in to_analyze)
#results = [analyze_stadt(d["stadt"], d["strategy"], d["normalized_steps"], d["avoid_multiple_components"]) for d in to_analyze]

import json

json.dump(results, open("robustness.json", "w"), indent=4)
