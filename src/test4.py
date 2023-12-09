from osmnx import geocoder

gdf_place = geocoder.geocode_to_gdf(
    "Wiesbaden, Germany"
)

polygon = gdf_place["geometry"].unary_union

print(polygon)
