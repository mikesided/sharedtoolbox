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
from pygments import styles as editor_styles
import qtawesome

# Local Imports
from sharedtoolbox import configs, style, event_handler
from sharedtoolbox.widgets.base import *

# ______________________________________________________________________________________________________________________


class StatusBarWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(StatusBarWidget, self).__init__(objectName='statuswidget', *args, **kwargs)
        self.setFixedHeight(22)

        # Widgets
        self.lbl_current_file = QLabel()
        self.lbl_saved = QLabel(parent=self, text='[Saved]', visible=False)
        self.lbl_unsaved = QLabel(parent=self, text='[Unsaved]', visible=False,
                                  styleSheet='color: {}; font: bold;'.format(style.STYLE.get('primary_active')))
        self.lbl_interpreter = QLabel()
        self.cb_editor_font = QComboBoxNoWheel(toolTip='Editor font')
        self.cb_editor_font.setFixedWidth(75)
        self.cb_editor_font.view().setFixedWidth(250)
        self.cb_editor_theme = QComboBoxNoWheel(toolTip='Editor theme')
        self.cb_editor_theme.setFixedWidth(100)
        self.cb_editor_theme.view().setFixedWidth(150)
        self.btn_toggle_smart_editor = QPushButton(objectName='toggleable', fixedSize=QSize(20, 20), toolTip='Toggle Smart Editor',
                                              icon=qtawesome.icon('fa5s.lightbulb', color='#ffffff'))
        self.btn_toggle_smart_editor.setCheckable(True)
        self.btn_toggle_console = QPushButton(objectName='toggleable', fixedSize=QSize(20, 20), toolTip='Toggle Console',
                                              icon=qtawesome.icon('mdi.console-line', color='#ffffff'))
        self.btn_toggle_console.setCheckable(True)

        # Layout
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(5, 0, 5, 0)
        self.layout().setSpacing(4)

        self.layout().addWidget(self.lbl_current_file)
        self.layout().addWidget(self.lbl_saved)
        self.layout().addWidget(self.lbl_unsaved)
        self.layout().addItem(HSpacer())
        self.layout().addWidget(self.lbl_interpreter)
        self.layout().addWidget(self.cb_editor_font)
        self.layout().addWidget(self.cb_editor_theme)
        self.layout().addWidget(self.btn_toggle_smart_editor)
        self.layout().addWidget(self.btn_toggle_console)

        # Init tool
        self.init()

        # Connections
        self.cb_editor_font.currentTextChanged.connect(self._on_cb_editor_font_currentTextChanged)
        self.cb_editor_theme.currentTextChanged.connect(self._on_cb_editor_theme_currentTextChanged)
        self.btn_toggle_smart_editor.toggled.connect(partial(setattr, configs.Prefs, 'use_smart_editor'))
        self.btn_toggle_console.toggled.connect(event_handler.console_toggled.emit)
        self.btn_toggle_console.toggled.connect(partial(setattr, configs.Prefs, 'console_toggled'))
        event_handler.file_opened.connect(self._on_current_file_changed)
        event_handler.file_state_changed.connect(self._on_file_state_changed)

    def init(self):
        """Init the status bar widget"""
        # Interpreter
        self.lbl_interpreter.setToolTip(sys.executable)
        self.lbl_interpreter.setText('Interpreter: {} ({}.{}.{})'.format(
            os.path.basename(sys.executable),
            sys.version_info.major, 
            sys.version_info.minor, 
            sys.version_info.micro)
            )
        
        # Editor font
        for font in sorted(QFontDatabase().families()):
            self.cb_editor_font.addItem(font)
        self.cb_editor_font.setCurrentIndex(0)
        self.cb_editor_font.setCurrentText(configs.Prefs.editor_font)

        # Editor theme
        for theme in sorted(editor_styles.get_all_styles()):
            self.cb_editor_theme.addItem(theme)
        self.cb_editor_theme.setCurrentIndex(0)
        self.cb_editor_theme.setCurrentText(configs.Prefs.editor_theme)

        # Smart editor
        self.btn_toggle_smart_editor.setChecked(configs.Prefs.use_smart_editor)

        # Console
        self.btn_toggle_console.setChecked(configs.Prefs.console_toggled)


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

    def _on_file_state_changed(self, state):
        """Triggered the current opened file's state has changed
        
        Args:
            state (bool): True: clean, False: unclean
        """
        self.lbl_saved.setVisible(state)
        self.lbl_unsaved.setVisible(not state)
    
    def _on_cb_editor_font_currentTextChanged(self, text):
        """Update the Preferences and send font_changed signal"""
        configs.Prefs.editor_font = text
        event_handler.font_changed.emit(text)

    def _on_cb_editor_theme_currentTextChanged(self, text):
        """Update the Preferences and send theme_changed signal"""
        configs.Prefs.editor_theme = text
        event_handler.theme_changed.emit(text)

    def _exit_handler(self):
        """Triggered on app quit"""
        configs.Prefs.set_pref_data('editor_theme', self.cb_editor_theme.currentText())
        configs.Prefs.set_pref_data('editor_font', self.cb_editor_font.currentText())
        configs.Prefs.set_pref_data('use_smart_editor', self.btn_toggle_smart_editor.isChecked())
        configs.Prefs.set_pref_data('console_toggled', self.btn_toggle_console.isChecked())

# ______________________________________________________________________________________________________________________
