# Satellite Data Acquisition Examples

Complete examples for all supported satellite data products.

Author: Peter Kongstad

## Available Products

### Optical Data (Cloud Filtering Required)

| Product | Provider | Resolution | Revisit | Archive Start | Example Link |
|---------|----------|------------|---------|---------------|--------------|
| **S2E84** | Element84 | 10-20m | 5 days | 2015 | [examples/s2e84](s2e84/) |
| **S2MPC** | Microsoft PC | 10-20m | 5 days | 2015 | [examples/s2mpc](s2mpc/) |
| **LANDSATMPC** | Microsoft PC | 30m | 16 days | 1972 | [examples/landsatmpc](landsatmpc/) |
| **HLS_SENTINEL** | Microsoft PC | 30m | ~5 days | 2013 | [examples/hlsmpc](hlsmpc/) |
| **HLS_LANDSAT** | Microsoft PC | 30m | ~16 days | 2013 | [examples/hlsmpc](hlsmpc/) |

### SAR Data (No Cloud Issues)

| Product | Provider | Resolution | Revisit | Archive Start | Example Link |
|---------|----------|------------|---------|---------------|--------------|
| **S1MPC** | Microsoft PC | 10m | 6 days | 2014 | [examples/s1mpc](s1mpc/) |

### Elevation Data (Static)

| Product | Provider | Resolution | Coverage | Type | Example Link |
|---------|----------|------------|----------|------|--------------|
| **CopDEM30MPC** | Microsoft PC | 30m | Global | DEM | [examples/cop30dem](cop30dem/) |

## Quick Comparison

### When to Use Each Product

**Sentinel-2 (S2E84 / S2MPC)**
- Best spatial resolution (10m)
- Frequent revisit (5 days)
- Recent data (2015-present)
- No historical data before 2015

**Landsat (LANDSATMPC)**
- Long historical archive (1972-present)
- Consistent calibration across decades
- Thermal bands available
- Lower resolution (30m)
- Less frequent (16 days)

**Sentinel-1 SAR (S1MPC)**
- Works through clouds
- Day and night imaging
- Great for water detection
- Harder to interpret than optical
- No color information

**Copernicus DEM (CopDEM30MPC)**
- Static elevation data
- No cloud or date issues
- Global coverage
- No time series
- Single data type (elevation)

**HLS (Harmonized Landsat Sentinel)**
- Combined Landsat 8/9 and Sentinel-2
- ~3 day revisit when using both sources
- Radiometrically harmonized
- Consistent 30m resolution
- Single band naming convention
- Best for high-frequency monitoring

## Common Parameters

### All Products Support

```python
from sat_data_acquisition import SatDataClient, ProcessingParams
from shapely.geometry import box

client = SatDataClient()

processing_params = ProcessingParams(
    satellite='S2MPC',  # or S2E84, S1MPC, LANDSATMPC, HLS_SENTINEL, HLS_LANDSAT, CopDEM30MPC
    search_method='geometry',
    bands=['red', 'green', 'blue'],  # HLS uses B04, B03, B02 for RGB
    clip_method='geometry'
)

geometry = box(lon_min, lat_min, lon_max, lat_max)

dataset = client.search_and_create_image(
    geometry=geometry,
    processing_params=processing_params,
    area_name='my_area'
)
```

### Product-Specific Parameters

| Parameter | S2E84/S2MPC | LANDSATMPC | HLS | S1MPC | CopDEM30MPC |
|-----------|-------------|------------|-----|-------|-------------|
| `start_date` | Required | Required | Required | Required | Ignored |
| `end_date` | Required | Required | Required | Required | Ignored |
| `cloud_coverage` | Supported | Supported | Supported | Ignored | Ignored |
| `bands` | RGB, NIR, SWIR | RGB, NIR, SWIR, Thermal | B01-B12 | VV, VH | data |

## Notebook Structure

Each product folder contains:

### 1. single_area_download.ipynb
Simple tutorial for downloading a single image/area.
- Define bounding box
- Download data
- Visualize
- Save to GeoTIFF

**Perfect for:** First-time users, quick testing

### 2. multi_image_download.ipynb
Advanced examples for time series and multiple areas.
- Time series download
- Multi-area processing from GeoJSON
- 3×3 grid visualization (3 areas × 3 time steps)
- Batch processing
- S3 upload examples

**Perfect for:** Production workflows, monitoring applications

### 3. README.md
Product-specific documentation including:
- Product characteristics
- Band information
- Common applications
- Code examples
- Visualization tips

## GeoJSON Format

For multi-area processing, your GeoJSON must include a `name` property:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "area_identifier",
        "description": "Optional description"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [lon1, lat1],
          [lon2, lat2],
          [lon3, lat3],
          [lon4, lat4],
          [lon1, lat1]
        ]]
      }
    }
  ]
}
```

Example GeoJSON with 3 global cities: [data/geojson/example_areas.geojson](data/geojson/example_areas.geojson)

## Output Structure

```
output/
├── copenhagen_20240615_red_green_blue.tif
├── copenhagen_20240620_red_green_blue.tif
├── london_20240615_red_green_blue.tif
├── london_20240620_red_green_blue.tif
├── seattle_20240615_red_green_blue.tif
└── seattle_20240620_red_green_blue.tif
```

Format: `{area_name}_{date}_{bands}.tif`

For DEM: `{area_name}_elevation.tif` (no date)

## Advanced Features

### S3 Upload

```python
from sat_data_acquisition.processing import save_to_s3

save_to_s3(
    dataset,
    bucket='your-bucket-name',
    prefix='satellite-data/area',
    area_name='copenhagen'
)
```

### Batch Processing with Multiprocessing

```python
from sat_data_acquisition.processing import batch_process_areas

batch_process_areas(
    gdf,
    processing_params,
    output_dir='./output',
    n_workers=4
)
```

### Custom Visualization

```python
import matplotlib.pyplot as plt
import numpy as np

# For optical data
rgb = dataset.sel(time=dataset.time.values[0]).to_array().values[:3]
rgb_scaled = np.clip(rgb / 3000, 0, 1)  # S2
# rgb_scaled = np.clip(rgb / 20000, 0, 1)  # Landsat

plt.imshow(rgb_scaled.transpose(1, 2, 0))
plt.show()

# For SAR data
vv = dataset['vv'].values
vv_db = 10 * np.log10(np.clip(vv, 1e-10, None))
plt.imshow(vv_db, cmap='gray', vmin=-25, vmax=0)
plt.show()

# For DEM
elevation = dataset['elevation'].values
plt.imshow(elevation, cmap='terrain')
plt.colorbar(label='Elevation (m)')
plt.show()
```

## Common Indices

### NDVI (Normalized Difference Vegetation Index)
```python
nir = dataset['nir'].values
red = dataset['red'].values
ndvi = (nir - red) / (nir + red + 1e-8)
```

### NDWI (Water Index)
```python
green = dataset['green'].values
nir = dataset['nir'].values
ndwi = (green - nir) / (green + nir + 1e-8)
```

### EVI (Enhanced Vegetation Index)
```python
nir = dataset['nir'].values
red = dataset['red'].values
blue = dataset['blue'].values
evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
```

## Troubleshooting

### No images found
- Check date range (start_date, end_date)
- Increase cloud_coverage threshold
- Verify geometry is valid
- Check if area has satellite coverage

### Memory issues
- Reduce area size
- Use fewer bands
- Process smaller time windows
- Use `clip_method='window'` with smaller `pixels`

### Slow downloads
- Use multiprocessing for batch processing
- Consider using S3 directly
- Reduce number of bands
- Check network connection

## See Also

- [Main README](../README.md) - Installation and setup
- [Development Guide](../DEVELOPMENT.md) - Contributing and testing
- [Code Quality Guide](../CODE_QUALITY.md) - Standards and best practices

## Citation

When using Satellite Data Acquisition, please cite:

```
Satellite Data Acquisition Tool
Author: Peter Kongstad
Year: 2026
```

Data providers:
- Sentinel-2: ESA Copernicus Programme
- Sentinel-1: ESA Copernicus Programme  
- Landsat: USGS/NASA Landsat Programme
- Copernicus DEM: European Space Agency
- STAC Catalogs: Microsoft Planetary Computer, Element84 Earth Search
