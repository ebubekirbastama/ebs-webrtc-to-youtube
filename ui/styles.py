APP_QSS = r'''
* { font-family: "Segoe UI"; font-size: 10pt; color: #26313a; }
QMainWindow, QWidget#Root { background: #e7eaed; }
QScrollArea { border: 0; background: transparent; }
QFrame#TopBar { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #f9fafb,stop:1 #cfd4d9); border:1px solid #b5bcc4; border-radius:14px; }
QFrame#Card { background:#f8f9fa; border:1px solid #c2c8ce; border-radius:14px; }
QLabel#Title { font-size:20pt; font-weight:800; color:#20272d; }
QLabel#SubTitle { color:#64717d; }
QLabel#CardTitle { font-size:11pt; font-weight:800; color:#26313a; padding-bottom:3px; }
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox { background:#ffffff; border:1px solid #aeb6bf; border-radius:8px; padding:7px; selection-background-color:#2f80ed; }
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus { border:2px solid #2f80ed; }
QTextEdit { padding:9px; }
QPushButton { min-height:38px; border-radius:9px; border:1px solid rgba(0,0,0,.18); padding:0 14px; font-weight:800; }
QPushButton:hover { border:2px solid rgba(0,0,0,.28); }
QPushButton:pressed { padding-top:2px; }
QPushButton#Blue { color:white; background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4b9cff,stop:1 #236fce); }
QPushButton#Green { color:white; background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4fcf87,stop:1 #24995a); }
QPushButton#Red { color:white; background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ff6b6b,stop:1 #c53535); }
QPushButton#Purple { color:white; background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #a56cff,stop:1 #7040c6); }
QPushButton#Orange { color:white; background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ffb44b,stop:1 #d77d13); }
QPushButton#Grey { color:#26313a; background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ffffff,stop:1 #d6dbe0); }
QLabel#StatusOk { background:#dff6e8; color:#1d7b48; border:1px solid #9bd8b6; border-radius:9px; padding:7px 11px; font-weight:800; }
QLabel#StatusIdle { background:#eef1f4; color:#66727d; border:1px solid #cbd1d7; border-radius:9px; padding:7px 11px; font-weight:800; }
QLabel#StatusBad { background:#fde6e6; color:#a12d2d; border:1px solid #e3aaaa; border-radius:9px; padding:7px 11px; font-weight:800; }
QGroupBox { border:1px solid #c7cdd3; border-radius:10px; margin-top:12px; padding-top:10px; font-weight:700; }
QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 5px; }
QCheckBox { spacing:7px; }
'''
