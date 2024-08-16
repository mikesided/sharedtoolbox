# System Imports
import os
import sys

# Third Party Imports
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

# Local Imports
from sharedtoolbox import style, configs
from sharedtoolbox.widgets.base import *

from sharedtoolbox.widgets import mainwidget

# ______________________________________________________________________________________________________________________


def launch():
    """Launch the SharedToolbox"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setFont(QFont(style.FONT))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setStyleSheet(style.get_stylesheet())
        self.setWindowTitle("Shared Toolbox")
        self.resize(*configs.Prefs.main_window_size)
        self.setMinimumSize(QSize(500, 300))

        # Set the central widget of the Window.
        self.main_widget = mainwidget.MainWidget(parent=self)
        self.setCentralWidget(self.main_widget)

    def closeEvent(self, event):
        self._exit_handler()
        super().closeEvent(event)

    def _exit_handler(self):
        """Triggered on app quit"""
        self.main_widget._exit_handler()
        
        configs.Prefs.set_pref_data('main_window_size', (self.width(), self.height()))
        


# ______________________________________________________________________________________________________________________
