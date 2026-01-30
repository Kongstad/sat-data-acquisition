import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class TypeUtils:
    @staticmethod
    def ensure_string(value: Any) -> str:
        """
        Ensure the given value is a string.

        Args:
            value: The value to convert.

        Returns:
            str: The converted string value.
        """
        if isinstance(value, float) and np.isnan(value):
            logger.warning(f"Encountered NaN value: {value}")
            return "nan"
        if not isinstance(value, str):
            logger.warning(f"Converted {value} to string")
            return str(value)
        return value


def get_native_band_name(band: str, satellite: str, settings: Any) -> str:
    """
    Get the native band name for a given satellite.

    Args:
        band: The band name.
        satellite: The satellite name.
        settings: Settings object.

    Returns:
        str: The native band name.
    """
    if satellite == "S2E84":
        native: str = settings.band_mapping_s2mpc.get(
            settings.band_mapping_s2e84.get(band, band), band
        )
        return native
    return band
