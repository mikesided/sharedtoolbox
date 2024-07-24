# System Imports
import os
import sys

# Third Party Imports
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

# Local Imports
from sharedtoolbox import configs
from sharedtoolbox.dialogs import infoDialog
from sharedtoolbox.widgets.base import *

from sharedtoolbox.widgets.editor import editor
from sharedtoolbox.widgets.nav import navigation
from sharedtoolbox.widgets.statusbar import statusBarWidget

# ______________________________________________________________________________________________________________________

class MainWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        # Properties

        # Widgets
        self.status_widget = statusBarWidget.StatusBarWidget(parent=self)  # StatusWidget must be constructed first to catch all events
        self.nav_widget = navigation.NavigationWidget(parent=self)
        self.editor_widget = editor.EditorWidget(parent=self)

        # Layout
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(10, 10, 10, 10)
        self.header_layout.setSpacing(0)
        self.body_splitter = QSplitter(childrenCollapsible=True)
        self.body_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().addLayout(self.header_layout)
        self.layout().addWidget(HLine())
        self.layout().addWidget(self.body_splitter)
        self.layout().addWidget(self.status_widget)

        self.header_layout.addWidget(QLabel(text='Shared Toolbox', objectName='title'))

        self.body_splitter.addWidget(self.nav_widget)
        self.body_splitter.addWidget(self.editor_widget)
        self.init_ui()

        # Connections

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
            configs.SHARED_SCRIPT_PATH
        ]:
            os.makedirs(dir, exist_ok=True)

        # Validate pinned files
        invalid_pinned_files = [file for file in configs.Prefs.get_pinned_files() if not os.path.isfile(file)]
        if invalid_pinned_files:
            dlg = infoDialog.InfoDialog(text="Some saved pinned files could not be found. They will be ignored.",
                                        desc=' -  \n'.join(invalid_pinned_files), info_level=3, parent=self)
            dlg.exec_()


    def _exit_handler(self):
        """Triggered on app quit"""
        self.nav_widget._exit_handler()
        self.editor_widget._exit_handler()
        self.status_widget._exit_handler()

# ______________________________________________________________________________________________________________________
