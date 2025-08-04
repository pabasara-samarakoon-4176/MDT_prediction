
import os
import sys
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import geohash2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

import string_constants as STR
import file_paths as PATH

mdt_data = pd.read_csv(PATH.MDT_DATA_FILE)

mdt_data[STR.GEOMETRY] = mdt_data.apply(lambda row: Point(row[STR.LON_COL], row[STR.LAT_COL]), axis=1)
mdt_data["geohash"] = mdt_data.apply(lambda row: geohash2.encode(row[STR.LAT_COL], row[STR.LON_COL], precision=8), axis=1)

mdt_gdf = gpd.GeoDataFrame(mdt_data, geometry=STR.GEOMETRY, crs="EPSG:4326")

road_data = gpd.read_file(PATH.ROAD_DATA_FILE)

road_data = road_data.to_crs("EPSG:5234")

road_data["length_m"] = road_data.geometry.length

road_data["centroid"] = road_data.geometry.centroid

centroids_geo = gpd.GeoSeries(road_data["centroid"], crs="EPSG:5234").to_crs("EPSG:4326")

road_data["geohash"] = centroids_geo.apply(lambda pt: geohash2.encode(pt.y, pt.x, precision=8))

grouped = road_data.groupby("geohash").agg(
    total_road_length=("length_m", "sum")
).reset_index()

grouped["road_density"] = grouped["total_road_length"] / 380

mdt_final = mdt_data.merge(grouped, on="geohash", how="left")

mdt_final["total_road_length"] = mdt_final["total_road_length"].fillna(0)
mdt_final["road_density"] = mdt_final["road_density"].fillna(0)


mdt_final = mdt_final.drop(columns=[STR.GEOMETRY])

mdt_final.to_csv(PATH.OUTPUT_FILE, index=False)

