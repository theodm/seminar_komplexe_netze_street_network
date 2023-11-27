#%%
import math

import networkx as nx
import osmnx as ox
from joblib import Memory

memory = Memory("cachedir", verbose=0)


# @memory.cache
# def cached_graph_from_place(place, network_type):
#     return ox.graph_from_place(place, network_type=network_type)

# G = cached_graph_from_place("Barcelona, Spanien", network_type="drive")

@memory.cache
def cached_graph_from_bbox(north, south, east, west, network_type):
    return ox.graph_from_bbox(north, south, east, west, network_type=network_type)

# G = cached_graph_from_bbox(50.1943, 49.9247, 8.4011, 8.0828, network_type="drive")

# 50.2604 49.8761 9.0088 7.9308
G = cached_graph_from_bbox(50.2604, 49.8761, 9.0088, 7.9308, network_type="drive")

G = ox.speed.add_edge_speeds(G)
G = ox.speed.add_edge_travel_times(G)
print("0")

print("1")

@memory.cache
def cached_edge_betweeness(G, weight):
    return nx.edge_betweenness_centrality(G, weight=weight)
    #
    # edge_centrality = nx.closeness_centrality(nx.line_graph(G))
    # nx.set_edge_attributes(G, edge_centrality, "edge_centrality")
    #
    # ec = ox.plot.get_edge_colors_by_attr(G, "edge_centrality", cmap="inferno")
    # fig, ax = ox.plot_graph(G, edge_color=ec, edge_linewidth=2, node_size=0)

import pyintergraph
import rustworkx as rw

for e in G.edges:
    G.edges[e]["edge_label"] = str(e)

rw_graph = rw.networkx_converter(G, True)

ec = rw.edge_betweenness_centrality(rw_graph)

print(2)
edge_betweenness_centrality = {}

index_map = rw_graph.edge_index_map()
for e, val in ec.items():
    edge_betweenness_centrality[eval(index_map[e][2]["edge_label"])] = val


#edge_betweenness_centrality = cached_edge_betweeness(G, "travel_time")

def modify_v(x):
    # log(x+1)
    return math.log(100 * x + 1)

edge_betweenness_centrality = {(k[0], k[1], 0): modify_v(v) for k, v in edge_betweenness_centrality.items()}


# Es werden nicht alle Kanten von edge_betweenness_centrality zurückgegeben,
# wir suchen die fehlenden Kanten und fügen sie mit dem Wert 0 hinzu
for edge in G.edges:
    if edge not in edge_betweenness_centrality.keys():
        edge_betweenness_centrality[edge] = 0

        nx.set_edge_attributes(
            G, edge_betweenness_centrality, "edge_betweenness_centrality")

ec = ox.plot.get_edge_colors_by_attr(
    G, "edge_betweenness_centrality", cmap="inferno")

fig, ax = ox.plot_graph(
    G, edge_color=ec, edge_linewidth=2, node_size=0, dpi=50, figsize=(30, 30), filepath="test.png", save=True)

print("3")

# %%
