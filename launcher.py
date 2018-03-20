# Launcher for the game.
# When compiled into an executable, this file takes the place of the executable in the directory structure.

from terra.main import Main
from terra.managers.managers import Managers

try:
    Main().run()
except Exception as err:
    Managers.error_logger.error("!=== Caught a fatal exception: ===!")
    Managers.error_logger.error("Exception: {}".format(err))
