from bootstrap import bootstrap
bootstrap()

import sys
from pathlib import Path
from PySide6.QtGui import QIcon, QPalette, QColor
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.styles import APP_QSS

ROOT = Path(__file__).resolve().parent


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('EBS Live Bridge')
    app.setOrganizationName('EBS')
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor('#f4f6f8'))
    palette.setColor(QPalette.WindowText, QColor('#26313a'))
    palette.setColor(QPalette.Base, QColor('#ffffff'))
    palette.setColor(QPalette.AlternateBase, QColor('#eef1f4'))
    palette.setColor(QPalette.ToolTipBase, QColor('#ffffff'))
    palette.setColor(QPalette.ToolTipText, QColor('#26313a'))
    palette.setColor(QPalette.Text, QColor('#26313a'))
    palette.setColor(QPalette.Button, QColor('#e4e8ec'))
    palette.setColor(QPalette.ButtonText, QColor('#26313a'))
    palette.setColor(QPalette.BrightText, QColor('#b42318'))
    palette.setColor(QPalette.Highlight, QColor('#dbe9f8'))
    palette.setColor(QPalette.HighlightedText, QColor('#26313a'))
    palette.setColor(QPalette.PlaceholderText, QColor('#7a8792'))
    app.setPalette(palette)
    app.setStyleSheet(APP_QSS)
    # PNG only: no SVG renderer / runtime QPainter conversion.
    icon = ROOT / 'logo.png'
    if icon.is_file():
        app.setWindowIcon(QIcon(str(icon)))
    w = MainWindow()
    w.showMaximized()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
