# System Imports
import os
import sys

# Third Party Imports
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

# Local Imports
from sharedtoolbox import style, configs
from sharedtoolbox.widgets.base import *

from sharedtoolbox.widgets import mainwidget

# ______________________________________________________________________________________________________________________


def launch():
    """Launch the SharedToolbox"""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setFont(QFont(style.FONT))
    window = MainWindow()
    window.setObjectName('sharedtoolbox')
    window.show()
    sys.exit(app.exec())

    
def launch_maya():
    from shiboken2 import wrapInstance
    import maya.OpenMayaUI as omui

    ptr = omui.MQtUtil.mainWindow()
    maya_main_window = wrapInstance(int(ptr), QWidget)
    window = MainWindow(parent=maya_main_window)
    window.setWindowFlags(Qt.Window)
    window.setObjectName('sharedtoolbox')
    window.show()


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
