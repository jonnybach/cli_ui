"""
    :author:
        PG GT EN LGT MT DA,
        Siemens Energy,
        Orlando - FL
"""

# System imports

# PyQt imports
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QTextOption, QFont, QTextCursor, QColor
from PyQt5 import QtCore

# My imports
from ..core.constrained_text import ConstrainedText


class ConstrainedTextEdit(QTextEdit):
    """Represents a text editor that dynamically modifies the read only text
    based on the current selection"""

    def __init__(self):
        super(ConstrainedTextEdit, self).__init__(parent=None)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setFont(QFont("Courier 10 Pitch", 10, 60))

    def load(self, constrained_text):

        # Get the rendered constrained text to display to the editor
        if not constrained_text.can_render():
            raise Exception("The constrained text to be displayed in the text editor is not properly configured.  Either the data or the file template has not been loaded.")
        raw_text = constrained_text.render_textlines()
        visible_text = raw_text.copy()

        # Make the text that is visible by striping out formatting rules
        for i, line in enumerate(visible_text):
            if line.strip().endswith(ConstrainedText.k_tag_ro):
                visible_text[i] = "%s\n" % line.split(ConstrainedText.k_tag_ro)[0]
            elif line.strip().endswith(ConstrainedText.k_tag_rw):
                visible_text[i] = "%s\n" % line.split(ConstrainedText.k_tag_rw)[0]
            elif line.strip().endswith(ConstrainedText.k_tag_map):
                visible_text[i] = "%s\n" % line.split(ConstrainedText.k_tag_map)[0]
            else:
                visible_text[i] = "%s\n" % visible_text[i]
        visible_text[-1] = visible_text[-1].split('\n')[0]
        self.setText("".join(visible_text))

        # Connect to cursor position changed signal
        self.cursorPositionChanged.connect(self._alter_read_write)

        # Differentiate read only versus read-write lines of text by color
        current_cursor = self.textCursor()
        current_cursor.beginEditBlock()
        position = 0
        for i, line in enumerate(raw_text):
            if line.strip().endswith(ConstrainedText.k_tag_rw):  # Writeable line of text
                cursor = QTextCursor(self.document())
                cursor.setPosition(position)
                cursor.setPosition(position + len(visible_text[i]), QTextCursor.KeepAnchor)
                char_format = self.currentCharFormat()
                char_format.setForeground(QColor("black"))
                cursor.setCharFormat(char_format)
                self.document().findBlockByLineNumber(i).setUserState(0)  # Add flag to denote that this line number is read-write
            elif line.strip().endswith(ConstrainedText.k_tag_map):  # Mapped input line of text
                cursor = QTextCursor(self.document())
                cursor.setPosition(position)
                cursor.setPosition(position + len(visible_text[i]), QTextCursor.KeepAnchor)
                char_format = self.currentCharFormat()
                char_format.setForeground(QColor("blue"))
                cursor.setCharFormat(char_format)
                self.document().findBlockByLineNumber(i).setUserState(1)  # Add flag to denote that this line number is read only
            elif line.strip().endswith(ConstrainedText.k_tag_ro):  # Read only line of text
                cursor = QTextCursor(self.document())
                cursor.setPosition(position)
                cursor.setPosition(position + len(visible_text[i]), QTextCursor.KeepAnchor)
                char_format = self.currentCharFormat()
                char_format.setForeground(QColor("black"))
                cursor.setCharFormat(char_format)
                self.document().findBlockByLineNumber(i).setUserState(1)  # Add flag to denote that this line number is read only
            else:  # Writeable line of text
                cursor = QTextCursor(self.document())
                cursor.setPosition(position)
                cursor.setPosition(position + len(visible_text[i]), QTextCursor.KeepAnchor)
                char_format = self.currentCharFormat()
                char_format.setForeground(QColor("black"))
                cursor.setCharFormat(char_format)
                self.document().findBlockByLineNumber(i).setUserState(0)  # Add flag to denote that this line number is writeable
            position += len(visible_text[i])

        current_cursor.endEditBlock()
        self.document().clearUndoRedoStacks()

    def _alter_read_write(self):
        """Alters the read/write permissions for the text editor based on the
        current position"""
        is_ro = self._evaluate_is_readonly()
        if is_ro:
            self.setReadOnly(True)
            self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.TextSelectableByKeyboard)
        else:
            self.setReadOnly(False)

    def _evaluate_is_readonly(self):
        """Protected method: Evaluates if the current position of the editor is
        readonly"""
        block = self.textCursor().block()
        if block.userState() == 1:
            return True
        else:
            return False
