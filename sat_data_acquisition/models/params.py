import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import List, Literal, Optional, Union

import geopandas as gpd
import numpy as np

from sat_data_acquisition.config.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


def get_default_bands(satellite: str) -> List[str]:
    """
    Returns the default bands for the given satellite.

    Args:
        satellite (str): The satellite identifier.

    Returns:
        List[str]: List of default bands for the specified satellite.

    Raises:
        ValueError: If no default bands are defined for the satellite.
    """
    default_bands = settings.default_bands
    if satellite in default_bands:
        bands: List[str] = default_bands[satellite]
        return bands
    else:
        raise ValueError(f"No default bands defined for satellite: {satellite}")


@dataclass
class ProcessingParams:
    """
    Parameters for processing satellite images.

    Attributes:
        satellite: The satellite or dataset identifier. Supported values:
            - S2MPC: Sentinel-2 from Microsoft Planetary Computer
            - S2E84: Sentinel-2 from Element84
            - S1MPC: Sentinel-1 from Microsoft Planetary Computer
            - LANDSATMPC: Landsat from Microsoft Planetary Computer
            - HLS_LANDSAT: Harmonized Landsat Sentinel (Landsat)
            - HLS_SENTINEL: Harmonized Landsat Sentinel (Sentinel-2)
            - CopDEM30MPC: Copernicus DEM 30m from Microsoft Planetary Computer
        search_method: The search method to use ('geometry' or 'tile').
        start_date: The start date for the image search (YYYY-MM-DD). Defaults to None.
        end_date: The end date for the image search (YYYY-MM-DD). Defaults to None.
        tile: The tile identifier (e.g., MGRS tile), required if search_method is 'tile'.
        bands: List of band names to include in the image.
            Defaults to None, which uses the default bands for the satellite defined in settings.
        cloud_coverage: The maximum cloud coverage for the search. Defaults to 25%.
        sort: Whether to sort the search results by date. Defaults to True.
        clip_method: The clipping method to use ('geometry' or 'window'). Defaults to 'geometry'.
        pixels: The pixel size for the 'window' clip method. Defaults to 256.
        dtype: Data type to save the image as. Defaults to None.
        fill_value: Value to fill missing data. Defaults to None.
        groupby: Grouping method for odc-stac. Use 'solar_day' to merge overlapping satellite
            tiles from the same day (recommended). Defaults to 'solar_day'.
    """

    satellite: Literal[
        "S2MPC",
        "S1MPC",
        "S2E84",
        "LANDSATMPC",
        "HLS_LANDSAT",
        "HLS_SENTINEL",
        "CopDEM30MPC",
    ]
    search_method: Literal["geometry", "tile"]
    start_date: Union[str, date, None] = None
    end_date: Union[str, date, None] = None
    tile: Optional[str] = None
    bands: List[str] = field(default_factory=list)
    cloud_coverage: int = 25
    sort: bool = True
    clip_method: Literal["geometry", "window"] = "geometry"
    pixels: int = 256
    dtype: Optional[Union[np.dtype, str]] = None
    fill_value: Optional[int] = None
    groupby: Optional[Literal["solar_day"]] = "solar_day"  # Merge overlapping tiles by solar day

    def __post_init__(self):
        if not self.bands:
            self.bands = get_default_bands(self.satellite)

    def load_gdf(
        self, file_path: str, row_slice: Optional[slice] = None
    ) -> Optional[gpd.GeoDataFrame]:
        """
        Load the GeoDataFrame if the search method is 'geometry'.

        Args:
            file_path: Path to the GeoJSON file.
            row_slice: Optional slice to apply to the GeoDataFrame.

        Returns:
            Loaded GeoDataFrame or None if not applicable.
        """
        if self.search_method == "geometry":
            try:
                gdf = gpd.read_file(file_path)
                if row_slice is not None:
                    gdf = gdf.iloc[row_slice]
                return gdf
            except FileNotFoundError:
                logger.error("GeoJSON file not found. Please ensure the file path is correct.")
        return None

    @staticmethod
    def usage():
        """Prints detailed information about each parameter and its usage."""
        print(str(ProcessingParams.__doc__))


@dataclass
class SaveParams:
    """
    Parameters for saving processed images.

    Attributes:
        output_path: Path to save the output locally. Defaults to None,
            which uses the default path from settings.
        s3_bucket: S3 bucket name for uploads. Defaults to None (no S3 upload).
        s3_path: S3 path prefix within bucket. Defaults to "sat_data_acquisition".
        save_to_local: Flag to save the file locally. Defaults to True.
        save_to_s3: Flag to save the file to S3. Defaults to False.
        merge_bands: Flag to merge bands into a single image. Defaults to True.
        save_as_geotiff: Flag to save the image as GeoTIFF. Defaults to True.
        save_as_numpy: Flag to save the image as numpy file. Defaults to False.
        enable_compression: Flag to enable DEFLATE compression for TIF files. Defaults to True.
        detailed_report: Flag to enable detailed profiling report. Defaults to False.
        custom_naming: Custom naming convention for saved files. This is a format string
            that can include placeholders for variables.
            For example: '{date}/{satellite}_{band_id}_{field_id}_{clip_method}.tif'.
        num_processes: Specify the number of cpu's to use for this processing task.
            Defaults to None (uses cpu_count - 1).
        verbose: Enable verbose logging. Defaults to False.
    """

    output_path: Optional[Path] = None
    s3_bucket: Optional[str] = None
    s3_path: str = "sat_data_acquisition"
    save_to_local: bool = True
    save_to_s3: bool = False
    merge_bands: bool = True
    save_as_geotiff: bool = True
    save_as_numpy: bool = False
    file_format: str = "geotiff"
    identifier_type: str = "area_name"
    enable_compression: bool = True
    detailed_report: bool = False
    custom_naming: Optional[str] = None
    num_processes: Optional[int] = None
    verbose: bool = False

    def __post_init__(self):
        # Set default output path from settings if not provided
        if self.output_path is None:
            self.output_path = get_settings().output_path

        # Set default S3 bucket from settings if not provided but S3 upload requested
        if self.save_to_s3 and self.s3_bucket is None:
            self.s3_bucket = get_settings().s3_bucket
            if self.s3_bucket is None:
                raise ValueError(
                    "S3 bucket must be specified either in SaveParams.s3_bucket or "
                    "SAT_DATA_S3_BUCKET environment variable when save_to_s3=True"
                )

    @staticmethod
    def usage():
        """Prints detailed information about each parameter and its usage."""
        print(str(SaveParams.__doc__))
