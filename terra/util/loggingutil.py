import logging
from pathlib import Path
from terra.resources.assetloading import AssetType, get_asset

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")


# Check if the logging directory exists, creating it if it doesn't
def check_log_dir_exists():
    path = Path(get_asset(AssetType.LOG))
    if not path.exists():
        path.mkdir(exist_ok=True)


# Create and return a new logger
def get_logger(name, level, filename):
    handler = logging.FileHandler(get_asset(AssetType.LOG, filename))
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
