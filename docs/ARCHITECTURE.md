# System Architecture

This document describes the high-level architecture of the `sat-data-acquisition` package.

## Data Flow Diagram

The following diagram illustrates how user requests are transformed into analysis-ready satellite data.

```mermaid
flowchart TD
    User([User Request]) --> Params[ProcessingParams]
    Params --> Client[SatDataClient]
    
    subgraph Providers
        Client --> MPC[Planetary Computer]
        Client --> E84[Element84]
    end
    
    MPC --> STAC_API[STAC API Search]
    E84 --> STAC_API
    
    STAC_API --> Loader[odc-stac Loader]
    
    subgraph Processing
        Loader --> XR[xarray Dataset]
        XR --> Clip[Spatial Clipping]
        Clip --> Reproject[UTM Reprojection]
    end
    
    Reproject --> Save[Save Module]
    
    Save --> Local[Local Storage]
    Save --> S3[S3 Upload]
    
    Local --> GeoTIFF1([GeoTIFF])
    Local --> NumPy1([NumPy Array])
    
    S3 --> GeoTIFF2([GeoTIFF])
    S3 --> NumPy2([NumPy Array])
```

## Core Components

1.  **SatDataClient**: The primary entry point that abstracts provider selection and search logic.
2.  **ProcessingParams**: A validated configuration model ensuring type-safe search and retrieval.
3.  **STAC Providers**: Modular adapters for different STAC catalogs (Microsoft Planetary Computer, Element84).
4.  **odc-stac Engine**: Handles the high-performance loading of Cloud-Optimized GeoTIFFs (COGs).
5.  **xarray Dataset**: The primary in-memory format, providing multi-dimensional, labeled arrays.

## Project Structure

```text
sat-data-acquisition/
├── sat_data_acquisition/          # Main package
│   ├── core/                      # STAC client, iterators
│   ├── providers/                 # Element84, MPC adapters
│   ├── models/                    # Pydantic models (ProcessingParams, etc.)
│   ├── processing/                # Image processing (Clipping, Reprojection), saving
│   ├── config/                    # Settings, logging
│   └── utils/                     # Helpers, exceptions, coordinate conversion
├── examples/                      # Jupyter notebooks and scripts by satellite
├── docs/                          # Comprehensive documentation (Architecture, Sources, Parameters)
├── tests/                         # Full test suite (Unit and Integration)
└── data/                          # Local data storage
    ├── geojson/                   # Area of Interest (AOI) definitions
    └── images/                    # Downloaded satellite imagery
```

## STAC-Native Philosophy

Unlike legacy systems that download entire scenes, this architecture is **STAC-native**. It queries metadata first and leverages lazy-loading to stream only the specific pixels required for the requested geometry, significantly reducing bandwidth and local storage requirements.
