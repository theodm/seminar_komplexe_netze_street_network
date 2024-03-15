
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


num = 0
num2 = 0

for d in data:
    if "strategy" not in d:
        print("error: " + d["stadt_name_gvad"] + " has no strategy")
        continue

    if "results" not in d:
        print("error: " + d["stadt_name_gvad"] + " has no results")
        continue

    if "strategy" in d and d["strategy"] != "random":
        continue

    if d["avoid_multiple_components"]:
        continue

    num = num + 1

    # find first step where num_components > 1
    first_step = 0
    diff = 0
    for r in d["results"]:
        if r["num_components"] > 1:
            first_step = r["step"]
            # calc difference of nodes of lagest component before this step and after

            diff = d["results"][first_step]["largest_component_num_nodes"] - d["results"][first_step - 1]["largest_component_num_nodes"]

            break

    if first_step == 0:
        continue

    if diff >= -1:
        continue

    print(d["stadt_name_gvad"], first_step, diff)
    num2 = num2 + 1

print(f"num: {num}, num2: {num2}")