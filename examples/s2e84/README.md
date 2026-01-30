# SatData Examples

This directory contains example notebooks demonstrating how to use SatData for satellite data retrieval.

## Available Examples

### single_area_download.ipynb
Quick start example for downloading a single satellite image:
- Simple bounding box area definition
- RGB true color visualization (TCI)
- Save to GeoTIFF
- Perfect for getting started

### multi_image_download.ipynb
Advanced example for downloading multiple satellite images:
- **Example 1**: Time series for single area
- **Example 2**: Multiple areas from GeoJSON file
- Time series visualization
- Local and S3 storage options

## Quick Start

1. Install SatData:
```bash
pip install -e ..
```

2. Open the notebook:
```bash
jupyter notebook multi_image_download.ipynb
```

3. Run the cells to download satellite imagery

## GeoJSON Format

For multiple area processing, create a GeoJSON file with a `name` property for each feature:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "area1"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[...]]
      }
    }
  ]
}
```

The `name` property is used in output filenames to identify each area.

## Example Data

Sample GeoJSON files are provided in `../data/geojson/`:
- `example_areas.geojson` - Three areas around Copenhagen

## Output

Downloaded images are saved to `../data/images/` with the structure:
```
data/images/
└── S2E84/
    └── 2024/
        └── tiff/
            ├── S2E84_2024-06-15_red_green_blue_nir_copenhagen_center.tif
            └── S2E84_2024-07-20_red_green_blue_vesterbro.tif
```

## Notes

- Requires AWS credentials for S3 upload functionality
- Default cloud coverage threshold is 30%
- Images are downloaded with multiprocessing for optimal performance
