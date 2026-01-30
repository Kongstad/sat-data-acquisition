"""Provider iterators for different satellite data sources."""

from sat_data_acquisition.providers.element84 import S2E84Iterator
from sat_data_acquisition.providers.mpc import (
    CopDEM30Iterator,
    HLSLandsatIterator,
    HLSSentinelIterator,
    LandsatMPCIterator,
    Sentinel1MPCIterator,
    Sentinel2MPCIterator,
)

# Provider registry mapping satellite names to iterator classes
PROVIDER_REGISTRY = {
    "S2E84": S2E84Iterator,
    "S2MPC": Sentinel2MPCIterator,
    "S1MPC": Sentinel1MPCIterator,
    "LANDSATMPC": LandsatMPCIterator,
    "HLS_LANDSAT": HLSLandsatIterator,
    "HLS_SENTINEL": HLSSentinelIterator,
    "CopDEM30MPC": CopDEM30Iterator,
}

__all__ = [
    "S2E84Iterator",
    "Sentinel2MPCIterator",
    "Sentinel1MPCIterator",
    "LandsatMPCIterator",
    "HLSLandsatIterator",
    "HLSSentinelIterator",
    "CopDEM30Iterator",
    "PROVIDER_REGISTRY",
]
