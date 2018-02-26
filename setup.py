import os
import shutil

from cx_Freeze import setup, Executable

options = {
    'build_exe': {
        'includes': [
            'terra'
        ],
        'include_files': ['resources', 'logs']
    }
}

# Clear the log directory before building
shutil.rmtree('logs')
os.mkdir('logs')

setup(name="Terra",
      version="0.1",
      description="Terra game",
      options=options,
      executables=[Executable("launcher.py", base="Win32GUI")])
