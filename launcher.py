# Launcher for the game.
# When compiled into an executable, this file takes the place of the executable in the directory structure.
from terra.main import Main
from terra.managers.errorlogger import ERROR_LOGGER


try:
    Main().run()
except Exception as err:
    ERROR_LOGGER.exception("Caught exception in the launcher.", err)

    # Still allow the exception to propagate normally
    raise err
