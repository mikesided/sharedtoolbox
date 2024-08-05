#!/usr/bin/env python
"""
    Name :         profileDialog.py
    Description :  Dialog to maintain user profiles

"""
# System Imports
import os
import sys
from functools import partial

# Third Party Imports
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import qtawesome

# Local Imports
from sharedtoolbox import configs, style, event_handler
from sharedtoolbox.widgets.base import *

from sharedtoolbox.dialogs import infoDialog

# ______________________________________________________________________________________________________________________


class ProfileDialog(QDialog):
    """
    Dialog that shows some information to the user
    """

    profile_changed = Signal(str)
    def __init__(self, *args, **kwargs):
        """Constructor:
        """
        super(ProfileDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle('Profiles')
        self.setMinimumSize(QSize(500, 400))
        self.setStyleSheet(style.get_stylesheet())

        # Widgets
        self.btn_new_profile = QPushButton(objectName='icon', text='New', icon=qtawesome.icon('fa.plus', color=style.STYLE.get('primary')))
        self.btn_rename_profile = QPushButton(objectName='icon', text='', icon=qtawesome.icon('fa.edit', color=style.STYLE.get('primary')))
        self.btn_delete_profile = QPushButton(objectName='icon', text='', icon=qtawesome.icon('fa.trash', color=style.STYLE.get('red')))
        self.cb_profile = QComboBoxNoWheel()
        self.cb_profile.addItems(sorted(configs.Prefs.profiles))
        self.cb_profile.setCurrentText(configs.Prefs.current_profile)
        browse_icon = qtawesome.icon('mdi.folder-edit', color=style.STYLE.get('primary'))
        self.le_local_script_path = QLineEdit(placeholderText=os.environ.get(configs.LOCAL_SCRIPT_ENV_VAR, configs.LOCAL_SCRIPT_PATH))
        self.btn_local_script_path = QPushButton(icon=browse_icon, objectName='icon')
        self.le_shared_script_path = QLineEdit(placeholderText=os.environ.get(configs.SHARED_SCRIPT_ENV_VAR, configs.SHARED_SCRIPT_PATH))
        self.btn_shared_script_path = QPushButton(icon=browse_icon, objectName='icon')
        self.le_project_root_path = QLineEdit(placeholderText=os.environ.get(configs.PROJECT_ROOT_ENV_VAR) or '')
        self.btn_project_root_path = QPushButton(icon=browse_icon, objectName='icon')
        self.le_project_script_dir = QLineEdit(placeholderText=os.environ.get(configs.PROJECT_SCRIPT_LOCATION_ENV_VAR, configs.PROJECT_SCRIPT_LOCATION))
        self.lw_env_vars = QListWidget()
        self.lw_env_vars.setSortingEnabled(True)
        self.lw_env_vars.addItems(['asdf', 'fdsa', 'asgsdfbfdnbfd'])
        self.btn_add_env_var = QPushButton(objectName='icon', icon=qtawesome.icon('fa.plus', color=style.STYLE.get('primary')))
        self.btn_del_env_var = QPushButton(objectName='icon', icon=qtawesome.icon('fa.trash', color=style.STYLE.get('red')))
        self.lw_env_var_value = QListWidget()
        self.lw_env_var_value.setDragDropMode(QAbstractItemView.DragDrop)
        self.lw_env_var_value.setDefaultDropAction(Qt.MoveAction)
        self.lw_env_var_value.addItems(['afasfasdf', 'fbfddfdsa', 'asgsA`1Qdfbfdnbfd'])
        for index in range(self.lw_env_var_value.count()):
            item = self.lw_env_var_value.item(index)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.btn_add_var_value = QPushButton(objectName='icon', icon=qtawesome.icon('fa.plus', color=style.STYLE.get('primary')))
        self.btn_del_var_value = QPushButton(objectName='icon', icon=qtawesome.icon('fa.trash', color=style.STYLE.get('red')))
        self.btn_clear_pinned_files = QPushButton(text='Clear all pinned files')

        # Layout
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(10, 10, 10, 10)
        self.layout().setSpacing(10)
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(4)
        self.layout().addLayout(self.header_layout)
        self.layout().addWidget(HLine())
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(5, 0, 5, 15)
        self.grid_layout.setVerticalSpacing(15)
        self.grid_layout.setHorizontalSpacing(5)
        self.layout().addLayout(self.grid_layout)
        self.layout().addItem(VSpacer())
        self.layout().addWidget(HLine())
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setContentsMargins(0, 0, 0, 0)
        self.footer_layout.setSpacing(10)
        self.layout().addLayout(self.footer_layout)

        # Set Header
        self.header_layout.addWidget(QLabel(text='Profile Settings', objectName='title'))
        self.header_layout.addItem(HSpacer())
        self.header_layout.addWidget(self.cb_profile)
        self.header_layout.addWidget(self.btn_new_profile)
        self.header_layout.addWidget(self.btn_rename_profile)
        self.header_layout.addWidget(self.btn_delete_profile)

        # Set Grid Layout        
        self.load_grid_layout()

        # Set button box        
        self.btn_accept = QPushButton(parent=self, text='Ok' , fixedWidth=80, fixedHeight=24)
        self.btn_accept.clicked.connect(self._on_accepted)
        self.btn_reject = QPushButton(parent=self, text='Cancel', fixedWidth=80, fixedHeight=24)
        self.btn_reject.clicked.connect(self.reject)
        self.btn_reject.setVisible(False)
        self.footer_layout.addItem(HSpacer())
        self.footer_layout.addWidget(self.btn_accept)

        # Init
        self.load_profile()

        # Connections
        self.btn_new_profile.clicked.connect(self._on_btn_new_profile_clicked)
        self.btn_rename_profile.clicked.connect(self._on_btn_rename_profile_clicked)
        self.btn_delete_profile.clicked.connect(self._on_btn_delete_profile_clicked)
        self.cb_profile.currentIndexChanged.connect(self._on_cb_profile_currentIndexChanged)
        self.btn_local_script_path.clicked.connect(self._on_btn_local_script_path_clicked)
        self.btn_shared_script_path.clicked.connect(self._on_btn_shared_script_path_clicked)
        self.btn_project_root_path.clicked.connect(self._on_btn_project_root_path_clicked)
        self.btn_clear_pinned_files.clicked.connect(self._on_btn_clear_pinned_files_clicked)

    def load_grid_layout(self):        
        # Script paths
        row = self.grid_layout.rowCount() + 1
        self.grid_layout.addWidget(QLabel(text='   Script Paths', objectName='title', fixedHeight=35), row, 0, 1, 2)

        row = self.grid_layout.rowCount() + 1
        self.grid_layout.addWidget(QLabel(text='Local Script Path    '), row, 0)
        self.grid_layout.addWidget(self.le_local_script_path, row, 1)
        self.grid_layout.addWidget(self.btn_local_script_path, row, 2)

        row = self.grid_layout.rowCount() + 1
        self.grid_layout.addWidget(QLabel(text='Shared Script Path    '), row, 0)
        self.grid_layout.addWidget(self.le_shared_script_path, row, 1)
        self.grid_layout.addWidget(self.btn_shared_script_path, row, 2)

        row = self.grid_layout.rowCount() + 1
        self.grid_layout.addWidget(QLabel(text='Project Root Path    '), row, 0)
        self.grid_layout.addWidget(self.le_project_root_path, row, 1)
        self.grid_layout.addWidget(self.btn_project_root_path, row, 2)

        row = self.grid_layout.rowCount() + 1
        self.grid_layout.addWidget(QLabel(text='Relative Project Script Dir    '), row, 0)
        self.grid_layout.addWidget(self.le_project_script_dir, row, 1)

        # Run Environment
        row = self.grid_layout.rowCount() + 1
        self.grid_layout.addWidget(QLabel(text='   Run environment', objectName='title', fixedHeight=35), row, 0, 1, 2)
    
        row = self.grid_layout.rowCount() + 1
        self.grid_layout.addWidget(QLabel(text='Environment Variables    ', alignment=Qt.AlignTop), row, 0)
        self.grid_layout.addWidget(self.lw_env_vars, row, 1)
        _v_layout = QVBoxLayout()
        _v_layout.setContentsMargins(0, 0, 0, 0)
        _v_layout.setSpacing(4)
        _v_layout.addWidget(self.btn_add_env_var)
        _v_layout.addWidget(self.btn_del_env_var)
        _v_layout.addItem(VSpacer())
        self.grid_layout.addLayout(_v_layout, row, 2)

        row = self.grid_layout.rowCount() + 1
        self.grid_layout.addWidget(QLabel(text='Variable Values    ', alignment=Qt.AlignTop), row, 0)
        self.grid_layout.addWidget(self.lw_env_var_value, row, 1)
        _v_layout = QVBoxLayout()
        _v_layout.setContentsMargins(0, 0, 0, 0)
        _v_layout.setSpacing(4)
        _v_layout.addWidget(self.btn_add_var_value)
        _v_layout.addWidget(self.btn_del_var_value)
        _v_layout.addItem(VSpacer())
        self.grid_layout.addLayout(_v_layout, row, 2)

        # Options
        row = self.grid_layout.rowCount() + 1
        self.grid_layout.addWidget(QLabel(text='   Options', objectName='title', fixedHeight=35), row, 0, 1, 2)
        
        row = self.grid_layout.rowCount() + 1
        self.grid_layout.addWidget(self.btn_clear_pinned_files, row, 0)

    def load_profile(self):
        """Loads the current profile in the widget"""
        self.le_local_script_path.setText(configs.Prefs.local_script_path)
        self.le_shared_script_path.setText(configs.Prefs.shared_script_path)
        self.le_project_root_path.setText(configs.Prefs.project_root_path)
        self.le_project_script_dir.setText(configs.Prefs.project_script_location)

    def reload_cb_profile(self, profile=None):
        """Reloads cb_profile
        
        Args:
            profile (str): Profile to set, optional
        """
        self.cb_profile.blockSignals(True)
        self.cb_profile.clear()
        self.cb_profile.addItems(sorted(configs.Prefs.profiles))
        if profile:
            self.cb_profile.setCurrentText(profile)
        else:
            self.cb_profile.setCurrentText(configs.Prefs.current_profile)
        self.cb_profile.blockSignals(False)
        
        configs.Prefs.set_pref_data('current_profile', self.cb_profile.currentText())
        configs.Prefs.load_profile(self.cb_profile.currentText())
        self.load_profile()

    def _on_accepted(self):
        """Save configs and accept dialog"""
        self._save_profile()
        configs.Prefs.set_pref_data('current_profile', self.cb_profile.currentText())
        self.accept()

    def _on_cb_profile_currentIndexChanged(self, *args):
        """
        Triggered when the profile has changed in the dialog.
        Save the current profile before switching
        """
        self._save_profile()
        configs.Prefs.set_pref_data('current_profile', self.cb_profile.currentText())
        configs.Prefs.load_profile(self.cb_profile.currentText())
        self.load_profile()

    def _on_btn_new_profile_clicked(self):
        """Create a new profile and switch to it"""
        text, confirmed = QInputDialog.getText(self, 'New Profile', "Enter the new profile's name")
        if confirmed and text:
            if text in configs.Prefs.profiles:
                dlg = infoDialog.InfoDialog(text='Profile "{}" already exists'.format(text)).exec_()
                return
            configs.Prefs.new_profile(profile_name=text)
            self.reload_cb_profile(profile=text)

    def _on_btn_rename_profile_clicked(self):
        current_profile = self.cb_profile.currentText()
        if current_profile == 'Default Profile':
            dlg = infoDialog.InfoDialog(text='Profile "{}" cannot be renamed'.format(current_profile)).exec_()
            return
        text, confirmed = QInputDialog.getText(self, 'Rename Profile', "Enter the new profile's name")
        if confirmed and text:
            if text in configs.Prefs.profiles:
                dlg = infoDialog.InfoDialog(parent=self, text='Profile "{}" already exists'.format(text)).exec_()
                return
            configs.Prefs.rename_profile(old_name=self.cb_profile.currentText(), new_name=text)
            self.reload_cb_profile(profile=text)

    def _on_btn_delete_profile_clicked(self):
        current_profile = self.cb_profile.currentText()
        if current_profile == 'Default Profile':
            dlg = infoDialog.InfoDialog(text='Profile "{}" cannot be deleted'.format(current_profile)).exec_()
            return
        confirmed = infoDialog.InfoDialog(
            parent=self, 
            text='Are you sure you want to delete the profile "{}"'.format(self.cb_profile.currentText()),
            info_level=3,
            confirm=True).exec_()
        if confirmed:
            configs.Prefs.delete_profile(current_profile)
            self.reload_cb_profile(profile='Default Profile')

    def _on_btn_local_script_path_clicked(self):
        dir = QFileDialog.getExistingDirectory(caption="Select Folder", dir=configs.Prefs.get_local_script_path())
        if dir:
            self.le_local_script_path.setText(os.path.normpath(dir))

    def _on_btn_shared_script_path_clicked(self):
        dir = QFileDialog.getExistingDirectory(caption="Select Folder", dir=configs.Prefs.get_shared_script_path())
        if dir:
            self.le_shared_script_path.setText(os.path.normpath(dir))

    def _on_btn_project_root_path_clicked(self):
        dir = QFileDialog.getExistingDirectory(caption="Select Folder", dir=configs.Prefs.get_project_root_path() or os.environ.get('USERPROFILE'))
        if dir:
            self.le_project_root_path.setText(os.path.normpath(dir))

    def _on_btn_clear_pinned_files_clicked(self):
        confirm = infoDialog.InfoDialog(
            text='Do you want to clear all pinned files for the current profile?',
            desc='\n'.join(configs.Prefs.get_pinned_files()),
            confirm=True
        ).exec_()
        if confirm:
            configs.Prefs.set_pref_profile_data('pinned_files', [])

    def _save_profile(self):
        """Saves the current profile"""
        le = self.le_local_script_path
        configs.Prefs.set_pref_profile_data('local_script_path', le.text())
        
        le = self.le_shared_script_path
        configs.Prefs.set_pref_profile_data('shared_script_path', le.text())

        le = self.le_project_root_path
        configs.Prefs.set_pref_profile_data('project_root_path', le.text())
        
        le = self.le_project_script_dir
        configs.Prefs.set_pref_profile_data('project_script_location', le.text())

        configs.Prefs.load_profile(self.cb_profile.currentText())

# ______________________________________________________________________________________________________________________
