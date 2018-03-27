# Launcher for the game.
# When compiled into an executable, this file takes the place of the executable in the directory structure.


from terra.main import Main
from terra.managers.managers import Managers

try:
    Main().run()
except Exception as err:
    Managers.error_logger.exception("Caught exception in the launcher.", err)

    # Still allow the exception to propagate normally
    raise err
