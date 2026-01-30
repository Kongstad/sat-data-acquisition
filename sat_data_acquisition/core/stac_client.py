from typing import TYPE_CHECKING, Any, Literal, Optional, TypeVar, Union

import numpy as np
import xarray
from rasterio.enums import Resampling
from shapely.geometry.base import BaseGeometry

from sat_data_acquisition.config.logging import get_logger
from sat_data_acquisition.config.settings import SatDataSettings, get_settings
from sat_data_acquisition.providers import PROVIDER_REGISTRY

if TYPE_CHECKING:
    from sat_data_acquisition.models.params import ProcessingParams

logger = get_logger(__name__)

# Define T for numpy data types
T = TypeVar("T", np.uint8, np.uint16, np.int16, np.uint32, np.int32, np.float32, np.float64)


class SatDataClient:
    """
    Unified interface for retrieving satellite images from different STAC sources.
    """

    def __init__(self, settings: "SatDataSettings | None" = None):
        self.settings: SatDataSettings = settings or get_settings()
        # Use Any to avoid abstract class instantiation issues in mypy
        self.iterators: dict[str, Any] = {
            name: cls() for name, cls in PROVIDER_REGISTRY.items()  # type: ignore[abstract]
        }

        self.valid_bands: dict[str, set[str]] = {
            "S1": {"vv", "vh"},
            "S2": set(self.settings.band_mapping_s2mpc.keys()),
            "LANDSAT": self.settings.valid_bands_landsat,
            "HLS": self.settings.valid_bands_hls,
            "CopDEM": self.settings.valid_bands_copdem30,
        }

    def validate_bands(self, satellite: str, bands: list[str]) -> None:
        """
        Validates that the provided bands are correct for the given satellite type.

        Args:
            satellite: The satellite type (e.g., "S1MPC", "S2MPC", "LANDSATMPC").
            bands: A list of band names to validate.

        Raises:
            ValueError: If any band names are invalid for the specified satellite.
        """
        valid_bands = set()

        if "HLS" in satellite:
            valid_bands = self.valid_bands["HLS"]
        elif "S1" in satellite:
            valid_bands = self.valid_bands["S1"]
        elif "S2" in satellite or "SENTINEL" in satellite:
            # Allow both common names and native names for S2
            valid_bands = set(self.settings.band_mapping_s2mpc.keys()) | set(
                self.settings.band_mapping_s2mpc.values()
            )
        elif "LANDSAT" in satellite:
            valid_bands = self.valid_bands["LANDSAT"]
        elif "CopDEM" in satellite:
            valid_bands = self.valid_bands["CopDEM"]
        else:
            raise ValueError(f"Satellite {satellite} is not supported for band validation.")

        invalid_bands = [band for band in bands if band not in valid_bands]
        if invalid_bands:
            sorted_valid_bands = sorted(list(valid_bands))
            error_message = (
                f"Invalid band names {invalid_bands} for satellite {satellite}. "
                f"Valid bands are: {sorted_valid_bands}"
            )
            logger.error(error_message)
            raise ValueError(error_message)

    def search_and_create_image(
        self,
        geometry: BaseGeometry | None = None,
        processing_params: Optional["ProcessingParams"] = None,
        # Individual parameters for backward compatibility
        satellite: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        bands: list[str] | None = None,
        search_method: Literal["geometry", "tile"] | None = None,
        tile: str | None = None,
        area_name: str | None = None,
        cloud_coverage: int | None = None,
        sort: bool = True,
        clip_method: str = "geometry",
        pixels: int = 256,
        resolution: int | None = None,
        epsg: int | None = None,
        dtype: Union[str, np.dtype, T, None] = None,
        fill_value: Union[int, float, None] = None,
        resampling: Resampling = Resampling.nearest,
        skip_inconsistent_items: bool = False,
        groupby: Literal["solar_day"] | None = None,
    ) -> xarray.Dataset:
        """
        Searches for and creates an image from a specified satellite source.

        Args:
            geometry: Geometry for search, required if search_method is "geometry".
            processing_params: ProcessingParams object containing all processing parameters.
                If provided, individual parameters are ignored.
            satellite: Satellite type (e.g., "S1MPC", "S2MPC", "S2E84").
            start_date: Start date for search (YYYY-MM-DD).
            end_date: End date for search (YYYY-MM-DD).
            bands: List of band names.
            search_method: The search method ("geometry" or "tile").
            tile: Tile ID, required if search_method is "tile".
            area_name: Optional name for the area/field. If provided, will be included
                in saved file paths.
            cloud_coverage: Max cloud coverage for S2/Landsat.
            sort: Whether to sort results by date. Defaults to True.
            clip_method: Clipping method ("geometry" or "window"). Defaults to "geometry".
            pixels: Pixel size for window clipping. Defaults to 256.
            resolution: Output resolution. Defaults to satellite default.
            epsg: Output EPSG code. Defaults to auto-detection.
            dtype: Output data type. Defaults to satellite default.
            fill_value: Nodata fill value. Defaults to satellite default.
            resampling: Resampling method. Defaults to Resampling.nearest.
            skip_inconsistent_items: Skip items with missing bands. Defaults to False.
            groupby: Grouping for `odc-stac`. Defaults to None.

        Returns:
            xarray.Dataset: The resulting image data.
        """
        # Use ProcessingParams if provided, otherwise use individual parameters
        if processing_params:
            satellite = processing_params.satellite
            start_date = str(processing_params.start_date)
            end_date = str(processing_params.end_date)
            bands = processing_params.bands
            search_method = processing_params.search_method
            tile = processing_params.tile
            cloud_coverage = processing_params.cloud_coverage
            sort = processing_params.sort
            clip_method = processing_params.clip_method
            pixels = processing_params.pixels
            dtype = processing_params.dtype
            fill_value = processing_params.fill_value
            groupby = processing_params.groupby
        elif not all([satellite, start_date, end_date, bands, search_method]):
            raise ValueError(
                "Either provide `processing_params` or all individual parameters "
                "(satellite, start_date, end_date, bands, search_method)"
            )

        if not satellite:
            raise ValueError("`satellite` must be specified")

        iterator = self.iterators.get(satellite)
        if not iterator:
            logger.error(f"Iterator not found for satellite '{satellite}'")
            logger.error(f"Available iterators: {list(self.iterators.keys())}")
            raise ValueError(f"Satellite '{satellite}' is not supported.")

        if search_method == "geometry":
            if not geometry:
                raise ValueError("`geometry` is required when `search_method` is 'geometry'.")
        elif search_method == "tile" and not tile:
            raise ValueError("`tile` is required when `search_method` is 'tile'.")

        if (
            satellite
            and satellite.startswith(("S1", "LANDSAT", "HLS"))
            and search_method != "geometry"
        ):
            raise ValueError(f"{satellite} only supports 'geometry' based search method.")

        kwargs = {
            "tile": tile if search_method == "tile" else None,
            "cloud_coverage": cloud_coverage,
        }

        if not start_date or not end_date or bands is None:
            raise ValueError("start_date, end_date and bands are required")

        search_kwargs: dict[str, Any] = {k: v for k, v in kwargs.items() if v is not None}

        xarr = iterator.search_and_create_image(
            start_date=start_date,
            end_date=end_date,
            bands=bands,
            geometry=geometry,
            sort=sort,
            resolution=resolution,
            epsg=epsg,
            clip_method=clip_method,
            pixels=pixels,
            dtype=dtype,
            fill_value=fill_value,
            resampling=resampling,
            skip_inconsistent_items=skip_inconsistent_items,
            groupby=groupby,
            **search_kwargs,
        )

        # Attach metadata
        xarr.attrs["satellite"] = iterator.satellite
        xarr.attrs["acquisition_date"] = str(xarr.time.dt.strftime("%Y-%m-%d").values[0])
        if tile:
            xarr.attrs["tile"] = tile
        if area_name:
            xarr.attrs["area_name"] = area_name

        return xarray.Dataset(xarr)
