
import math

import networkx as nx
import osmnx
import osmnx as ox
from joblib import Memory

memory = Memory("cachedir", verbose=0)

from timeit import default_timer as timer



@memory.cache
def cached_graph_from_place(place, network_type):
    return ox.graph_from_place(place, network_type=network_type)

def mdig_to_graph(G: nx.MultiDiGraph, weight="length"):
    """
    Konvertiert einen MultiDiGraph von osmnx in einen normalen Graph aus NetworkX,
    also weder mit parallelen Kanten noch mit Kantenrichtungen.

    Hintergrund: osmnx bietet die folgenden Konvertierungen an:
     - MultiDiGraph -> DiGraph
     - MultiDiGraph -> MultiGraph
    für weitere Experimente brauchen wir aber auch die Konvertierung
     - MultiDiGprah -> Graph
    """

    # Zuerst entfernen wir die Kantenrichtungen, das lassen wir von osmnx
    # machen. (MultiDiGraph -> MultiGraph)
    G = osmnx.utils_graph.get_undirected(G)

    # Der folgende Code kommt aus der Methode
    # osmnx.utils_graph.get_digraph

    to_remove = []

    # identify all the parallel edges in the MultiGraph
    parallels = ((u, v) for u, v in G.edges(keys=False) if len(G.get_edge_data(u, v)) > 1)

    # among all sets of parallel edges, remove all except the one with the
    # minimum "weight" attribute value
    for u, v in set(parallels):
        k_min, _ = min(G.get_edge_data(u, v).items(), key=lambda x: x[1][weight])
        to_remove.extend((u, v, k) for k in G[u][v] if k != k_min)

    G.remove_edges_from(to_remove)

    return nx.Graph(G)




G = cached_graph_from_place("Wiesbaden, Germany", network_type="drive")

print("1")
G = mdig_to_graph(G)

print("2")
# draw with osmnx
fig, ax = ox.plot_graph(nx.MultiDiGraph(G))

print("3")

# Test small worldiness of G
print("sigma: " + str(nx.algorithms.smallworld.sigma(G, niter=10, nrand=1)))
print("omega: " + str(nx.algorithms.smallworld.omega(G, niter=10, nrand=1)))


