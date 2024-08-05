import os
from sharedtoolbox import configs
from sharedtoolbox.core import eventHandler, stdHandler

event_handler = eventHandler.EventHandler()
std_out_handler = stdHandler.StdOutHandler(event_handler) 
std_err_handler = stdHandler.StdErrHandler(event_handler) 

configs.Prefs()

# Temporary config
os.environ['SHAREDTOOLBOX_PROJECT_ROOT'] = r'C:\Users\Michael\AppData\Roaming\sharedtoolbox\projects'

# Create config file
if not os.path.exists(configs.PREFS_FILE_PATH):
    if not os.path.exists(os.path.dirname(configs.PREFS_FILE_PATH)):
        os.makedirs(os.path.dirname(configs.PREFS_FILE_PATH))
    with open(configs.PREFS_FILE_PATH, 'w') as f:
        f.write('{}')
