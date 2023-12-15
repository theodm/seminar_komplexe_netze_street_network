import osm2geojson
import overpass
from gemeindeverzeichnis.gemeindeverzeichnis import load_gemeindeverzeichnis
from gemeindeverzeichnis.objects.Gemeinde import Gemeinde

def geojson_from_regionalschluessel(regionalschluessel: str):
    api = overpass.API()

    response_xml = api.get(f'relation["de:regionalschluessel"="{regionalschluessel}"];out geom;', build=False)

    geojson = osm2geojson.xml2geojson(response_xml)

    return geojson

result = []

gemeindeverzeichnis = load_gemeindeverzeichnis()
for regionalschluessel, gemeinde in gemeindeverzeichnis.items():

    # nur Hessen
    if not regionalschluessel.startswith("06"):
        continue

    if not isinstance(gemeinde, Gemeinde):
        continue
    geojson = geojson_from_regionalschluessel(regionalschluessel)

    def access(fn):
        try:
            return fn("")
        except:
            return None

    result.append({
        "stadt_name_gvad": gemeinde.name,

        "osm_id": access(lambda _: geojson["features"][0]["properties"]["id"]),
        "osm_type": access(lambda _: geojson["features"][0]["properties"]["type"]),

        "stadt_name_osm": access(lambda _: geojson["features"][0]["properties"]["tags"]["name"]),
        "stadt_name:de_osm": access(lambda _: geojson["features"][0]["properties"]["tags"]["name:de"]),
        "stadt_description_osm": access(lambda _: geojson["features"][0]["properties"]["tags"]["description"]),
        "stadt_license_plate_code_osm": access(lambda _: geojson["features"][0]["properties"]["tags"]["license_plate_code"]),
        "stadt_population_osm": access(lambda _: geojson["features"][0]["properties"]["tags"]["population"]),

        "admin_level": access(lambda _: geojson["features"][0]["properties"]["tags"]["admin_level"]),

        "bevolkerung": gemeinde.bevoelkerung,
        "flaeche": gemeinde.flaeche_in_km2,
        "bevoelkerungsdichte": gemeinde.bevoelkerung / gemeinde.flaeche_in_km2,

        "regionalschluessel": regionalschluessel,
        "geojson": geojson,
    })

for r in result:
    print({k: v for k, v in r.items() if k != "geojson"})

import json
with open("result.json", "w") as f:
    json.dump(result, f, indent=4)

print("done")
