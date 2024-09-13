"""
    Name: syntaxHighlighter.py
    Description: Contains the Python code syntax highlighter
    
"""
# System Imports
import re

# Third Party Imports
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *
from superqt.utils import CodeSyntaxHighlight

# Local Imports

# ______________________________________________________________________________________________________________________

class PythonHighligter(CodeSyntaxHighlight):
    
    def __init__(self, *args):
        super(PythonHighligter, self).__init__(*args)

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QColor(170, 170, 100))

    def highlightBlock(self, text):
        super(PythonHighligter, self).highlightBlock(text)

        # Do multi-line strings
        # in_multiline = self.match_multiline(text, "'''", 1, self.multiLineCommentFormat)
        # if not in_multiline:
        #    in_multiline = self.match_multiline(text, '"""', 2, self.multiLineCommentFormat)  

    
    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegularExpression`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.

        REF: 
            https://github.com/sidmehraajm/rigBuilder/blob/main/editor.py
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = 0
            # Move past this match
            add = 3
        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = 3
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + 3
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start -= 1
        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
           return False         
        
# ______________________________________________________________________________________________________________________
