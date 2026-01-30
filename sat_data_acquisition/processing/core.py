"""
Core processing functionality for batch satellite imagery operations.
"""

import logging
import multiprocessing as mp
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import geopandas as gpd
from tqdm import tqdm

from sat_data_acquisition.config.settings import SatDataSettings
from sat_data_acquisition.models.params import ProcessingParams, SaveParams
from sat_data_acquisition.processing.save import save_geotiff, save_numpy

logger = logging.getLogger(__name__)


def process_single_item(
    geometry_info: tuple,
    processing_params: ProcessingParams,
    save_params: SaveParams,
    settings: SatDataSettings,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Process a single geometry item (field, tile, etc.).

    Args:
        geometry_info: Tuple of (identifier, geometry, row_dict) from GeoDataFrame iteration.
        processing_params: Parameters for data retrieval and processing.
        save_params: Parameters for saving output files.
        settings: SatData configuration settings.
        verbose: Enable verbose logging for this process.

    Returns:
        Dictionary with processing results and status.
    """
    identifier, geometry, row_dict = geometry_info

    try:
        # Import inside function for multiprocessing compatibility
        from sat_data_acquisition.config.logging import configure_logging
        from sat_data_acquisition.core.stac_client import SatDataClient

        # Configure logging for this process
        if not verbose:
            configure_logging(verbose=False)

        client = SatDataClient(settings=settings)

        # Get images
        images = client.search_and_create_image(
            geometry=geometry,
            processing_params=processing_params,
        )

        if not images:
            logger.warning(f"No images found for {identifier}")
            return {
                "identifier": identifier,
                "status": "no_data",
                "error": None,
                "images_saved": 0,
            }

        # Save images
        images_saved = 0
        for image_result in images:
            # Cast to Any to access get() on Hashable/Any
            res: Any = image_result
            image = res.get("image")
            datetime = str(res.get("datetime"))
            satellite = processing_params.satellite
            provider = str(res.get("provider", "unknown"))

            if image is None:
                continue

            output_path: str = str(save_params.output_path) if save_params.output_path else ""

            # Save based on format
            if save_params.file_format == "geotiff":
                save_geotiff(
                    image=image,
                    identifier=identifier,
                    datetime=datetime,
                    satellite=satellite,
                    provider=provider,
                    band=processing_params.bands[0] if processing_params.bands else None,
                    output_path=output_path,
                    save_to_local=save_params.save_to_local,
                    identifier_type=save_params.identifier_type,
                    enable_compression=save_params.enable_compression,
                    settings=settings,
                    custom_naming=save_params.custom_naming,
                    merge_bands=save_params.merge_bands,
                    save_to_s3=save_params.save_to_s3,
                    s3_bucket=save_params.s3_bucket,
                    s3_path=save_params.s3_path,
                )
            elif save_params.file_format == "numpy":
                save_numpy(
                    image=image,
                    identifier=identifier,
                    datetime=datetime,
                    satellite=satellite,
                    provider=provider,
                    band=processing_params.bands[0] if processing_params.bands else "",
                    output_path=output_path,
                    save_to_local=save_params.save_to_local,
                    identifier_type=save_params.identifier_type,
                    settings=settings,
                    custom_naming=save_params.custom_naming,
                    merge_bands=save_params.merge_bands,
                    save_to_s3=save_params.save_to_s3,
                    s3_bucket=save_params.s3_bucket,
                    s3_path=save_params.s3_path,
                )

            images_saved += 1

        return {
            "identifier": identifier,
            "status": "success",
            "error": None,
            "images_saved": images_saved,
        }

    except Exception as e:
        logger.error(f"Error processing {identifier}: {e}", exc_info=verbose)
        return {
            "identifier": identifier,
            "status": "error",
            "error": str(e),
            "images_saved": 0,
        }


def process_batch(
    geometries: Union[gpd.GeoDataFrame, List[tuple]],
    processing_params: ProcessingParams,
    save_params: SaveParams,
    settings: Optional[SatDataSettings] = None,
    n_workers: Optional[int] = None,
    verbose: bool = False,
) -> List[Dict[str, Any]]:
    """
    Process multiple geometries in parallel with progress tracking.

    Args:
        geometries: GeoDataFrame with geometries to process or list of
            (identifier, geometry, row_dict) tuples.
        processing_params: Parameters for data retrieval and processing.
        save_params: Parameters for saving output files.
        settings: SatData configuration settings (defaults to SatDataSettings()).
        n_workers: Number of parallel workers (defaults to cpu_count - 1, min 1).
        verbose: Enable verbose logging.

    Returns:
        List of result dictionaries for each processed item.
    """
    if settings is None:
        settings = SatDataSettings()

    # Prepare geometry items
    if isinstance(geometries, gpd.GeoDataFrame):
        # Convert GeoDataFrame to list of tuples
        geometry_items: List[tuple] = [
            (str(row.get("field_id", f"field_{idx}")), row["geometry"], row.to_dict())
            for idx, row in geometries.iterrows()
        ]
    else:
        geometry_items = geometries

    total_items = len(geometry_items)

    if total_items == 0:
        logger.warning("No geometries to process")
        return []

    # Determine number of workers
    if n_workers is None:
        cpu_count = mp.cpu_count()
        n_workers = max(1, cpu_count - 1)  # Leave one CPU free

    logger.info(f"Processing {total_items} items with {n_workers} workers")

    # Create partial function with fixed parameters
    process_func = partial(
        process_single_item,
        processing_params=processing_params,
        save_params=save_params,
        settings=settings,
        verbose=verbose,
    )

    # Process with multiprocessing and progress bar
    results = []

    if n_workers == 1:
        # Single-threaded for debugging
        for item in tqdm(geometry_items, desc="Processing", disable=not verbose):
            result = process_func(item)
            results.append(result)
    else:
        # Multiprocessing
        with mp.Pool(processes=n_workers) as pool:
            results = list(
                tqdm(
                    pool.imap(process_func, geometry_items),
                    total=total_items,
                    desc="Processing fields",
                    unit="field",
                )
            )

    # Summary statistics
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    no_data_count = sum(1 for r in results if r["status"] == "no_data")
    total_images = sum(r["images_saved"] for r in results)

    logger.info(
        f"Processing complete: {success_count} succeeded, {error_count} errors, "
        f"{no_data_count} no data, {total_images} total images saved"
    )

    return results


def create_output_structure(
    base_path: Union[str, Path],
    satellite: str,
    file_format: str = "geotiff",
) -> Path:
    """
    Create standardized output directory structure.

    Args:
        base_path: Base output directory path.
        satellite: Satellite name (e.g., "S2E84", "LANDSATMPC").
        file_format: Output file format ("geotiff" or "numpy").

    Returns:
        Path object for the created directory.
    """
    base_path = Path(base_path)
    output_path = base_path / satellite / file_format
    output_path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Created output structure: {output_path}")
    return output_path
