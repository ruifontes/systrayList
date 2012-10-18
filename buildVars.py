
# Build customizations
# Change this file instead of sconstruct, whenever possible.

import os.path

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
pythonSources = [os.path.join("addon", "globalPlugins", "systrayList", "*.py"), os.path.join("addon", "installTasks.py")]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources 

