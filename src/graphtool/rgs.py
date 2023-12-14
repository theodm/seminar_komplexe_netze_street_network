import overpass
from gemeindeverzeichnis.gemeindeverzeichnis import load_gemeindeverzeichnis
from gemeindeverzeichnis.objects.Gemeinde import Gemeinde
from osmnx import graph_from_polygon
import osm2geojson
import geopandas as gpd




gemeindeverzeichnis = load_gemeindeverzeichnis()

gemeindeverzeichnis = {k: v for k, v in gemeindeverzeichnis.items() if isinstance(v, Gemeinde) and k.startswith("06")}

for regionalschluessel in gemeindeverzeichnis:
    geojson = geojson_from_regionalschluessel(regionalschluessel)
    print(geojson)
    break

