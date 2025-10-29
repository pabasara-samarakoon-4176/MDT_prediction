import os
import sys
import rasterio
import pandas as pd
import geohash2
import geopandas as gpd
import numpy as np
from shapely.geometry import Point  

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

import string_constants as STR  # Make sure you're importing STR
import file_paths as PATH

# Load your main dataset first
mdt_data = pd.read_csv(PATH.INPUT_FILE)

# Create geometry and geohash columns (same as in building density code)
mdt_data[STR.GEOMETRY] = mdt_data.apply(lambda row: Point(row[STR.LON_COL], row[STR.LAT_COL]), axis=1)
mdt_data["geohash"] = mdt_data.apply(lambda row: geohash2.encode(row[STR.LAT_COL], row[STR.LON_COL], precision=8), axis=1)
mdt_gdf = gpd.GeoDataFrame(mdt_data, geometry=STR.GEOMETRY, crs="EPSG:4326")

worldpop_raster_path = PATH.WORLDPOP_RASTER_FILE   

with rasterio.open(worldpop_raster_path) as src:
    population_raster = src.read(1)  
    transform = src.transform

rows, cols = population_raster.shape

data = []
for row in range(rows):
    for col in range(cols):
        pop_value = population_raster[row, col]
        if np.isnan(pop_value) or pop_value <= 0:
            continue  # skip empty/no data cells
        lon, lat = rasterio.transform.xy(transform, row, col)
        geohash = geohash2.encode(lat, lon, precision=8)
        data.append((geohash, pop_value))

pop_df = pd.DataFrame(data, columns=["geohash", "population"])

grouped_pop = pop_df.groupby("geohash").agg(
    total_population=("population", "sum")
).reset_index()

grouped_pop["population_density"] = grouped_pop["total_population"] / 380

# FIX: Merge with grouped_pop instead of grouped (which doesn't exist)
mdt_final = mdt_data.merge(grouped_pop, on="geohash", how="left")

mdt_final["total_population"] = mdt_final["total_population"].fillna(0).astype(int)
mdt_final["population_density"] = mdt_final["population_density"].fillna(0)

# Optional: Drop the geometry column if you don't need it in the final output
# mdt_final = mdt_final.drop(columns=[STR.GEOMETRY])
mdt_final = mdt_final.drop(columns=[STR.GEOMETRY])
mdt_final.to_csv(PATH.OUTPUT_FILE, index=False)

print("✅ Population density successfully added and saved to:", PATH.OUTPUT_FILE)