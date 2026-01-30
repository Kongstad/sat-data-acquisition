"""
Satellite Data Acquisition - Lightweight Satellite Data Retrieval

Pragmatic tool for downloading and processing satellite imagery from multiple
public STAC catalogs including Sentinel-2, Sentinel-1, Landsat, and elevation data.
"""

from sat_data_acquisition.__version__ import __version__
from sat_data_acquisition.config.logging import configure_logging, get_logger
from sat_data_acquisition.core.stac_client import SatDataClient
from sat_data_acquisition.models.params import ProcessingParams, SaveParams
from sat_data_acquisition.processing import process_batch

__all__ = [
    "__version__",
    "SatDataClient",
    "ProcessingParams",
    "SaveParams",
    "process_batch",
    "configure_logging",
    "get_logger",
]
