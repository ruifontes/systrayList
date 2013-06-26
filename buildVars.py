# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)
_ = lambda x : x

# Add-on information variables
addon_info = {
	# add-on Name
	"addon-name" : "systrayList",
	# Add-on description
	# TRANSLATORS: Summary for this add-on to be shown on installation and add-on informaiton.
	"addon-summary" : _("sysTrayList - list sys tray and task bar elements"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on installation and add-on information
	"addon-description" : _("""Shows the list of buttons on the System Tray with NVDA+F11 once, twice shows running task lists."""),
	# version
	"addon-version" : "2.0-dev",
	# Author(s)
	"addon-author" : "Rui Fontes <rui.fontes@tiflotecnia.com>, Rui Batista <ruiandrebatista@gmail.com>, NVDA Community Contributors",
	# URL for the add-on documentation support
	"addon-url" : "http://addons.nvda-project.org"
}

import os.path

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
pythonSources = [os.path.join("addon", "globalPlugins", "systrayList", "*.py"), os.path.join("addon", "installTasks.py")]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = []
