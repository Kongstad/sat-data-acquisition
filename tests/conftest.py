"""
Pytest configuration and fixtures.

Author: Peter Kongstad
"""

import pytest
from shapely.geometry import Point, box

from sat_data_acquisition.config.settings import SatDataSettings
from sat_data_acquisition.models.params import ProcessingParams, SaveParams


@pytest.fixture
def settings():
    """Provide SatDataSettings instance."""
    return SatDataSettings()


@pytest.fixture
def test_geometry():
    """Provide a simple test geometry (Copenhagen area)."""
    copenhagen = Point(12.5683, 55.6761)
    return copenhagen.buffer(0.01)  # ~1km buffer


@pytest.fixture
def test_bbox():
    """Provide a bounding box geometry."""
    return box(12.5, 55.6, 12.6, 55.7)


@pytest.fixture
def processing_params():
    """Provide standard processing parameters for testing."""
    return ProcessingParams(
        satellite="S2E84",
        search_method="geometry",
        bands=["red", "green", "blue"],
        start_date="2024-06-01",
        end_date="2024-06-30",
        cloud_coverage=30,
    )


@pytest.fixture
def save_params(tmp_path):
    """Provide save parameters using temporary directory."""
    return SaveParams(
        output_path=str(tmp_path),
        save_to_local=True,
        save_to_s3=False,
        save_as_geotiff=True,
        enable_compression=False,
        verbose=False,
    )


@pytest.fixture
def mock_image_data():
    """Provide mock image data structure."""
    import numpy as np
    import xarray as xr

    # Create simple mock imagery
    data = np.random.rand(3, 100, 100).astype(np.float32)
    coords = {
        "band": [1, 2, 3],
        "y": range(100),
        "x": range(100),
    }

    image = xr.DataArray(
        data,
        coords=coords,
        dims=["band", "y", "x"],
        attrs={"datetime": "2024-06-15", "satellite": "S2E84"},
    )

    return {
        "image": image,
        "datetime": "2024-06-15",
        "satellite": "S2E84",
        "provider": "E84",
    }
