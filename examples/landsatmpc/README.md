# Landsat Examples (Microsoft Planetary Computer)

Examples for downloading Landsat 8/9 imagery from Microsoft Planetary Computer.

## Notebooks

### 1. [single_area_download.ipynb](single_area_download.ipynb)
Quick start tutorial for downloading a single Landsat image.

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
- Long-term change analysis
- Historical data access

**Perfect for:** Long-term monitoring, historical analysis

## Product Characteristics

- **Product**: Landsat 8/9 Level-2 Surface Reflectance
- **Source**: Microsoft Planetary Computer
- **Resolution**: 30m (optical), 100m (thermal)
- **Revisit**: 16 days (single satellite), 8 days (constellation)
- **Bands**: red, green, blue, nir, swir1, swir2, coastal, pan, thermal
- **Cloud Coverage**: Filterable (default: <25%)
- **Date Range**: Required (start_date, end_date)
- **Historical Archive**: 1972-present (Landsat 1-9)

## Key Advantages

1. **Long Historical Record**: Data since 1972
2. **Consistent Calibration**: Across entire archive
3. **Free and Open**: USGS Landsat program
4. **Thermal Bands**: Unique capability (Landsat 8/9)
5. **Global Coverage**: Every location on Earth

## Landsat vs Sentinel-2

| Feature | Landsat 8/9 | Sentinel-2 |
|---------|-------------|------------|
| Spatial Resolution | 30m | 10-20m |
| Temporal Resolution | 16 days | 5 days |
| Historical Archive | 1972-present | 2015-present |
| Thermal Bands | Yes | No |
| Swath Width | 185 km | 290 km |
| Best Use Case | Long-term change | Recent monitoring |

**When to use Landsat:**
- Historical analysis (before 2015)
- Long-term trend detection (decades)
- Thermal analysis (surface temperature)
- Consistent time series (1972-present)

**When to use Sentinel-2:**
- Recent data (2015-present)
- Higher spatial resolution needed
- More frequent revisits (every 5 days)

## Quick Start

```python
from sat_data_acquisition import SatDataClient, ProcessingParams
from shapely.geometry import box

client = SatDataClient()

processing_params = ProcessingParams(
    satellite='LANDSATMPC',
    search_method='geometry',
    start_date='2024-01-01',
    end_date='2024-12-31',
    bands=['red', 'green', 'blue'],
    cloud_coverage=20
)

geometry = box(-122.356, 47.582, -122.308, 47.630)  # Seattle

dataset = client.search_and_create_image(
    geometry=geometry,
    processing_params=processing_params
)
```

## Available Bands

| Band | Wavelength | Resolution | Description |
|------|------------|------------|-------------|
| coastal | 0.43-0.45 µm | 30m | Coastal/Aerosol |
| blue | 0.45-0.51 µm | 30m | Blue |
| green | 0.53-0.59 µm | 30m | Green |
| red | 0.64-0.67 µm | 30m | Red |
| nir | 0.85-0.88 µm | 30m | Near Infrared |
| swir1 | 1.57-1.65 µm | 30m | Shortwave IR 1 |
| swir2 | 2.11-2.29 µm | 30m | Shortwave IR 2 |
| pan | 0.50-0.68 µm | 15m | Panchromatic |
| thermal | 10.6-12.5 µm | 100m | Thermal (Landsat 8/9 only) |

## Common Indices

### NDVI (Vegetation)
```python
nir = dataset['nir'].values
red = dataset['red'].values
ndvi = (nir - red) / (nir + red + 1e-8)
```

### NDWI (Water)
```python
green = dataset['green'].values
nir = dataset['nir'].values
ndwi = (green - nir) / (green + nir + 1e-8)
```

### NDBI (Built-up)
```python
swir1 = dataset['swir1'].values
nir = dataset['nir'].values
ndbi = (swir1 - nir) / (swir1 + nir + 1e-8)
```

## Applications

1. **Long-term Land Cover Change**: Deforestation, urbanization (1972-present)
2. **Agricultural Monitoring**: Crop health, yield estimation
3. **Water Resources**: Lake/reservoir monitoring, drought assessment
4. **Urban Planning**: City expansion, land use change
5. **Climate Studies**: Glacier retreat, sea ice extent
6. **Disaster Response**: Fire mapping, flood extent
7. **Thermal Analysis**: Urban heat islands, water temperature

## Output Structure

```
output/
├── seattle_20240615_merged.tif
├── seattle_20240701_merged.tif
└── seattle_20240717_merged.tif
```

## See Also

- [S2MPC Examples](../s2mpc/) - Sentinel-2 for recent high-res data
- [S2E84 Examples](../s2e84/) - Sentinel-2 from Element84
- [Main Examples README](../README.md) - All product examples
