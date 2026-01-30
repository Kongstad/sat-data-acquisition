# Satellite Data Acquisition

Python package for downloading satellite imagery from multiple sources with a standardized API.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Version](https://img.shields.io/badge/version-0.9.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**[Full Documentation on GitHub](https://github.com/Kongstad/sat-data-acquisition)**

## Features

- **Multiple satellites**: Sentinel-2, Sentinel-1, Landsat 8/9, HLS, Copernicus DEM
- **Flexible providers**: Element84, Microsoft Planetary Computer  
- **Smart search**: By coordinates or GeoJSON geometries
- **Multi-temporal**: Download imagery across date ranges
- **Cloud filtering**: Configurable cloud coverage thresholds
- **Storage options**: Local disk or AWS S3
- **Type-safe API**: Pydantic validation for all parameters

## Installation

```bash
pip install sat-data-acquisition
```

## Quick Start

```python
from sat_data_acquisition import SatDataClient, ProcessingParams

# Define area (Copenhagen example)
geometry = {
    "type": "Polygon",
    "coordinates": [[
        [12.5464, 55.6761], [12.5864, 55.6761],
        [12.5864, 55.7061], [12.5464, 55.7061],
        [12.5464, 55.6761]
    ]]
}

# Configure search
processing_params = ProcessingParams(
    satellite='S2MPC',
    bands=['red', 'green', 'blue', 'nir'],
    start_date='2024-06-01',
    end_date='2024-08-31',
    cloud_coverage=20,
)

# Download imagery
client = SatDataClient()
dataset = client.search_and_create_image(
    geometry=geometry,
    processing_params=processing_params,
)

print(f"Downloaded {len(dataset.time)} images")
# Returns xarray.Dataset with shape: {'time': 12, 'y': 344, 'x': 291}
```

## Visualization

```python
import matplotlib.pyplot as plt
import numpy as np

# Get first image
image = dataset.isel(time=0)
rgb = np.dstack([image['red'], image['green'], image['blue']])

# Display
plt.imshow(rgb / 3000)
plt.title(f"Sentinel-2 - {str(image.time.values)[:10]}")
plt.show()
```

## Save to Disk

```python
from sat_data_acquisition import SaveParams
from sat_data_acquisition.processing import save_data

save_params = SaveParams(
    output_path='./data/images',
    save_to_local=True,
    save_as_geotiff=True,
    merge_bands=True,  # Single multi-band file vs separate files per band
)

for time_val in dataset.time.values:
    save_data(
        image=dataset.sel(time=time_val),
        identifier='copenhagen',
        datetime=str(time_val),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params,
    )
```

## Available Satellites

| Satellite | Bands | Resolution | Revisit | Providers |
|-----------|-------|------------|---------|-----------|
| Sentinel-2 | RGB, NIR, SWIR, SCL | 10-60m | 5 days | MPC, E84 |
| Sentinel-1 | VV, VH (SAR) | 10m | 12 days | MPC |
| Landsat 8/9 | RGB, NIR, SWIR, Thermal | 30m | 16 days | MPC |
| HLS Sentinel | B01-B12 (harmonized) | 30m | 5 days | MPC |
| HLS Landsat | B01-B12 (harmonized) | 30m | 16 days | MPC |
| Copernicus DEM | Elevation | 30m | Static | MPC |

## Common Use Cases

### Temporal Analysis

```python
# Download monthly imagery for growing season
processing_params = ProcessingParams(
    satellite='S2MPC',
    bands=['red', 'green', 'blue', 'nir'],
    start_date='2024-04-01',
    end_date='2024-10-01',
    cloud_coverage=15,
)

dataset = client.search_and_create_image(geometry, processing_params)
# Analyze vegetation changes over time with xarray
```

### SAR for All-Weather Monitoring

```python
# Sentinel-1 works through clouds
processing_params = ProcessingParams(
    satellite='S1MPC',
    bands=['vv', 'vh'],  # Radar polarizations
    start_date='2024-01-01',
    end_date='2024-12-31',
)
```

### S3 Storage

```python
save_params = SaveParams(
    output_path='./temp',
    save_to_local=False,
    save_to_s3=True,
    s3_bucket='my-satellite-data',
    s3_path='projects/monitoring',
)
```

## Documentation

Visit the [GitHub repository](https://github.com/Kongstad/sat-data-acquisition) for:

- Comprehensive guides: Detailed satellite specifications, processing parameters, and save options
- Working examples: Jupyter notebooks for each satellite with visualization
- Architecture docs: System design and data flow diagrams

## Requirements

- Python 3.12+
- Core dependencies: xarray, rasterio, geopandas, odc-stac, pystac-client

## STAC-Native Philosophy

Unlike legacy systems that download entire scenes, this package is **STAC-native**. It queries metadata first and leverages lazy-loading to stream only the specific pixels required for your geometry, significantly reducing bandwidth and storage requirements.

## License

MIT License - see [LICENSE](https://github.com/Kongstad/sat-data-acquisition/blob/main/LICENSE)

## Acknowledgments

- [Element84](https://www.element84.com/) for Earth Search STAC API
- [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/) for open data access
- ESA for Sentinel satellite programs
- NASA/USGS for Landsat data

## Support

- Issues: [GitHub Issues](https://github.com/Kongstad/sat-data-acquisition/issues)
- Documentation: [GitHub Repository](https://github.com/Kongstad/sat-data-acquisition)
