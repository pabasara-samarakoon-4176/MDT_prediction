

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

building_data = gpd.read_file(PATH.BUILDING_DATA_FILE)

building_data = building_data.to_crs("EPSG:5234")

building_data["centroid"] = building_data.geometry.centroid

centroids_geo = gpd.GeoSeries(building_data["centroid"], crs="EPSG:5234").to_crs("EPSG:4326")

building_data["geohash"] = centroids_geo.apply(lambda pt: geohash2.encode(pt.y, pt.x, precision=8))

grouped = building_data.groupby("geohash").agg(
    building_count=("geohash", "count")
).reset_index()

grouped["building_density"] = grouped["building_count"] / 380

mdt_final = mdt_data.merge(grouped, on="geohash", how="left")

mdt_final["building_count"] = mdt_final["building_count"].fillna(0).astype(int)
mdt_final["building_density"] = mdt_final["building_density"].fillna(0)

mdt_final = mdt_final.drop(columns=[STR.GEOMETRY])

mdt_final.to_csv(PATH.OUTPUT_FILE, index=False)

