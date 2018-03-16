import logging
import os

from terra.resources.assets import AssetType, get_asset
from terra.strings import phase_strings, LANGUAGE


# Logs errors or crashes that occur during the operation of the game
class ErrorLogger:
    def __init__(self):
        super().__init__()

        filename = "error.log"

        # Create the log dir if it doesn't exist
        if not os.path.isdir(get_asset(AssetType.LOG, "")):
            os.mkdir(AssetType.LOG.value)

        logging.basicConfig(format="%(message)s",
                            filename=get_asset(AssetType.LOG, filename),
                            level=logging.INFO)

    def error(self, error):
        logging.error("[ERROR]: {}".format(error))

    def warn(self, error):
        logging.warning("[WARN]: {}".format(error))
