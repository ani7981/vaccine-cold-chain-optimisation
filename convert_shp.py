import shapefile
import json
import sys

def convert_shp_to_geojson(shp_path, geojson_path):
    print(f"Reading {shp_path}...")
    reader = shapefile.Reader(shp_path)
    
    buffer = []
    shapes = reader.shapes()
    for shape in shapes:
        geom = shape.__geo_interface__
        buffer.append(dict(type="Feature", geometry=geom, properties={})) 

    print(f"Writing {geojson_path}...")
    with open(geojson_path, "w") as geojson_file:
        geojson_file.write(json.dumps({"type": "FeatureCollection", "features": buffer}))
    print("Done!")

if __name__ == '__main__':
    convert_shp_to_geojson("India_State.shp", "data/india/india_boundaries.geojson")
