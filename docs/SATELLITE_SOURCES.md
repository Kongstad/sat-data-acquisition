# Satellite Data Sources

Comprehensive guide to available satellite data sources, their characteristics, and available bands.

## Sentinel-2 (Optical)

**Provider**: Element84 (S2E84), Microsoft Planetary Computer (S2MPC)  
**Product**: Level-2A Surface Reflectance  
**Resolution**: 10m, 20m, 60m (band dependent)  
**Revisit Time**: ~5 days  
**Data Range**: 2015 - present  

### Available Bands

| Band Name | Native | Wavelength (µm) | Resolution | Description |
|-----------|---------|-----------------|------------|-------------|
| coastal | B01 | 0.443 | 60m | Coastal aerosol |
| blue | B02 | 0.490 | 10m | Blue |
| green | B03 | 0.560 | 10m | Green |
| red | B04 | 0.665 | 10m | Red |
| rededge1 | B05 | 0.705 | 20m | Red Edge 1 |
| rededge2 | B06 | 0.740 | 20m | Red Edge 2 |
| rededge3 | B07 | 0.783 | 20m | Red Edge 3 |
| nir | B08 | 0.842 | 10m | Near Infrared |
| nir08 | B8A | 0.865 | 20m | Near Infrared narrow |
| nir09 | B09 | 0.945 | 60m | Water vapor |
| cirrus | B10 | 1.375 | 60m | Cirrus |
| swir16 | B11 | 1.610 | 20m | SWIR 1 |
| swir22 | B12 | 2.190 | 20m | SWIR 2 |
| scl | SCL | - | 20m | Scene Classification Layer |

### Scene Classification Layer (SCL)

The SCL band provides pixel-level classification for cloud masking:

| Value | Classification |
|-------|----------------|
| 0 | No Data |
| 1 | Saturated or defective |
| 2 | Dark Area Pixels |
| 3 | Cloud Shadows |
| 4 | Vegetation |
| 5 | Bare Soils |
| 6 | Water |
| 7 | Clouds low probability |
| 8 | Clouds medium probability |
| 9 | Clouds high probability |
| 10 | Thin Cirrus |
| 11 | Snow/Ice |

### Common Use Cases

- **True Color**: `['red', 'green', 'blue']` or `['B04', 'B03', 'B02']`
- **False Color IR**: `['nir', 'red', 'green']` or `['B08', 'B04', 'B03']`
- **NDVI**: `['red', 'nir']` or `['B04', 'B08']`
- **Cloud Masking**: Include `'scl'` or `'SCL'` in bands

### Example

```python
params = ProcessingParams(
    satellite='S2MPC',  # or 'S2E84'
    bands=['red', 'green', 'blue', 'nir', 'scl'],
    cloud_coverage=20,
    # ... other params
)
```

---

## Sentinel-1 (SAR)

**Provider**: Microsoft Planetary Computer (S1MPC)  
**Product**: GRD (Ground Range Detected), Radiometrically Terrain Corrected  
**Resolution**: 10m  
**Revisit Time**: ~6 days (single satellite), ~3 days (constellation)  
**Data Range**: 2014 - present  

### Available Bands

| Band | Polarization | Description |
|------|--------------|-------------|
| VV | Vertical-Vertical | Co-polarization |
| VH | Vertical-Horizontal | Cross-polarization |

### Characteristics

- **All-weather**: Works through clouds, rain, and darkness
- **Water Detection**: Water appears very dark (low backscatter)
- **Urban Areas**: Buildings show high backscatter
- **No Color**: Grayscale intensity data only

### Common Use Cases

- Flood mapping and monitoring
- Ship detection
- Agriculture monitoring through clouds
- Change detection
- Urban monitoring

### Example

```python
params = ProcessingParams(
    satellite='S1MPC',
    bands=['VV', 'VH'],
    search_method='geometry',  # Only geometry search supported
    # No cloud_coverage parameter (SAR sees through clouds)
)
```

---

## Landsat 8/9

**Provider**: Microsoft Planetary Computer (LANDSATMPC)  
**Product**: Collection 2 Level-2 Surface Reflectance  
**Resolution**: 30m (15m panchromatic)  
**Revisit Time**: 16 days  
**Data Range**: 1972 - present (historical Landsat data available)  

### Available Bands

| Band | Wavelength (µm) | Resolution | Description |
|------|-----------------|------------|-------------|
| coastal | 0.43-0.45 | 30m | Coastal/Aerosol |
| blue | 0.45-0.51 | 30m | Blue |
| green | 0.53-0.59 | 30m | Green |
| red | 0.64-0.67 | 30m | Red |
| nir08 | 0.85-0.88 | 30m | Near Infrared |
| swir16 | 1.57-1.65 | 30m | SWIR 1 |
| swir22 | 2.11-2.29 | 30m | SWIR 2 |
| lwir11 | 10.60-11.19 | 100m | Thermal Infrared |
| qa_pixel | - | 30m | Quality Assessment |

### Key Advantage

**Long Historical Archive**: Landsat provides consistent data since 1972, making it ideal for:
- Long-term change detection
- Historical analysis
- Decadal trend monitoring
- Thermal analysis (unique to Landsat)

### Example

```python
params = ProcessingParams(
    satellite='LANDSATMPC',
    bands=['red', 'green', 'blue', 'nir08', 'lwir11'],
    cloud_coverage=30,
    start_date='1990-01-01',  # Historical data available!
)
```

---

## HLS (Harmonized Landsat Sentinel)

**Provider**: Microsoft Planetary Computer  
**Products**: HLS_LANDSAT (L30), HLS_SENTINEL (S30)  
**Resolution**: 30m  
**Revisit Time**: ~3 days (combined)  
**Data Range**: 2013 - present (L30), 2015 - present (S30)

### Available Bands

The HLS product harmonizes Landsat-8 and Sentinel-2 data to a common 30m grid.

| Band Name | OLI Band | MSI Band | L30 Subdataset | S30 Subdataset | Description |
|-----------|----------|----------|----------------|----------------|-------------|
| coastal | 1 | 1 | 01 | 01 | Coastal aerosol |
| blue | 2 | 2 | 02 | 02 | Blue |
| green | 3 | 3 | 03 | 03 | Green |
| red | 4 | 4 | 04 | 04 | Red |
| rededge1 | - | 5 | - | 05 | Red-edge 1 |
| rededge2 | - | 6 | - | 06 | Red-edge 2 |
| rededge3 | - | 7 | - | 07 | Red-edge 3 |
| nir_broad | - | 8 | - | 08 | NIR broad |
| nir_narrow| 5 | 8A | 05 | 09 | NIR narrow |
| swir1 | 6 | 11 | 06 | 12 | SWIR 1 |
| swir2 | 7 | 12 | 07 | 13 | SWIR 2 |
| water_vapor | - | 9 | - | 10 | Water vapor |
| cirrus | 9 | 10 | 08 | 11 | Cirrus |
| thermal1 | 10 | - | 09 | - | Thermal infrared 1 |
| thermal2 | 11 | - | 10 | - | Thermal infrared 2 |
| qa | - | - | 11 | 14 | Quality Assessment |

### Key Advantage

**Seamless Fusion**: HLS products harmonize Landsat 8 and Sentinel-2 data to create a virtual constellation with:
- More frequent revisits (~3 days)
- Consistent radiometry
- Single band naming convention

### Example

```python
params = ProcessingParams(
    satellite='HLS_SENTINEL',  # or 'HLS_LANDSAT'
    bands=['red', 'green', 'blue', 'nir_narrow'],
    cloud_coverage=20,
)
```

---

## Copernicus DEM 30m

**Provider**: Microsoft Planetary Computer (CopDEM30MPC)  
**Product**: Global Digital Elevation Model  
**Resolution**: 30m (1 arc-second)  
**Coverage**: Global (90°N to 90°S)  
**Type**: Static elevation data  

### Available Band

| Band | Description |
|------|-------------|
| data | Elevation in meters above mean sea level |

### Characteristics

- **Static Data**: No temporal component (single global dataset)
- **No Dates Required**: start_date and end_date ignored
- **No Cloud Coverage**: DEM has no atmospheric effects
- **Global Coverage**: Worldwide consistent dataset

### Common Use Cases

- Terrain analysis
- Slope and aspect calculation
- Watershed delineation
- Visibility analysis
- 3D visualization

### Example

```python
params = ProcessingParams(
    satellite='CopDEM30MPC',
    bands=['data'],
    search_method='geometry',
    # No dates or cloud_coverage needed
)
```

---

## Quick Comparison

| Feature | S2 | S1 | Landsat | HLS | CopDEM |
|---------|----|----|---------|-----|--------|
| Resolution | 10m | 10m | 30m | 30m | 30m |
| Revisit | 5d | 3-6d | 16d | 3d | - |
| Cloud-free | No | Yes | No | No | Yes |
| Historical | 2015+ | 2014+ | 1972+ | 2013+ | Static |
| Thermal | No | No | Yes | Yes | No |
| Night | No | Yes | No | No | - |
| Color | Yes | No | Yes | Yes | No |

---

## Band Naming

The package supports both **common names** and **native names** for Sentinel-2:

```python
# These are equivalent:
bands=['red', 'green', 'blue']  # Common names
bands=['B04', 'B03', 'B02']      # Native names

# Mix and match:
bands=['red', 'B03', 'blue', 'nir']  # Also works
```

For other satellites, use the native band names shown in tables above.
