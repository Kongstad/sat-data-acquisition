"""
Unit tests for configuration and settings.

Author: Peter Kongstad
"""

from sat_data_acquisition.config.logging import configure_logging, get_logger
from sat_data_acquisition.config.settings import SatDataSettings


class TestSatDataSettings:
    """Test configuration settings."""

    def test_default_settings(self, settings):
        """Test default settings are loaded correctly."""
        assert str(settings.e84_api) == "https://earth-search.aws.element84.com/v1"
        assert str(settings.mpc_api) == "https://planetarycomputer.microsoft.com/api/stac/v1"
        assert settings.s3_path == "sat_data_acquisition"

    def test_band_mappings_exist(self, settings):
        """Test that band mappings are defined."""
        assert hasattr(settings, "band_mapping_s2mpc")
        assert hasattr(settings, "band_mapping_s2e84")
        assert len(settings.band_mapping_s2mpc) > 0
        assert len(settings.band_mapping_s2e84) > 0

    def test_resolution_mappings_exist(self, settings):
        """Test that resolution mappings are defined."""
        assert hasattr(settings, "resolution_mapping")
        assert len(settings.resolution_mapping) > 0
        assert 10 in settings.resolution_mapping.values()

    def test_s3_configuration(self):
        """Test S3 configuration options."""
        settings = SatDataSettings(s3_bucket="test-bucket", s3_path="test/path")
        assert settings.s3_bucket == "test-bucket"
        assert settings.s3_path == "test/path"


class TestLogging:
    """Test logging configuration."""

    def test_configure_logging_verbose(self):
        """Test verbose logging configuration."""
        configure_logging(verbose=True)
        logger = get_logger("test")
        assert logger is not None

    def test_configure_logging_quiet(self):
        """Test quiet logging configuration."""
        configure_logging(verbose=False)
        logger = get_logger("test")
        assert logger is not None

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a valid logger."""
        logger = get_logger("test_module")
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
