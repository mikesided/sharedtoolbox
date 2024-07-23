# System Imports
import os
import sys
import json

# Third Party Imports

# Local Imports

# ______________________________________________________________________________________________________________________

# Scripts
LOCAL_CONFIGS_PATH = os.path.join(os.environ.get('APPDATA'), 'sharedtoolbox')
SHARED_CONFIGS_PATH = os.path.join(os.environ.get('PROGRAMDATA'), 'sharedtoolbox')
PREFS_FILE_PATH = os.path.join(LOCAL_CONFIGS_PATH, '.config.json')

# ENV Vars will overwrite configured paths if set
LOCAL_SCRIPT_ENV_VAR = 'SHAREDTOOLBOX_USER_PATH'
SHARED_SCRIPT_ENV_VAR = 'SHAREDTOOLBOX_GLOBAL_PATH'
PROJECT_ROOT_ENV_VAR = 'SHAREDTOOLBOX_PROJECT_ROOT'
PROJECT_SCRIPT_LOCATION_ENV_VAR = 'SHAREDTOOLBOX_PROJECT_SCRIPT_LOCATION'

LOCAL_SCRIPT_PATH = os.path.join(LOCAL_CONFIGS_PATH, 'scripts')
SHARED_SCRIPT_PATH = os.path.join(SHARED_CONFIGS_PATH, 'scripts')
PROJECT_ROOT_PATH = ''
PROJECT_SCRIPT_LOCATION = '.sharedtoolbox/scripts'
            

class Prefs:
    
    use_smart_editor = None
    
    def __init__(self):
        data = self._read_prefs_data()

        Prefs.use_smart_editor = data.get('use_smart_editor', True)
    
    @staticmethod
    def _read_prefs_data():
        with open(PREFS_FILE_PATH, 'r') as f:
            data = json.loads(f.read())
        return data

    @staticmethod
    def _save_prefs_data(data):
        with open(PREFS_FILE_PATH, 'w') as f:
            f.write(json.dumps(data))

    @classmethod
    def add_pinned_file(cls, file):
        """Appends a pinned file to the configs"""
        data = cls._read_prefs_data()
        data.setdefault('pinned_files', [])
        data['pinned_files'].append(file)
        cls._save_prefs_data(data)

    @classmethod
    def remove_pinned_file(cls, file):
        """Removes a pinned file to the configs"""
        data = cls._read_prefs_data()
        data.setdefault('pinned_files', [])
        data['pinned_files'].remove(file)
        cls._save_prefs_data(data)

    @classmethod
    def get_pinned_files(cls):
        """Gets all pinned files from configs
        
        Returns:
            list: List of pinned files
        """
        data = cls._read_prefs_data()
        return data.get('pinned_files', [])


# ______________________________________________________________________________________________________________________
