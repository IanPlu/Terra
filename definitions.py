import sys
from pathlib import Path


# Determine the root directory. Asset loading will start from here.
if getattr(sys, 'frozen', False):
    # The application is frozen / packaged into an executable
    ROOT_DIR = Path(sys.executable).parent
else:
    # We're debugging or running unit tests
    ROOT_DIR = Path(__file__).parent
