# Processing Parameters

Complete reference for `ProcessingParams` configuration options.

## Overview

`ProcessingParams` controls how satellite data is searched and retrieved. All parameters are validated when the object is created.

```python
from sat_data_acquisition import ProcessingParams

params = ProcessingParams(
    satellite='S2MPC',
    search_method='geometry',
    start_date='2024-01-01',
    end_date='2024-12-31',
    bands=['red', 'green', 'blue'],
    cloud_coverage=20,
)
```

## Required Parameters

### satellite
**Type**: `str`  
**Required**: Yes  
**Options**: `'S2MPC'`, `'S2E84'`, `'S1MPC'`, `'LANDSATMPC'`, `'HLS_LANDSAT'`, `'HLS_SENTINEL'`, `'CopDEM30MPC'`

The satellite/dataset identifier.

```python
satellite='S2MPC'  # Sentinel-2 from Microsoft Planetary Computer
satellite='S2E84'  # Sentinel-2 from Element84
satellite='S1MPC'  # Sentinel-1 SAR from MPC
```

See [SATELLITE_SOURCES.md](SATELLITE_SOURCES.md) for complete details on each satellite.

### search_method
**Type**: `str`  
**Required**: Yes  
**Options**: `'geometry'`, `'tile'`

How to search for satellite data.

```python
search_method='geometry'  # Search by geographic area (most common)
search_method='tile'      # Search by MGRS tile ID (S2 only)
```

**Note**: Sentinel-1, Landsat, and HLS only support `'geometry'` search.

## Date Parameters

### start_date
**Type**: `str` or `datetime.date`  
**Required**: Yes (except CopDEM)  
**Format**: `'YYYY-MM-DD'`

Start of temporal search range.

```python
start_date='2024-06-01'
start_date='2023-01-01'  # Works with historical data for Landsat
```

### end_date
**Type**: `str` or `datetime.date`  
**Required**: Yes (except CopDEM)  
**Format**: `'YYYY-MM-DD'`

End of temporal search range.

```python
end_date='2024-06-30'
```

**Note**: CopDEM30MPC ignores date parameters (static elevation data).

## Band Selection

### bands
**Type**: `List[str]`  
**Required**: No (uses satellite defaults)  
**Default**: Satellite-specific (typically RGB + NIR)

List of bands to retrieve. If omitted, uses default bands for the satellite.

```python
# Sentinel-2 examples (common or native names)
bands=['red', 'green', 'blue']           # RGB
bands=['B04', 'B03', 'B02']              # RGB (native)
bands=['red', 'nir']                     # For NDVI
bands=['red', 'green', 'blue', 'scl']    # RGB + cloud mask

# Sentinel-1 examples
bands=['VV', 'VH']  # Both polarizations

# Landsat examples
bands=['red', 'green', 'blue', 'nir08', 'lwir11']  # RGB + NIR + thermal
```

**Default bands per satellite:**
- S2MPC/S2E84: `['B02', 'B03', 'B04', 'B08']` (RGB + NIR)
- S1MPC: `['VV', 'VH']`
- LANDSATMPC: `['red', 'green', 'blue', 'nir08']`
- CopDEM30MPC: `['data']`

See [SATELLITE_SOURCES.md](SATELLITE_SOURCES.md) for all available bands per satellite.

## Search Filtering

### cloud_coverage
**Type**: `int`  
**Required**: No  
**Default**: `25`  
**Range**: 0-100

Maximum cloud coverage percentage. Only applicable to optical satellites.

```python
cloud_coverage=20  # Maximum 20% clouds
cloud_coverage=10  # Very clear scenes only
cloud_coverage=50  # More relaxed (more images available)
```

**Applicable to**: S2MPC, S2E84, LANDSATMPC, HLS_LANDSAT, HLS_SENTINEL  
**Ignored by**: S1MPC (SAR), CopDEM30MPC (no clouds)

### tile
**Type**: `str`  
**Required**: Only if `search_method='tile'`  
**Format**: MGRS tile ID (e.g., `'33UUB'`)

MGRS tile identifier for tile-based search.

```python
tile='33UUB'     # Copenhagen area
tile='30UXC'     # London area
search_method='tile'  # Must use tile search method
```

**Applicable to**: S2MPC, S2E84, CopDEM30MPC  
**Not supported by**: S1MPC, LANDSATMPC, HLS satellites

## Processing Options

### sort
**Type**: `bool`  
**Required**: No  
**Default**: `True`

Sort results by acquisition date (oldest first).

```python
sort=True   # Sort chronologically (recommended)
sort=False  # Return in API order
```

### clip_method
**Type**: `str`  
**Required**: No  
**Default**: `'geometry'`  
**Options**: `'geometry'`, `'window'`

How to clip the output image.

```python
clip_method='geometry'  # Clip exactly to geometry shape (default)
clip_method='window'    # Clip to bounding box rectangle
```

**geometry**: Precise clipping to polygon/geometry shape. Slightly slower but exact.  
**window**: Fast rectangular clipping. Good for large batch processing.

### pixels
**Type**: `int`  
**Required**: No  
**Default**: `256`

Pixel dimensions when using `clip_method='window'`. Output will be `pixels × pixels`.

```python
pixels=256   # 256x256 output
pixels=512   # 512x512 output (higher resolution)
```

Only relevant when `clip_method='window'`.

### groupby
**Type**: `str` or `None`  
**Required**: No  
**Default**: `'solar_day'`  
**Options**: `'solar_day'`, `None`

How to group overlapping satellite tiles from the same acquisition.

```python
groupby='solar_day'  # Merge tiles from same day (recommended)
groupby=None         # Keep separate (may result in 4D arrays)
```

**Recommendation**: Leave as `'solar_day'` to automatically merge overlapping tiles.

## Data Type Options

### dtype
**Type**: `str` or `np.dtype`  
**Required**: No  
**Default**: Satellite-specific

Output data type for the array.

```python
dtype='uint16'  # Unsigned 16-bit integer (Sentinel-2, Landsat)
dtype='float32' # 32-bit float (Sentinel-1, CopDEM)
```

**Defaults:**
- S2MPC/S2E84: `'uint16'`
- S1MPC: `'float32'`
- LANDSATMPC: `'uint16'`
- HLS: `'int16'`
- CopDEM30MPC: `'float32'`

Usually best to leave as default unless you have specific requirements.

### fill_value
**Type**: `int` or `float`  
**Required**: No  
**Default**: Satellite-specific

Value used for nodata/missing pixels.

```python
fill_value=0       # Use 0 for nodata
fill_value=-9999   # Common nodata value
```

**Defaults:**
- S2MPC/S2E84: `0`
- S1MPC: `-32768`
- LANDSATMPC: `0`
- HLS: `-9999`
- CopDEM30MPC: `-32767`

## Complete Example

```python
from sat_data_acquisition import ProcessingParams

# Comprehensive configuration
params = ProcessingParams(
    # Core parameters
    satellite='S2MPC',
    search_method='geometry',
    start_date='2024-06-01',
    end_date='2024-08-31',
    
    # Band selection
    bands=['red', 'green', 'blue', 'nir', 'scl'],
    
    # Filtering
    cloud_coverage=15,
    sort=True,
    
    # Processing
    clip_method='geometry',
    pixels=256,
    groupby='solar_day',
    
    # Optional data type
    dtype='uint16',
    fill_value=0,
)
```

## Validation

All parameters are validated when creating `ProcessingParams`:

```python
# This will raise ValueError - invalid satellite
params = ProcessingParams(
    satellite='INVALID',
    search_method='geometry',
)

# This will raise ValueError - tile search not supported for S1
params = ProcessingParams(
    satellite='S1MPC',
    search_method='tile',  # Error!
)

# This will raise ValueError - missing required bands
params = ProcessingParams(
    satellite='S2MPC',
    bands=['invalid_band'],
)
```

## See Also

- [SATELLITE_SOURCES.md](SATELLITE_SOURCES.md) - All available satellites and bands
- [SAVE_PARAMETERS.md](SAVE_PARAMETERS.md) - Output and storage options
- [Examples](../examples/) - Working code examples
