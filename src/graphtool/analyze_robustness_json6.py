
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

# "stadt_name_gvad": "Essen, Stadt",
# "osm_id": 62713,
# "osm_type": "relation",
# "stadt_name_osm": "Essen",
# "stadt_name:de_osm": null,
# "stadt_description_osm": null,
# "stadt_license_plate_code_osm": "E",
# "stadt_population_osm": "569884",
# "admin_level": "6",
# "bevolkerung": 584580,
# "flaeche": 2103.4,
# "bevoelkerungsdichte": 277.92146049253586,
# "regionalschluessel": "051130000000"
# load from ./robustness.json and plot x-axis: step, y-axis: largest_component_avg_path_length_tt for each strategy

import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

path = "./robustness.json"

data = json.load(open(path, "r"))

# filter all data where bevolkerung > 629047

data = [d for d in data if d and d["bevolkerung"] > 629047]

staedte = {

}


for d in data:
    if not d:
        continue

    if "strategy" not in d:
        continue

    if "results" not in d:
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

    # if first_step == 0:
    #     num_no_break[d["strategy"]] = num_no_break[d["strategy"]] + 1
    #     continue

    if d["stadt_name_gvad"] not in staedte:
        staedte[d["stadt_name_gvad"]] = {
        }

    if first_step > 0:
        largest_smallest_component = d["results"][0]["num_nodes"] - d["results"][first_step]["largest_component_num_nodes"]
    else:
        largest_smallest_component = None
    staedte[d["stadt_name_gvad"]][d["strategy"]] = {
        "name": d["stadt_name_gvad"],
        "strategy": d["strategy"],
        "num_nodes": d["results"][0]["num_nodes"],
        "num_edges": d["results"][0]["num_edges"],
        "steps_to_first_break": first_step if first_step > 0 else None,
        "size_of_resulting_smaller_component": largest_smallest_component if first_step > 0 else None,
        "size_of_resulting_smaller_component_percent": ((largest_smallest_component) / d["results"][0]["num_nodes"]) if first_step > 0 else None,
        "avg_path_length_begin": d["results"][0]["largest_component_avg_path_length"],
        "avg_path_length_end": d["results"][first_step-1]["largest_component_avg_path_length"] if rr else d["results"][len(d["results"]) - 1]["largest_component_avg_path_length"],
        "avg_path_length_tt_begin": d["results"][0]["largest_component_avg_path_length_tt"],
        "avg_path_length_tt_end": d["results"][first_step-1]["largest_component_avg_path_length_tt"] if rr else d["results"][len(d["results"]) - 1]["largest_component_avg_path_length_tt"],

    }



# Relevante Spalten
# Strategy
# Name der Stadt
# Anzahl Knoten
# Anzahl Kanten
# Anzahl der Schritte bis zum ersten Break
# Größe der resultierenden kleineren Komponente
# Größe der resultierenden kleineren Komponente in Prozent zur Anzahl Knoten

# create pandas dataframe
import pandas as pd

df = pd.DataFrame(columns=["name", "strategy", "num_nodes", "num_edges", "steps_to_first_break", "size_of_resulting_smaller_component", "size_of_resulting_smaller_component_percent"])

# add data
for stadt in staedte:
    for strategy in staedte[stadt]:
        df = pd.concat([df, pd.DataFrame([staedte[stadt][strategy]])])

# print to html
df.to_html("staedte.html")
