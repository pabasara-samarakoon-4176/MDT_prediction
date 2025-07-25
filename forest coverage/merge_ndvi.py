import pandas as pd
import rasterio
from rasterio.transform import rowcol
import numpy as np

# -----------------------------
# Step 1: Load MDT CSV
# -----------------------------
mdt_df = pd.read_csv("sri-lanka.csv")

# Rename if needed
lat_col = "Latitude_of_MDT"
lon_col = "Longitude_of_MDT"

# Initialize empty NDVI column
mdt_df["NDVI"] = np.nan

# -----------------------------
# Step 2: Load NDVI TIFFs
# -----------------------------
ndvi_files = ["ndvi_west.tiff", "ndvi_east.tiff"]

# Load all rasters
rasters = []
for file in ndvi_files:
    src = rasterio.open(file)
    data = src.read(1).astype(np.float32) / 65535.0  # Normalize 16-bit NDVI
    rasters.append((src, data))

# -----------------------------
# Step 3: For each MDT point, find NDVI value
# -----------------------------
def get_ndvi(lat, lon):
    for src, ndvi_data in rasters:
        try:
            row, col = rowcol(src.transform, lon, lat)
            if (0 <= row < ndvi_data.shape[0]) and (0 <= col < ndvi_data.shape[1]):
                return float(ndvi_data[row, col])
        except:
            continue
    return np.nan  # If point is outside both rasters

print("🔍 Extracting NDVI for MDT points...")
mdt_df["NDVI"] = mdt_df.apply(lambda row: get_ndvi(row[lat_col], row[lon_col]), axis=1)

# -----------------------------
# Step 4: Save Output
# -----------------------------
mdt_df.to_csv("mdt_with_ndvi.csv", index=False)
print("✅ Saved: mdt_with_ndvi.csv")
