"""
Tests for utility functions.

Author: Peter Kongstad
"""

import pytest
from shapely.geometry import Point, box

from sat_data_acquisition.utils.coordinate_converter import (
    geometry_from_epsg_to_epsg,
    get_transformer,
    get_utm_epsg,
)
from sat_data_acquisition.utils.exceptions import (
    ConfigurationError,
    ImageCreationError,
    SatDataError,
    STACSearchError,
)


class TestCoordinateConverter:
    """Tests for coordinate conversion functions."""

    def test_get_transformer(self):
        """Test getting CRS transformer."""
        transformer = get_transformer(4326, 32632)
        assert transformer is not None

    def test_geometry_conversion(self):
        """Test converting geometry between CRS."""
        point = Point(12.5, 55.6)  # Copenhagen in WGS84
        converted = geometry_from_epsg_to_epsg(point, 4326, 32632)

        assert converted.geom_type == "Point"
        assert converted.x != point.x

    def test_polygon_conversion(self):
        """Test converting polygon geometry."""
        polygon = box(12.5, 55.6, 12.6, 55.7)
        converted = geometry_from_epsg_to_epsg(polygon, 4326, 32632)

        assert converted.geom_type == "Polygon"

    def test_get_utm_epsg(self):
        """Test getting UTM EPSG code from coordinates."""
        epsg = get_utm_epsg(12.5, 55.6)
        # Copenhagen is in zone 32 or 33 depending on exact calculation
        assert 32632 <= epsg <= 32633


class TestExceptions:
    """Tests for custom exceptions."""

    def test_sat_data_acquisition_error_base(self):
        """Test base SatDataError exception."""
        with pytest.raises(SatDataError):
            raise SatDataError("Test error")

    def test_exception_hierarchy(self):
        """Test that all exceptions inherit from SatDataError."""
        assert issubclass(ConfigurationError, SatDataError)
        assert issubclass(STACSearchError, SatDataError)
        assert issubclass(ImageCreationError, SatDataError)
