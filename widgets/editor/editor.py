"""
    Name: editor.py
    Description: General editor panel with its controls
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
from sharedtoolbox.dialogs import infoDialog
from sharedtoolbox.widgets.editor import pythonEditor, filesWidget

# ______________________________________________________________________________________________________________________

class EditorWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(EditorWidget, self).__init__(objectName='editorwidget', *args, **kwargs)
        self.setMinimumWidth(100)
        self.resize(*configs.Prefs.editor_widget_size)

        # Properties

        # Widgets
        self.editor_controls_wid = EditorControls(editor=self)
        self.files_wid = filesWidget.FilesWidget()

        # Layout
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.editor_controls_wid)
        self.layout().addWidget(self.files_wid)

        # Connections
        event_handler.shortcut_save.connect(self.save_file)
        event_handler.shortcut_run_selection.connect(self.run_selection)
        event_handler.shortcut_run_all.connect(self.run_all)

    def save_file(self):
        """Saves the current file, if any"""
        btn = self.files_wid.selected_file_btn
        if btn:
            file = btn.file
            with open(file, 'w') as f:
                f.write(btn.editor.toPlainText())
            event_handler.file_saved.emit(file)

    def reveal_file(self):
        """Reveal the current file in a file explorer, if any"""
        btn = self.files_wid.selected_file_btn
        if btn:
            if os.path.isfile(btn.file):
                os.startfile(os.path.dirname(btn.file))

    def run_all(self):
        """Run the current script"""
        user_code = self.files_wid.selected_file_btn.editor.toPlainText()
        self._run_code(user_code)

    def run_selection(self):
        """Run the selected text of the current script"""
        user_code = self.files_wid.selected_file_btn.editor.textCursor().selection().toPlainText()
        self._run_code(user_code)

    def _run_code(self, user_code):
        """Runs the given user_code
        
        Args:
            user_code (str): Code to run
        """
        exec(user_code)

    def _exit_handler(self):
        """Triggered on app quit"""
        configs.Prefs.set_pref_data('editor_widget_size', (self.width(), self.height()))

class EditorControls(QFrame):

    def __init__(self, editor, *args, **kwargs):
        super(EditorControls, self).__init__(objectName='editorcontrols', *args, **kwargs)
        self.editor = editor
        self.setFixedHeight(40)

        # Widgets
        self.btn_save = QPushButton(icon=qtawesome.icon('fa.save', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Ctrl+S] Save the current file')
        self.btn_reveal = QPushButton(icon=qtawesome.icon('ei.folder-open', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='Reveal the current file in a file browser')
        self.btn_move_btn_l = QPushButton(icon=qtawesome.icon('fa.angle-double-left', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Ctrl+Alt+LeftArrow] Move the current tab to the left')
        self.btn_prev_btn = QPushButton(icon=qtawesome.icon('fa.angle-left', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Alt+LeftArrow] Open the previous tab')
        self.btn_next_btn = QPushButton(icon=qtawesome.icon('fa.angle-right', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Alt+RightArrow] Open the next tab')
        self.btn_move_btn_r = QPushButton(icon=qtawesome.icon('fa.angle-double-right', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Ctrl+Alt+RightArrow] Move the current tab to the right')
        self.btn_indent = QPushButton(icon=qtawesome.icon('ri.indent-increase', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Shift+Tab] Indent selected lines')
        self.btn_run_selection = QPushButton(icon=qtawesome.icon('ph.play-light', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                             toolTip='[F3] Run highlighted code')
        self.btn_run_all = QPushButton(icon=qtawesome.icon('ph.play-fill', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                       toolTip='[F5] Run current script')
        
        # Layout
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(10, 0, 10, 0)
        self.layout().setSpacing(4)

        self.layout().addWidget(self.btn_save)
        self.layout().addWidget(self.btn_reveal)
        self.layout().addItem(Spacer(w=30))
        self.layout().addWidget(self.btn_move_btn_l)
        self.layout().addWidget(self.btn_prev_btn)
        self.layout().addWidget(self.btn_next_btn)
        self.layout().addWidget(self.btn_move_btn_r)
        self.layout().addItem(Spacer(w=30))
        self.layout().addWidget(self.btn_indent) # TO CONNECT
        self.layout().addItem(HSpacer())
        self.layout().addWidget(self.btn_run_selection)
        self.layout().addWidget(self.btn_run_all)
        self.layout().addItem(HSpacer())

        self._set_btn_options()

        # Connections        
        self.btn_save.clicked.connect(self.editor.save_file)
        self.btn_reveal.clicked.connect(self.editor.reveal_file)
        self.btn_move_btn_l.clicked.connect(event_handler.move_filebtn_left.emit)
        self.btn_prev_btn.clicked.connect(event_handler.select_previous_filebtn.emit)
        self.btn_next_btn.clicked.connect(event_handler.select_next_filebtn.emit)
        self.btn_move_btn_r.clicked.connect(event_handler.move_filebtn_right.emit)
        self.btn_run_all.clicked.connect(self.editor.run_all)
        self.btn_run_selection.clicked.connect(self.editor.run_selection)

    def _set_btn_options(self):
        """Set default styling options to buttons"""
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and hasattr(item, 'widget') and isinstance(item.widget(), QPushButton):
                btn = item.widget()
                btn.setObjectName('icon')
                btn.setStyleSheet(btn.styleSheet())
                btn.setFixedSize(QSize(24, 24))



# ______________________________________________________________________________________________________________________
