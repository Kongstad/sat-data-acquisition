"""
Tests for processing operations.

Author: Peter Kongstad
"""

import numpy as np
import rasterio
import xarray as xr

from sat_data_acquisition.models.params import SaveParams
from sat_data_acquisition.processing.save import save_data
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

    def test_merge_bands_geotiff(self, tmp_path, settings):
        """Test that merge_bands=True creates single multi-band GeoTIFF."""
        # Create mock 3-band image
        data = np.random.rand(3, 10, 10).astype(np.float32) * 1000
        coords = {"band": ["red", "green", "blue"], "y": range(10), "x": range(10)}
        image = xr.DataArray(data, coords=coords, dims=["band", "y", "x"])

        # Add CRS metadata
        image = image.rio.write_crs("EPSG:32633")

        save_params = SaveParams(
            output_path=str(tmp_path),
            save_to_local=True,
            save_as_geotiff=True,
            merge_bands=True,
        )

        save_data(
            image=image,
            identifier="test_area",
            datetime="2024-06-15T10:30:00",
            satellite="S2MPC",
            provider="MPC",
            save_params=save_params,
        )

        # Check that single file was created
        tiff_files = list(tmp_path.glob("**/*.tif"))
        assert len(tiff_files) == 1, "Should create exactly one merged file"

        # Verify it has 3 bands
        with rasterio.open(tiff_files[0]) as src:
            assert src.count == 3, "Merged file should have 3 bands"
            assert "merged" in tiff_files[0].name, "Filename should contain 'merged'"

    def test_separate_bands_geotiff(self, tmp_path, settings):
        """Test that merge_bands=False creates separate single-band GeoTIFFs."""
        # Create mock 3-band image
        data = np.random.rand(3, 10, 10).astype(np.float32) * 1000
        coords = {"band": ["red", "green", "blue"], "y": range(10), "x": range(10)}
        image = xr.DataArray(data, coords=coords, dims=["band", "y", "x"])

        # Add CRS metadata
        image = image.rio.write_crs("EPSG:32633")

        save_params = SaveParams(
            output_path=str(tmp_path),
            save_to_local=True,
            save_as_geotiff=True,
            merge_bands=False,
        )

        save_data(
            image=image,
            identifier="test_area",
            datetime="2024-06-15T10:30:00",
            satellite="S2MPC",
            provider="MPC",
            save_params=save_params,
        )

        # Check that 3 separate files were created
        tiff_files = list(tmp_path.glob("**/*.tif"))
        assert len(tiff_files) == 3, "Should create 3 separate files (one per band)"

        # Verify each has 1 band
        for tiff_file in tiff_files:
            with rasterio.open(tiff_file) as src:
                assert src.count == 1, f"{tiff_file.name} should have 1 band"

            # Check that band names are in filenames
            assert any(
                band in tiff_file.name for band in ["red", "green", "blue"]
            ), f"Filename {tiff_file.name} should contain band name"

    def test_merge_bands_numpy(self, tmp_path, settings):
        """Test that merge_bands=True creates single 3D numpy array."""
        # Create mock 3-band image
        data = np.random.rand(3, 10, 10).astype(np.float32) * 1000
        coords = {"band": ["red", "green", "blue"], "y": range(10), "x": range(10)}
        image = xr.DataArray(data, coords=coords, dims=["band", "y", "x"])

        save_params = SaveParams(
            output_path=str(tmp_path),
            save_to_local=True,
            save_as_numpy=True,
            merge_bands=True,
        )

        save_data(
            image=image,
            identifier="test_area",
            datetime="2024-06-15T10:30:00",
            satellite="S2MPC",
            provider="MPC",
            save_params=save_params,
        )

        # Check that single file was created
        npy_files = list(tmp_path.glob("**/*.npy"))
        assert len(npy_files) == 1, "Should create exactly one merged file"

        # Verify it has shape (3, 10, 10)
        array = np.load(npy_files[0])
        assert array.shape == (3, 10, 10), "Merged array should be 3D with shape (bands, h, w)"
        assert "merged" in npy_files[0].name, "Filename should contain 'merged'"

    def test_separate_bands_numpy(self, tmp_path, settings):
        """Test that merge_bands=False creates separate 2D numpy arrays."""
        # Create mock 3-band image
        data = np.random.rand(3, 10, 10).astype(np.float32) * 1000
        coords = {"band": ["red", "green", "blue"], "y": range(10), "x": range(10)}
        image = xr.DataArray(data, coords=coords, dims=["band", "y", "x"])

        save_params = SaveParams(
            output_path=str(tmp_path),
            save_to_local=True,
            save_as_numpy=True,
            merge_bands=False,
        )

        save_data(
            image=image,
            identifier="test_area",
            datetime="2024-06-15T10:30:00",
            satellite="S2MPC",
            provider="MPC",
            save_params=save_params,
        )

        # Check that 3 separate files were created
        npy_files = list(tmp_path.glob("**/*.npy"))
        assert len(npy_files) == 3, "Should create 3 separate files (one per band)"

        # Verify each has shape (10, 10)
        for npy_file in npy_files:
            array = np.load(npy_file)
            assert array.shape == (10, 10), f"{npy_file.name} should be 2D with shape (h, w)"

            # Check that band names are in filenames
            assert any(
                band in npy_file.name for band in ["red", "green", "blue"]
            ), f"Filename {npy_file.name} should contain band name"
