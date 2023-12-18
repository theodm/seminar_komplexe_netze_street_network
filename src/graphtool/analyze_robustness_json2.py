
# json looks like:
# [
#     {
#         "stadt_name": "Koblenz, Deutschland",
#         "strategy": "random",
#         "steps": 100,
#         "results": [
#             {
#                 "step": 1,
#                 "num_components": 2,
#                 "largest_component_num_nodes": 2825,
#                 "largest_component_num_edges": 3683,
#                 "largest_component_avg_path_length": 32.091832585424555,
#                 "largest_component_diameter": 90.0,
#                 "largest_component_avg_path_length_tt": 405.11870094512295,
#                 "largest_component_diameter_tt": 1195.7000000000003,
#                 "num_edges": 3684,
#                 "num_nodes": 2827
#             },

# load from ./robustness.json and plot x-axis: step, y-axis: largest_component_avg_path_length_tt for each strategy

import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

path = "./robustness.json"

data = json.load(open(path, "r"))

for d in data:
    print(d["strategy"])

    x = []
    y = []

    for r in d["results"]:
        x.append(r["step"])
        y.append(r["normalized_largest_component_avg_path_length_tt"] if "normalized_largest_component_avg_path_length_tt" in r else 1)

    plt.plot(x, y)

plt.legend([d["strategy"] for d in data])
plt.show()

# plot to file

plt.savefig("robustness.png")