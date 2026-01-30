from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class SatDataSettings(BaseSettings):
    """SatData configuration settings for public satellite data sources."""

    # API endpoints
    e84_api: str = "https://earth-search.aws.element84.com/v1"
    mpc_api: str = "https://planetarycomputer.microsoft.com/api/stac/v1"

    # Collection names
    s1_collection: str = "sentinel-1-rtc"
    s2_collection: str = "sentinel-2-l2a"
    landsat_collection: str = "landsat-c2-l2"
    hls_landsat_collection: str = "hls2-l30"
    hls_sentinel_collection: str = "hls2-s30"
    copdem30_collection: str = "cop-dem-glo-30"

    # Paths
    log_path: Path = Path("data/log")
    output_path: Path = Path("data/images")
    s3_bucket: str | None = None
    s3_path: str = "sat_data_acquisition"

    # Band mappings for Sentinel-2
    s2_band_mapping: dict = {
        "coastal": "B01",
        "blue": "B02",
        "green": "B03",
        "red": "B04",
        "rededge1": "B05",
        "rededge2": "B06",
        "rededge3": "B07",
        "nir": "B08",
        "nir08": "B8A",
        "nir09": "B09",
        "cirrus": "B10",
        "swir16": "B11",
        "swir22": "B12",
        "scl": "SCL",
    }
    band_mapping_s2mpc: dict[str, str] = {
        **{k: k for k in s2_band_mapping.keys()},  # Identity mapping for common names
        **{v: v for v in s2_band_mapping.values()},  # Identity mapping for native names
    }
    band_mapping_s2e84: dict[str, str] = {
        **{k: k for k in s2_band_mapping.keys()},  # Identity mapping for common names
        **{v: v for v in s2_band_mapping.values()},  # Identity mapping for native names
    }

    # Resolution mappings (in meters)
    resolution_mapping: dict = {
        "S2MPC": 10,
        "S2E84": 10,
        "S1MPC": 10,
        "LANDSATMPC": 30,
        "HLS_LANDSAT": 30,
        "HLS_SENTINEL": 30,
        "CopDEM30MPC": 30,
    }

    # Data type and nodata value mappings
    dtype_dict: dict = {
        "S2MPC": ("uint16", 0),
        "S2E84": ("uint16", 0),
        "S1MPC": ("float32", -32768),
        "LANDSATMPC": ("uint16", 0),
        "HLS_LANDSAT": ("int16", -9999),
        "HLS_SENTINEL": ("int16", -9999),
        "CopDEM30MPC": ("float32", -32767),
    }

    # Default bands for each satellite
    default_bands: dict = {
        "S2MPC": ["B02", "B03", "B04", "B08"],
        "S2E84": ["blue", "green", "red", "nir"],
        "S1MPC": ["VV", "VH"],
        "LANDSATMPC": ["red", "green", "blue", "nir08"],
        "HLS_LANDSAT": ["B04", "B03", "B02", "B05"],
        "HLS_SENTINEL": ["B04", "B03", "B02", "B08"],
        "CopDEM30MPC": ["data"],
    }

    # Valid bands per satellite
    valid_bands_landsat: set = {
        "coastal",
        "blue",
        "green",
        "red",
        "nir08",
        "swir16",
        "swir22",
        "lwir11",
        "qa_pixel",
    }

    valid_bands_hls: set = {
        "coastal",
        "blue",
        "green",
        "red",
        "rededge1",
        "rededge2",
        "rededge3",
        "nir_broad",
        "nir_narrow",
        "swir1",
        "swir2",
        "water_vapor",
        "cirrus",
        "thermal1",
        "thermal2",
        "qa",
        # Keep numeric band names for backward compatibility
        "B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A",
        "B09", "B10", "B11", "B12", "QA",
    }

    valid_bands_copdem30: set = {"data"}

    # Satellite capabilities (cloud coverage filtering, tile-based search)
    satellite_configs: dict = {
        "LANDSATMPC": {"cloud_coverage": True, "tile": False},
        "S2MPC": {"cloud_coverage": True, "tile": True},
        "S2E84": {"cloud_coverage": True, "tile": True},
        "S1MPC": {"cloud_coverage": False, "tile": False},
        "HLS_LANDSAT": {"cloud_coverage": True, "tile": False},
        "HLS_SENTINEL": {"cloud_coverage": True, "tile": False},
        "CopDEM30MPC": {"cloud_coverage": True, "tile": True},
    }

    # Provider mapping
    provider_mapping: dict = {
        "S1MPC": "MPC",
        "S2MPC": "MPC",
        "LANDSATMPC": "MPC",
        "S2E84": "E84",
        "HLS_LANDSAT": "MPC",
        "HLS_SENTINEL": "MPC",
        "CopDEM30MPC": "MPC",
    }

    # Configure to read environment variables with the prefix "SAT_DATA_"
    model_config = SettingsConfigDict(
        env_prefix="SAT_DATA_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings(**kwargs):
    """Get satellite data acquisition settings singleton."""
    return SatDataSettings(**kwargs)
