from abc import abstractmethod
from collections import Counter
from datetime import datetime
from typing import Any, Callable, Literal, Optional, TypeVar, Union

import numpy as np
import odc.stac
import pystac
import rioxarray  # noqa: F401
import xarray
from odc.stac import configure_rio
from pystac_client import Client
from rasterio.enums import Resampling
from shapely.geometry.base import BaseGeometry

from sat_data_acquisition.config.logging import get_logger
from sat_data_acquisition.config.settings import get_settings
from sat_data_acquisition.utils.coordinate_converter import (
    WGS84_EPSG,
    geometry_from_epsg_to_epsg,
    get_utm_epsg,
)

logger = get_logger(__name__)

# Configure rio for odc-stac
configure_rio(cloud_defaults=True)

# Define T for numpy data types
T = TypeVar("T", np.uint8, np.uint16, np.int16, np.uint32, np.int32, np.float32, np.float64)


class STACImageIterator:
    """
    Base class for iterating and interacting with STAC API images.

    This class provides the basic functionality to open a STAC API client,
    perform searches, and retrieve images.

    Attributes:
        band_mapping: Optional dict to map common band names to native names.
        reproject_wgs84_to_utm: If True, WGS84 data will be reprojected to local UTM.
        use_native_resolution: If True, use native COG resolution instead of requested resolution.
    """

    band_mapping: dict | None = None
    reproject_wgs84_to_utm: bool = True
    use_native_resolution: bool = False

    @property
    @abstractmethod
    def satellite(self) -> str:
        """Define the satellite identifier for this iterator."""
        raise NotImplementedError("Satellite property must be implemented by subclasses.")

    @property
    @abstractmethod
    def api_url(self) -> str:
        """Define the STAC API URL for this iterator."""
        raise NotImplementedError("api_url property must be implemented by subclasses.")

    @property
    @abstractmethod
    def collection(self) -> str:
        """Define the STAC collection for this iterator."""
        raise NotImplementedError("collection property must be implemented by subclasses.")

    @abstractmethod
    def search_items(
        self,
        start_date: str,
        end_date: str,
        geometry: Optional[BaseGeometry] = None,
        query: Optional[dict] = None,
        sort: bool = True,
        **kwargs,
    ) -> list[pystac.Item]:
        """
        Abstract method to search the STAC API. Must be implemented by subclasses.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            geometry: Geometry to intersect the search. Defaults to None.
            query: Additional query parameters. Defaults to None.
            sort: Flag to sort results by date. Defaults to True.

        Returns:
            list[pystac.Item]: A list of matching STAC items.
        """
        raise NotImplementedError("search_items must be implemented by subclasses.")

    def _open_client(self, modifier: Callable | None = None, headers: dict | None = None) -> Client:
        """Open connection to STAC API."""
        try:
            return Client.open(self.api_url, modifier=modifier, headers=headers)
        except Exception as e:
            logger.error(f"Failed to open STAC client: {e}")
            raise ConnectionError(f"Failed to connect to STAC API at {self.api_url}") from e

    def _search(
        self,
        start_date: str | None,
        end_date: str | None,
        geometry: BaseGeometry | None = None,
        query: dict | None = None,
        modifier: Callable | None = None,
        headers: dict | None = None,
        sort: bool = True,
    ) -> list[pystac.Item]:
        """
        Searches the STAC API with provided parameters and returns a list of items.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            geometry: Geometry for the intersection query. Defaults to None.
            query: Additional query parameters. Defaults to None.
            modifier: Function to modify the request. Defaults to None.
            headers: HTTP headers for the request. Defaults to None.
            sort: Flag to sort the results based on the date. Defaults to True.

        Returns:
            list[pystac.Item]: A list of STAC items that match the query.

        Raises:
            ValueError: If the datetime range is invalid.
            RuntimeError: If the request to the STAC API fails.
        """
        if start_date and end_date and start_date > end_date:
            raise ValueError("The start_date must be before the end_date.")

        logger.debug(f"Searching STAC API for satellite: {self.satellite}")

        try:
            client = self._open_client(modifier=modifier, headers=headers)
            search_params: dict[str, Any] = {
                "collections": [self.collection],
                "intersects": geometry,
                "query": query,
                "limit": 100,
            }
            if start_date and end_date:
                search_params["datetime"] = f"{start_date}/{end_date}"

            items = client.search(**search_params).item_collection()

        except Exception as e:
            logger.error(f"Error searching STAC API: {e}")
            raise RuntimeError("Failed to perform search on STAC API") from e

        if sort:
            sorted_items = sorted(
                items, key=lambda x: self._parse_date(x.properties.get("datetime"))
            )
            return list(sorted_items)

        logger.info(f"Found {len(items)} items for {self.satellite} matching the search query.")
        return list(items)

    @staticmethod
    def _get_epsg(items: list[pystac.Item], epsg: int | None) -> int:
        """
        Return an EPSG value either from that provided, or from the most common CRS in the STAC item
        list.

        Args:
            items: List of STAC items.
            epsg: EPSG code.

        Returns:
            int: The determined EPSG code.
        """
        if epsg is not None:
            return epsg

        epsg_values = []
        for item in items:
            epsg_code = item.properties.get("proj:epsg") or item.properties.get("proj:code")
            if epsg_code:
                if isinstance(epsg_code, str) and epsg_code.startswith("EPSG:"):
                    epsg_code = int(epsg_code.split(":")[-1])
                epsg_values.append(epsg_code)

        if not epsg_values:
            raise ValueError("No EPSG code found in STAC items and no default EPSG was provided.")

        return Counter(epsg_values).most_common(1)[0][0]

    @staticmethod
    def _get_clipping_geometry(
        geometry: BaseGeometry, epsg: int, resolution: int, clip_method: str, pixels: int
    ) -> BaseGeometry:
        """
        Process the geometry for clipping, projecting to a given EPSG for window buffering.

        Args:
            geometry: Input geometry in EPSG:4326.
            epsg: The target EPSG code for projection and buffering.
            resolution: Pixel resolution in meters.
            clip_method: Clipping method, either "geometry" or "window".
            pixels: The number of pixels to buffer for the "window" method.

        Returns:
            BaseGeometry: The processed clipping geometry in EPSG:4326.
        """
        if clip_method == "geometry":
            return geometry

        if clip_method == "window":
            # Project, buffer, and project back
            projected_geom = geometry_from_epsg_to_epsg(geometry, WGS84_EPSG, epsg)
            buffered_geom = projected_geom.centroid.buffer((0.5 * pixels) * resolution, cap_style=3)
            return geometry_from_epsg_to_epsg(buffered_geom, epsg, WGS84_EPSG)

        return geometry

    def create_image(
        self,
        items: list[pystac.Item],
        bands: list[str],
        resolution: Optional[int] = None,
        epsg: Optional[int] = None,
        geometry: Optional[BaseGeometry] = None,
        clip_method: str = "geometry",
        pixels: int = 0,
        dtype: Optional[Union[np.dtype, T]] = None,
        fill_value: Optional[Union[int, float]] = None,
        resampling: Resampling = Resampling.nearest,
        skip_inconsistent_items: bool = False,
        groupby: Optional[Literal["solar_day"]] = None,
        rescale: bool = False,
    ) -> xarray.Dataset:
        """
        Creates an xarray Dataset from a list of STAC items.

        Items typically store their assets in the local projected CRS. But some collections store
        the assets in EPSG:4326. To make the image creation compatible across collections, images
        that are in EPSG:4326 are converted to the local projected CRS using the provided geometry,
        and also returned in the projected CRS. If no geometry is provided, images are returned in
        EPSG:4326.

        Args:
            items: List of STAC items to process.
            bands: List of asset (band) names to include.
            resolution: Output resolution in meters. Defaults to satellite default.
            epsg: Output EPSG code. Defaults to the most common from items.
            geometry: Geometry to clip the output. Defaults to None.
            clip_method: Clipping method, "geometry" or "window". Defaults to "geometry".
            pixels: Pixel size for "window" clipping. Defaults to 0.
            dtype: Numpy datatype for the output array. Defaults to satellite default.
            fill_value: Fill value for nodata pixels. Defaults to satellite default.
            resampling: Resampling method. Defaults to Resampling.nearest.
            skip_inconsistent_items: If True, skips items missing requested bands.
                Defaults to False.
            groupby: Grouping for `odc-stac` backend. Defaults to None.
            rescale: Whether to rescale data. Defaults to False.

        Returns:
            xarray.Dataset: The stacked and processed image data.
        """
        if not items:
            raise ValueError("No STAC items provided to create an image.")

        if self.band_mapping:
            bands = [self.band_mapping.get(band, band) for band in bands]

        settings = get_settings()

        # Set defaults from settings if not provided
        resolution = resolution or settings.resolution_mapping[self.satellite]
        if dtype is None:
            dtype = np.dtype(settings.dtype_dict[self.satellite][0])
        else:
            dtype = np.dtype(dtype)

        if fill_value is None:
            fill_value = settings.dtype_dict[self.satellite][1]
        else:
            fill_value = fill_value

        logger.debug(
            f"Loading {len(items)} items for {self.satellite} at {resolution}m resolution."
        )

        # Determine output EPSG if not explicitly provided
        collection_id = items[0].collection_id
        if not epsg:
            native_epsg = self._get_epsg(items=items, epsg=epsg)
            if native_epsg == WGS84_EPSG and geometry and self.reproject_wgs84_to_utm:
                epsg = get_utm_epsg(lon=geometry.centroid.x, lat=geometry.centroid.y)
                logger.warning(
                    f"Assets in collection `{collection_id}` stored in EPSG:{WGS84_EPSG}, "
                    f"but will be re-projected to EPSG:{epsg} for clipping and image creation."
                )
            else:
                epsg = native_epsg

        # Avoid triggering reprojection in odc.stac.load when data is already in target CRS
        native_epsg = self._get_epsg(items=items, epsg=None)
        use_native_crs = epsg == native_epsg
        crs = None if use_native_crs else f"EPSG:{epsg}"

        # Use native COG resolution if requested by subclass (e.g. CopDEM30)
        load_resolution = None if self.use_native_resolution else resolution

        geometry_proj = None
        geometry_geo = None
        if geometry:
            geometry_geo = self._get_clipping_geometry(
                geometry=geometry,
                epsg=epsg,
                resolution=resolution,
                clip_method=clip_method,
                pixels=pixels,
            )
            geometry_proj = geometry_from_epsg_to_epsg(geometry_geo, WGS84_EPSG, epsg)

        # Load data using odc.stac
        out = odc.stac.load(
            items,
            bands,
            crs=crs,
            resolution=load_resolution,
            geopolygon=geometry_geo if geometry else None,
            resampling=resampling.name.lower(),
            dtype=dtype,
            rescale=rescale,
            fail_on_error=not skip_inconsistent_items,
            groupby=groupby,
            nodata=fill_value,
            chunks={"x": 1024, "y": 1024},
            anchor="floating",  # required to get correct pixel size from window clipping
        )

        if isinstance(out, xarray.DataArray):
            out = out.to_dataset(dim="band")

        if geometry_proj:
            out = out.rio.clip([geometry_proj])

        return out

    def search_and_create_image(
        self,
        start_date: str,
        end_date: str,
        bands: list[str],
        geometry: Optional[BaseGeometry] = None,
        query: Optional[dict] = None,
        sort: bool = True,
        resolution: Optional[int] = None,
        epsg: Optional[int] = None,
        clip_method: str = "geometry",
        pixels: int = 0,
        dtype: Optional[Union[np.dtype, T]] = None,
        fill_value: Optional[Union[int, float]] = None,
        resampling: Resampling = Resampling.nearest,
        skip_inconsistent_items: bool = False,
        groupby: Optional[Literal["solar_day"]] = None,
        **kwargs,
    ) -> xarray.Dataset:
        """
        High-level wrapper to search for STAC items and create an image.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            bands: List of band names to retrieve.
            geometry: Geometry to clip the dataset. Defaults to None.
            query: Additional query parameters for the search. Defaults to None.
            sort: Whether to sort items by date. Defaults to True.
            resolution: Output resolution in meters. Defaults to satellite default.
            epsg: Output EPSG code. Defaults to auto-detection.
            clip_method: Clipping method, "geometry" or "window". Defaults to "geometry".
            pixels: Pixel size for "window" clipping. Defaults to 0.
            dtype: Numpy datatype for the output. Defaults to satellite default.
            fill_value: Fill value for nodata pixels. Defaults to satellite default.
            resampling: Resampling method. Defaults to Resampling.nearest.
            skip_inconsistent_items: If True, skips items missing requested bands.
                Defaults to False.
            groupby: Grouping for `odc-stac` backend. Defaults to None.

        Returns:
            xarray.Dataset: The resulting image data.
        """
        search_geometry = geometry
        # If clipping to a window, buffer the search geometry to ensure all relevant items are found
        if geometry and clip_method == "window":
            # Determine EPSG from geometry for accurate buffering
            temp_epsg = get_utm_epsg(lon=geometry.centroid.x, lat=geometry.centroid.y)
            res = resolution or get_settings().resolution_mapping[self.satellite]
            search_geometry = self._get_clipping_geometry(
                geometry=geometry,
                epsg=temp_epsg,
                resolution=res,
                clip_method=clip_method,
                pixels=pixels,
            )

        items = self.search_items(
            start_date=start_date,
            end_date=end_date,
            geometry=search_geometry,
            query=query,
            sort=sort,
            **kwargs,
        )

        return self.create_image(
            items=items,
            bands=bands,
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
            rescale=False,
        )

    def _parse_date(self, date_string: str | None) -> datetime:
        """Parse the datestring with support for multiple ISO 8601 formats,
        including timezone offsets.

        Args:
            date_string: Date string.

        Returns:
            datetime: Parsed datetime object.
        """
        if date_string is None:
            return datetime.min

        try:
            # Try parsing ISO 8601 strings with `+00:00` timezone
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except ValueError:
            # Fall back to explicitly defined formats
            try:
                return datetime.strptime(
                    date_string, "%Y-%m-%dT%H:%M:%S.%fZ"
                )  # Microseconds included
            except ValueError:
                try:
                    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")  # No microseconds
                except ValueError as e:
                    # Log unexpected formats for debugging
                    logger.error(f"Failed to parse datetime: '{date_string}'. Error: {e}")
                    raise
