# Sentinel-1 SAR Examples (Microsoft Planetary Computer)

Examples for downloading Sentinel-1 SAR imagery from Microsoft Planetary Computer (S1MPC).

## Notebooks

### 1. [single_area_download.ipynb](single_area_download.ipynb)
Quick start tutorial for downloading a single SAR image.

**Key Features:**
- Simple bounding box definition
- Single SAR image download
- VV and VH polarization visualization
- Save to GeoTIFF

**Perfect for:** First-time SAR users, quick testing

### 2. [multi_image_download.ipynb](multi_image_download.ipynb)
Advanced examples for SAR time series and multiple areas.

**Key Features:**
- Time series download (multiple dates)
- Multi-area processing from GeoJSON
- 3×3 grid visualization (3 areas × 3 time steps)
- SAR analysis tips (ratio, change detection)
- All-weather monitoring

**Perfect for:** Change detection, flood mapping, continuous monitoring

## Product Characteristics

- **Product**: Sentinel-1 GRD (Ground Range Detected)
- **Source**: Microsoft Planetary Computer
- **Resolution**: 10m (IW mode)
- **Revisit**: ~6 days (single satellite), ~3 days (constellation)
- **Bands**: VV, VH polarizations
- **Cloud Coverage**: N/A - SAR works through clouds!
- **Date Range**: Required (start_date, end_date)
- **All-weather**: Day and night imaging capability

## Key Differences from Optical Data

| Feature | Optical (S2) | SAR (S1) |
|---------|-------------|----------|
| Cloud filtering | Required | Not needed |
| Wavelength | Visible/IR | Microwave |
| Time of day | Daytime | 24/7 |
| Water detection | Dark (NIR) | Very dark |
| Vegetation | Green (visible) | Volume scattering |
| Urban areas | Visible details | High backscatter |

## Quick Start

```python
from sat_data_acquisition import SatDataClient, ProcessingParams
from shapely.geometry import box

client = SatDataClient()

# No cloud_coverage parameter for SAR!
processing_params = ProcessingParams(
    satellite='S1MPC',
    search_method='geometry',
    start_date='2024-01-01',
    end_date='2024-12-31',
    bands=['vv', 'vh']  # SAR polarizations
)

geometry = box(12.544, 55.670, 12.584, 55.700)

dataset = client.search_and_create_image(
    geometry=geometry,
    processing_params=processing_params
)
```

## SAR Visualization

```python
import numpy as np

# Convert to dB scale for visualization
vv = dataset['vv'].values
vv_db = 10 * np.log10(np.clip(vv, 1e-10, None))

# Plot
plt.imshow(vv_db, cmap='gray', vmin=-25, vmax=0)
plt.colorbar(label='dB')
```

## Common Applications

1. **Flood Mapping**: Water appears very dark (low backscatter)
2. **Ship Detection**: Ships appear bright on dark water
3. **Agriculture**: Monitor crops through clouds
4. **Change Detection**: Compare images from different dates
5. **Urban Monitoring**: Buildings have high backscatter

## Output Structure

```
output/
├── copenhagen_20240615_vv_vh.tif
├── copenhagen_20240621_vv_vh.tif
└── copenhagen_20240627_vv_vh.tif
```

## See Also

- [S2MPC Examples](../s2mpc/) - Sentinel-2 optical data
- [COP30DEM Examples](../cop30dem/) - Digital elevation model
- [Main Examples README](../README.md) - All product examples
