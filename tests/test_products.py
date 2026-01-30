"""
Integration tests for different satellite products.

Tests each supported product type with basic functionality.
Run with: pytest tests/test_products.py -v

Author: Peter Kongstad
"""

import pytest
from shapely.geometry import box

from sat_data_acquisition import SatDataClient
from sat_data_acquisition.models.params import ProcessingParams

# Test geometry (small area in Copenhagen)
TEST_GEOMETRY = box(12.5683 - 0.01, 55.6761 - 0.01, 12.5683 + 0.01, 55.6761 + 0.01)


@pytest.fixture
def client():
    """Create SatDataClient instance."""
    return SatDataClient()


class TestS2MPC:
    """Tests for Sentinel-2 Microsoft Planetary Computer."""

    @pytest.mark.integration
    # @pytest.mark.skip(reason="Requires live API access")
    def test_s2mpc_basic_download(self, client):
        """Test basic S2MPC download."""
        params = ProcessingParams(
            satellite="S2MPC",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["red", "green", "blue"],
            cloud_coverage=20,
        )

        dataset = client.search_and_create_image(geometry=TEST_GEOMETRY, processing_params=params)

        assert dataset is not None
        assert "red" in dataset.data_vars
        assert "green" in dataset.data_vars
        assert "blue" in dataset.data_vars

    def test_s2mpc_params_validation(self):
        """Test S2MPC parameter validation."""
        params = ProcessingParams(
            satellite="S2MPC",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["red", "green", "blue"],
            cloud_coverage=20,
        )

        assert params.satellite == "S2MPC"
        assert params.cloud_coverage == 20
        assert "red" in params.bands


class TestS2E84:
    """Tests for Sentinel-2 Element84."""

    @pytest.mark.integration
    # @pytest.mark.skip(reason="Requires live API access")
    def test_s2e84_basic_download(self, client):
        """Test basic S2E84 download."""
        params = ProcessingParams(
            satellite="S2E84",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["red", "green", "blue"],
            cloud_coverage=20,
        )

        dataset = client.search_and_create_image(geometry=TEST_GEOMETRY, processing_params=params)

        assert dataset is not None
        assert "red" in dataset.data_vars

    def test_s2e84_params_validation(self):
        """Test S2E84 parameter validation."""
        params = ProcessingParams(
            satellite="S2E84",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["red", "green", "blue", "nir"],
            cloud_coverage=15,
        )

        assert params.satellite == "S2E84"
        assert params.cloud_coverage == 15
        assert len(params.bands) == 4


class TestS1MPC:
    """Tests for Sentinel-1 SAR Microsoft Planetary Computer."""

    @pytest.mark.integration
    # @pytest.mark.skip(reason="Requires live API access")
    def test_s1mpc_basic_download(self, client):
        """Test basic S1MPC SAR download."""
        params = ProcessingParams(
            satellite="S1MPC",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["vv", "vh"],  # SAR polarizations
        )

        dataset = client.search_and_create_image(geometry=TEST_GEOMETRY, processing_params=params)

        assert dataset is not None
        assert "vv" in dataset.data_vars or "vh" in dataset.data_vars

    def test_s1mpc_no_cloud_coverage(self):
        """Test that S1MPC ignores cloud_coverage parameter."""
        params = ProcessingParams(
            satellite="S1MPC",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["vv", "vh"],
            cloud_coverage=50,  # Should be ignored
        )

        # Should not raise error even with cloud_coverage set
        assert params.satellite == "S1MPC"
        assert "vv" in params.bands


class TestLANDSATMPC:
    """Tests for Landsat Microsoft Planetary Computer."""

    @pytest.mark.integration
    # @pytest.mark.skip(reason="Requires live API access")
    def test_landsat_basic_download(self, client):
        """Test basic Landsat download."""
        params = ProcessingParams(
            satellite="LANDSATMPC",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["red", "green", "blue"],
            cloud_coverage=20,
        )

        dataset = client.search_and_create_image(geometry=TEST_GEOMETRY, processing_params=params)

        assert dataset is not None
        assert "red" in dataset.data_vars

    def test_landsat_params_validation(self):
        """Test Landsat parameter validation."""
        params = ProcessingParams(
            satellite="LANDSATMPC",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["red", "green", "blue", "nir", "swir1", "swir2"],
            cloud_coverage=15,
        )

        assert params.satellite == "LANDSATMPC"
        assert len(params.bands) == 6


class TestCopDEM30MPC:
    """Tests for Copernicus DEM 30m."""

    @pytest.mark.integration
    # @pytest.mark.skip(reason="Requires live API access")
    def test_dem_basic_download(self, client):
        """Test basic DEM download."""
        params = ProcessingParams(satellite="CopDEM30MPC", search_method="geometry", bands=["data"])

        dataset = client.search_and_create_image(geometry=TEST_GEOMETRY, processing_params=params)

        assert dataset is not None
        assert "data" in dataset.data_vars

    def test_dem_no_dates_needed(self):
        """Test that DEM doesn't require dates."""
        params = ProcessingParams(
            satellite="CopDEM30MPC",
            search_method="geometry",
            bands=["data"],
            # No start_date or end_date
        )

        assert params.satellite == "CopDEM30MPC"
        assert params.start_date is None
        assert params.end_date is None

    def test_dem_ignores_cloud_coverage(self):
        """Test that DEM ignores cloud_coverage."""
        params = ProcessingParams(
            satellite="CopDEM30MPC",
            search_method="geometry",
            bands=["data"],
            cloud_coverage=50,  # Should be ignored
        )

        # Should not raise error
        assert params.satellite == "CopDEM30MPC"


class TestHLSSentinel:
    """Tests for HLS Sentinel."""

    @pytest.mark.integration
    # @pytest.mark.skip(reason="Requires live API access")
    def test_hls_sentinel_basic_download(self, client):
        """Test basic HLS Sentinel download."""
        params = ProcessingParams(
            satellite="HLS_SENTINEL",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["B04", "B03", "B02"],
            cloud_coverage=20,
        )

        dataset = client.search_and_create_image(geometry=TEST_GEOMETRY, processing_params=params)

        assert dataset is not None
        assert "B04" in dataset.data_vars
        assert "B03" in dataset.data_vars
        assert "B02" in dataset.data_vars

    def test_hls_sentinel_params_validation(self):
        """Test HLS Sentinel parameter validation."""
        params = ProcessingParams(
            satellite="HLS_SENTINEL",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["B04", "B03", "B02", "B05"],
            cloud_coverage=15,
        )

        assert params.satellite == "HLS_SENTINEL"
        assert params.cloud_coverage == 15
        assert "B04" in params.bands


class TestHLSLandsat:
    """Tests for HLS Landsat."""

    @pytest.mark.integration
    # @pytest.mark.skip(reason="Requires live API access")
    def test_hls_landsat_basic_download(self, client):
        """Test basic HLS Landsat download."""
        params = ProcessingParams(
            satellite="HLS_LANDSAT",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["B04", "B03", "B02"],
            cloud_coverage=20,
        )

        dataset = client.search_and_create_image(geometry=TEST_GEOMETRY, processing_params=params)

        assert dataset is not None
        assert "B04" in dataset.data_vars

    def test_hls_landsat_params_validation(self):
        """Test HLS Landsat parameter validation."""
        params = ProcessingParams(
            satellite="HLS_LANDSAT",
            search_method="geometry",
            start_date="2024-06-01",
            end_date="2024-06-30",
            bands=["B04", "B03", "B02", "B05", "B06", "B07"],
            cloud_coverage=15,
        )

        assert params.satellite == "HLS_LANDSAT"
        assert len(params.bands) == 6


class TestProductComparison:
    """Comparative tests across products."""

    def test_all_products_accept_geometry_search(self):
        """Test that all products support geometry search."""
        products = [
            "S2MPC",
            "S2E84",
            "S1MPC",
            "LANDSATMPC",
            "HLS_SENTINEL",
            "HLS_LANDSAT",
            "CopDEM30MPC",
        ]

        for satellite in products:
            if satellite == "CopDEM30MPC":
                bands = ["data"]
            elif satellite.startswith("HLS"):
                bands = ["B04"]
            else:
                bands = ["red"]

            params = ProcessingParams(satellite=satellite, search_method="geometry", bands=bands)
            assert params.search_method == "geometry"

    def test_optical_products_support_cloud_filtering(self):
        """Test that optical products support cloud coverage."""
        optical_products = ["S2MPC", "S2E84", "LANDSATMPC", "HLS_SENTINEL", "HLS_LANDSAT"]

        for satellite in optical_products:
            if satellite.startswith("HLS"):
                bands = ["B04", "B03", "B02"]
            else:
                bands = ["red", "green", "blue"]

            params = ProcessingParams(
                satellite=satellite,
                search_method="geometry",
                start_date="2024-01-01",
                end_date="2024-12-31",
                bands=bands,
                cloud_coverage=20,
            )
            assert params.cloud_coverage == 20

    def test_sar_and_dem_ignore_cloud_coverage(self):
        """Test that SAR and DEM ignore cloud coverage."""
        non_optical = ["S1MPC", "CopDEM30MPC"]

        for satellite in non_optical:
            params = ProcessingParams(
                satellite=satellite,
                search_method="geometry",
                bands=["vv"] if satellite == "S1MPC" else ["data"],
                cloud_coverage=50,  # Should be ignored
            )
            # Should not raise error - parameter is accepted but ignored
            assert params.satellite == satellite

    def test_hls_band_naming(self):
        """Test that HLS products use B## band naming convention."""
        hls_products = ["HLS_SENTINEL", "HLS_LANDSAT"]

        for satellite in hls_products:
            params = ProcessingParams(
                satellite=satellite,
                search_method="geometry",
                start_date="2024-01-01",
                end_date="2024-12-31",
                bands=["B04", "B03", "B02"],  # HLS uses B## naming
                cloud_coverage=20,
            )
            assert all(band.startswith("B") for band in params.bands)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
