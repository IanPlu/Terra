# Launcher for the game.
# When compiled into an executable, this file takes the place of the executable in the directory structure.

import traceback

from terra.main import Main
from terra.managers.managers import Managers

try:
    Main().run()
except Exception as err:
    stacktrace = "\n".join(traceback.format_tb(err.__traceback__))

    Managers.error_logger.error("!=== Caught a fatal exception: ===!")
    Managers.error_logger.error("Exception: \n{}".format(stacktrace))

    # Still allow the exception to propagate normally
    raise err
