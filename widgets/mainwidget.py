# System Imports
import os
import sys

# Third Party Imports
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import qtawesome

# Local Imports
from sharedtoolbox import configs, style, event_handler
from sharedtoolbox.widgets.base import *

from sharedtoolbox.dialogs import infoDialog, profileDialog
from sharedtoolbox.widgets.editor import editor
from sharedtoolbox.widgets.nav import navigation
from sharedtoolbox.widgets.statusbar import statusBarWidget

# ______________________________________________________________________________________________________________________

class MainWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        # Properties

        # Widgets
        self.cb_profile = QComboBoxNoWheel()
        self.cb_profile.addItems(sorted(configs.Prefs.profiles))
        self.cb_profile.setCurrentText(configs.Prefs.current_profile)
        self.btn_profile_settings = QPushButton(objectName='icon',
                                                icon=qtawesome.icon('fa.gear', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]))
        self.btn_reload = QPushButton(objectName='icon',
                                      icon=qtawesome.icon('mdi.reload', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]))
        self.status_widget = statusBarWidget.StatusBarWidget(parent=self)  # StatusWidget must be constructed first to catch all events
        self.nav_widget = navigation.NavigationWidget(parent=self)
        self.editor_widget = editor.EditorWidget(parent=self)

        # Layout
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(10, 10, 10, 10)
        self.header_layout.setSpacing(4)
        self.body_splitter = QSplitter(childrenCollapsible=True)
        self.body_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().addLayout(self.header_layout)
        self.layout().addWidget(HLine())
        self.layout().addWidget(self.body_splitter)
        self.layout().addWidget(self.status_widget)

        # Header layout
        self.header_layout.addWidget(QLabel(text='Shared Toolbox', objectName='title'))
        self.header_layout.addItem(HSpacer())
        self.header_layout.addWidget(self.cb_profile)
        self.header_layout.addWidget(self.btn_profile_settings)
        self.header_layout.addWidget(self.btn_reload)

        # Splitter
        self.body_splitter.addWidget(self.nav_widget)
        self.body_splitter.addWidget(self.editor_widget)
        self.init_ui()

        # Connections
        self.btn_profile_settings.clicked.connect(self._show_settings)
        self.cb_profile.currentTextChanged.connect(self._on_profile_changed)
        self.btn_reload.clicked.connect(self.reload)

        # Init
        self.bootstrap()
        self.editor_widget.files_wid.stacked_layout.currentWidget().setFocus()

    def init_ui(self):
        """Init UI"""
        pass

    def bootstrap(self):
        """Bootstrap the tool to do some validation"""
        # Create all required config folders
        for dir in [
            configs.LOCAL_CONFIGS_PATH,
            configs.LOCAL_SCRIPT_PATH,
            configs.SHARED_CONFIGS_PATH,
            configs.SHARED_SCRIPT_PATH,
            configs.TEMP_SCRIPT_PATH
        ]:
            os.makedirs(dir, exist_ok=True)

        # Validate pinned files
        pinned_files = configs.Prefs.get_pinned_files()
        valid_pinned_files = configs.Prefs.get_pinned_files(valid_only=True)
        invalid_pinned_files = [file for file in pinned_files if file not in valid_pinned_files]
        if invalid_pinned_files:
            dlg = infoDialog.InfoDialog(text="Some saved pinned files could not be found. They will be ignored.",
                                        desc=' -  \n'.join(invalid_pinned_files), info_level=3, parent=self)
            dlg.exec_()

    def reload(self, silent=False):
        """Reloads the widget"""
        if not silent:
            infoDialog.InfoDialog(parent=self, text='Reloading profile..').exec_()
        self.bootstrap()
        self.nav_widget.reload()
        self.editor_widget.reload()


    def _on_profile_changed(self, profile, silent=False):
        """Triggered when the profile changed
        
        Args:
            profile (str): New profile
        """
        configs.Prefs.set_pref_data('current_profile', profile)
        configs.Prefs.load_profile(profile)
        self.reload(silent=silent)

    def _show_settings(self):
        """Open the profile settings dialog"""
        dlg = profileDialog.ProfileDialog(parent=self)
        dlg.accepted.connect(self._on_profileDialog_accepted)
        dlg.exec_()

    def _on_profileDialog_accepted(self):
        """
        Triggered when the profile dialog was accepted.
        Reload the profile combobox and set new current profile if needed
        """
        previous_profile = self.cb_profile.currentText()
        self.cb_profile.blockSignals(True)
        self.cb_profile.clear()
        self.cb_profile.addItems(sorted(configs.Prefs.profiles))
        self.cb_profile.setCurrentText(configs.Prefs.current_profile)
        self.cb_profile.blockSignals(False)
        if previous_profile != configs.Prefs.current_profile:
            self._on_profile_changed(self.cb_profile.currentText())
        elif infoDialog.InfoDialog(
            parent=self, 
            text='Reload profile? This will close any unpinned tabs.', 
            desc='Environment variable changes do not need to be reloaded to take effect.', 
            confirm=True).exec_():
            self._on_profile_changed(self.cb_profile.currentText(), silent=True)


    def _exit_handler(self):
        """Triggered on app quit"""
        self.nav_widget._exit_handler()
        self.editor_widget._exit_handler()
        self.status_widget._exit_handler()

# ______________________________________________________________________________________________________________________
