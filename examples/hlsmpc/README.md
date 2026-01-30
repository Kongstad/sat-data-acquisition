# HLS (Harmonized Landsat Sentinel) Examples

Examples for downloading harmonized Landsat and Sentinel-2 data from Microsoft Planetary Computer.

## What is HLS?

HLS (Harmonized Landsat Sentinel) combines Landsat 8/9 and Sentinel-2 data into a seamless, analysis-ready dataset:

- **Higher temporal resolution**: ~3 day revisit time (vs 5-16 days for individual sensors)
- **Consistent 30m resolution**: Sentinel-2 bands resampled to match Landsat
- **Radiometric harmonization**: Cross-calibrated for consistent measurements
- **Single band naming**: Unified naming convention (B01-B12)

## Available Examples

### Single Area Download
- **[single_area_download.ipynb](single_area_download.ipynb)**: Quick start for downloading HLS imagery
- Shows both HLS_LANDSAT and HLS_SENTINEL options
- RGB visualization with proper stretching

### Multi-Image Download
- **[multi_image_download.ipynb](multi_image_download.ipynb)**: Advanced time series and multi-area examples
- Time series visualization
- Multiple area processing from GeoJSON
- Save to disk functionality

## Key Features

- 30m resolution (harmonized)
- 2-3 day revisit time when combining both sources
- Analysis-ready data (atmospherically corrected)
- Cloud masking with QA band
- SWIR and NIR bands for vegetation analysis

## Use Cases

- **High-frequency monitoring**: More observations than Landsat or Sentinel-2 alone
- **Gap filling**: Use both sensors to reduce cloud impacts
- **Time series analysis**: Consistent data for trend detection
- **Agriculture**: Frequent observations during growing season
- **Change detection**: Better temporal resolution for detecting changes

## Band Information

HLS uses a unified band naming convention:

| Band | Description | Wavelength (µm) |
|------|-------------|-----------------|
| B01 | Coastal Aerosol | 0.43-0.45 |
| B02 | Blue | 0.45-0.51 |
| B03 | Green | 0.53-0.59 |
| B04 | Red | 0.64-0.67 |
| B05 | NIR | 0.85-0.88 |
| B06 | SWIR 1 | 1.57-1.65 |
| B07 | SWIR 2 | 2.11-2.29 |
| B08 | Pan | 0.50-0.68 |
| B09 | Cirrus | 1.36-1.38 |
| B10 | TIR 1 | 10.60-12.51 |
| B11 | TIR 2 | 11.50-12.51 |
| B12 | QA | Quality flags |

## Notes

- HLS data is only available from 2013 onwards
- Both HLS_LANDSAT and HLS_SENTINEL share the same band names
- Use geometry-based search (tile search not supported)
- Cloud coverage filtering available
- Surface reflectance data (already atmospherically corrected)

For more details, see the [main documentation](../../docs/SATELLITE_SOURCES.md).
