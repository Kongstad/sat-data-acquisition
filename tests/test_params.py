"""
Tests for parameter models.

Author: Peter Kongstad
"""

from datetime import date

import pytest

from sat_data_acquisition.models.params import ProcessingParams, SaveParams


class TestProcessingParams:
    """Tests for ProcessingParams model."""

    def test_valid_params(self):
        """Test creating ProcessingParams with valid parameters."""
        params = ProcessingParams(
            satellite="S2E84",
            search_method="geometry",
            bands=["red", "green", "blue"],
            start_date="2024-01-01",
            end_date="2024-01-31",
            cloud_coverage=20,
        )

        assert params.satellite == "S2E84"
        assert params.search_method == "geometry"
        assert params.bands == ["red", "green", "blue"]
        assert params.cloud_coverage == 20

    def test_default_bands(self):
        """Test that default bands are loaded when not specified."""
        params = ProcessingParams(
            satellite="S2E84",
            search_method="geometry",
        )

        # Should have default bands populated
        assert len(params.bands) > 0

    def test_date_as_string(self):
        """Test dates can be specified as strings."""
        params = ProcessingParams(
            satellite="S2E84",
            search_method="geometry",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        assert params.start_date == "2024-01-01"
        assert params.end_date == "2024-01-31"

    def test_date_as_date_object(self):
        """Test dates can be specified as date objects."""
        params = ProcessingParams(
            satellite="S2E84",
            search_method="geometry",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        assert params.start_date == date(2024, 1, 1)
        assert params.end_date == date(2024, 1, 31)

    def test_cloud_coverage_default(self):
        """Test default cloud coverage value."""
        params = ProcessingParams(
            satellite="S2E84",
            search_method="geometry",
        )

        assert params.cloud_coverage == 25  # Default value


class TestSaveParams:
    """Tests for SaveParams model."""

    def test_valid_save_params(self, tmp_path):
        """Test creating SaveParams with valid parameters."""
        params = SaveParams(
            output_path=tmp_path,
            save_to_local=True,
            save_to_s3=False,
            save_as_geotiff=True,
            enable_compression=True,
        )

        assert params.output_path == tmp_path
        assert params.save_to_local is True
        assert params.save_to_s3 is False
        assert params.save_as_geotiff is True

    def test_s3_requires_bucket(self):
        """Test that S3 save requires bucket specification."""
        with pytest.raises(ValueError, match="S3 bucket must be specified"):
            SaveParams(
                save_to_s3=True,
                s3_bucket=None,
            )

    def test_s3_with_bucket(self):
        """Test S3 save with bucket specified."""
        params = SaveParams(
            save_to_s3=True,
            s3_bucket="test-bucket",
        )

        assert params.save_to_s3 is True
        assert params.s3_bucket == "test-bucket"

    def test_default_values(self):
        """Test default parameter values."""
        params = SaveParams()

        assert params.save_to_local is True
        assert params.save_to_s3 is False
        assert params.merge_bands is True
        assert params.save_as_geotiff is True
        assert params.save_as_numpy is False
        assert params.enable_compression is True
        assert params.verbose is False

    def test_verbose_flag(self):
        """Test verbose logging flag."""
        params = SaveParams(verbose=True)
        assert params.verbose is True

        params = SaveParams(verbose=False)
        assert params.verbose is False

    def test_custom_naming(self):
        """Test custom naming convention."""
        params = SaveParams(custom_naming="{date}/{satellite}_{band}.tif")

        assert params.custom_naming == "{date}/{satellite}_{band}.tif"
