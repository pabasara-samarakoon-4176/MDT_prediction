

import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.sample import sample_gen
from shapely.geometry import Point

MDT_FILE = "data/SriLanka.csv"   
ELEVATION_RASTER = "data/elevation.tif"
SLOPE_RASTER = "data/slope.tif"
OUTPUT_FILE = "data/mdt_with_terrain.csv"

LAT_COL = "Latitude_of_MDT"
LON_COL = "Longitude_of_MDT"

df = pd.read_csv(MDT_FILE)

df["geometry"] = df.apply(lambda row: Point(row[LON_COL], row[LAT_COL]), axis=1)
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

def extract_raster_values(gdf, raster_path, value_column):
    with rasterio.open(raster_path) as src:
        
        gdf_proj = gdf.to_crs(src.crs)
        coords = [(geom.x, geom.y) for geom in gdf_proj.geometry]
        values = [val[0] if val[0] is not None else None for val in src.sample(coords)]
        gdf[value_column] = values
    return gdf


gdf = extract_raster_values(gdf, ELEVATION_RASTER, "elevation")
gdf = extract_raster_values(gdf, SLOPE_RASTER, "slope")

def classify_terrain(row):
    if row["elevation"] < 50 and row["slope"] < 5:
        return "Easy"
    elif row["elevation"] < 200 and row["slope"] < 15:
        return "Moderate"
    else:
        return "Hard"

gdf["terrain_index"] = gdf.apply(classify_terrain, axis=1)


gdf.drop(columns=["geometry"]).to_csv(OUTPUT_FILE, index=False)
