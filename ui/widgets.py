from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton


class Card(QFrame):
    def __init__(self, title='', parent=None):
        super().__init__(parent)
        self.setObjectName('Card')
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 18)
        lay.setSpacing(10)
        self.body = lay
        if title:
            t = QLabel(title)
            t.setObjectName('CardTitle')
            lay.addWidget(t)


class ActionButton(QPushButton):
    """Paint-safe button: visual effects are QSS-only; no QPainter/QGraphicsEffect."""
    def __init__(self, text, kind='Blue', parent=None):
        super().__init__(text, parent)
        self.setObjectName(kind)
        self.setCursor(__import__('PySide6.QtGui', fromlist=['QCursor']).QCursor(
            __import__('PySide6.QtCore', fromlist=['Qt']).Qt.PointingHandCursor
        ))


class StatusLabel(QLabel):
    def set_state(self, state, text):
        self.setText(text)
        self.setObjectName({'ok': 'StatusOk', 'bad': 'StatusBad'}.get(state, 'StatusIdle'))
        style = self.style()
        if style:
            style.unpolish(self)
            style.polish(self)
        self.update()
