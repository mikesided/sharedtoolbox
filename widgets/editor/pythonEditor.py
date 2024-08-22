"""
    Name: pythonEditor.py
    Description: Represents the QPlainTextEdit in which code is shown/edited
    
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
from superqt.utils import CodeSyntaxHighlight

# Local Imports
from sharedtoolbox import configs, style, event_handler
from sharedtoolbox.widgets.base import *

# ______________________________________________________________________________________________________________________


class LineNumberArea(QWidget):

    WIDTH = 38
    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self.setObjectName('codeeditorlines')
        self.setFixedWidth(self.WIDTH)
        self.code_editor = editor

    def sizeHint(self):
        return Qsize(self.WIDTH, 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super(CodeEditor, self).__init__(*args, **kwargs)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setObjectName('codeeditor')
        self.line_number_area = LineNumberArea(self)
        self._set_theme()
        self.is_selected = False

        self.connect(self, SIGNAL('updateRequest(QRect,int)'), self.update_line_number_area)
        self.connect(self, SIGNAL('cursorPositionChanged()'), self.highlight_current_line)
        self.highlight_current_line()

        self.setViewportMargins(LineNumberArea.WIDTH + 2, 0, 0, 0)
        self.installEventFilter(self)

        # Connections
        # In connections, be mindful of checking if the current editor is currently selected/focus with self.is_selected
        # Because by default, all active editors are listening to events.
        event_handler.shortcut_indent.connect(self._indent_selection)
        event_handler.shortcut_unindent.connect(self._unindent_selection)
        event_handler.theme_changed.connect(self._set_theme)
        event_handler.font_changed.connect(self._set_theme)
        
    def eventFilter(self, obj, event, *args):
        """Event Filter"""
        # Only catch current active editor
        if event.type() == QEvent.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            # Catch shortcuts and fire signals
            if self._handle_keyboard_shortcuts(key, modifiers):
                return True

            # Smart Editor functionality
            if configs.Prefs.use_smart_editor:
                result = self._handle_smart_editor(event, key, modifiers)
                if isinstance(result, bool):
                    return result
                
        return super().eventFilter(obj, event)
    
    def _handle_keyboard_shortcuts(self, key, modifiers):
        """Checks to see if a keyboard shortcut was pressed
        
        Returns:
            bool: Shortcut handled?
        """
        if key == Qt.Key_S and modifiers == Qt.KeyboardModifier.ControlModifier:
            event_handler.shortcut_save.emit()
        if key == Qt.Key_N and modifiers == Qt.KeyboardModifier.ControlModifier:
            event_handler.shortcut_new_temp_file.emit()
        elif key == Qt.Key_Left and modifiers == Qt.KeyboardModifier.AltModifier:
            event_handler.shortcut_previous_filebtn.emit()
        elif key == Qt.Key_Right and modifiers == Qt.KeyboardModifier.AltModifier:
            event_handler.shortcut_next_filebtn.emit()
        elif key == Qt.Key_Left and modifiers == Qt.KeyboardModifier.AltModifier | Qt.KeyboardModifier.ControlModifier:
            event_handler.move_filebtn_left.emit()
        elif key == Qt.Key_Right and modifiers == Qt.KeyboardModifier.AltModifier | Qt.KeyboardModifier.ControlModifier:
            event_handler.move_filebtn_right.emit()
        elif key == Qt.Key_Tab and modifiers == Qt.KeyboardModifier.NoModifier:
            event_handler.shortcut_indent.emit()
        elif key == Qt.Key_Backtab and modifiers == Qt.KeyboardModifier.ShiftModifier:
            event_handler.shortcut_unindent.emit()
        elif key == Qt.Key_F3:
            event_handler.shortcut_run_selection.emit()
        elif key == Qt.Key_F5:
            event_handler.shortcut_run_all.emit()
        elif key == Qt.Key_Return and modifiers == Qt.KeyboardModifier.ShiftModifier:
            if self.textCursor().hasSelection():
                event_handler.shortcut_run_selection.emit()
            else:
                event_handler.shortcut_run_all.emit()
        elif key == Qt.Key_Return and modifiers:
            # Ignore modifier+enter
            pass
        else:
            return False
        return True
    
    def _handle_smart_editor(self, event, key, modifiers):
        """Smart editor functionality
        
        Returns:
            bool|None: Returns True if the event should be consumed, else sent to super()
        """
        text_cursor = self.textCursor()
        start_pos = text_cursor.position()
        if key in [Qt.Key_Return, Qt.Key_Enter]:
            # Handle new lines
            with EditBlock(self.textCursor()):
                self.event(event)
                self._set_new_line_indentation()
            return True
        elif key == Qt.Key_Backspace:
            with EditBlock(self.textCursor()):
                text = text_cursor.block().text()
                # Track if we are removing a line after the keypress
                to_prev_line = len(text) == 0
                # Track the deleted character
                deleted_char = text[text_cursor.positionInBlock()-1] if text else '\n'

                self.event(event)
                # Handle backspace to the previous indent if required
                current_text = text_cursor.block().text()
                if current_text and deleted_char == ' ' and current_text.strip() == '':
                    self._unindent()
                # Remove all trailing whitespaces from previous line if required
                if to_prev_line and current_text.strip() == '':
                    for i in range(len(current_text)):
                        text_cursor.deletePreviousChar()
            return True
        elif key in [Qt.Key_Apostrophe, Qt.Key_QuoteDbl]:
            # Add twice, keep cursor in the middle, unless next character is the same, then only move forward
            with EditBlock(text_cursor):
                if start_pos > 1 and self.document().characterAt(start_pos-1) == self._get_key(key)\
                and self.document().characterAt(start_pos-2) == self._get_key(key):
                    # Only add once if the previous 2 characters are already quotes
                    text_cursor.insertText(self._get_key(key))
                elif self.document().characterAt(start_pos) != self._get_key(key):
                    # Add twice
                    text_cursor.insertText(self._get_key(key)*2)
                text_cursor.setPosition(start_pos + 1)
                self.setTextCursor(text_cursor)
            return True
        elif key in [Qt.Key_BracketLeft, Qt.Key_ParenLeft, Qt.Key_BraceLeft]:
            # Add twice, keep cursor in the middle, unless next character is the same, then only move forward
            with EditBlock(text_cursor):
                text_cursor.insertText(self._get_key(key) + self._get_key(key, opposite=True))
                text_cursor.setPosition(start_pos + 1)
                self.setTextCursor(text_cursor)
            return True        
        elif key in [Qt.Key_BracketRight, Qt.Key_ParenRight, Qt.Key_BraceRight]:
            # Add twice, keep cursor in the middle, unless next character is the same, then only move forward
            with EditBlock(text_cursor):
                if self.document().characterAt(start_pos) != self._get_key(key):
                    text_cursor.insertText(self._get_key(key))
                text_cursor.setPosition(start_pos + 1)
                self.setTextCursor(text_cursor)
            return True     

    @staticmethod 
    def _get_key(key, opposite=False):
        """Returns the actual key for the given Qt.Key_??
        
        Returns:
            str: Mapped key
        """
        if key == Qt.Key_Apostrophe:
            return "'"
        elif key == Qt.Key_QuoteDbl:
            return '"'
        elif key == Qt.Key_BracketLeft:
            return ']' if opposite else '[' 
        elif key == Qt.Key_ParenLeft:
            return ')' if opposite else '(' 
        elif key == Qt.Key_BraceLeft:
            return '}' if opposite else '{' 
        elif key == Qt.Key_BracketRight:
            return '[' if opposite else ']' 
        elif key == Qt.Key_ParenRight:
            return '(' if opposite else ')' 
        elif key == Qt.Key_BraceRight:
            return '{' if opposite else '}' 
    
    def _set_new_line_indentation(self):
        """Handles a new line to set the indentation
        """
        text_cursor = self.textCursor()
        text_cursor.movePosition(QTextCursor.PreviousBlock)
        previous_line = text_cursor.block().text()
        text_cursor.movePosition(QTextCursor.NextBlock)
        line_keyword = previous_line.strip().split(' ')[0]

        indentation = len(previous_line) - len(previous_line.lstrip())
        if line_keyword in ['class', 'def', 'elif', 'else', 'except', 'finally', 'for', 'if', 'try', 'while']:
            # Increase the indentation
            text_cursor.insertText(' ' * indentation)
            self._indent()
        elif line_keyword in ['break', 'continue', 'return', 'yield', 'pass']:
            # Decrease the indentation
            text_cursor.insertText(' ' * indentation)
            self._unindent()
        else:
            text_cursor.insertText(' ' * indentation)

    def _unindent(self, text_cursor=None):
        """Unindent the text
        
        Args:
            text_cursor (QTextCursor): Provide if altered with, optional

        Returns:
            int: Number of chars deleted
        """
        text_cursor = text_cursor or self.textCursor()
        removed_chars = 0
        with EditBlock(text_cursor):
            current_text = text_cursor.block().text()
            leading_spaces = (len(current_text) - len(current_text.lstrip(' ')))
            if leading_spaces == 0:
                return
            for i in range((leading_spaces % 4) or 4):
                if text_cursor.block().text() != '':
                    text_cursor.deletePreviousChar()
                    removed_chars += 1

        return removed_chars
                    
    def _indent(self, text_cursor=None):
        """Indent the text
        
        Args:
            text_cursor (QTextCursor): Provide if altered with, optional
            
        Returns:
            int: Number of chars added
        """
        text_cursor = text_cursor or self.textCursor()
        added_chars = 0
        with EditBlock(text_cursor):
            current_text = text_cursor.block().text()
            leading_spaces = (len(current_text) - len(current_text.lstrip(' ')))
            for i in range(4 - (leading_spaces % 4)):
                text_cursor.insertText(' ')
                added_chars += 1

        return added_chars

    def _indent_selection(self):
        """Indent the selected lines (or indent from cursor position)"""
        if not self.is_selected:
            return
        text_cursor = self.textCursor()
        end_pos = text_cursor.selectionEnd()
        with EditBlock(text_cursor):
            if text_cursor.hasSelection():
                # Set cursor at start of line
                text_cursor.setPosition(text_cursor.selectionStart())
                text_cursor.setPosition(text_cursor.position() - text_cursor.positionInBlock())
                while text_cursor.position() <= end_pos:
                    added_chars = self._indent(text_cursor=text_cursor)
                    if added_chars:
                        end_pos += added_chars
                    _block = text_cursor.blockNumber()
                    if _block + 1 == self.blockCount():
                        break
                    while text_cursor.blockNumber() == _block:
                        text_cursor.setPosition(text_cursor.position() + 1)
            else:
                # Indent if we are at the beginning of the block, else simply add 4 lines at the current position
                if text_cursor.atBlockStart():
                    added_chars = self._indent()
                    if added_chars:
                        end_pos += added_chars
                else:
                    text_cursor.insertText(' ' * 4)
        
    def _unindent_selection(self):
        """Unindent the selected lines (or the current line)"""
        if not self.is_selected:
            return
        text_cursor = self.textCursor()
        end_pos = text_cursor.selectionEnd()
        with EditBlock(text_cursor):
            text_cursor.setPosition(text_cursor.selectionStart())
            text_cursor.setPosition(text_cursor.position() - text_cursor.positionInBlock())
            while text_cursor.position() <= end_pos:
                _block = text_cursor.blockNumber()
                block_text = text_cursor.block().text()
                if not block_text.strip() == '':
                    while block_text[text_cursor.positionInBlock()] == ' ':
                        text_cursor.setPosition(text_cursor.position() + 1)
                    removed_chars = self._unindent(text_cursor=text_cursor)
                    if removed_chars:
                        end_pos -= removed_chars
                if _block + 1 == self.blockCount():
                    break
                while text_cursor.blockNumber() == _block:
                    text_cursor.setPosition(text_cursor.position() + 1)

    def _set_theme(self, *args):
        """Apply a new theme"""
        self._highlighter = CodeSyntaxHighlight(self.document(), 'python', configs.Prefs.editor_theme)

        # Additional colors
        background_color = self._highlighter.formatter.style.background_color
        highlight_color = self._highlighter.formatter.style.highlight_color
        line_number_color = self._highlighter.formatter.style.line_number_color
        #self.setStyleSheet('background-color: {};'.format(background_color))
        
        for k, v in self._highlighter.formatter._style.items():
            # Remove background colors from the formatter
            v.setBackground(QColor('transparent'))

            # Set font
            if hasattr(v, 'setFontFamilies'):
                v.setFontFamilies([configs.Prefs.editor_font])
            else:
                v.setFontFamily(configs.Prefs.editor_font)
                        

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(),
                       rect.height())


    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect();
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(),
                    LineNumberArea.WIDTH, cr.height()))


    def lineNumberAreaPaintEvent(self, event):
        mypainter = QPainter(self.line_number_area)

        # Draw Background
        mypainter.fillRect(event.rect(), '#171717')

        # Draw border
        pen = QPen()
        pen.setColor(style.STYLE.get('dark_2'))
        mypainter.setPen(pen)
        p = QPainterPath()
        p.addRect(LineNumberArea.WIDTH - 1, 0, 1, self.height())
        mypainter.drawPath(p)

        # Line number text color
        pen = QPen()
        mypainter.setPen(style.STYLE.get('primary_active'))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                mypainter.drawText(0, top, self.line_number_area.width(), height, Qt.AlignCenter, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1




    def highlight_current_line(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            lineColor = QColor(style.STYLE.get('dark_1'))

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)


class EditBlock(object):
    def __init__(self, text_cursor):
        """Constructor
       Starts an edit block. To be used with the "with" statement
        Args:
            text_cursor: QTextCursor
        """
        self.text_cursor = text_cursor

    def __enter__(self, *args):
        self.text_cursor.beginEditBlock()
        
    def __exit__(self, *args):
        self.text_cursor.endEditBlock()


# ______________________________________________________________________________________________________________________
