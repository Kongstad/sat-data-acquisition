# Satellite Data Acquisition

Python package for downloading satellite imagery from multiple sources with a unified API.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **Multiple satellites**: Sentinel-2, Sentinel-1, Landsat 8/9, HLS (Harmonized Landsat Sentinel), Copernicus DEM
- **Flexible data providers**: Element84, Microsoft Planetary Computer
- **Smart search**: By coordinates or area identifier from GeoJSON
- **Multi-temporal support**: Download imagery across time ranges
- **Cloud filtering**: Configurable cloud coverage thresholds
- **Storage options**: Save to local disk or AWS S3
- **Type-safe API**: Pydantic models for all parameters
- **Production ready**: Automatic retries, comprehensive logging

## Quick Start

### Installation

**With UV (recommended - 10-100x faster):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv && source .venv/bin/activate
uv pip install -e .
```

**With pip:**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### Basic Usage

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

# Download
client = SatDataClient()
dataset = client.search_and_create_image(
    geometry=geometry,
    processing_params=processing_params,
)

print(f"Downloaded {len(dataset.time)} images")
# Image shape: {'time': 12, 'y': 344, 'x': 291}
```

### Visualization

```python
import matplotlib.org/matplotlib.pyplot as plt
import numpy as np

# Get first image
image = dataset.isel(time=0)
rgb = np.dstack([image['red'], image['green'], image['blue']])

# Display
plt.imshow(rgb / 3000)
plt.title(f"Sentinel-2 - {str(image.time.values)[:10]}")
plt.show()
```

### Save to Disk

```python
from sat_data_acquisition.processing import save_geotiff

for time_val in dataset.time.values:
    save_geotiff(
        image=dataset.sel(time=time_val),
        identifier='copenhagen',
        datetime=str(time_val)[:10],
        satellite='S2MPC',
        provider='MPC',
        output_path='./data/images',
        save_to_local=True,
        identifier_type='area_name',
        enable_compression=True,
    )
```

## Available Satellites

| Satellite | Bands | Resolution | Revisit | Provider |
|-----------|-------|------------|---------|----------|
| Sentinel-2 | RGB, NIR, SWIR, SCL | 10-60m | 5 days | MPC, E84 |
| Sentinel-1 | VV, VH (SAR) | 10m | 12 days | MPC |
| Landsat 8/9 | RGB, NIR, SWIR, Thermal | 30m | 16 days | MPC |
| HLS Sentinel | B01-B12 (harmonized) | 30m | 5 days | MPC |
| HLS Landsat | B01-B12 (harmonized) | 30m | 16 days | MPC |
| Copernicus DEM | Elevation | 30m | Static | MPC |

**Note**: HLS (Harmonized Landsat Sentinel) provides radiometrically harmonized data from Landsat 8/9 and Sentinel-2, enabling seamless time-series analysis with ~3 day combined revisit frequency.

## Documentation

**Comprehensive guides in [docs/](docs/)**

- **[SATELLITE_SOURCES.md](docs/SATELLITE_SOURCES.md)** - All satellites, bands, wavelengths, resolutions, and use cases
- **[PROCESSING_PARAMETERS.md](docs/PROCESSING_PARAMETERS.md)** - Complete search and processing configuration
- **[SAVE_PARAMETERS.md](docs/SAVE_PARAMETERS.md)** - Local and S3 storage configuration

**Working examples in [examples/](examples/)**

- [S2MPC](examples/s2mpc/) - Sentinel-2 (Microsoft Planetary Computer)
- [S2E84](examples/s2e84/) - Sentinel-2 (Element84)
- [S1MPC](examples/s1mpc/) - Sentinel-1 SAR
- [LandsatMPC](examples/landsatmpc/) - Landsat 8/9
- [HLSMPC](examples/hlsmpc/) - HLS (Harmonized Landsat Sentinel)
- [CopDEM](examples/cop30dem/) - Copernicus DEM

Each example includes single image and multi-image notebooks with visualization.

## Project Structure

📖 **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - High-level system design and data flow

```
sat-data-acquisition/
├── sat_data_acquisition/          # Main package
│   ├── core/                      # STAC client, iterators
│   ├── providers/                 # Element84, MPC adapters
│   ├── models/                    # Pydantic models
│   ├── processing/                # Image processing, saving
│   ├── config/                    # Settings, logging
│   └── utils/                     # Helpers, exceptions
├── examples/                      # Jupyter notebooks by satellite
├── docs/                          # Comprehensive documentation
├── tests/                         # Test suite
└── data/                          # Local data storage
    ├── geojson/                   # Example geometries
    └── images/                    # Downloaded imagery
```

## Common Use Cases

### Temporal Analysis
```python
# Download monthly imagery for entire growing season
processing_params = ProcessingParams(
    satellite='S2MPC',
    bands=['red', 'green', 'blue', 'nir'],
    start_date='2024-04-01',
    end_date='2024-10-01',
    cloud_coverage=15,
)

dataset = client.search_and_create_image(geometry, processing_params)
# Returns xarray with time dimension for analysis
```

### Cloud Masking with SCL
```python
# Use Scene Classification Layer for cloud filtering
processing_params = ProcessingParams(
    satellite='S2MPC',
    bands=['red', 'green', 'blue', 'nir', 'scl'],
    cloud_coverage=30,  # Allows more scenes
)

dataset = client.search_and_create_image(geometry, processing_params)

# Mask clouds using SCL band
# See SATELLITE_SOURCES.md for SCL classification values
```

### SAR for All-Weather Monitoring
```python
# Sentinel-1 works through clouds
processing_params = ProcessingParams(
    satellite='S1MPC',
    bands=['vv', 'vh'],  # Polarizations
    start_date='2024-01-01',
    end_date='2024-12-31',
)
```

### Multi-Area Batch Processing
```python
import geopandas as gpd

# Load multiple areas
areas = gpd.read_file('data/geojson/example_areas.geojson')

for idx, area in areas.iterrows():
    geometry = area['geometry'].__geo_interface__
    dataset = client.search_and_create_image(geometry, processing_params)
    # Process and save
```

## Advanced Features

### Provider Selection

Different providers have different characteristics:

```python
# Microsoft Planetary Computer (MPC)
# - Global coverage, always available
# - Authentication token handled automatically
processing_params = ProcessingParams(satellite='S2MPC')

# Element84 (E84)
# - Better for US/Americas
# - Different band scaling
processing_params = ProcessingParams(satellite='S2E84')
```

See [SATELLITE_SOURCES.md](docs/SATELLITE_SOURCES.md) for provider details.

### Overlapping Tile Handling

By default, overlapping satellite passes from the same day are merged:

```python
processing_params = ProcessingParams(
    groupby='solar_day',  # Default: merges same-day tiles
    # groupby=None,       # Keep separate tiles (advanced)
)
```

### S3 Storage

```python
from sat_data_acquisition.processing import save_geotiff

save_geotiff(
    image=image,
    identifier='field_123',
    datetime='2024-06-15',
    satellite='S2MPC',
    provider='MPC',
    output_path='./temp',
    save_to_local=False,  # Don't save locally
    save_to_s3=True,      # Upload to S3
    s3_bucket='my-satellite-data',
    s3_path='projects/monitoring',
)
```

See [SAVE_PARAMETERS.md](docs/SAVE_PARAMETERS.md) for full S3 configuration.

## Development

### Using the Makefile

The project includes a `Makefile` to simplify common development tasks.

**Linting and Type Checking:**
```bash
make lint
```
This runs `ruff`, `flake8`, and `mypy` to ensure code quality and type safety.

**Code Formatting:**
```bash
make format
```
This automatically formats the code using `black` and `isort`.

**Running Tests:**
```bash
# Run all tests
make test

# Run fast tests only (skips slow integration tests)
make test-fast

# Run tests with coverage report
make test-cov
```

**Cleanup:**
```bash
make clean
```
Removes build artifacts, cache files, and temporary test data.

### Manual Testing

You can also run pytest directly:
```bash
pytest tests/
```

### Docker Deployment (Optional)

```bash
# Build image
docker build -t sat-data-acquisition .

# Run container
docker run -v $(pwd)/data:/app/data sat-data-acquisition
```

### Environment Variables

```bash
# AWS credentials for S3 (optional)
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

# Logging level (optional)
export LOG_LEVEL=INFO
```

## Requirements

- Python 3.12+
- UV package manager (recommended) or pip
- Docker (optional, for deployment)

## Contributing

Contributions welcome! This is a portfolio project demonstrating clean code practices:

- Type hints throughout
- Pydantic models for validation
- Comprehensive error handling
- Extensive documentation
- Test coverage

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Element84 for Earth Search STAC API
- Microsoft Planetary Computer for open data access
- ESA for Sentinel satellite programs
- NASA/USGS for Landsat data

## Support

- **Documentation**: See [docs/](docs/) directory
- **Examples**: Check [examples/](examples/) notebooks
- **Issues**: Open an issue on GitHub

## What's Next?

1. **Explore examples**: Open [examples/s2mpc/single_area_download.ipynb](examples/s2mpc/single_area_download.ipynb)
2. **Read documentation**: Start with [SATELLITE_SOURCES.md](docs/SATELLITE_SOURCES.md)
3. **Try your own data**: Modify example GeoJSON in [data/geojson/](data/geojson/)
4. **Customize processing**: See [PROCESSING_PARAMETERS.md](docs/PROCESSING_PARAMETERS.md)

Happy satellite data hunting!
