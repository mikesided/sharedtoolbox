#!/usr/bin/env python
"""
    Name :         infoDialog.py
    Description :  Dialog to show the user some information

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
from sharedtoolbox import configs, style
from sharedtoolbox.widgets.base import *
from sharedtoolbox.widgets.editor import pythonEditor

# ______________________________________________________________________________________________________________________



class InfoDialog(QDialog):
    """
    Dialog that shows some information to the user
    """

    def __init__(self, text, desc='', confirm=False, info_level=2, *args, **kwargs):
        """Constructor
        
        Args:
            text (str): Information text
            desc (str): Descrption, optional
            confirm (bool): Yes/No window with signals? Defaults to false.
            info_level (int): 1: debug, 2: info, 3: warning, 4: error, 5: critical. Defaults to 2
        """
        super(InfoDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle('Shared Toolbox')
        self.setMinimumWidth(300)
        self.setStyleSheet(style.get_stylesheet())

        # Widgets
        self.lbl_icon = QLabel()
        self.lbl_text = QLabel(text=text)
        self.lbl_desc = QLabel(enabled=False, text=desc)
        
        if info_level == 2:
            self.lbl_icon.setPixmap(qtawesome.icon('ei.info-circle', color=style.STYLE.get('primary')).pixmap(QSize(24, 24)))
        elif info_level == 3:
            self.lbl_icon.setPixmap(qtawesome.icon('ei.warning-sign', color='#ffcc00').pixmap(QSize(24, 24)))
        elif info_level >3 :
            self.lbl_icon.setPixmap(qtawesome.icon('ei.error', color='#cc3300').pixmap(QSize(24, 24)))

        # Layout
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(10, 10, 10, 10)
        self.layout().setSpacing(15)
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(10, 15, 5, 15)
        self.header_layout.setSpacing(10)
        self.layout().addLayout(self.header_layout)
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(5, 0, 5, 15)
        self.main_layout.setSpacing(15)
        self.layout().addLayout(self.main_layout)
        self.layout().addWidget(HLine())
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setContentsMargins(0, 0, 0, 0)
        self.footer_layout.setSpacing(10)
        self.layout().addLayout(self.footer_layout)

        # Set Header
        self.header_layout.addWidget(self.lbl_icon)
        self.header_layout.addWidget(self.lbl_text)
        self.header_layout.addItem(HSpacer())

        # Set main layout
        if desc:
            self.main_layout.addWidget(self.lbl_desc)

        # Set button box        
        self.btn_accept = QPushButton(parent=self, text='Yes' if confirm else 'Ok', fixedWidth=80, fixedHeight=24)
        self.btn_accept.clicked.connect(self.accept)
        self.btn_reject = QPushButton(parent=self, text='No' if confirm else 'Close', fixedWidth=80, fixedHeight=24)
        self.btn_reject.clicked.connect(self.reject)
        if confirm:
            self.footer_layout.addItem(HSpacer())
            self.footer_layout.addWidget(self.btn_reject)
            self.footer_layout.addWidget(self.btn_accept)
        else:
            self.btn_reject.setVisible(False)
            self.footer_layout.addItem(HSpacer())
            self.footer_layout.addWidget(self.btn_accept)


# ______________________________________________________________________________________________________________________
