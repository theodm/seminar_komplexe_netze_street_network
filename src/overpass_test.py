import osmnx
import overpass
from osmnx import graph_from_polygon

api = overpass.API()

response_xml = api.get('relation["de:amtlicher_gemeindeschluessel"~"06414.*"];out geom;', build=False)

import osm2geojson

geojson = osm2geojson.xml2geojson(response_xml, filter_used_refs=False, log_level='INFO')

print(geojson)

import geopandas as gpd

# create and return the GeoDataFrame
gdf = gpd.GeoDataFrame.from_features(geojson)

polygon = gdf["geometry"].unary_union

# create graph using this polygon(s) geometry
G = graph_from_polygon(
    polygon,
    network_type="drive"
)

print(G.number_of_nodes())
print(G.number_of_edges())