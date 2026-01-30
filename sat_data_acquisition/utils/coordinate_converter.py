from functools import lru_cache

import pyproj
import utm
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform

from sat_data_acquisition.config.logging import get_logger

logger = get_logger(__name__)


WGS84_EPSG = 4326
WGS84_PROJ4 = "+proj=longlat +datum=WGS84 +no_defs +type=crs"


@lru_cache(maxsize=4)
def get_transformer(in_epsg: int, out_epsg: int) -> pyproj.Transformer:
    """Get pyproj transformer to convert from one projection to another. Cache it as the same
    transformer might be used for multiple geometries.

    Args:
        in_epsg: Input EPSG code.
        out_epsg: Output EPSG code.

    Returns:
        pyproj.Transformer: Transformer object for coordinate transformation.
    """
    # Get the right CRS if the requested EPSG is 4326
    crs_from = pyproj.CRS(in_epsg) if in_epsg != WGS84_EPSG else WGS84_PROJ4
    crs_to = pyproj.CRS(out_epsg) if out_epsg != WGS84_EPSG else WGS84_PROJ4

    return pyproj.Transformer.from_crs(crs_from, crs_to)


def geometry_from_epsg_to_epsg(geometry: BaseGeometry, in_epsg: int, out_epsg: int) -> BaseGeometry:
    """Converts a geometry from one EPSG to another.

    Args:
        geometry: Geometry object to transform.
        in_epsg: Input EPSG code.
        out_epsg: Output EPSG code.

    Returns:
        BaseGeometry: Re-projected geometry.
    """
    transformer = get_transformer(in_epsg, out_epsg)

    # Errcheck will force to raise an error in case of wrong projection
    projection = transform(
        lambda x, y, z=None: transformer.transform(x, y, errcheck=True), geometry
    )

    return projection


def get_utm_epsg(lon: float, lat: float) -> int:
    """Determine the UTM EPSG code for a given lon/lat using the utm library.

    Args:
        lon: Longitude in degrees.
        lat: Latitude in degrees.

    Returns:
        int: UTM EPSG code.
    """
    _, _, zone_number, _ = utm.from_latlon(lat, lon)
    south = lat < 0
    epsg: int = 32700 + zone_number if south else 32600 + zone_number
    return epsg
