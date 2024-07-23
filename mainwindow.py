# System Imports
import os
import sys

# Third Party Imports
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

# Local Imports
from sharedtoolbox import style
from sharedtoolbox.widgets.base import *

from sharedtoolbox.widgets import mainwidget

# ______________________________________________________________________________________________________________________


def launch():
    """Launch the SharedToolbox"""
    app = QApplication(sys.argv)
    app.setFont(QFont(style.FONT))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setStyleSheet(style.get_stylesheet())
        self.setWindowTitle("Shared Toolbox")
        self.setMinimumSize(QSize(800, 600))

        # Set the central widget of the Window.
        self.main_widget = mainwidget.MainWidget(parent=self)
        self.setCentralWidget(self.main_widget)


# ______________________________________________________________________________________________________________________
