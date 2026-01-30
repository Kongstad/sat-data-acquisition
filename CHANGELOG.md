# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.9.0] - 2026-01-30

### Added
- Initial stable release of sat-data-acquisition package
- Multi-satellite support: Sentinel-2 (MPC, E84), Sentinel-1, Landsat 8/9, HLS, Copernicus DEM
- STAC-native architecture for efficient satellite data retrieval
- Flexible search methods: geometry-based and identifier-based
- Multiple save formats: GeoTIFF (georeferenced) and NumPy (raw arrays)
- Storage options: local disk and AWS S3
- Band merging options: single multi-band file or separate files per band
- Cloud filtering with configurable thresholds
- Pydantic models for type-safe parameter validation
- Comprehensive test suite (53 tests, 68% coverage)
- GitHub Actions CI/CD pipeline
- Extensive documentation:
  - SATELLITE_SOURCES.md - Band specifications and use cases
  - PROCESSING_PARAMETERS.md - Search and filtering configuration
  - SAVE_PARAMETERS.md - Storage and output configuration
  - ARCHITECTURE.md - System design and data flow
- 12 Jupyter notebooks with working examples
- 6 Python example scripts demonstrating common workflows

### Features by Satellite
- **Sentinel-2 (S2MPC, S2E84)**: 10-60m resolution, RGB/NIR/SWIR bands, 5-day revisit
- **Sentinel-1 (S1MPC)**: 10m resolution, SAR (VV/VH), all-weather monitoring
- **Landsat 8/9 (LANDSATMPC)**: 30m resolution, multispectral + thermal bands
- **HLS Sentinel/Landsat**: 30m harmonized data for seamless time-series
- **Copernicus DEM (CopDEM30MPC)**: 30m elevation data

### Technical Implementation
- Python 3.12+ with UV package manager support
- Type hints throughout codebase
- Professional error handling and logging
- Automatic retry logic for network operations
- Configurable compression for GeoTIFF files
- Custom naming patterns for saved files
- Multi-temporal dataset support with xarray

### Quality Assurance
- Comprehensive test coverage with pytest
- Static type checking with mypy
- Code quality enforcement with ruff and flake8
- Automated CI/CD with GitHub Actions
- Professional documentation and examples

### API Highlights
```python
# Simple, clean API
from sat_data_acquisition import SatDataClient, ProcessingParams, SaveParams

client = SatDataClient()
params = ProcessingParams(
    satellite='S2MPC',
    bands=['red', 'green', 'blue'],
    start_date='2024-06-01',
    end_date='2024-08-31',
)
dataset = client.search_and_create_image(geometry, params)
```

## [0.2.0] - 2025-12-15 (Pre-release)

### Added
- SaveParams refactoring for cleaner save interface
- Support for both GeoTIFF and NumPy formats
- S3 storage integration
- Custom naming patterns

### Changed
- Simplified save API from 15+ parameters to SaveParams object
- Improved error handling and logging

## [0.1.0] - 2025-10-01 (Initial Development)

### Added
- Basic satellite data download functionality
- Sentinel-2 and Landsat support
- Simple geometry-based search
- Local file storage

[Unreleased]: https://github.com/Kongstad/sat-data-acquisition/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Kongstad/sat-data-acquisition/releases/tag/v1.0.0
[0.2.0]: https://github.com/Kongstad/sat-data-acquisition/releases/tag/v0.2.0
[0.1.0]: https://github.com/Kongstad/sat-data-acquisition/releases/tag/v0.1.0
