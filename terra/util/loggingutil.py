import logging
import os
from terra.resources.assets import AssetType, get_asset

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")


# Check if the logging directory exists, creating it if it doesn't
def check_log_dir_exists():
    if not os.path.isdir(get_asset(AssetType.LOG, "")):
        os.mkdir(AssetType.LOG.value)


# Create and return a new logger
def get_logger(name, level, filename):
    handler = logging.FileHandler(get_asset(AssetType.LOG, filename))
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
