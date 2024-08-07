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
LOCAL_SCRIPT_ENV_VAR = 'SHAREDTOOLBOX_LOCAL_PATH'
SHARED_SCRIPT_ENV_VAR = 'SHAREDTOOLBOX_SHARED_PATH'
PROJECT_ROOT_ENV_VAR = 'SHAREDTOOLBOX_PROJECT_ROOT'
PROJECT_SCRIPT_LOCATION_ENV_VAR = 'SHAREDTOOLBOX_PROJECT_SCRIPT_LOCATION'

LOCAL_SCRIPT_PATH = os.path.join(LOCAL_CONFIGS_PATH, 'scripts')
SHARED_SCRIPT_PATH = os.path.join(SHARED_CONFIGS_PATH, 'scripts')
PROJECT_ROOT_PATH = ''
PROJECT_SCRIPT_LOCATION = '.sharedtoolbox' + os.sep + 'scripts'
TEMP_SCRIPT_PATH = os.path.join(LOCAL_CONFIGS_PATH, 'temp')
            

class Prefs:
    
    # General
    profiles = None
    current_profile = None
    nav_widget_size = None
    editor_widget_size = None
    console_widget_size = None
    main_window_size = None

    # Tool Prefs
    use_smart_editor = None
    editor_theme = None
    editor_font = None
    console_toggled = None

    # Profile
    local_script_path = None
    shared_script_path = None
    project_root_path = None
    project_script_location = None
    env_vars = None
    
    def __init__(self):
        self._bootstrap_configs()
        data = self.read_prefs_data()

        Prefs.profiles = list(data.get('profiles', {'Default Profile': {}}).keys())
        Prefs.current_profile = data.get('current_profile', 'Default Profile')
        Prefs.main_window_size = data.get('main_window_size', (800, 600))
        Prefs.nav_widget_size = data.get('nav_widget_size', (200, 600))
        Prefs.editor_widget_size = data.get('editor_widget_size', (600, 600))
        Prefs.console_widget_size = data.get('console_widget_size', (600, 100))

        Prefs.use_smart_editor = data.get('use_smart_editor', True)
        Prefs.editor_theme = data.get('editor_theme', 'native')
        Prefs.editor_font = data.get('editor_font', 'Consolas')
        Prefs.console_toggled = data.get('console_toggled', True)
        
        self.load_profile(self.current_profile)

    def _bootstrap_configs(self):
        """Bootstraps the config file"""
        data = self.read_prefs_data()
        data.setdefault('profiles', {})
        self._save_prefs_data(data)

    @classmethod
    def load_profile(cls, profile):
        """Loads the given profile
        
        Args:
            profile (str): Profile name
        """
        if cls.current_profile != profile:
            cls.current_profile = profile
        profile_data = cls.read_prefs_profile_data()
        cls.local_script_path = profile_data.get('local_script_path')
        cls.shared_script_path = profile_data.get('shared_script_path')
        cls.project_root_path = profile_data.get('project_root_path')
        cls.project_script_location = profile_data.get('project_script_location')
        cls.env_vars = profile_data.get('env')

    @classmethod
    def new_profile(cls, profile_name):
        data = cls.read_prefs_data()
        data['profiles'].setdefault(profile_name, {'env': {'PYTHONPATH': ['{{{ENVIRONMENT}}}']}})
        cls.set_pref_data('profiles', data.get('profiles'))
        Prefs.profiles = list(data.get('profiles').keys())
        
    @classmethod
    def rename_profile(cls, old_name, new_name):
        data = cls.read_prefs_data()
        if old_name in cls.profiles and not new_name in cls.profiles:
            data['profiles'][new_name] = data['profiles'].get(old_name)
            del(data['profiles'][old_name])
            cls.set_pref_data('profiles', data.get('profiles'))
            Prefs.profiles = list(data.get('profiles').keys())
        
    @classmethod
    def delete_profile(cls, profile_name):
        data = cls.read_prefs_data()
        if profile_name in data['profiles'].keys():
            del(data['profiles'][profile_name])
            cls.set_pref_data('profiles', data.get('profiles'))
            Prefs.profiles = list(data.get('profiles').keys())
            cls.load_profile('Default Profile')
                
    @staticmethod
    def read_prefs_data():
        with open(PREFS_FILE_PATH, 'r') as f:
            data = json.loads(f.read())
        return data

    @staticmethod
    def _save_prefs_data(data):
        with open(PREFS_FILE_PATH, 'w') as f:
            f.write(json.dumps(data, indent=4))
            
    @classmethod
    def read_prefs_profile_data(cls):
        data = cls.read_prefs_data()
        return data['profiles'].get(cls.current_profile, {})

    @classmethod
    def _save_prefs_profile_data(cls, profile_data):
        data = cls.read_prefs_data()
        data['profiles'][cls.current_profile] = profile_data
        cls._save_prefs_data(data)

    @classmethod
    def set_pref_data(cls, key, value):
        """Sets the value to a given key in the preferences file
        
        Args:
            key (str): Json key
            value: Value to set
        """
        data = cls.read_prefs_data()
        data[key] = value
        cls._save_prefs_data(data)

    @classmethod
    def set_pref_profile_data(cls, key, value):
        """Sets the value to a given key in the preferences file, in the current profile
        
        Args:
            key (str): Json key
            value: Value to set
        """
        profile_data = cls.read_prefs_profile_data()
        profile_data[key] = value
        cls._save_prefs_profile_data(profile_data)

    @classmethod
    def add_pinned_file(cls, file):
        """Appends a pinned file to the configs"""
        profile_data = cls.read_prefs_profile_data()
        profile_data.setdefault('pinned_files', [])
        profile_data['pinned_files'].append(file)
        cls._save_prefs_profile_data(profile_data)

    @classmethod
    def remove_pinned_file(cls, file):
        """Removes a pinned file from the configs"""
        profile_data = cls.read_prefs_profile_data()
        profile_data.setdefault('pinned_files', [])
        profile_data['pinned_files'].remove(file)
        cls._save_prefs_profile_data(profile_data)

    @classmethod
    def get_pinned_files(cls, valid_only=False):
        """Gets all pinned files from the current profile

        Args:
            valid_only (bool): Only return files that exist in the current environment and are found on disk. Defaults to False
        
        Returns:
            list: List of pinned files
        """
        profile_data = cls.read_prefs_profile_data()
        pinned_files = []
        if valid_only:
            for file in cls.get_pinned_files():
                _file = os.path.normpath(file)
                if _file.startswith(os.path.normpath(cls.get_local_script_path()))\
                or _file.startswith(os.path.normpath(cls.get_shared_script_path()))\
                or _file.startswith(os.path.normpath(os.path.join(cls.get_project_root_path(), cls.get_project_script_location())))\
                or _file.startswith(TEMP_SCRIPT_PATH):
                    if os.path.isfile(_file):
                        pinned_files.append(file)
        else:
            pinned_files = profile_data.get('pinned_files', [])
        return pinned_files
    
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
            cls.set_pref_profile_data(key='pinned_files', value=pinned_files)

    @classmethod
    def get_local_script_path(cls):
        """Returns the configured local script path"""
        return cls.local_script_path or os.environ.get(LOCAL_SCRIPT_ENV_VAR, LOCAL_SCRIPT_PATH)

    @classmethod
    def get_shared_script_path(cls):
        """Returns the configured shared script path"""
        return cls.shared_script_path or os.environ.get(SHARED_SCRIPT_ENV_VAR, SHARED_SCRIPT_PATH)
    
    @classmethod
    def get_project_root_path(cls):
        """Returns the configured project path"""
        return cls.project_root_path

    @classmethod
    def get_project_script_location(cls):
        """Returns the configured project script location (relative to the project root path)"""
        return cls.project_script_location or os.environ.get('PROJECT_SCRIPT_LOCATION_ENV_VAR', PROJECT_SCRIPT_LOCATION)
    
    @classmethod
    def get_temp_script_path(cls):
        """Returns the temporary script location"""
        return TEMP_SCRIPT_PATH




# ______________________________________________________________________________________________________________________
