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
    
    # General
    nav_widget_size = None
    editor_widget_size = None
    main_window_size = None

    # Tool Prefs
    use_smart_editor = None
    editor_theme = None
    editor_font = None
    
    def __init__(self):
        data = self._read_prefs_data()

        Prefs.main_window_size = data.get('main_window_size', (800, 600))
        Prefs.nav_widget_size = data.get('nav_widget_size', (200, 600))
        Prefs.editor_widget_size = data.get('editor_widget_size', (600, 600))

        Prefs.use_smart_editor = data.get('use_smart_editor', True)
        Prefs.editor_theme = data.get('editor_theme', 'native')
        Prefs.editor_font = data.get('editor_font', 'Consolas')

                
    @staticmethod
    def _read_prefs_data():
        with open(PREFS_FILE_PATH, 'r') as f:
            data = json.loads(f.read())
        return data

    @staticmethod
    def _save_prefs_data(data):
        with open(PREFS_FILE_PATH, 'w') as f:
            f.write(json.dumps(data, indent=4))

    @classmethod
    def set_pref_data(cls, key, value):
        """Sets the value to a given key in the preferences file
        
        Args:
            key (str): Json key
            value: Value to set
        """
        data = cls._read_prefs_data()
        data[key] = value
        cls._save_prefs_data(data)

    @classmethod
    def add_pinned_file(cls, file):
        """Appends a pinned file to the configs"""
        data = cls._read_prefs_data()
        data.setdefault('pinned_files', [])
        data['pinned_files'].append(file)
        cls._save_prefs_data(data)

    @classmethod
    def remove_pinned_file(cls, file):
        """Removes a pinned file from the configs"""
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
    
    @classmethod
    def swap_pinned_files(cls, file_1, file_2):
        """Swap two pinned files from configs
        
        Args:
            file_1 (str): First file path to swap
            file_2 (str): Second file path to swap
        """
        # Swap pinned files in configs
        pinned_files = cls.get_pinned_files()
        if file_1 in pinned_files and file_2 in pinned_files:
            f1 = pinned_files.index(file_1)
            f2 = pinned_files.index(file_2)
            pinned_files[f1], pinned_files[f2] = pinned_files[f2], pinned_files[f1]
            cls.set_pref_data(key='pinned_files', value=pinned_files)


# ______________________________________________________________________________________________________________________
