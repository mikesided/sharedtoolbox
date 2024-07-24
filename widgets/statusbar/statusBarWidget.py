"""
    Name: statusBarWidget.py
    Description: Wiget that acts as the status bar on the bottom of the app
"""
# System Imports
import os
import sys
from functools import partial
import tempfile

# Third Party Imports
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import qtawesome

# Local Imports
from sharedtoolbox import configs, style, event_handler
from sharedtoolbox.widgets.base import *

# ______________________________________________________________________________________________________________________


class StatusBarWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(StatusBarWidget, self).__init__(objectName='statuswidget', *args, **kwargs)
        self.setFixedHeight(18)

        # Widgets
        self.lbl_current_file = QLabel()
        self.lbl_interpreter = QLabel()

        # Layout
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(5, 0, 5, 0)
        self.layout().setSpacing(4)

        self.layout().addWidget(self.lbl_current_file)
        self.layout().addItem(HSpacer())
        self.layout().addWidget(self.lbl_interpreter)

        # Connections
        event_handler.file_opened.connect(self._on_current_file_changed)

        self.init()


    def init(self):
        """Init the status bar widget"""
        self.lbl_interpreter.setToolTip(sys.executable)
        self.lbl_interpreter.setText('Interpreter: {} ({}.{}.{})'.format(
            os.path.basename(sys.executable),
            sys.version_info.major, 
            sys.version_info.minor, 
            sys.version_info.micro)
            )

    def _on_current_file_changed(self, file):
        """Triggered when the opened file has changed
        
        Args:
            file (str): Opened file path
        """
        file = os.path.normpath(file)
        self.lbl_current_file.setText(file)
        self.lbl_current_file.setToolTip(file)
        if len(file.split(os.sep)) > 5:
            self.lbl_current_file.setText('[...]' + os.sep + os.sep.join(file.split(os.sep)[-5:]))


    def _exit_handler(self):
        """Triggered on app quit"""
        pass

# ______________________________________________________________________________________________________________________
