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
        self.lineNumberArea = LineNumberArea(self)
        self._highlighter = CodeSyntaxHighlight(self.document(), 'python', 'monokai')

        self.connect(self, SIGNAL('updateRequest(QRect,int)'), self.updateLineNumberArea)
        self.connect(self, SIGNAL('cursorPositionChanged()'), self.highlightCurrentLine)
        self.highlightCurrentLine()

        self.setViewportMargins(LineNumberArea.WIDTH, 0, 0, 0)
        self.installEventFilter(self)
        
    def eventFilter(self, obj, event, *args):
        """Event Filter"""

        # Handle key pressed to make the editor more intelligent
        if configs.Prefs.use_smart_editor:
            if event.type() == QEvent.KeyPress:
                text_cursor = self.textCursor()
                key = event.key()
                modifiers = event.modifiers()
                if key in [Qt.Key_Return, Qt.Key_Enter]:
                    # Handle new lines
                    self.event(event)
                    self._set_new_line_indentation()
                    return True
                
                elif key == Qt.Key_Backspace:
                    # Track if we are removed a line after the keypress
                    if len(text_cursor.block().text()) == 0:
                        to_prev_line = True
                    else:
                        to_prev_line = False

                    self.event(event)

                    # Handle backspace to the previous indent if required
                    current_text = text_cursor.block().text()
                    if current_text.strip() == '':
                        self._move_to_current_indent()
                    # Remove all whitespaces from previous line if required
                    if to_prev_line and current_text.strip() == '':
                        for i in range(len(current_text)):
                            text_cursor.deletePreviousChar()
                        
                    return True
        
        return super().eventFilter(obj, event)
    
    
    def _set_new_line_indentation(self):
        """Handles a new line to set the indentation"""
        text_cursor = self.textCursor()
        text_cursor.movePosition(QTextCursor.PreviousBlock)
        previous_line = text_cursor.block().text()
        text_cursor.movePosition(QTextCursor.NextBlock)
        line_keyword = previous_line.strip().split(' ')[0]

        indentation = len(previous_line) - len(previous_line.lstrip())
        if line_keyword in ['class', 'def', 'elif', 'else', 'except', 'finally', 'for', 'if', 'try', 'while']:
            # Increase the indentation
            text_cursor.insertText(' ' * indentation)
            self._move_to_next_indent()
            #indentation = indentation + 4
            #text_cursor.insertText(' ' * indentation)
        elif line_keyword in ['break', 'continue', 'return', 'yield', ]:
            # Decrease the indentation
            text_cursor.insertText(' ' * indentation)
            self._move_to_current_indent()
            if indentation >= 4:
                for i in range(4):
                    text_cursor.deletePreviousChar()
            #text_cursor.insertText(' ' * indentation)
        else:
            text_cursor.insertText(' ' * indentation)

    def _move_to_current_indent(self):
        """Moves the current cursor to the current indentation level"""
        text_cursor = self.textCursor()
        current_text = text_cursor.block().text()
        for i in range((current_text.count(' ') % 4)):
            if text_cursor.block().text() != '':
                text_cursor.deletePreviousChar()
                
    def _move_to_next_indent(self):
        """Moves the current cursor to the next indentation level"""
        text_cursor = self.textCursor()
        current_text = text_cursor.block().text()
        for i in range(4 - (current_text.count(' ') % 4)):
            text_cursor.insertText(' ')
    

    def updateLineNumberArea(self, rect, dy):

        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(),
                       rect.height())


    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect();
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                    LineNumberArea.WIDTH, cr.height()))


    def lineNumberAreaPaintEvent(self, event):
        mypainter = QPainter(self.lineNumberArea)

        #mypainter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                mypainter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignCenter, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1


    def highlightCurrentLine(self):
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

# ______________________________________________________________________________________________________________________
