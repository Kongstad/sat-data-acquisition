from typing import Literal, TypeVar, Union

import numpy as np
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


class S2E84Iterator(STACImageIterator):
    """Element84 Sentinel-2 image iterator."""

    @property
    def satellite(self) -> str:
        return "S2E84"

    @property
    def api_url(self) -> str:
        return str(get_settings().e84_api)

    @property
    def collection(self) -> str:
        return str(get_settings().s2_collection)

    def _construct_query(self, query: dict | None, cloud_coverage: int, tile: str | None) -> dict:
        """Construct query parameters for Element84 Sentinel-2 search."""
        query = query or {}
        if tile:
            query["grid:code"] = {"eq": f"MGRS-{tile}"}
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
        cloud_coverage: int = 75,
        **kwargs,
    ) -> list[pystac.Item]:
        """
        Search the Element84 STAC API for Sentinel-2 products.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            geometry: Geometry for intersection search. Defaults to None.
            query: Additional query parameters. Defaults to None.
            sort: Flag to sort results by date. Defaults to True.
            tile: MGRS tile ID for search. Defaults to None.
            cloud_coverage: Maximum cloud cover percentage. Defaults to 75.

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
        Creates an xarray Dataset from S2E84 items, mapping common band names to provider-specific
        names.

        Element84 uses common names (red, green, blue) which we map to official
        names (B04, B03, B02) for consistency across providers.
        """
        band_mapping = get_settings().band_mapping_s2e84
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
