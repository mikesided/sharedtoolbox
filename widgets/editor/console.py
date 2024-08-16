"""
    Name: console.py
    Description: Output console
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
from sharedtoolbox.widgets.editor import pythonEditor, filesWidget

# ______________________________________________________________________________________________________________________


class ConsoleWidget(QFrame):
    
    def __init__(self, *args, **kwargs):
        super(ConsoleWidget, self).__init__(objectName='consolewidget', *args, **kwargs)
        self.setMinimumHeight(50)
        self.setVisible(configs.Prefs.console_toggled)
        self.resize(self.width(), 75)
        
        # Properties

        # Widgets
        self.console = Console()
        self.btn_clear = QPushButton(objectName='icon', toolTip='Clear Logs',
                                    icon=qtawesome.icon('mdi.format-clear', color=style.STYLE.get('primary')))

        # Layout
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(10, 4, 10, 0)
        self.layout().addLayout(self.header_layout)
        self.layout().addWidget(self.console)

        self.header_layout.addWidget(QLabel(text='>  Console', enabled=False))
        self.header_layout.addItem(HSpacer())
        self.header_layout.addWidget(self.btn_clear)

        # Connections
        self.btn_clear.clicked.connect(lambda: self.console.setPlainText(''))
        event_handler.console_toggled.connect(self.setVisible)


class Console(QTextEdit):

    def __init__(self, *args, **kwargs):
        super(Console, self).__init__(objectName='console', *args, **kwargs)
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Connections
        event_handler.std_out_write.connect(self._write)
        event_handler.std_err_write.connect(self._write)
        event_handler.console_write_html.connect(self._write_html)

    def _write(self, text):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)
        self.moveCursor(QTextCursor.End)
        QApplication.processEvents()

    def _write_html(self, html):
        self.moveCursor(QTextCursor.End)
        self.insertHtml(html)
        self.moveCursor(QTextCursor.End)
        QApplication.processEvents()


# ______________________________________________________________________________________________________________________
