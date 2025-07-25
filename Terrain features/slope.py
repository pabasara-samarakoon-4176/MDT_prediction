import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

input_path = "data/elevation.tif"
output_path = "data/elevation_utm.tif"
dst_crs = "EPSG:32644"  # Example: UTM zone 44N (for Sri Lanka). Adjust if needed.

with rasterio.open(input_path) as src:
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds)
    kwargs = src.meta.copy()
    kwargs.update({
        "crs": dst_crs,
        "transform": transform,
        "width": width,
        "height": height
    })

    with rasterio.open(output_path, "w", **kwargs) as dst:
        for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.bilinear)
