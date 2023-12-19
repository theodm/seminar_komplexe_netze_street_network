
import math
import os
import graph_tool.all as gt

import osm2geojson
import overpass

from joblib import Parallel, delayed

import osmnx as ox
import networkx as nx
import pyintergraph
from osmnx import graph_from_polygon

from src.server.graph.mdig_to_graph import mdig_to_graph

import geopandas as gpd
from shapely.geometry import Polygon

from src.server.graph.nx_to_dual_graph import osmnx_to_dual_graph

import matplotlib.pyplot as plt

def graph_from_geojson(geojson):
    gdf = gpd.GeoDataFrame.from_features(geojson)

    print(f"gdf: {gdf}")

    # filter out all Polygon and MultiPolygon
    gdf = gdf[gdf["geometry"].type.isin(["Polygon", "MultiPolygon"])]

    polygon = gdf["geometry"].unary_union

    # create graph using this polygon(s) geometry
    G = graph_from_polygon(
        polygon,
        network_type="drive"
    )

    return G


errored_staedte = []
def analyze_stadt(stadt):
    try:
        stadt_name = stadt["stadt_name_gvad"]

        print("Analyzing", stadt_name)
        #print(stadt)

        MDG = graph_from_geojson(stadt["geojson"])

        #print number of nodes
        print("Number of nodes:", len(MDG.nodes))
    except Exception as e:
        print("Error while loading MDG", e)
        print(e)

        # print stacktrace
        import traceback
        traceback.print_exc()


        errored_staedte.append({
            "stadt": stadt,
            "error": str(e)
        })
        return
    
import json

staedte = json.load(open("src/graphtool/result.json", "r"))

# sort by area descending
staedte.sort(key=lambda x: x["bevolkerung"], reverse=True)

# filter names to contains Lübeck or Mainz
staedte = list(filter(lambda x: "Lübeck" in x["stadt_name_gvad"] or "Mainz" in x["stadt_name_gvad"], staedte))

for stadt in staedte:
    analyze_stadt(stadt)

# write to json
import json

with open("data/errored.json", "r") as f:
    json.dump(errored_staedte, f)

