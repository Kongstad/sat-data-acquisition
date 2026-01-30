import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Optional, Union

import numpy as np
import xarray

from sat_data_acquisition.processing.utils import TypeUtils, get_native_band_name

logger = logging.getLogger(__name__)

# Conditional boto3 import
try:
    import boto3

    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
    logger.warning("boto3 not available. S3 uploads will be disabled.")


def save_file(
    local_path: Path,
    save_to_local: bool,
    save_function: Callable[[Union[str, Path]], None],
    save_to_s3: bool = False,
    s3_bucket: Optional[str] = None,
    s3_path: str = "",
    output_path: Optional[Path] = None,
) -> None:
    """
    Save files locally and/or to S3, preserving folder structure.

    Args:
        local_path: Path to save the file locally.
        save_to_local: Flag to save the file locally.
        save_function: Function to save the file.
        save_to_s3: Flag to save the file to S3 storage.
        s3_bucket: S3 bucket name.
        s3_path: Base path in S3 bucket.
        output_path: Base output path for computing relative paths.
    """
    # Create the directory structure if saving locally
    if save_to_local:
        os.makedirs(local_path.parent, exist_ok=True)

    # Decide the file path to use (local or temporary)
    file_path = local_path if save_to_local else Path(tempfile.mktemp(suffix=local_path.suffix))

    try:
        # Save the file using the provided function
        save_function(file_path)

        # Log for local saving
        if save_to_local:
            logger.debug(f"Saved to: {local_path}")

        # Upload to S3
        if save_to_s3:
            if not HAS_BOTO3:
                logger.error("boto3 is required for S3 uploads. Install with: pip install boto3")
                raise ImportError("boto3 not available")

            if not s3_bucket:
                raise ValueError("s3_bucket must be specified when save_to_s3=True")

            # Compute relative path for S3
            if output_path:
                relative_path = str(local_path.relative_to(output_path))
            else:
                relative_path = local_path.name

            s3_object_key = f"{s3_path.strip('/')}/{relative_path}"

            s3_client = boto3.client("s3")
            s3_client.upload_file(str(file_path), s3_bucket, s3_object_key)
            logger.info(f"Uploaded to S3: s3://{s3_bucket}/{s3_object_key}")

    finally:
        # Clean up temporary file if it exists and not saving locally
        if not save_to_local and file_path and file_path.exists():
            os.remove(file_path)
            logger.debug("Cleaned up temporary file")


def save_image(
    identifier: str,
    datetime: str,
    satellite: str,
    band: str,
    output_path: str,
    save_to_local: bool,
    file_type: str,
    save_function: Callable[[Union[str, Path]], None],
    settings: Any,
    custom_naming: Optional[str] = None,
    merge_bands: bool = False,
    save_to_s3: bool = False,
    s3_bucket: Optional[str] = None,
    s3_path: str = "",
    **kwargs,
) -> None:
    """
    Save images as GeoTIFF or numpy files.

    Args:
        identifier: Area name, field ID, or tile ID associated with the image.
            For ad-hoc queries without a name, use a generic identifier like "area".
        datetime: Date and time of the image.
        satellite: Satellite identifier.
        band: Band identifier.
        output_path: Path to save the output.
        save_to_local: Flag to save the file locally.
        file_type: Type of file to save ('tiff' or 'npy').
        save_function: Function to save the file.
        settings: Settings object.
        custom_naming: Custom naming convention for saved files.
        merge_bands: Flag to indicate if bands are merged.
    """
    datetime = TypeUtils.ensure_string(datetime)
    identifier = TypeUtils.ensure_string(identifier) if identifier else "area"

    if datetime.lower() == "nan":
        logger.error(f"Encountered nan date for identifier {identifier}. Skipping save.")
        return

    file_ext = "tif" if file_type == "tiff" else "npy"
    band = "merged" if merge_bands else band

    date = datetime.split("T")[0]
    naming_params = {
        "datetime": datetime,
        "date": date,
        "band_id": band,
        "area_name": identifier,
        "satellite": satellite,
        "file_type": file_ext,
        **kwargs,
    }

    if custom_naming:
        file_name = custom_naming.format(**naming_params)
        local_path = Path(f"{output_path}/{file_name}")
        logger.info(f"Using custom naming: {file_name}")
    else:
        # Include identifier in filename only if provided
        if identifier and identifier != "area":
            file_name = f"{satellite}_{date}_{band}_{identifier}.{file_ext}"
        else:
            file_name = f"{satellite}_{date}_{band}.{file_ext}"
        subfolder = f"{satellite}/{date[:4]}/{file_type}"
        local_path = Path(f"{output_path}/{subfolder}/{file_name}")
        logger.debug(f"Using default naming: {file_name}")

    save_file(
        local_path=local_path,
        save_to_local=save_to_local,
        save_function=save_function,
        save_to_s3=save_to_s3,
        s3_bucket=s3_bucket,
        s3_path=s3_path,
        output_path=Path(output_path),
    )


def save_geotiff(
    image: Union[xarray.DataArray, xarray.Dataset],
    identifier: str,
    datetime: str,
    satellite: str,
    provider: str,
    output_path: str,
    save_to_local: bool,
    identifier_type: str,
    enable_compression: bool,
    settings: Any,
    band: Optional[str] = None,
    custom_naming: Optional[str] = None,
    merge_bands: bool = False,
    save_to_s3: bool = False,
    s3_bucket: Optional[str] = None,
    s3_path: str = "",
    **kwargs,
) -> None:
    """
    Save images as GeoTIFF, ensuring band names are preserved for datasets.

    Args:
        image: Image data to save (all bands in the dataset are saved).
        identifier: Field ID or Tile ID associated with the image.
        datetime: Date and time of the image.
        satellite: Satellite identifier.
        provider: Data provider identifier.
        output_path: Path to save the output.
        save_to_local: Flag to save the file locally.
        identifier_type: Type of identifier, either "field" or "tile".
        enable_compression: Flag to enable DEFLATE compression for TIF files.
        settings: Settings object.
        band: Optional band label for filename. If not provided, auto-generated from image bands.
        custom_naming: Custom naming convention for saved files.
        merge_bands: Flag to indicate if bands are merged.
    """

    def _save(path: Union[str, Path]) -> None:
        """Saves the GeoTIFF."""
        image_to_save = image
        if isinstance(image, xarray.Dataset):
            # Convert to DataArray
            image_to_save = image.to_array(dim="band")

        # Get nodata value from settings
        nodata_value = settings.dtype_dict.get(satellite, (None, None))[1]

        # Set the nodata attribute on the DataArray
        if nodata_value is not None:
            image_to_save.rio.write_nodata(nodata_value, inplace=True)

        compression = "DEFLATE" if enable_compression else "NONE"
        image_to_save.rio.to_raster(path, compress=compression, nodata=nodata_value)

    try:
        # Auto-generate band label if not provided
        if band is None:
            if isinstance(image, xarray.Dataset):
                bands_list = [str(b) for b in image.data_vars]
                band = "_".join(bands_list[:3]) + ("_etc" if len(bands_list) > 3 else "")
            else:
                band = "data"

        band_name = "merged" if merge_bands else get_native_band_name(band, satellite, settings)
        save_image(
            identifier=identifier,
            datetime=datetime,
            satellite=satellite,
            band=band_name,
            output_path=output_path,
            save_to_local=save_to_local,
            file_type="tiff",
            save_function=_save,
            settings=settings,
            custom_naming=custom_naming,
            merge_bands=merge_bands,
            save_to_s3=save_to_s3,
            s3_bucket=s3_bucket,
            s3_path=s3_path,
            provider=provider,
            identifier_type=identifier_type,
            **kwargs,
        )
        logger.debug(f"Saved GeoTIFF: {identifier} on {datetime}")
    except Exception as e:
        logger.error(f"Error saving GeoTIFF for {identifier} on {datetime}: {e}")
        raise


def save_numpy(
    image: Union[xarray.DataArray, xarray.Dataset],
    identifier: str,
    datetime: str,
    satellite: str,
    provider: str,
    band: str,
    output_path: str,
    save_to_local: bool,
    identifier_type: str,
    settings: Any,
    custom_naming: Optional[str] = None,
    merge_bands: bool = False,
    save_to_s3: bool = False,
    s3_bucket: Optional[str] = None,
    s3_path: str = "",
    **kwargs,
) -> None:
    """
    Save images as numpy files.

    Args:
        image: Image data to save.
        identifier: Field ID or Tile ID associated with the image.
        datetime: Date and time of the image.
        satellite: Satellite identifier.
        provider: Data provider identifier.
        band: Band identifier.
        output_path: Path to save the output.
        save_to_local: Flag to save the file locally.
        identifier_type: Type of identifier, either "field" or "tile".
        settings: Settings object.
        custom_naming: Custom naming convention for saved files.
        merge_bands: Flag to indicate if bands are merged.
    """
    band = get_native_band_name(band, satellite, settings) if not merge_bands else "merged"

    save_image(
        identifier=identifier,
        datetime=datetime,
        satellite=satellite,
        band=band,
        output_path=output_path,
        save_to_local=save_to_local,
        file_type="npy",
        save_function=lambda path: np.save(
            path,
            (image.to_array(dim="band") if isinstance(image, xarray.Dataset) else image).values,
        ),
        save_to_s3=save_to_s3,
        s3_bucket=s3_bucket,
        s3_path=s3_path,
        settings=settings,
        custom_naming=custom_naming,
        merge_bands=merge_bands,
        provider=provider,
        identifier_type=identifier_type,
        **kwargs,
    )
