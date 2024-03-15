
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

data = [d for d in data if d and d["stadt_name_gvad"] == "Frankfurt am Main, Stadt"]
# filter elements with avoid_multiple_components
data = [d for d in data if not d["avoid_multiple_components"]]

strategies = [
    "random",
    "betweenness_with_recomputation",
    "betweenness_with_recomputation_tt",
    "betweenness",
    "betweenness_tt"
]

# plot step to largest_component_avg_path_length

for e in data:
    steps = [r["step"] for r in e["results"]]
    largest_component_avg_path_length = [r["largest_component_avg_path_length"] for r in e["results"]]

    plt.plot(steps, largest_component_avg_path_length, label=e["strategy"])

plt.xlabel("step")
plt.ylabel("largest_component_avg_path_length")
plt.legend()
plt.show()