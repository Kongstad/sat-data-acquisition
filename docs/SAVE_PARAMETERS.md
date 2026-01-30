# Save Parameters

Complete reference for `SaveParams` configuration options for saving and storing satellite imagery.

## Overview

`SaveParams` controls how processed satellite images are saved to disk and/or cloud storage.

```python
from sat_data_acquisition import SaveParams

save_params = SaveParams(
    output_path='./data/images',
    save_to_local=True,
    file_format='geotiff',
    enable_compression=True,
)
```

## Storage Destination

### save_to_local
**Type**: `bool`  
**Required**: No  
**Default**: `True`

Save files to local disk.

```python
save_to_local=True   # Save to local filesystem
save_to_local=False  # Don't save locally (S3 only)
```

### save_to_s3
**Type**: `bool`  
**Required**: No  
**Default**: `False`

Upload files to AWS S3.

```python
save_to_s3=True   # Upload to S3
save_to_s3=False  # Local only
```

**Storage Options:**
- **Local only**: `save_to_local=True`, `save_to_s3=False`
- **S3 only**: `save_to_local=False`, `save_to_s3=True` (temp files cleaned up)
- **Both**: `save_to_local=True`, `save_to_s3=True` (redundancy)

## Local Storage

### output_path
**Type**: `str` or `Path`  
**Required**: Yes  
**Default**: `'data/images'`

Base directory for saving files locally.

```python
output_path='./data/images'
output_path='/mnt/satellite_data'
output_path='~/projects/imagery'
```

Files are organized automatically:
```
output_path/
├── S2MPC/
│   └── 2024/
│       └── tiff/
│           └── S2MPC_2024-06-15_red_green_blue_copenhagen.tif
├── S2E84/
│   └── 2024/
│       └── tiff/
└── LANDSATMPC/
    └── 2024/
        └── tiff/
```

### identifier_type
**Type**: `str`  
**Required**: No  
**Default**: `'area_name'`  
**Options**: `'area_name'`, `'field_id'`, `'custom'`

How to name output files.

```python
identifier_type='area_name'  # Use area name in filename
identifier_type='field_id'   # Use field ID
identifier_type='custom'     # Custom identifier
```

Example filenames:
- `area_name`: `S2MPC_2024-06-15_red_green_blue_copenhagen.tif`
- `field_id`: `S2MPC_2024-06-15_red_green_blue_field_12345.tif`
- `custom`: `S2MPC_2024-06-15_red_green_blue_my_custom_id.tif`

## AWS S3 Storage

### s3_bucket
**Type**: `str`  
**Required**: If `save_to_s3=True`  
**Default**: `None`

AWS S3 bucket name.

```python
s3_bucket='my-satellite-data'
s3_bucket='company-earth-observation'
```

**Note**: Bucket must exist and you must have write permissions.

### s3_path
**Type**: `str`  
**Required**: No  
**Default**: `'sat_data_acquisition'`

Prefix path within S3 bucket.

```python
s3_path='sat_data_acquisition'        # Default
s3_path='projects/my_project'         # Project-specific
s3_path='users/john/copenhagen'       # User-specific
```

Full S3 path structure:
```
s3://bucket/s3_path/satellite/year/format/filename
s3://my-data/projects/demo/S2MPC/2024/tiff/S2MPC_2024-06-15_red_green_blue_copenhagen.tif
```

### AWS Credentials

The package uses standard AWS credential chain:

1. **Environment variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_DEFAULT_REGION=us-east-1
   ```

2. **AWS credentials file** (`~/.aws/credentials`):
   ```ini
   [default]
   aws_access_key_id = your_key
   aws_secret_access_key = your_secret
   region = us-east-1
   ```

3. **IAM role** (if running on EC2/ECS/Lambda)

## File Format

### file_format
**Type**: `str`  
**Required**: No  
**Default**: `'geotiff'`  
**Options**: `'geotiff'`, `'numpy'`

Output file format.

```python
file_format='geotiff'  # GeoTIFF format (georeferenced)
file_format='numpy'    # NumPy array (.npy)
```

**GeoTIFF** (recommended):
- Georeferenced (includes CRS and coordinates)
- Readable by QGIS, ArcGIS, GDAL
- Industry standard for satellite imagery
- Larger file size

**NumPy**:
- Plain array data (no georeferencing)
- Smaller file size
- Faster to read/write
- Good for ML pipelines where georeferencing not needed

## Compression

### enable_compression
**Type**: `bool`  
**Required**: No  
**Default**: `True`

Enable GeoTIFF compression (LZW algorithm).

```python
enable_compression=True   # Compress files (recommended)
enable_compression=False  # No compression (faster but larger)
```

**Impact:**
- Compression: ~30-60% smaller files, slightly slower write
- No compression: Faster writes, much larger files

**Recommendation**: Leave enabled unless you need maximum write speed.

### merge_bands
**Type**: `bool`  
**Required**: No  
**Default**: `True`

Merge all bands into single multi-band file vs. separate files per band.

```python
merge_bands=True   # Single file with multiple bands (recommended)
merge_bands=False  # Separate file per band
```

**Single file** (merge_bands=True):
```
S2MPC_2024-06-15_red_green_blue_nir_copenhagen.tif
```

**Separate files** (merge_bands=False):
```
S2MPC_2024-06-15_red_copenhagen.tif
S2MPC_2024-06-15_green_copenhagen.tif
S2MPC_2024-06-15_blue_copenhagen.tif
S2MPC_2024-06-15_nir_copenhagen.tif
```

## Naming

### custom_naming
**Type**: `str` or `None`  
**Required**: No  
**Default**: `None`

Custom naming pattern for output files.

```python
custom_naming='{satellite}_{date}_{identifier}.tif'
custom_naming='project_{identifier}_{date}.tif'
```

Available placeholders:
- `{satellite}`: Satellite name (S2MPC, S2E84, etc.)
- `{date}`: Acquisition date (YYYY-MM-DD)
- `{identifier}`: Area name or field ID
- `{bands}`: Band names joined with underscores
- `{provider}`: Provider name (MPC, E84)

**Default naming** (if `custom_naming=None`):
```
{satellite}_{date}_{bands}_{identifier}.tif
```

## Examples

### Example 1: Local Storage Only

Simple local storage with defaults:

```python
from sat_data_acquisition import SaveParams

save_params = SaveParams(
    output_path='./data/images',
    save_to_local=True,
    save_to_s3=False,
    file_format='geotiff',
    enable_compression=True,
)
```

### Example 2: S3 Storage Only

Cloud-only storage with automatic local cleanup:

```python
save_params = SaveParams(
    output_path='./temp',  # Temp dir, files deleted after S3 upload
    save_to_local=False,
    save_to_s3=True,
    s3_bucket='my-satellite-data',
    s3_path='projects/monitoring',
    file_format='geotiff',
    enable_compression=True,
)
```

### Example 3: Both Local and S3

Redundant storage for safety:

```python
save_params = SaveParams(
    output_path='/mnt/archive',
    save_to_local=True,
    save_to_s3=True,
    s3_bucket='backup-satellite-data',
    s3_path='archive/2024',
    file_format='geotiff',
    enable_compression=True,
)
```

### Example 4: NumPy Format for ML

Lightweight NumPy arrays for machine learning:

```python
save_params = SaveParams(
    output_path='./training_data',
    save_to_local=True,
    file_format='numpy',  # .npy format
    merge_bands=True,
    enable_compression=False,  # Not applicable to numpy
    identifier_type='field_id',
)
```

### Example 5: Custom Naming

Custom file naming pattern:

```python
save_params = SaveParams(
    output_path='./data',
    custom_naming='project_{identifier}_{satellite}_{date}.tif',
    # Results in: project_copenhagen_S2MPC_2024-06-15.tif
)
```

## Complete Configuration

```python
from sat_data_acquisition import SaveParams

save_params = SaveParams(
    # Storage destinations
    save_to_local=True,
    save_to_s3=True,
    
    # Local paths
    output_path='./data/satellite_images',
    
    # S3 configuration
    s3_bucket='my-satellite-bucket',
    s3_path='projects/agriculture/2024',
    
    # File format
    file_format='geotiff',
    enable_compression=True,
    merge_bands=True,
    
    # Naming
    identifier_type='area_name',
    custom_naming=None,  # Use default naming
)
```

## Usage in Code

### With SatDataClient

```python
from sat_data_acquisition import SatDataClient, ProcessingParams, SaveParams
from sat_data_acquisition.processing import save_geotiff

client = SatDataClient()

processing_params = ProcessingParams(
    satellite='S2MPC',
    bands=['red', 'green', 'blue'],
    # ... other params
)

save_params = SaveParams(
    output_path='./data',
    save_to_local=True,
)

# Get imagery
dataset = client.search_and_create_image(
    geometry=geometry,
    processing_params=processing_params,
)

# Save
for idx, time_val in enumerate(dataset.time.values):
    image_slice = dataset.sel(time=time_val)
    date_str = str(time_val)[:10]
    
    save_geotiff(
        image=image_slice,
        identifier='copenhagen',
        datetime=date_str,
        satellite='S2MPC',
        provider='MPC',
        output_path=save_params.output_path,
        save_to_local=save_params.save_to_local,
        identifier_type=save_params.identifier_type,
        enable_compression=save_params.enable_compression,
        # ... other save_params attributes
    )
```

## File Size Considerations

Typical file sizes (10m resolution, 1024x1024 pixels, 4 bands):

| Configuration | Size | Notes |
|---------------|------|-------|
| GeoTIFF, compressed | ~8-15 MB | Recommended |
| GeoTIFF, uncompressed | ~35-40 MB | Fast writes |
| NumPy, compressed | ~4-6 MB | No georef |
| NumPy, uncompressed | ~16 MB | Fastest |

## Troubleshooting

### S3 Upload Fails

```python
# Check AWS credentials
import boto3
s3 = boto3.client('s3')
s3.list_buckets()  # Should not error
```

### Permission Errors

```bash
# Check bucket permissions
aws s3 ls s3://my-bucket/

# Grant write access
aws s3api put-bucket-acl --bucket my-bucket --acl private
```

### Large File Sizes

```python
# Enable compression
save_params = SaveParams(
    enable_compression=True,  # Can save 50-70% space
)

# Use NumPy format if georeferencing not needed
save_params = SaveParams(
    file_format='numpy',  # Smaller than GeoTIFF
)
```

## See Also

- [PROCESSING_PARAMETERS.md](PROCESSING_PARAMETERS.md) - Data retrieval parameters
- [SATELLITE_SOURCES.md](SATELLITE_SOURCES.md) - Available satellites and bands
- [Examples](../examples/) - Working code examples
