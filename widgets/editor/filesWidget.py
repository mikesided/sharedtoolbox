"""
    Name: filesWidget.py
    Description: Widget that holds the list of files, as buttons.
                 Each button holds its editor, which is parented to the editor's stackedlayout.
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
from sharedtoolbox.widgets.editor import pythonEditor

# ______________________________________________________________________________________________________________________


class FilesWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(FilesWidget, self).__init__(objectName='fileswidget', *args, **kwargs)

        # Properties
        self._file_btns = []
        self.selected_file_btn = None

        # Layout
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.btn_layout = HScrollLayout()
        self.btn_layout.scroll_area.setFixedHeight(24)
        self.btn_layout.setContentsMargins(8, 0, 8, 0)
        self.btn_layout.setSpacing(0)
        self.btn_layout.addItem(HSpacer())
        #self.layout().addLayout(self.btn_layout)
        self.layout().addWidget(self.btn_layout.scroll_area)
        self.stacked_layout = QStackedLayout()
        self.layout().addLayout(self.stacked_layout)

        # Connections
        event_handler.file_clicked.connect(self._add_file_tab)
        event_handler.move_filebtn_left.connect(self._move_filebtn_left)
        event_handler.move_filebtn_right.connect(self._move_filebtn_right)
        event_handler.shortcut_move_filebtn_left.connect(self._move_filebtn_left)
        event_handler.shortcut_move_filebtn_right.connect(self._move_filebtn_right)
        event_handler.shortcut_previous_filebtn.connect(self._select_previous_filebtn)
        event_handler.shortcut_next_filebtn.connect(self._select_next_filebtn)

        # Init
        self.stacked_layout.addWidget(QLabel(text='\n\nSelect a file to get started..', 
                                             alignment=Qt.AlignHCenter, enabled=False))
        for file in configs.Prefs.get_pinned_files():
            if os.path.isfile(file):
                self._add_file_tab(file, pinned=True)
        if self._file_btns:
            self.select_btn(self._file_btns[0])

    def select_btn(self, btn):
        """Selects the given button
        
        Args:
            btn (FileButton): Button to select
        """
        if btn is None:
            self.selected_file_btn = None
            return
        for btn_ in self._file_btns:
            btn_.selected = False
        btn.selected = True
        self.stacked_layout.setCurrentWidget(btn.editor)
        self.selected_file_btn = btn
        event_handler.file_opened.emit(btn.file)
        
    def _add_file_tab(self, file, pinned=False):
        """Adds a file tab
        
        Args:
            file (str): File path
            pinned (bool): Pinned? Defaults to False. Only works on new tabs

        Returns:
            FileButton: File button added
        """
        for btn in self._file_btns:
            if os.path.normpath(btn.file) == os.path.normpath(file):
                self.select_btn(btn)
                return btn
        else:
            btn = FileButton(file=file, pinned=pinned)
            self.stacked_layout.addWidget(btn.editor)
            btn.clicked.connect(partial(self.select_btn, btn))
            btn.closed.connect(partial(self._on_filebtn_closed, btn))
            btn.pinnedChanged.connect(partial(self._on_filebtn_pinnedChanged, btn))
            self._file_btns.append(btn)
            self.btn_layout.insertWidget(self.btn_layout.count() - 1, btn)
            self.select_btn(btn)
            return btn

    def _on_filebtn_closed(self, btn):
        """Triggered when a FileButton has been closed
        
        Args:
            btn (FileButton): File button closed
        """
        if btn.selected:
            for i in range(self.btn_layout.count()):
                item = self.btn_layout.itemAt(i-1)
                if hasattr(item, 'widget') and item.widget() == btn:
                    if i > 1:
                        self.select_btn(self.btn_layout.itemAt(i-2).widget())
                    else:
                        self.select_btn(None)

        self._file_btns.remove(btn)
        btn.editor.deleteLater()
        btn.deleteLater()

    def _on_filebtn_pinnedChanged(self, btn, pinned):
        """Triggered when a filebutton has been pinned/unpinned
        Move the button in the layout to its new slot
        
        Args:
            btn (FileButton): Button that changed state
            pinned (bool): Pinned/Unpinned
        """
        # Move it at the end
        self.btn_layout.insertWidget(self.btn_layout.count()-2, btn)
        
        if pinned:
            for i in range(self.btn_layout.count()):
                item = self.btn_layout.itemAt(i-1)
                if not item or not hasattr(item, 'widget'):
                    continue
                btn_ = item.widget()
                # Set the button at the end of the pinned buttons
                if btn_.pinned == False:
                    self.btn_layout.insertWidget(i-1, btn)
                    break

    def _move_filebtn_left(self):
        """Moves the current file button to the left"""
        if not self.selected_file_btn:
            return
        current_index = self.btn_layout.indexOf(self.selected_file_btn)
        if current_index == 0:
            return
        prev_btn = self.btn_layout.itemAt(current_index-1).widget()
        if not self.selected_file_btn.pinned and prev_btn.pinned:
            # Do not allow unpinned tabs to move into pinned ones
            return
        self.btn_layout.insertWidget(current_index-1, self.selected_file_btn)
        # Swap pinned files in configs
        configs.Prefs.swap_pinned_files(self.selected_file_btn.file, prev_btn.file)
        

    def _move_filebtn_right(self):
        """Moves the current file button to the right"""
        if not self.selected_file_btn:
            return
        current_index = self.btn_layout.indexOf(self.selected_file_btn)
        if current_index >= self.btn_layout.count() - 2:
            return
        next_btn = self.btn_layout.itemAt(current_index+1).widget()
        if self.selected_file_btn.pinned and not next_btn.pinned:
            # Do not allow pinned tabs to move into unpinned tabs
            return
        self.btn_layout.insertWidget(current_index+1, self.selected_file_btn)
        # Swap pinned files in configs
        configs.Prefs.swap_pinned_files(self.selected_file_btn.file, next_btn.file)

    def _select_previous_filebtn(self):
        if not self.selected_file_btn:
            return
        current_index = self.btn_layout.indexOf(self.selected_file_btn)
        if current_index >= 1:
            prev_btn = self.btn_layout.itemAt(current_index-1).widget()
            prev_btn.clicked.emit()

    def _select_next_filebtn(self):
        if not self.selected_file_btn:
            return
        current_index = self.btn_layout.indexOf(self.selected_file_btn)
        if current_index < self.btn_layout.count() - 2:
            next_btn = self.btn_layout.itemAt(current_index+1).widget()
            next_btn.clicked.emit()


class FileButton(QFrame):

    clicked = Signal()
    closed = Signal()
    pinnedChanged = Signal(bool)
    def __init__(self, file, pinned=False, volatile=False, *args, **kwargs):
        """Constructor
        The button that lives in the FilesWidget. Also contains its python code editor
        
        Args:
            file (str): File path
            pinned (bool): Is file pinned to fileswidget? Defaults to False
            volatile (bool): Is this file a volatile (temporary) tab? Defaults to False.
        """
        super(FileButton, self).__init__(objectName='filebutton', *args, **kwargs)
        self.setFixedHeight(24)
        self.file = os.path.normpath(file)
        self._pinned = pinned
        self.volatile = volatile

        # Widgets
        self.icon_locked = qtawesome.icon('fa.lock', color=style.STYLE.get('primary'))
        self.icon_unlocked = qtawesome.icon('fa.unlock', color=style.STYLE.get('white_disabled'))
        self.icon_close = qtawesome.icon('fa.close', color=style.STYLE.get('white_disabled'))
        self.btn_lock = QPushButton(fixedSize=QSize(16, 16), objectName='invisible', visible=False,
                                    icon=self.icon_locked if pinned else self.icon_unlocked)
        self.lbl_name = QLabel(text=os.path.normpath(file).split(os.sep)[-1], alignment=Qt.AlignCenter)
        self.btn_close = QPushButton(objectName='invisible', fixedSize=QSize(10, 16))
        self.editor = pythonEditor.CodeEditor()

        # Layout
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(2)
        self.layout().addWidget(self.btn_lock)
        self.layout().addWidget(self.lbl_name)
        self.layout().addWidget(self.btn_close)
        
        self.selected = False

        # Connections
        self.btn_lock.clicked.connect(self._on_btn_lock_clicked)
        self.btn_close.clicked.connect(self._on_btn_close_clicked)

        # Init
        self._read_file()


    @property
    def selected(self):
        return self._selected
    
    @selected.setter
    def selected(self, selected):
        self._selected = selected
        self.setProperty('selected', selected)
        self.setStyleSheet(self.styleSheet())
        if selected:
            self.btn_lock.setVisible(True)
        elif not self.pinned:
            self.btn_lock.setVisible(False)

    @property
    def pinned(self):
        return self._pinned
    
    @pinned.setter
    def pinned(self, pinned):
        before_state = self._pinned
        self._pinned = pinned
        if pinned:
            configs.Prefs.add_pinned_file(self.file)
            self.btn_lock.setIcon(self.icon_locked)
        else:
            configs.Prefs.remove_pinned_file(self.file)
            self.btn_lock.setIcon(self.icon_unlocked)
        if before_state != pinned:
            self.pinnedChanged.emit(pinned)
        if pinned is False and self.selected is False:
            self.btn_lock.setVisible(False)

    def _on_btn_lock_clicked(self):
        """Pins/Unpins the file"""
        self.pinned = not self.pinned

    def _on_btn_close_clicked(self):
        """Close the file, unpin if pinned"""
        if self.pinned:
            self.pinned = False
        self.closed.emit()

    def _read_file(self):
        """Reads the file and set it to the editor"""
        with open(self.file, 'r') as f:
            self.editor.setPlainText(f.read())

    def mousePressEvent(self, event):
        self.clicked.emit()
        return super().mousePressEvent(event)
    
    def enterEvent(self, event):
        self.btn_close.setIcon(self.icon_close)
        return super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.btn_close.setIcon(QIcon())
        return super().leaveEvent(event)

# ______________________________________________________________________________________________________________________
