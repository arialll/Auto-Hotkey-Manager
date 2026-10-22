"""Simple toast notification helper."""
import os

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont


class Toast(QWidget):
    def __init__(self, parent, message, duration=2200):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        container = QWidget(self)
        container.setStyleSheet(
            "background-color: #313244; border: 1px solid #45475a; "
            "border-radius: 8px; padding: 8px 14px;"
        )
        lay = QHBoxLayout(container)
        lay.setContentsMargins(10, 6, 10, 6)
        lbl = QLabel(message, container)
        lbl.setStyleSheet("color: #cdd6f4; font-weight: 600;")
        lay.addWidget(lbl)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)

        self.adjustSize()
        self._position(parent)

        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(0.0)

        self._fade_in = QPropertyAnimation(self.opacity, b"opacity")
        self._fade_in.setDuration(180)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.OutCubic)

        self._fade_out = QPropertyAnimation(self.opacity, b"opacity")
        self._fade_out.setDuration(220)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.InCubic)
        self._fade_out.finished.connect(self.close)

        self.show()
        self._fade_in.start()
        QTimer.singleShot(duration, self._start_fade_out)

    def _position(self, parent):
        if parent is None:
            return
        self.adjustSize()
        pr = parent.rect()
        bottom_right = parent.mapToGlobal(pr.bottomRight())
        from PySide6.QtCore import QPoint
        self.move(bottom_right - QPoint(self.width() + 24, self.height() + 24))

    def _start_fade_out(self):
        self._fade_out.start()


def show_toast(parent, message, duration=2200):
    Toast(parent, message, duration)