"""
Integration tests for SatDataClient.

These tests make actual API calls and should be marked as slow/integration.

Author: Peter Kongstad
"""

import pytest
from shapely.geometry import Point

from sat_data_acquisition import SatDataClient
from sat_data_acquisition.models.params import ProcessingParams


@pytest.mark.integration
@pytest.mark.slow
class TestSatDataClientIntegration:
    """Integration tests for SatDataClient (requires internet)."""

    def test_client_initialization(self):
        """Test that client initializes correctly."""
        client = SatDataClient()
        assert client is not None
        assert hasattr(client, "settings")
        assert hasattr(client, "iterators")

    def test_provider_registry(self):
        """Test that provider registry is populated."""
        client = SatDataClient()
        assert len(client.iterators) > 0
        assert "S2E84" in client.iterators
        assert "S2MPC" in client.iterators

    # @pytest.mark.skip(reason="Makes actual API call - enable for manual testing")
    def test_search_and_create_image(self):
        """Test actual image search and download."""
        client = SatDataClient()

        # Small test area
        copenhagen = Point(12.5683, 55.6761)
        geometry = copenhagen.buffer(0.01)

        params = ProcessingParams(
            satellite="S2E84",
            search_method="geometry",
            bands=["red"],  # Just one band for speed
            start_date="2024-06-01",
            end_date="2024-06-30",
            cloud_coverage=30,
            # resolution=10,
            # limit=1,
        )

        dataset = client.search_and_create_image(
            geometry=geometry,
            processing_params=params,
        )

        assert dataset is not None
        assert "red" in dataset.data_vars
