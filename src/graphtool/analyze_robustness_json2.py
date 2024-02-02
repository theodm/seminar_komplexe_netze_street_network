
# json looks like:
# [
#     {
#         "stadt_name": "Simmerath",
#         "strategy": "random",
#         "normalized_steps": 0.02,
#         "real_normalized_steps": 0.020127118644067795,
#         "real_real_steps": 19,
#         "results": [
#             {
#                 "step": 0,
#                 "normalized_step": 0,
#                 "num_components": 1,
#                 "largest_component_num_nodes": 735,
#                 "largest_component_num_edges": 944,
#                 "largest_component_avg_path_length": 21.39575154312406,
#                 "largest_component_diameter": 52.0,
#                 "largest_component_avg_path_length_tt": 479.57910285640105,
#                 "largest_component_diameter_tt": 1465.3000000000002,
#                 "normalized_largest_component_avg_path_length": 1.0,
#                 "normalized_largest_component_diameter": 1.0,
#                 "normalized_largest_component_avg_path_length_tt": 1.0,
#                 "normalized_largest_component_diameter_tt": 1.0,
#                 "num_edges": 944,
#                 "num_nodes": 735
#             },

# load from ./robustness.json and plot x-axis: step, y-axis: largest_component_avg_path_length_tt for each strategy

import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

path = "./robustness.json"

data = json.load(open(path, "r"))

name = []

for d in data:
    if not d:
        continue


    if "strategy" not in d:
        continue

    if "results" not in d:
        continue

    # if not d["stadt_name_gvad"] or not "Hagen" in d["stadt_name_gvad"]:
    #     continue

    if "bevolkerung" in d and d["bevolkerung"] < 600000:
        continue

    if "strategy" in d and d["strategy"] != "betweenness_with_recomputation_tt":
        continue

    if "stadt_name_gvad" in d and d["stadt_name_gvad"] in name:
        continue

    if "avoid_multiple_components" in d and not d["avoid_multiple_components"]:
        continue

    x = []
    y = []
    name.append(d["stadt_name_gvad"])

    for r in d["results"]:
        x.append(r["step"])
        y.append(r["normalized_largest_component_avg_path_length_tt"])

    plt.plot(x, y)

plt.legend(name)
plt.show()

# plot to file

plt.savefig("robustness.png")