import math
import os
import graph_tool.all as gt

from joblib import Parallel, delayed

import osmnx as ox
import networkx as nx
import pyintergraph

from src.server.graph.mdig_to_graph import mdig_to_graph

import geopandas as gpd
from shapely.geometry import Polygon

from src.server.graph.nx_to_dual_graph import osmnx_to_dual_graph

import matplotlib.pyplot as plt
# Deutsche Hauptstädte
deutsche_staedte = [
    "Kiel, Germany",
    "Hamburg, Germany",
    "Bremen, Germany",
    "Berlin, Germany",
    "Potsdam, Germany",
    "Schwerin, Germany",
    "Hannover, Germany",
    "Düsseldorf, Germany",
    "Magdeburg, Germany",
    "Erfurt, Germany",
    "Mainz, Germany",
    "Saarbrücken, Germany",
    "Wiesbaden, Germany",
    "Frankfurt, Germany",
    "Koblenz, Germany",
    "Dresden, Germany",
    "Stuttgart, Germany",
    "München, Germany",
]


# deutsche_staedte = [
#     "Frauenstein, Wiesbaden, Germany",
#     "Flonheim, Germany",
#
#     "Norderney, Germany",
#     "Fehmarn, Germany",
#     "Füssen, Germany",
#     "Winterberg, Germany",
#     "Borkum, Germany",
#     "Rothenburg ob der Tauber, Germany",
#     "Cochem, Germany",
#     "Kühlungsborn, Germany",
#
# ]

# deutsche_staedte = [
#     "Koblenz, Germany",
#     "Wiesbaden, Germany",
# ]

# deutsche_staedte = [
#     "Tegernsee, Germany",
#     "Berchtesgaden, Germany",
#     "Kühlungsborn, Germany",
#     "Heiligenhafen, Germany",
#     "Meersburg, Germany",
#     "Kusel, Germany",
#     "Bad Schandau, Germany",
#     "Oberwiesenthal, Germany",
#     "Königsberg, Germany",
#     "Kappeln, Germany",
#     "Braunlage, Germany",
#     "Oberhof, Germany",
#     "Bad Ems, Germany",
#     "Lichtenberg, Bayern, Germany",
#     "Rehau, Germany",
#     "Sassnitz, Germany",
#     "Miltenberg, Germany",
#     "Plön, Schleswig-Holstein, Germany",
#     "Volkach, Germany",
# ]


def graph_from_geocode(place):
    return ox.graph_from_place(place, network_type="drive")


def convert_graph_to_graphtool(G):
    for e in G.edges:
        G.edges[e]["_edge_label"] = str(e)

    for n in G.nodes:
        G.nodes[n]["_node_label"] = str(n)

    graph_tool_graph = pyintergraph.nx2gt(G, "node_label")
    return graph_tool_graph


def get_graph_bbox(G):
    nodes = G.nodes
    max_north = min_south = nodes[list(nodes)[0]]["y"]
    max_east = min_west = nodes[list(nodes)[0]]["x"]

    for n in nodes:
        n_data = nodes[n]
        y = n_data["y"]
        x = n_data["x"]

        if y > max_north:
            max_north = y
        elif y < min_south:
            min_south = y
        if x > max_east:
            max_east = x
        elif x < min_west:
            min_west = x

    return max_north, min_south, max_east, min_west


def get_bbox_area(bbox):
    # with geopandas

    north, south, east, west = bbox

    polygon = Polygon(
        [
            (west, north),
            (east, north),
            (east, south),
            (west, south),
        ]
    )

    gdf = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:4326")
    gdf = gdf.to_crs("EPSG:3857")

    return gdf.area[0] / 10 ** 6

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



def save_edge_plot_with_attribute(G, attribute_name, filepath):
    MDG = nx.MultiDiGraph(G)

    ec = ox.plot.get_edge_colors_by_attr(
        MDG, attribute_name, cmap="inferno")

    fig, ax = ox.plot_graph(
        MDG, edge_color=ec, edge_linewidth=2, node_size=0, dpi=50, figsize=(30, 30), filepath=filepath, save=True)

def save_node_plot_with_attribute(G, attribute_name, filepath):
    MDG = nx.MultiDiGraph(G)

    nc = ox.plot.get_node_colors_by_attr(
        MDG, attribute_name, cmap="inferno")

    fig, ax = ox.plot_graph(
        MDG, node_color=nc, node_size=35, edge_linewidth=1,dpi=50, figsize=(30, 30), filepath=filepath, save=True)


def closeness_centrality(G, _G, weight=None):
    vb = gt.closeness(_G, weight=_G.edge_properties[weight] if weight else None)

    node_closeness_centrality = {}

    for v in _G.vertices():
        node = eval(_G.vertex_properties["_node_label"][v])

        node_closeness_centrality[node] = vb[v]

    node_closeness_centrality = {k: v for k, v in node_closeness_centrality.items()}

    for node in G.nodes:
        if node not in node_closeness_centrality.keys():
            node_closeness_centrality[node] = 0

    nx.set_node_attributes(
        G, node_closeness_centrality, "node_closeness_centrality")

def save_degree_histogram_plot(G, filepath):
    plt.clf()
    degrees = [d for n, d in G.degree()]
    plt.hist(degrees, bins=range(min(degrees), max(degrees) + 1, 1))

    # high quality
    plt.savefig(filepath, dpi=300)

def calculate_graph_path_metrics(_G, weight=None):
    shortest_distance_matrix = gt.shortest_distance(_G, weights=_G.edge_properties[weight] if weight else None)

    avg_path_length = sum([sum(i) for i in shortest_distance_matrix]) / (_G.num_vertices() ** 2 - _G.num_vertices())
    diameter = max([max(i) for i in shortest_distance_matrix])

    return avg_path_length, diameter


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



OUTPUT_DIRECTORY = "./data/graphs"

# Create output directory if not exists
if not os.path.exists(OUTPUT_DIRECTORY):
    os.makedirs(OUTPUT_DIRECTORY)

infos = []


def analyze_stadt(stadt):
    print(f"Analysiere nun: {stadt}")

    stadt_file_name = (stadt
                       .replace(", ", "_")
                       .replace(" ", "_"))

    MDG = graph_from_geocode(stadt)

    # add travel_time attribute to edges
    ox.add_edge_speeds(MDG)
    ox.add_edge_travel_times(MDG)

    G = mdig_to_graph(MDG)

    # remove self loops
    G.remove_edges_from(nx.selfloop_edges(G))

    # Bounding Box of graph
    bbox = get_graph_bbox(G)
    # Area of bounding box
    bbox_area = get_bbox_area(bbox)

    # Get simple data from graph
    # number of nodes
    num_nodes = G.number_of_nodes()
    # number of edges
    num_edges = G.number_of_edges()

    degrees = G.degree()
    degrees_values = dict(degrees).values()
    # avg degree
    avg_degree = sum(degrees_values) / num_nodes
    # min degree
    min_degree = min(degrees_values)
    # max degree
    max_degree = max(degrees_values)

    save_degree_histogram_plot(G, filepath=f"{OUTPUT_DIRECTORY}/{stadt_file_name}_degree_histogram.png")

    # avg clustering coefficient
    global_cluster_coefficient_avg = nx.average_clustering(G)

    _G = convert_graph_to_graphtool(G)

    avg_path_length, diameter  = calculate_graph_path_metrics(_G)
    avg_path_length_tt, diameter_tt  = calculate_graph_path_metrics(_G, weight="travel_time")
    avg_path_length_lgt, diameter_lgt  = calculate_graph_path_metrics(_G, weight="length")

    # Dualer Graph
    DG = osmnx_to_dual_graph(G)

    # nodes of dual graph
    num_nodes_dual = DG.number_of_nodes()
    # edges of dual graph
    num_edges_dual = DG.number_of_edges()

    # degrees of dual graph
    degrees_dual = DG.degree()
    degrees_values_dual = dict(degrees_dual).values()
    # avg degree of dual graph
    avg_degree_dual = sum(degrees_values_dual) / num_nodes_dual
    # min degree of dual graph
    min_degree_dual = min(degrees_values_dual)
    # max degree of dual graph
    max_degree_dual = max(degrees_values_dual)

    save_degree_histogram_plot(DG, filepath=f"{OUTPUT_DIRECTORY}/{stadt_file_name}_degree_histogram_dual.png")

    # avg clustering coefficient of dual graph
    global_cluster_coefficient_avg_dual = nx.average_clustering(DG)

    _DG = convert_graph_to_graphtool(DG)

    avg_path_length_dual, diameter_dual = calculate_graph_path_metrics(_DG)

    # betweenness centrality in primal graph
    relative_betweenness_centrality(G, _G)
    save_edge_plot_with_attribute(G, "edge_betweenness_centrality", filepath=f"{OUTPUT_DIRECTORY}/{stadt_file_name}_be.png")

    relative_betweenness_centrality(G, _G, weight="travel_time")
    save_edge_plot_with_attribute(G, "edge_betweenness_centrality", filepath=f"{OUTPUT_DIRECTORY}/{stadt_file_name}_be_tt.png")

    relative_betweenness_centrality(G, _G, weight="length")
    save_edge_plot_with_attribute(G, "edge_betweenness_centrality", filepath=f"{OUTPUT_DIRECTORY}/{stadt_file_name}_be_lgt.png")

    # betweenness centrality in dual graph
    relative_betweenness_centrality(DG, _DG)
    map_dual_node_attribute_to_primal_edges_attribute(G, DG, "node_betweenness_centrality")
    save_edge_plot_with_attribute(G, "node_betweenness_centrality", filepath=f"{OUTPUT_DIRECTORY}/{stadt_file_name}_dbe.png")

    # closeness centrality in primal graph
    closeness_centrality(G, _G)
    save_node_plot_with_attribute(G, "node_closeness_centrality", filepath=f"{OUTPUT_DIRECTORY}/{stadt_file_name}_cn.png")

    closeness_centrality(G, _G, weight="travel_time")
    save_node_plot_with_attribute(G, "node_closeness_centrality", filepath=f"{OUTPUT_DIRECTORY}/{stadt_file_name}_cn_tt.png")

    closeness_centrality(G, _G, weight="length")
    save_node_plot_with_attribute(G, "node_closeness_centrality", filepath=f"{OUTPUT_DIRECTORY}/{stadt_file_name}_cn_lgt.png")

    # closeness centrality in dual graph
    closeness_centrality(DG, _DG)
    map_dual_node_attribute_to_primal_edges_attribute(G, DG, "node_closeness_centrality")
    save_edge_plot_with_attribute(G, "node_closeness_centrality", filepath=f"{OUTPUT_DIRECTORY}/{stadt_file_name}_dcn.png")

    # print(f"===")
    # print(f"=== {stadt}")
    # print(f"===")
    # print(f"")
    # print(f"Bounding Box: {bbox}")
    # print(f"Fläche: {bbox_area} (einfache Schätzung)")
    # print(f"")
    # print("Informationen zum primalen Graphen")
    # print(f"")
    # print(f"Anzahl Knoten: {num_nodes}")
    # print(f"Anzahl Kanten: {num_edges}")
    # print(f"")
    # print(f"Durchschnittlicher Knotengrad: {avg_degree}")
    # print(f"Minimaler Knotengrad: {min_degree}")
    # print(f"Maximaler Knotengrad: {max_degree}")
    # print(f"")
    # print(f"Durchschnittlicher Clustering-Koeffizient: {global_cluster_coefficient_avg}")
    # print(f"")
    # print(f"Duchschnittliche Pfadlänge: {avg_path_length}")
    # print(f"Durchmesser: {diameter}")
    # print(f"Pseudodurchmesser: {pseudo_diameter}")
    # print(f"")
    # print("Informationen zum dualen Graphen")
    # print(f"")
    # print(f"Anzahl Knoten: {num_nodes_dual}")
    # print(f"Anzahl Kanten: {num_edges_dual}")
    # print(f"")
    # print(f"Durchschnittlicher Knotengrad: {avg_degree_dual}")
    # print(f"Minimaler Knotengrad: {min_degree_dual}")
    # print(f"Maximaler Knotengrad: {max_degree_dual}")
    # print(f"")
    # print(f"Durchschnittlicher Clustering-Koeffizient: {global_cluster_coefficient_avg_dual}")
    # print(f"")
    # print(f"Duchschnittliche Pfadlänge: {avg_path_length_dual}")
    # print(f"Durchmesser: {diameter_dual}")
    # print(f"Pseudodurchmesser: {pseudo_diameter_dual}")
    # print(f"")

    # Save information
    info = {
        "name": stadt,
        "bounding_box": bbox,
        "bounding_box_area": bbox_area,
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "avg_degree": avg_degree,
        "min_degree": min_degree,
        "max_degree": max_degree,
        "avg_cluster_coeff": global_cluster_coefficient_avg,
        "avg_path_length": avg_path_length,
        "diameter": diameter,
        "avg_path_length_tt": avg_path_length_tt,
        "diameter_tt": diameter_tt,
        "avg_path_length_lgt": avg_path_length_lgt,
        "diameter_lgt": diameter_lgt,
        "num_nodes_dual": num_nodes_dual,
        "num_edges_dual": num_edges_dual,
        "avg_degree_dual": avg_degree_dual,
        "min_degree_dual": min_degree_dual,
        "max_degree_dual": max_degree_dual,
        "avg_cluster_coeff_dual": global_cluster_coefficient_avg_dual,
        "avg_path_length_dual": avg_path_length_dual,
        "diameter_dual": diameter_dual,
    }

    return info


infos = Parallel(n_jobs=-1)(delayed(analyze_stadt)(stadt) for stadt in deutsche_staedte)
#infos = [analyze_stadt(stadt) for stadt in deutsche_staedte]

# Output as Table with pandas as html to file
import pandas as pd

df = pd.DataFrame(infos)

# sort by bounding box area
df = df.sort_values(by=["bounding_box_area"], ascending=True)


# highlight min and max in each column
def highlight_min(s):
    is_min = s == s.min()
    return ['background-color: yellow' if v else '' for v in is_min]


def highlight_max(s):
    is_max = s == s.max()
    return ['background-color: red' if v else '' for v in is_max]


html = df.style.apply(highlight_min).apply(highlight_max).to_html()

with open(f"{OUTPUT_DIRECTORY}/graph_infos.html", "w") as f:
    f.write(html)

import webbrowser

webbrowser.open(f"{OUTPUT_DIRECTORY}/graph_infos.html")
