import logging.config

from sat_data_acquisition.config.settings import get_settings

# Get settings
settings = get_settings()

# Ensure the error log directory exists
error_log_path = settings.log_path / "errors" / "error_log.txt"
error_log_path.parent.mkdir(parents=True, exist_ok=True)


def configure_logging(verbose: bool = False):
    """Configure logging with appropriate verbosity level."""
    console_level = "DEBUG" if verbose else "INFO"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s-%(levelname)s-%(name)s:%(funcName)s:%(lineno)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
            "simple": {
                "format": "%(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "level": console_level,
                "class": "logging.StreamHandler",
                "formatter": "simple" if not verbose else "standard",
            },
            "error_file_handler": {
                "level": "ERROR",
                "class": "logging.FileHandler",
                "formatter": "standard",
                "filename": str(error_log_path),
                "mode": "a",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "WARNING",  # Suppress noisy third-party logs
            },
            "sat_data_acquisition": {
                "handlers": ["console", "error_file_handler"],
                "propagate": False,
                "level": console_level,
            },
            # Suppress noisy dependencies
            "rasterio": {"level": "WARNING"},
            "fiona": {"level": "WARNING"},
            "odc": {"level": "WARNING"},
            "urllib3": {"level": "WARNING"},
            "boto3": {"level": "WARNING"},
            "botocore": {"level": "WARNING"},
        },
    }

    logging.config.dictConfig(logging_config)


def get_logger(name, verbose: bool = False):
    """Get a logger with appropriate configuration."""
    configure_logging(verbose)
    return logging.getLogger(name)
