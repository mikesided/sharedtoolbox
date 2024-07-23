# System Imports
import os
import sys

# Third Party Imports
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

# Local Imports
from sharedtoolbox.widgets.base import *

from sharedtoolbox.widgets import navigation, editor

# ______________________________________________________________________________________________________________________

class MainWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        # Properties

        # Widgets
        self.nav_widget = navigation.NavigationWidget(parent=self)
        self.editor_widget = editor.EditorWidget(parent=self)

        # Layout
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(10, 10, 10, 10)
        self.header_layout.setSpacing(0)
        self.body_splitter = QSplitter(childrenCollapsible=False)
        self.body_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().addLayout(self.header_layout)
        self.layout().addWidget(HLine())
        self.layout().addWidget(self.body_splitter)

        self.header_layout.addWidget(QLabel(text='Shared Toolbox', objectName='title'))

        self.body_splitter.addWidget(self.nav_widget)
        self.body_splitter.addWidget(self.editor_widget)
        self.init_ui()

        # Connections

        # Init
        

    def init_ui(self):
        """Init UI"""
        pass

# ______________________________________________________________________________________________________________________
