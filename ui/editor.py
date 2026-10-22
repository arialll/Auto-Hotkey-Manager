"""Code editor component for AutoHotkey files.

Uses QTextEdit with a custom QSyntaxHighlighter for AHK syntax and a line-number gutter.
"""
from PySide6.QtWidgets import (
    QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QAbstractItemView,
)
from PySide6.QtWidgets import QFrame
from PySide6.QtGui import (
    QFont, QColor, QSyntaxHighlighter, QTextCharFormat, QTextCursor,
    QKeySequence, QShortcut, QPainter, QFontMetrics,
)
from PySide6.QtCore import Qt, QRegularExpression, Signal, QRect, QSize, QObject


class AHKHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor("#cba6f7"))
        keyword_fmt.setFontWeight(700)
        keywords = [
            "if", "else", "loop", "while", "for", "return", "break", "continue",
            "gosub", "goto", "function", "class", "global", "local", "static",
            "try", "catch", "throw", "finally", "switch", "case", "default",
            "until", "in", "is", "not", "and", "or", "true", "false",
        ]
        for kw in keywords:
            pattern = QRegularExpression(r"\b" + kw + r"\b", QRegularExpression.CaseInsensitiveOption)
            self.rules.append((pattern, keyword_fmt))

        builtin_fmt = QTextCharFormat()
        builtin_fmt.setForeground(QColor("#89b4fa"))
        builtins = [
            "MsgBox", "Send", "SendInput", "SendPlay", "Click", "MouseMove",
            "Sleep", "Run", "RunWait", "WinActivate", "WinClose", "WinWait",
            "Hotkey", "SetTimer", "SetKeyDelay", "SetTitleMatchMode",
            "FileRead", "FileAppend", "FileDelete", "IniRead", "IniWrite",
            "StrSplit", "SubStr", "InStr", "RegExMatch", "RegExReplace",
            "Array", "Map", "Object", "Gui", "TrayTip", "SoundBeep",
        ]
        for b in builtins:
            pattern = QRegularExpression(r"\b" + b + r"\b")
            self.rules.append((pattern, builtin_fmt))

        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor("#a6e3a1"))
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_fmt))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), string_fmt))

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#6c7086"))
        comment_fmt.setFontItalic(True)
        self.rules.append((QRegularExpression(r";.*$"), comment_fmt))
        self.block_comment_fmt = comment_fmt

        number_fmt = QTextCharFormat()
        number_fmt.setForeground(QColor("#fab387"))
        self.rules.append((QRegularExpression(r"\b\d+(\.\d+)?\b"), number_fmt))

        label_fmt = QTextCharFormat()
        label_fmt.setForeground(QColor("#f9e2af"))
        label_fmt.setFontWeight(700)
        self.rules.append((QRegularExpression(r"^[^\s].*::", QRegularExpression.MultilineOption), label_fmt))

        directive_fmt = QTextCharFormat()
        directive_fmt.setForeground(QColor("#f38ba8"))
        self.rules.append((QRegularExpression(r"^#.*$", QRegularExpression.MultilineOption), directive_fmt))

        var_fmt = QTextCharFormat()
        var_fmt.setForeground(QColor("#94e2d5"))
        self.rules.append((QRegularExpression(r"%[A-Za-z_][A-Za-z0-9_]*%"), var_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)

        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            idx = text.find("/*")
            start_index = idx if idx != -1 else -1
        if start_index >= 0:
            end_index = text.find("*/", start_index + 2)
            if end_index == -1:
                self.setCurrentBlockState(1)
                end_index = len(text)
            else:
                end_index += 2
            self.setFormat(start_index, end_index - start_index, self.block_comment_fmt)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    save_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setTabStopDistance(28)
        self._highlighter = AHKHighlighter(self.document())

        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 8 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#181825"))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#6c7086"))
                painter.drawText(0, top, self.line_number_area.width() - 4,
                                 self.fontMetrics().height(), Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def set_content(self, text: str):
        self.setPlainText(text)

    def get_content(self) -> str:
        return self.toPlainText()

    def clear_editor(self):
        self.clear()