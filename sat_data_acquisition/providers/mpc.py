from typing import Literal, TypeVar, Union

import numpy as np
import planetary_computer
import pystac
import xarray
from rasterio.enums import Resampling
from shapely.geometry.base import BaseGeometry

from sat_data_acquisition.config.logging import get_logger
from sat_data_acquisition.config.settings import get_settings
from sat_data_acquisition.core.base_iterator import STACImageIterator

logger = get_logger(__name__)

# Define T for numpy data types
T = TypeVar("T", np.uint8, np.uint16, np.int16, np.uint32, np.int32, np.float32, np.float64)


class MPCIterator(STACImageIterator):
    """Base iterator for Microsoft Planetary Computer, which requires signing items."""

    def _search(self, *args, **kwargs) -> list[pystac.Item]:
        """Search and sign items from Microsoft Planetary Computer."""
        items = super()._search(*args, **kwargs)
        return [planetary_computer.sign(item) for item in items]


class Sentinel1MPCIterator(MPCIterator):
    """Microsoft Planetary Computer Sentinel-1 iterator."""

    @property
    def satellite(self) -> str:
        return "S1MPC"

    @property
    def api_url(self) -> str:
        return str(get_settings().mpc_api)

    @property
    def collection(self) -> str:
        return str(get_settings().s1_collection)

    def search_items(
        self,
        start_date: str,
        end_date: str,
        geometry: BaseGeometry | None = None,
        query: dict | None = None,
        sort: bool = True,
        **kwargs,
    ) -> list[pystac.Item]:
        """
        Search the MPC STAC API for Sentinel-1 products. A geometry is required.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            geometry: Geometry for intersection search (required).
            query: Additional query parameters. Defaults to None.
            sort: Flag to sort results by date. Defaults to True.

        Returns:
            list[pystac.Item]: A list of matching STAC items.
        """
        return self._search(
            start_date=start_date,
            end_date=end_date,
            geometry=geometry,
            query=query,
            sort=sort,
            modifier=planetary_computer.sign_inplace,
        )


class Sentinel2MPCIterator(MPCIterator):
    """Microsoft Planetary Computer Sentinel-2 iterator."""

    @property
    def satellite(self) -> str:
        return "S2MPC"

    @property
    def api_url(self) -> str:
        return str(get_settings().mpc_api)

    @property
    def collection(self) -> str:
        return str(get_settings().s2_collection)

    def _construct_query(self, query: dict | None, cloud_coverage: int, tile: str | None) -> dict:
        """Construct query parameters for MPC Sentinel-2 search."""
        query = query or {}
        if tile:
            query["s2:mgrs_tile"] = {"eq": tile}
        query["eo:cloud_cover"] = {"lt": cloud_coverage}
        return query

    def search_items(
        self,
        start_date: str,
        end_date: str,
        geometry: BaseGeometry | None = None,
        query: dict | None = None,
        sort: bool = True,
        tile: str | None = None,
        cloud_coverage: int = 25,
        **kwargs,
    ) -> list[pystac.Item]:
        """
        Search the MPC STAC API for Sentinel-2 products.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            geometry: Geometry for intersection search. Defaults to None.
            query: Additional query parameters. Defaults to None.
            sort: Flag to sort results by date. Defaults to True.
            tile: MGRS tile ID for search. Defaults to None.
            cloud_coverage: Maximum cloud cover percentage. Defaults to 25.

        Returns:
            list[pystac.Item]: A list of matching STAC items.
        """
        full_query = self._construct_query(query=query, cloud_coverage=cloud_coverage, tile=tile)
        return self._search(
            start_date=start_date, end_date=end_date, geometry=geometry, query=full_query, sort=sort
        )

    def create_image(
        self,
        items: list[pystac.Item],
        bands: list[str],
        resolution: int | None = None,
        epsg: int | None = None,
        geometry: BaseGeometry | None = None,
        clip_method: str = "geometry",
        pixels: int = 0,
        dtype: Union[np.dtype, T, None] = None,
        fill_value: Union[int, float, None] = None,
        resampling: Resampling = Resampling.nearest,
        skip_inconsistent_items: bool = False,
        groupby: Literal["solar_day"] | None = None,
        rescale: bool = False,
    ) -> xarray.Dataset:
        """
        Creates an xarray Dataset from S2MPC items, mapping common band names to provider-specific
        names.
        """
        band_mapping = get_settings().band_mapping_s2mpc
        mapped_bands = [band_mapping.get(band, band) for band in bands]

        out = super().create_image(
            items=items,
            bands=mapped_bands,
            resolution=resolution,
            epsg=epsg,
            geometry=geometry,
            clip_method=clip_method,
            pixels=pixels,
            dtype=dtype,
            fill_value=fill_value,
            resampling=resampling,
            skip_inconsistent_items=skip_inconsistent_items,
            groupby=groupby,
            rescale=rescale,
        )

        # Rename the variables back to the official band names for consistency
        reverse_mapping = {v: k for k, v in band_mapping.items() if v in out.data_vars}
        return out.rename(reverse_mapping)


class LandsatMPCIterator(MPCIterator):
    """Microsoft Planetary Computer Landsat iterator."""

    @property
    def satellite(self) -> str:
        return "LANDSATMPC"

    @property
    def api_url(self) -> str:
        return str(get_settings().mpc_api)

    @property
    def collection(self) -> str:
        return str(get_settings().landsat_collection)

    def _construct_query(self, query: dict | None, cloud_coverage: int) -> dict:
        """Construct query parameters for Landsat search."""
        query = query or {}
        query["eo:cloud_cover"] = {"lt": cloud_coverage}
        return query

    def search_items(
        self,
        start_date: str,
        end_date: str,
        geometry: BaseGeometry | None = None,
        query: dict | None = None,
        sort: bool = True,
        cloud_coverage: int = 75,
        **kwargs,
    ) -> list[pystac.Item]:
        """
        Search the MPC STAC API for Landsat products.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            geometry: Geometry for intersection search. Defaults to None.
            query: Additional query parameters. Defaults to None.
            sort: Flag to sort results by date. Defaults to True.
            cloud_coverage: Maximum cloud cover percentage. Defaults to 75.

        Returns:
            list[pystac.Item]: A list of matching STAC items.
        """
        full_query = self._construct_query(query=query, cloud_coverage=cloud_coverage)
        return self._search(
            start_date=start_date, end_date=end_date, geometry=geometry, query=full_query, sort=sort
        )


class HLSLandsatIterator(MPCIterator):
    """Microsoft Planetary Computer HLS Landsat iterator."""

    @property
    def satellite(self):
        return "HLS_LANDSAT"

    @property
    def api_url(self) -> str:
        return str(get_settings().mpc_api)

    @property
    def collection(self) -> str:
        return str(get_settings().hls_landsat_collection)

    def search_items(
        self,
        start_date: str,
        end_date: str,
        geometry: BaseGeometry | None = None,
        query: dict | None = None,
        sort: bool = True,
        **kwargs,
    ) -> list[pystac.Item]:
        """Search the MPC STAC API for HLS Landsat products."""
        return self._search(
            geometry=geometry,
            start_date=start_date,
            end_date=end_date,
            query=query,
            sort=sort,
        )


class HLSSentinelIterator(MPCIterator):
    """Microsoft Planetary Computer HLS Sentinel iterator."""

    @property
    def satellite(self):
        return "HLS_SENTINEL"

    @property
    def api_url(self) -> str:
        return str(get_settings().mpc_api)

    @property
    def collection(self) -> str:
        return str(get_settings().hls_sentinel_collection)

    def search_items(
        self,
        start_date: str,
        end_date: str,
        geometry: BaseGeometry | None = None,
        query: dict | None = None,
        sort: bool = True,
        **kwargs,
    ) -> list[pystac.Item]:
        """Search the MPC STAC API for HLS Sentinel products."""
        return self._search(
            geometry=geometry,
            start_date=start_date,
            end_date=end_date,
            query=query,
            sort=sort,
        )


class CopDEM30Iterator(MPCIterator):
    """Microsoft Planetary Computer Copernicus DEM 30m iterator."""

    # CopDEM30 should remain in native EPSG:4326 (avoid precision issues)
    reproject_wgs84_to_utm = False
    # Use native COG resolution for CopDEM30
    use_native_resolution = True

    @property
    def satellite(self) -> str:
        return "CopDEM30MPC"

    @property
    def api_url(self) -> str:
        return str(get_settings().mpc_api)

    @property
    def collection(self) -> str:
        return str(get_settings().copdem30_collection)

    def search_items(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        geometry: BaseGeometry | None = None,
        query: dict | None = None,
        sort: bool = True,
        **kwargs,
    ) -> list[pystac.Item]:
        """
        Search the MPC STAC API for Copernicus DEM 30m products.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            geometry: Geometry for intersection search. Defaults to None.
            query: Additional query parameters. Defaults to None.
            sort: Flag to sort results by date. Defaults to True.

        Returns:
            list[pystac.Item]: A list of matching STAC items.
        """
        # CopDEM30 does not use datetime in search
        return self._search(
            start_date=None,
            end_date=None,
            geometry=geometry,
            query=query,
            sort=sort,
            modifier=planetary_computer.sign_inplace,
        )
