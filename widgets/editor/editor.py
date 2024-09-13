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
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *
import qtawesome

# Local Imports
from sharedtoolbox import configs, style, event_handler
from sharedtoolbox.widgets.base import *
from sharedtoolbox.core import codeHandler
from sharedtoolbox.dialogs import infoDialog
from sharedtoolbox.widgets.editor import pythonEditor, filesWidget, console

# ______________________________________________________________________________________________________________________

class EditorWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(EditorWidget, self).__init__(objectName='editorwidget', *args, **kwargs)
        self.setMinimumWidth(100)
        self.resize(*configs.Prefs.editor_widget_size)

        # Properties

        # Widgets
        self.splitter = QSplitter(Qt.Vertical, childrenCollapsible=False)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editor_controls_wid = EditorControls(editor=self)
        self.files_wid = filesWidget.FilesWidget()
        self.console_wid = console.ConsoleWidget()

        # Layout
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().addWidget(self.editor_controls_wid)
        self.layout().addWidget(self.splitter)
        self.splitter.addWidget(self.files_wid)
        self.splitter.addWidget(self.console_wid)

        #self.splitter.setStretchFactor(0, 3)
        #self.splitter.setStretchFactor(1, 1)

        # Connections
        event_handler.shortcut_new_temp_file.connect(self.new_temp_file)
        event_handler.shortcut_save.connect(self.save_file)
        event_handler.shortcut_run_selection.connect(self.run_selection)
        event_handler.shortcut_run_all.connect(self.run_all)        

    def reload(self):
        """Reload the widget"""
        self.files_wid._exit_handler()
        self.files_wid.deleteLater()
        self.files_wid = filesWidget.FilesWidget()
        self.splitter.insertWidget(0, self.files_wid)

    def new_temp_file(self):
        """Creates a new temp file"""
        fd, file = tempfile.mkstemp(suffix='.py', dir=configs.TEMP_SCRIPT_PATH)
        os.close(fd)
        self.files_wid._add_file_tab(file=file)

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
        codeHandler.CodeHandler.run_code(user_code)

    def _exit_handler(self):
        """Triggered on app quit"""
        self.files_wid._exit_handler()
        configs.Prefs.set_pref_data('editor_widget_size', (self.width(), self.height()))

class EditorControls(QFrame):

    def __init__(self, editor, *args, **kwargs):
        super(EditorControls, self).__init__(objectName='editorcontrols', *args, **kwargs)
        self.editor = editor
        self.setFixedHeight(40)
        self.setFocusPolicy(Qt.NoFocus)  # Remove focus so the focus stays on the editor when clicking buttons

        # Widgets
        self.btn_new_temp_file = QPushButton(icon=qtawesome.icon('fa.plus', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Ctrl+N] Create a new temporary file')
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
        self.btn_undo = QPushButton(icon=qtawesome.icon('mdi6.undo', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Ctrl+Z] Undo')
        self.btn_redo = QPushButton(icon=qtawesome.icon('mdi6.redo', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Ctrl+Y] Redo')
        self.btn_unindent = QPushButton(icon=qtawesome.icon('ri.indent-decrease', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Tab] Decrease indentation on selected lines')
        self.btn_indent = QPushButton(icon=qtawesome.icon('ri.indent-increase', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Tab] Increase indentation on selected lines')
        self.btn_run_selection = QPushButton(icon=qtawesome.icon('ph.play-light', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[F3] Run highlighted code')
        self.btn_run_all = QPushButton(icon=qtawesome.icon('ph.play-fill', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[F5] Run current script')
        self.btn_go_to_line = QPushButton(icon=qtawesome.icon('ph.list-numbers', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Ctrl+G] Go To Line Number')
        self.btn_find = QPushButton(icon=qtawesome.icon('mdi.magnify', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Ctrl+H] Find & Replace in document')
        self.btn_find_replace = QPushButton(icon=qtawesome.icon('mdi.find-replace', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Ctrl+H] Find & Replace in document')
        self.btn_zoom_in = QPushButton(icon=qtawesome.icon('msc.zoom-in', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Ctrl+9] Zoom in text')
        self.btn_zoom_out = QPushButton(icon=qtawesome.icon('msc.zoom-out', color=style.STYLE.get('primary'), options=[{'scale_factor': 1.25}]),
                                    toolTip='[Ctrl+0] Zoom out text')
        
        # Layout
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(10, 0, 10, 0)
        self.layout().setSpacing(4)

        self.layout().addWidget(self.btn_new_temp_file)
        self.layout().addWidget(self.btn_save)
        self.layout().addWidget(self.btn_reveal)
        self.layout().addItem(Spacer(w=30))
        self.layout().addWidget(self.btn_undo)
        self.layout().addWidget(self.btn_redo)
        self.layout().addWidget(self.btn_unindent)
        self.layout().addWidget(self.btn_indent)
        #self.layout().addItem(Spacer(w=30))
        self.layout().addItem(HSpacer())
        self.layout().addWidget(self.btn_move_btn_l)
        self.layout().addWidget(self.btn_prev_btn)
        self.layout().addWidget(self.btn_next_btn)
        self.layout().addWidget(self.btn_move_btn_r)
        self.layout().addItem(HSpacer())
        self.layout().addWidget(self.btn_run_selection)
        self.layout().addWidget(self.btn_run_all)
        self.layout().addItem(Spacer(w=30))
        self.layout().addWidget(self.btn_go_to_line)
        self.layout().addWidget(self.btn_find)
        self.layout().addWidget(self.btn_find_replace)
        self.layout().addWidget(self.btn_zoom_in)
        self.layout().addWidget(self.btn_zoom_out)
        #self.layout().addItem(HSpacer())

        self._set_btn_options()

        # Connections        
        self.btn_new_temp_file.clicked.connect(self.editor.new_temp_file)
        self.btn_save.clicked.connect(self.editor.save_file)
        self.btn_reveal.clicked.connect(self.editor.reveal_file)
        self.btn_unindent.clicked.connect(event_handler.unindent_text.emit)
        self.btn_indent.clicked.connect(event_handler.indent_text.emit)
        self.btn_move_btn_l.clicked.connect(event_handler.move_filebtn_left.emit)
        self.btn_prev_btn.clicked.connect(event_handler.select_previous_filebtn.emit)
        self.btn_next_btn.clicked.connect(event_handler.select_next_filebtn.emit)
        self.btn_move_btn_r.clicked.connect(event_handler.move_filebtn_right.emit)
        self.btn_run_all.clicked.connect(self.editor.run_all)
        self.btn_run_selection.clicked.connect(self.editor.run_selection)

    def eventFilter(self, obj, event, *args):
        """Event Filter"""
        # Send keyboard shortcuts to the active editor
        if event.type() == QEvent.KeyPress:
            if self.editor.files_wid.selected_file_btn:
                self.editor.files_wid.selected_file_btn.editor.eventFilter(obj, event, args)
                
        return super().eventFilter(obj, event)

    def _set_btn_options(self):
        """Set default styling options to buttons"""
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and hasattr(item, 'widget') and isinstance(item.widget(), QPushButton):
                btn = item.widget()
                btn.setObjectName('icon')
                btn.setStyleSheet(btn.styleSheet())
                btn.setFixedSize(QSize(24, 24))
                btn.setFocusPolicy(Qt.NoFocus)  # Remove focus so the focus stays on the editor when clicking buttons


# ______________________________________________________________________________________________________________________
