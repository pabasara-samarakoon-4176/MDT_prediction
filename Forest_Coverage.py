# File: Forest_Coverage.py
# Description: Adds forest coverage info to MDT points using GeoHash-8 and one OSM forest shapefile

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import geohash2

# Constants
LAT_COL = "Latitude_of_MDT"
LON_COL = "Longitude_of_MDT"
GEOMETRY = "geometry"




# File paths
MDT_CSV_PATH = "Sri-Lanka.csv"
FOREST_SHP_PATH = "gis_osm_natural_free_1.shp"
OUTPUT_FILE = "Sri-Lanka_with_forest_coverage.csv"

# Load MDT CSV
mdt_data = pd.read_csv(MDT_CSV_PATH)

# Convert MDT data to GeoDataFrame with geometry and geohash
mdt_data[GEOMETRY] = mdt_data.apply(lambda row: Point(row[LON_COL], row[LAT_COL]), axis=1)
mdt_data["geohash"] = mdt_data.apply(lambda row: geohash2.encode(row[LAT_COL], row[LON_COL], precision=8), axis=1)
mdt_gdf = gpd.GeoDataFrame(mdt_data, geometry=GEOMETRY, crs="EPSG:4326")

# Load forest shapefile
forest_gdf = gpd.read_file(FOREST_SHP_PATH)
forest_gdf = forest_gdf.to_crs("EPSG:4326")

# Compute centroids of forest polygons and assign geohash
forest_gdf["centroid"] = forest_gdf.geometry.centroid
forest_gdf["geohash"] = forest_gdf["centroid"].apply(lambda pt: geohash2.encode(pt.y, pt.x, precision=8))

# Get unique geohashes that contain forest
forest_cells = forest_gdf["geohash"].dropna().unique().tolist()

# Assign forest coverage: 1 if MDT geohash is in forest_cells
mdt_gdf["forest_coverage"] = mdt_gdf["geohash"].apply(lambda gh: 1 if gh in forest_cells else 0)

# Save output without geometry
mdt_gdf.drop(columns=[GEOMETRY], inplace=True)
mdt_gdf.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Forest coverage added and saved to: {OUTPUT_FILE}")
