"""
Tests for processing operations.

Author: Peter Kongstad
"""

from sat_data_acquisition.processing.utils import get_native_band_name


class TestBandMapping:
    """Tests for band name mapping."""

    def test_get_native_band_name(self, settings):
        """Test getting native band names."""
        band_name = get_native_band_name("red", "S2E84", settings)
        assert band_name is not None
        assert isinstance(band_name, str)

    def test_band_name_passthrough(self, settings):
        """Test that band names are returned."""
        band_name = get_native_band_name("custom_band", "S2E84", settings)
        assert band_name == "custom_band"


class TestSaveOperations:
    """Tests for save parameters."""

    def test_save_params_fixture(self, save_params):
        """Test that save_params fixture is properly configured."""
        assert save_params.save_to_local is True
        assert save_params.save_to_s3 is False
        assert save_params.save_as_geotiff is True
