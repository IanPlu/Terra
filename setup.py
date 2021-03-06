import os
import zipfile

from cx_Freeze import setup, Executable

options = {
    'build_exe': {
        'includes': [
            'terra'
        ],
        'include_files': ['resources', 'logs'],
        'include_msvcr': True
    }
}

setup(name="Terra",
      version="0.1",
      description="Terra game",
      options=options,
      requires=['pygame', 'cx_Freeze', 'opensimplex'],
      executables=[Executable("launcher.py", base="Win32GUI")])

# Zip up the created file
zipf = zipfile.ZipFile('Terra.zip', 'w', zipfile.ZIP_DEFLATED)
for root, dirs, files in os.walk('build/'):
    for file in files:
        zipf.write(os.path.join(root, file))
zipf.close()
