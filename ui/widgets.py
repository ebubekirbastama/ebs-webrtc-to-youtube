from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

class Card(QFrame):
    def __init__(self,title='',parent=None):
        super().__init__(parent); self.setObjectName('Card'); lay=QVBoxLayout(self); lay.setContentsMargins(18,16,18,18); lay.setSpacing(10); self.body=lay
        if title:
            t=QLabel(title); t.setObjectName('CardTitle'); lay.addWidget(t)
class ActionButton(QPushButton):
    def __init__(self,text,kind='Blue',parent=None):
        super().__init__(text,parent); self.setObjectName(kind); self._fx=QGraphicsDropShadowEffect(self); self._fx.setBlurRadius(16); self._fx.setOffset(0,3); self._fx.setColor(QColor(0,0,0,48)); self.setGraphicsEffect(self._fx)
    def enterEvent(self,e): self._fx.setBlurRadius(24); self._fx.setOffset(0,5); super().enterEvent(e)
    def leaveEvent(self,e): self._fx.setBlurRadius(16); self._fx.setOffset(0,3); super().leaveEvent(e)
class StatusLabel(QLabel):
    def set_state(self,state,text):
        self.setText(text); self.setObjectName({'ok':'StatusOk','bad':'StatusBad'}.get(state,'StatusIdle')); self.style().unpolish(self); self.style().polish(self)
