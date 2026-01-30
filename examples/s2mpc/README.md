# Sentinel-2 Examples (Microsoft Planetary Computer)

Examples for downloading Sentinel-2 imagery from Microsoft Planetary Computer (S2MPC).

## Notebooks

### 1. [single_area_download.ipynb](single_area_download.ipynb)
Quick start tutorial for downloading a single satellite image.

**Key Features:**
- Simple bounding box definition
- Single image download
- RGB visualization
- Save to GeoTIFF

**Perfect for:** First-time users, quick testing

### 2. [multi_image_download.ipynb](multi_image_download.ipynb)
Advanced examples for time series and multiple areas.

**Key Features:**
- Time series download (multiple dates)
- Multi-area processing from GeoJSON
- 3×3 grid visualization (3 areas × 3 time steps)
- Batch processing examples
- S3 upload examples

**Perfect for:** Production workflows, monitoring applications

## Product Characteristics

- **Product**: Sentinel-2 Level-2A Surface Reflectance
- **Source**: Microsoft Planetary Computer
- **Resolution**: 10m-60m (band dependent)
- **Revisit**: ~5 days
- **Bands**: red, green, blue, nir, swir16, swir22, etc.
- **Cloud Coverage**: Filterable (default: <25%)
- **Date Range**: Required (start_date, end_date)

## GeoJSON Format

When using multiple areas, your GeoJSON must include a `name` property:

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
        "coordinates": [[...]]
      }
    }
  ]
}
```

## Quick Start

```python
from sat_data_acquisition import SatDataClient, ProcessingParams
from shapely.geometry import box

client = SatDataClient()

processing_params = ProcessingParams(
    satellite='S2MPC',
    search_method='geometry',
    start_date='2024-01-01',
    end_date='2024-12-31',
    bands=['red', 'green', 'blue'],
    cloud_coverage=20
)

geometry = box(12.544, 55.670, 12.584, 55.700)

dataset = client.search_and_create_image(
    geometry=geometry,
    processing_params=processing_params
)
```

## Output Structure

```
output/
├── copenhagen_20240615_merged.tif
├── copenhagen_20240620_merged.tif
└── copenhagen_20240625_merged.tif
```

## See Also

- [S2E84 Examples](../s2e84/) - Sentinel-2 from Element84
- [S1MPC Examples](../s1mpc/) - Sentinel-1 SAR data
- [Main Examples README](../README.md) - All product examples
