# File: add_road_density.py
# Description: Adds road density info to MDT points using GeoHash-8 aggregation.

import os
import sys
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import geohash2

# Add project root to import config modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Import constants and file paths
import string_constants as STR
import file_paths as PATH

# Load MDT CSV data
mdt_data = pd.read_csv(PATH.MDT_DATA_FILE)

# Assign geometry and GeoHash-8 to each MDT point
mdt_data[STR.GEOMETRY] = mdt_data.apply(lambda row: Point(row[STR.LON_COL], row[STR.LAT_COL]), axis=1)
mdt_data["geohash"] = mdt_data.apply(lambda row: geohash2.encode(row[STR.LAT_COL], row[STR.LON_COL], precision=8), axis=1)

# Convert MDT data to GeoDataFrame
mdt_gdf = gpd.GeoDataFrame(mdt_data, geometry=STR.GEOMETRY, crs="EPSG:4326")

# Load road shapefile
road_data = gpd.read_file(PATH.ROAD_DATA_FILE)

# Reproject to metric CRS for length calculations (Sri Lanka UTM Zone)
road_data = road_data.to_crs("EPSG:5234")

# Calculate road lengths in meters
road_data["length_m"] = road_data.geometry.length

# Compute centroids of road segments
road_data["centroid"] = road_data.geometry.centroid

# Convert centroids to GeoSeries in geographic CRS for geohashing
centroids_geo = gpd.GeoSeries(road_data["centroid"], crs="EPSG:5234").to_crs("EPSG:4326")

# Assign GeoHash-8 based on centroid location
road_data["geohash"] = centroids_geo.apply(lambda pt: geohash2.encode(pt.y, pt.x, precision=8))

# Group by GeoHash and sum lengths
grouped = road_data.groupby("geohash").agg(
    total_road_length=("length_m", "sum")
).reset_index()

# Normalize road length per 380 m² GeoHash cell → meters per m²
grouped["road_density"] = grouped["total_road_length"] / 380

# Merge road density back to MDT
mdt_final = mdt_data.merge(grouped, on="geohash", how="left")

# Fill missing values for cells with no roads
mdt_final["total_road_length"] = mdt_final["total_road_length"].fillna(0)
mdt_final["road_density"] = mdt_final["road_density"].fillna(0)

# Drop geometry before saving
mdt_final = mdt_final.drop(columns=[STR.GEOMETRY])

# Save to output file
mdt_final.to_csv(PATH.OUTPUT_FILE, index=False)

print(f"✅ Road density (GeoHash-8) added to MDT data at: {PATH.OUTPUT_FILE}")
