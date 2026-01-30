"""Custom exceptions for SatData satellite data retrieval."""


class SatDataError(Exception):
    """Base exception for all SatData errors."""

    pass


class ConfigurationError(SatDataError):
    """Raised when there's a configuration problem."""

    pass


class STACSearchError(SatDataError):
    """Raised when STAC search fails."""

    pass


class ImageCreationError(SatDataError):
    """Raised when image creation from STAC fails."""

    pass


class BandValidationError(SatDataError):
    """Raised when band validation fails."""

    pass


class GeometryError(SatDataError):
    """Raised when there's a geometry-related problem."""

    pass


class SaveError(SatDataError):
    """Raised when saving output fails."""

    pass


class UnsupportedSatelliteError(SatDataError):
    """Raised when an unsupported satellite is requested."""

    pass
