
# json looks like:
#   {
#     "step": 46,
#     "num_components": 2,
#     "largest_component_num_nodes": 2491,
#     "largest_component_num_edges": 3497,
#     "largest_component_avg_path_length": 31.265697394153086,
#     "largest_component_diameter": 82.0,
#     "largest_component_avg_path_length_tt": 355.9560892143439,
#     "largest_component_diameter_tt": 1243.8000000000002,
#     "num_edges": 6595,
#     "num_nodes": 4826
# },
# {
#     "step": 47,
#     "num_components": 2,
#     "largest_component_num_nodes": 2491,
#     "largest_component_num_edges": 3496,
#     "largest_component_avg_path_length": 31.286064369884194,
#     "largest_component_diameter": 82.0,
#     "largest_component_avg_path_length_tt": 357.95806251904406,
#     "largest_component_diameter_tt": 1243.8000000000002,
#     "num_edges": 6594,
#     "num_nodes": 4826
# }
#

# load from /robustness and plot x-axis: step, y-axis: largest_component_length_tt

import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

path = "./robustness/Wiesbaden_Hessen_Deutschland_rb.json"

data = json.load(open(path, "r"))

x = []
y = []

for d in data:
    x.append(d["step"])
    y.append(d["largest_component_avg_path_length_tt"])

x2 = []
y2 = []

for d in data:
    x2.append(d["step"])
    y2.append(d["largest_component_avg_path_length"])

x3 = []
y3 = []

for d in data:
    x3.append(d["step"])
    y3.append(d["largest_component_diameter_tt"])

x4 = []
y4 = []

for d in data:
    x4.append(d["step"])
    y4.append(d["largest_component_diameter"])

x5 = []
y5 = []

for d in data:
    x5.append(d["step"])
    y5.append(d["largest_component_num_edges"])



# plot to file
plt.plot(x, y)
plt.plot(x2, y2)
plt.plot(x3, y3)
plt.plot(x4, y4)
plt.plot(x5, y5)


plt.xlabel("step")
plt.savefig("robustness.png")
plt.show()


