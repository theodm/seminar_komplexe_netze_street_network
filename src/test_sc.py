import networkx as nx
from joblib import Memory
from street_continuity.all import *


memory = Memory("cachedir", verbose=0)
@memory.cache
def cached_graph_from_place(place, network_type):
    return ox.graph_from_place(place, network_type=network_type)
# load the primal graph from osmnx
oxg = cached_graph_from_place("Wiesbaden, Germany", network_type="drive")
p_graph = from_osmnx(oxg=oxg, use_label=True)

# alternatively, you can load the graph from a csv file
# p_graph = read_csv(nodes_filename='test-nodes.csv', edges_filename='test-edges.csv', directory='data', use_label=True, has_header=False)

# maps the primal graph to the dual representation
# use_label = True: uses HICN algorithm
# use_label = False: uses ICN algorithm
d_graph = dual_mapper(primal_graph=p_graph, min_angle=170)
#
# def convert_dual_graph_to_networkx(d_graph: DualGraph):
#     d_graph.build_graph()

newg = nx.Graph()
# iterate values of node_dictionary
for _, node in d_graph.node_dictionary.items():
    newg.add_node(node.did, original_edges=node.edges, names=node.names)

for _, edge in d_graph.edge_dictionary.items():
    newg.add_edge(edge[0], edge[1])

# use greedy coloring to color the nodes
colors = nx.greedy_color(newg, strategy="largest_first")
max_color = max(colors.values())




# select nodes with degree > 50
# nodes_d = [n for n, d in newg.degree() if d > 50]
#
# for node in nodes_d:
#     print(node)
#     print(newg.nodes[node]["names"])


# # Es werden nicht alle Kanten von edge_betweenness_centrality zurückgegeben,
# # wir suchen die fehlenden Kanten und fügen sie mit dem Wert 0 hinzu
# for edge in p_graph.edges:
#

# select nodes with degree > 50
nodes_d = [n for n, d in newg.degree() if d > 15]

for e in oxg.edges:
    oxg.edges[e]["show_factor"] = 0

for n in nodes_d:
    print(n)
    print(newg.nodes[n]["names"])

    for e in newg.nodes[n]["original_edges"]:
        print(e)
        for i in range(10):
            if oxg.has_edge(e[0], e[1], i):
                edge = oxg.edges[e[0], e[1], i]
                print(edge)

                edge["show_factor"] = 1

            if oxg.has_edge(e[1], e[0], i):
                edge = oxg.edges[e[1], e[0], i]
                print(edge)

                edge["show_factor"] = 1



ec = ox.plot.get_edge_colors_by_attr(oxg, "show_factor", cmap="Paired")

fig, ax = ox.plot_graph(
    oxg, edge_color=ec, edge_linewidth=2, node_size=0, dpi=5000, figsize=(30, 30))




# you must create the data directory before running this command
#dxg = write_graphml(graph=d_graph, filename='file.graphml', directory='data')
#write_supplementary(graph=d_graph, filename='supplementary.txt', directory='data')