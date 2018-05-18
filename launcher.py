# Launcher for the game.
# When compiled into an executable, this file takes the place of the executable in the directory structure.
from sys import exc_info

from terra.main import Main
from terra.managers.errorlogger import ERROR_LOGGER

try:
    Main().run()
except Exception as err:
    ERROR_LOGGER.exception("Caught exception in the launcher.", err)

    # Allow the exception to propagate normally
    exc = exc_info()
    raise exc[0].with_traceback(exc[1], exc[2])
