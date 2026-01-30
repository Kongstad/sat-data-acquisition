# Copernicus DEM 30m Examples (Microsoft Planetary Computer)

Examples for downloading Copernicus DEM 30m digital elevation data.

## Notebooks

### 1. [single_area_download.ipynb](single_area_download.ipynb)
Quick start tutorial for downloading DEM data for a single area.

**Key Features:**
- Simple bounding box definition
- DEM download (no dates needed)
- Elevation visualization with terrain colormap
- Hillshade generation
- Save to GeoTIFF

**Perfect for:** Elevation analysis, terrain visualization

### 2. [multi_area_download.ipynb](multi_area_download.ipynb)
Examples for downloading DEM for multiple areas.

**Key Features:**
- Multi-area processing from GeoJSON
- Elevation statistics comparison
- Hillshade visualization for multiple areas
- Advanced terrain analysis examples
- Slope and aspect calculations

**Perfect for:** Regional analysis, comparative topography

## Product Characteristics

- **Product**: Copernicus DEM GLO-30 (30m resolution)
- **Source**: Microsoft Planetary Computer
- **Resolution**: 30m (1 arc-second)
- **Coverage**: Global (90°N to 90°S)
- **Vertical Accuracy**: ~4m (absolute), ~2m (relative)
- **Bands**: elevation (meters above sea level)
- **Time**: Static (no time series)
- **Cloud Coverage**: N/A - elevation data

## Key Differences from Other Products

| Feature | Optical/SAR | DEM |
|---------|-------------|-----|
| Time dimension | Multiple dates | Static |
| Cloud filtering | Required (optical) | N/A |
| Date range | Required | Not needed |
| Typical use | Change detection | Terrain analysis |
| Bands | Spectral/polarization | Elevation only |

## Quick Start

```python
from sat_data_acquisition import SatDataClient, ProcessingParams
from shapely.geometry import box

client = SatDataClient()

# No dates or cloud_coverage for DEM!
processing_params = ProcessingParams(
    satellite='CopDEM30MPC',
    search_method='geometry',
    bands=['elevation']
)

geometry = box(12.544, 55.670, 12.584, 55.700)

dataset = client.search_and_create_image(
    geometry=geometry,
    processing_params=processing_params
)
```

## Visualization Examples

### Basic Elevation Map
```python
import matplotlib.pyplot as plt

elevation = dataset['elevation'].values

plt.imshow(elevation, cmap='terrain')
plt.colorbar(label='Elevation (m)')
plt.title('Elevation Map')
```

### Hillshade
```python
import numpy as np

def hillshade(elevation, azimuth=315, altitude=45):
    azimuth = np.radians(azimuth)
    altitude = np.radians(altitude)
    
    dy, dx = np.gradient(elevation)
    slope = np.arctan(np.sqrt(dx**2 + dy**2))
    aspect = np.arctan2(-dx, dy)
    
    shaded = np.sin(altitude) * np.sin(slope) + \
             np.cos(altitude) * np.cos(slope) * \
             np.cos(azimuth - aspect)
    
    return 255 * (shaded + 1) / 2

hs = hillshade(elevation)
plt.imshow(hs, cmap='gray')
```

### Slope Map
```python
def calculate_slope(elevation, pixel_size=30):
    dy, dx = np.gradient(elevation, pixel_size)
    slope = np.arctan(np.sqrt(dx**2 + dy**2))
    return np.degrees(slope)

slope = calculate_slope(elevation)
plt.imshow(slope, cmap='YlOrRd')
plt.colorbar(label='Slope (degrees)')
```

## Common Applications

1. **Topographic Analysis**: Contour maps, relief visualization
2. **Hydrological Modeling**: Watershed delineation, flow direction
3. **Solar Analysis**: Combined with aspect for solar potential
4. **Viewshed Analysis**: Line-of-sight calculations
5. **3D Visualization**: Drape satellite imagery over terrain
6. **Flood Risk Assessment**: Identify low-lying areas
7. **Volume Calculations**: Cut-and-fill analysis

## Output Structure

```
output/
├── copenhagen_elevation.tif
├── london_elevation.tif
└── seattle_elevation.tif
```

Note: DEM files don't have dates in the filename since elevation is static.

## Technical Details

- **Vertical Datum**: EGM2008 geoid
- **Horizontal Datum**: WGS84
- **Data Type**: Float32 (meters)
- **NoData Value**: Varies (oceans typically -32767 or NaN)
- **Coordinate System**: Geographic (lat/lon) or projected

## See Also

- [S2MPC Examples](../s2mpc/) - Combine with optical imagery
- [S1MPC Examples](../s1mpc/) - Terrain effects on SAR
- [Main Examples README](../README.md) - All product examples
