from bootstrap import bootstrap
bootstrap()
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.styles import APP_QSS

def main():
    app=QApplication(sys.argv); app.setStyle('Fusion'); app.setStyleSheet(APP_QSS)
    w=MainWindow(); w.showMaximized(); return app.exec()
if __name__=='__main__': raise SystemExit(main())
