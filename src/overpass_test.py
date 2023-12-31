import osmnx
import overpass
from osmnx import graph_from_polygon
import osm2geojson
import geopandas as gpd

api = overpass.API()


response_xml = api.get('relation["de:regionalschluessel"="064140000000"];out geom;', build=False)


geojson = osm2geojson.xml2geojson(response_xml, filter_used_refs=False, log_level='INFO')

print(geojson)


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