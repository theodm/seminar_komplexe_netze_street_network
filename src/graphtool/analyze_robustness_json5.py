
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

num_no_break = {
    "random": 0,
    "betweenness_with_recomputation": 0,
    "betweenness_with_recomputation_tt": 0,
    "betweenness": 0,
    "betweenness_tt": 0,
}

steps_to_first_break = {
    "random": [],
    "betweenness_with_recomputation": [],
    "betweenness_with_recomputation_tt": [],
    "betweenness": [],
    "betweenness_tt": [],
}

size_of_resulting_smaller_component = {
    "random": [],
    "betweenness_with_recomputation": [],
    "betweenness_with_recomputation_tt": [],
    "betweenness": [],
    "betweenness_tt": [],
}

num = 0



for d in data:
    if not d:
        continue

    num = num + 1

    if "strategy" not in d:
        continue

    if "results" not in d:
        continue

    if "stadt_name_gvad" in d and d["stadt_name_gvad"] in name:
        continue

    if "avoid_multiple_components" in d and d["avoid_multiple_components"]:
        continue

    # find first step where num_components > 1
    first_step = 0
    normalized_step = 0
    rr = None
    for r in d["results"]:
        if r["num_components"] > 1:
            first_step = r["step"]
            normalized_step = r["normalized_step"]
            rr = r
            break

    if first_step == 0:
        num_no_break[d["strategy"]] = num_no_break[d["strategy"]] + 1
        continue

    size_of_resulting_smaller_component[d["strategy"]].append(
        (rr["largest_component_num_nodes"] - d["results"][first_step - 1]["largest_component_num_nodes"]) / d["results"][0]["largest_component_num_nodes"]
    )

    steps_to_first_break[d["strategy"]].append(rr["normalized_step"])

# print formatted
for k, v in steps_to_first_break.items():
    print(k, sum(v) / len(v))

for k, v in num_no_break.items():
    print(k, v)

for k, v in size_of_resulting_smaller_component.items():
    print(k, sum(v) / len(v))
