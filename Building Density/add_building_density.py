# File: add_building_density.py
# Description: Adds building density info to MDT points using GeoHash-8 aggregation.

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

# Load building shapefile
building_data = gpd.read_file(PATH.BUILDING_DATA_FILE)

# Reproject to metric CRS (Sri Lanka UTM Zone)
building_data = building_data.to_crs("EPSG:5234")

# Compute accurate building centroids in projected CRS
building_data["centroid"] = building_data.geometry.centroid

# Reproject centroids back to EPSG:4326 for GeoHashing
centroids_geo = gpd.GeoSeries(building_data["centroid"], crs="EPSG:5234").to_crs("EPSG:4326")

# Assign GeoHash-8 to each building centroid
building_data["geohash"] = centroids_geo.apply(lambda pt: geohash2.encode(pt.y, pt.x, precision=8))

# Count number of buildings per GeoHash
grouped = building_data.groupby("geohash").agg(
    building_count=("geohash", "count")
).reset_index()

# Compute building density (approx 380 m² for GeoHash-8 cell)
grouped["building_density"] = grouped["building_count"] / 380

# Merge building density back to MDT data
mdt_final = mdt_data.merge(grouped, on="geohash", how="left")

# Fill missing values (for geohash cells with no buildings)
mdt_final["building_count"] = mdt_final["building_count"].fillna(0).astype(int)
mdt_final["building_density"] = mdt_final["building_density"].fillna(0)

# Drop geometry column before saving
mdt_final = mdt_final.drop(columns=[STR.GEOMETRY])

# Save to CSV
mdt_final.to_csv(PATH.OUTPUT_FILE, index=False)

print(f"✅ Building density (GeoHash-8) added to MDT data at: {PATH.OUTPUT_FILE}")
