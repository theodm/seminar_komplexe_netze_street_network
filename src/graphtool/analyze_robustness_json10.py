
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

# filter strategy

x = []
y = []
color = []
n = []


for d in data:
    if "strategy" in d and d["strategy"] != "betweenness_with_recomputation_tt":
        continue

    if "avoid_multiple_components" in d and d["avoid_multiple_components"]:
        continue

    # find first step where num_components > 1
    first_step = 0
    normalized_step = 0
    rr = None
    for i in range(len(d["results"])):
        r = d["results"][i]
        if r["num_components"] > 1:
            first_step = r["step"]
            normalized_step = r["normalized_step"]
            rr = r
            break



    if first_step > 0:
        largest_smallest_component = d["results"][0]["num_nodes"] - d["results"][first_step][
            "largest_component_num_nodes"]
    else:
        largest_smallest_component = None
        continue

    ss = ((largest_smallest_component) / d["results"][0]["num_nodes"]) * 100 if first_step > 0 else None

    round_ss = round(ss, 2) if ss else None

    x += [d["results"][0]["num_nodes"]]
    y += [normalized_step * 100]
    n += [{
        "bevolkerung": d["bevolkerung"],
        "name": d["stadt_name_gvad"] + " (t: " + str(round(d["results"][first_step-1]["normalized_largest_component_avg_path_length_tt"] * 100 - 100, 2)) + " %)"
    }]




fig, ax = plt.subplots()

# scatter plot y-axis: first_step x-axis: bevolkerung
ax.scatter(x, y)


for i, txt in enumerate(n):
    if txt["bevolkerung"] > 400000:
        ax.annotate(txt["name"], (x[i], y[i]), fontsize=12)

# label x-axis: Anzahl Knoten
# label y-axis: Anzahl entfernter Kanten (in %)

plt.xlabel("Anzahl Knoten")
plt.ylabel("Anzahl entfernter Kanten (in %)")

plt.legend()
plt.show()

# plot to file

plt.savefig("robustness.png")