import logging
import traceback

from terra.util.loggingutil import get_logger, check_log_dir_exists


# Logs errors or crashes that occur during the operation of the game.
class ErrorLogger:
    def __init__(self):
        super().__init__()

        filename = "error.log"
        check_log_dir_exists()
        self.logger = get_logger("ErrorLogger", logging.INFO, filename)

    def error(self, error):
        self.logger.error("[ERROR]: {}".format(error))

    def warn(self, error):
        self.logger.warning("[WARN]: {}".format(error))

    # Log an exception + traceback/stacktrace.
    def exception(self, context, exc):
        self.error(context)
        stacktrace = "\n".join(traceback.format_tb(exc.__traceback__))
        self.error("!=== Caught a fatal exception: ===!")
        self.error("Exception: \n{}\n{}".format(exc, stacktrace))


# Import and use this instead of creating a new ErrorLogger.
ERROR_LOGGER = ErrorLogger()
