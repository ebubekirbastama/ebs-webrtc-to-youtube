"""
EBS WebRTC → YouTube Live
Modern desktop GUI for the existing headless bridge.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QProcess, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QImage
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QFileDialog,
    QFrame, QGridLayout, QVBoxLayout, QHBoxLayout, QMessageBox, QLayout,
)

ROOT = Path(__file__).resolve().parent
CORE = ROOT / "src" / "webrtc_to_youtube.py"
ASSETS = ROOT / "assets"
DEFAULT_LOGO = ASSETS / "logo.svg"
CACHE_DIR = Path(tempfile.gettempdir()) / "ebs-webrtc-to-youtube"
CACHE_LOGO = CACHE_DIR / "ebubekir-logo.png"


def ensure_logo_png() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if CACHE_LOGO.exists():
        return CACHE_LOGO
    renderer = QSvgRenderer(str(DEFAULT_LOGO))
    image = QImage(920, 920, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    image.save(str(CACHE_LOGO), "PNG")
    return CACHE_LOGO


class Card(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 18, 20, 20)
        self.layout.setSpacing(12)
        if title:
            lbl = QLabel(title)
            lbl.setObjectName("CardTitle")
            self.layout.addWidget(lbl)


class StatusDot(QLabel):
    def __init__(self, text="Hazır", parent=None):
        super().__init__(text, parent)
        self.setObjectName("StatusDot")
        self.set_status("idle")

    def set_status(self, status: str, text: str | None = None):
        self.setProperty("status", status)
        if text:
            self.setText(text)
        self.style().unpolish(self)
        self.style().polish(self)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.process = QProcess(self)
        self.buffer = ""
        self.answer_code = ""
        self.setWindowTitle("EBS WebRTC → YouTube Live")
        self.setMinimumSize(1040, 720)
        self.resize(1240, 820)
        self.setWindowIcon(QIcon(str(DEFAULT_LOGO)))
        self._build_ui()
        self._connect_process()
        self._apply_style()
        self._set_idle()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(28, 24, 28, 24)
        main.setSpacing(18)

        header = QHBoxLayout()
        brand = QHBoxLayout()
        logo = QLabel()
        logo.setFixedSize(78, 78)
        logo.setScaledContents(True)
        logo.setPixmap(QPixmap(str(DEFAULT_LOGO)))
        brand.addWidget(logo)
        titles = QVBoxLayout()
        title = QLabel("EBS WebRTC → YouTube")
        title.setObjectName("AppTitle")
        subtitle = QLabel("Professional live relay console")
        subtitle.setObjectName("Subtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        brand.addLayout(titles)
        header.addLayout(brand)
        header.addStretch()
        self.status = StatusDot("SİSTEM HAZIR")
        header.addWidget(self.status)
        main.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)

        webrtc = Card("WEBRTC • GİRİŞ")
        webrtc.layout.addWidget(QLabel("Yayıncıdan gelen Offer / davet kodunu gir."))
        self.offer = QTextEdit()
        self.offer.setPlaceholderText("Offer / davet kodunu buraya yapıştır…")
        self.offer.setMinimumHeight(150)
        self.offer.setMaximumHeight(190)
        webrtc.layout.addWidget(self.offer)
        offer_row = QHBoxLayout()
        self.clear_offer = QPushButton("Temizle")
        self.clear_offer.setObjectName("GhostButton")
        self.generate = QPushButton("BAĞLANTIYI BAŞLAT  ›")
        self.generate.setObjectName("PrimaryButton")
        offer_row.addWidget(self.clear_offer)
        offer_row.addStretch()
        offer_row.addWidget(self.generate)
        webrtc.layout.addLayout(offer_row)

        youtube = Card("YOUTUBE • ÇIKIŞ")
        self.rtmp = QLineEdit(os.getenv("YOUTUBE_RTMP", ""))
        self.rtmp.setPlaceholderText("rtmp://a.rtmp.youtube.com/live2/STREAM_KEY")
        self.rtmp.setEchoMode(QLineEdit.Password)
        youtube.layout.addWidget(self._field("RTMP / STREAM KEY", self.rtmp))
        rtmp_row = QHBoxLayout()
        self.reveal = QPushButton("Göster")
        self.reveal.setObjectName("GhostButton")
        self.reveal.setCheckable(True)
        rtmp_row.addWidget(self.reveal)
        rtmp_row.addStretch()
        youtube.layout.addLayout(rtmp_row)

        self.ffmpeg = QLineEdit(r"C:\ffmpeg.exe")
        ffmpeg_row = QHBoxLayout()
        ffmpeg_row.addWidget(self.ffmpeg)
        browse = QPushButton("Seç")
        browse.setObjectName("GhostButton")
        browse.clicked.connect(self.choose_ffmpeg)
        ffmpeg_row.addWidget(browse)
        youtube.layout.addWidget(self._field("FFMPEG", ffmpeg_row))

        grid.addWidget(webrtc, 0, 0)
        grid.addWidget(youtube, 0, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        main.addLayout(grid)

        settings = Card("YAYIN • GÖRÜNTÜ & LOGO")
        settings_grid = QGridLayout()
        settings_grid.setHorizontalSpacing(14)
        settings_grid.setVerticalSpacing(10)

        self.resolution = QComboBox()
        self.resolution.addItems(["1920x1080", "1280x720", "854x480"])
        self.fps = QSpinBox()
        self.fps.setRange(15, 60)
        self.fps.setValue(30)
        self.bitrate = QLineEdit("5500k")
        self.maxrate = QLineEdit("6500k")
        self.reencode = QCheckBox("H.264 yeniden encode")
        self.reencode.setChecked(False)

        self.logo_path = QLineEdit(str(DEFAULT_LOGO))
        self.logo_path.setReadOnly(True)
        logo_browse = QPushButton("Logo seç")
        logo_browse.setObjectName("GhostButton")
        logo_browse.clicked.connect(self.choose_logo)

        self.logo_position = QComboBox()
        self.logo_position.addItems(["top-left", "top-right", "bottom-left", "bottom-right"])
        self.logo_position.setCurrentText("top-right")
        self.logo_width = QSpinBox()
        self.logo_width.setRange(40, 800)
        self.logo_width.setValue(220)
        self.logo_opacity = QDoubleSpinBox()
        self.logo_opacity.setRange(0.05, 1.0)
        self.logo_opacity.setSingleStep(0.05)
        self.logo_opacity.setValue(0.90)

        fields = [
            ("Çözünürlük", self.resolution), ("FPS", self.fps),
            ("Video Bitrate", self.bitrate), ("Maxrate", self.maxrate),
            ("Logo konumu", self.logo_position), ("Logo genişliği", self.logo_width),
            ("Logo opacity", self.logo_opacity),
        ]
        for i, (name, widget) in enumerate(fields):
            r, c = divmod(i, 4)
            settings_grid.addWidget(self._label(name), r * 2, c)
            settings_grid.addWidget(widget, r * 2 + 1, c)

        logo_row = QHBoxLayout()
        logo_row.addWidget(self.logo_path)
        logo_row.addWidget(logo_browse)
        settings_grid.addWidget(self._label("Logo dosyası"), 4, 0)
        settings_grid.addLayout(logo_row, 5, 0, 1, 3)
        settings_grid.addWidget(self.reencode, 5, 3)
        settings.layout.addLayout(settings_grid)
        main.addWidget(settings)

        bottom = QGridLayout()
        bottom.setHorizontalSpacing(16)
        answer = Card("ANSWER • YAYINCIYA GERİ GÖNDER")
        self.answer = QTextEdit()
        self.answer.setReadOnly(True)
        self.answer.setPlaceholderText("Bağlantı oluşturulduğunda Answer kodu burada görünecek.")
        self.answer.setMinimumHeight(120)
        answer.layout.addWidget(self.answer)
        answer_buttons = QHBoxLayout()
        self.copy_answer = QPushButton("ANSWER KOPYALA")
        self.copy_answer.setObjectName("SecondaryButton")
        self.copy_answer.setEnabled(False)
        answer_buttons.addWidget(self.copy_answer)
        answer_buttons.addStretch()
        answer.layout.addLayout(answer_buttons)

        log_card = Card("CANLI LOG")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(120)
        log_card.layout.addWidget(self.log)
        bottom.addWidget(answer, 0, 0)
        bottom.addWidget(log_card, 0, 1)
        bottom.setColumnStretch(0, 1)
        bottom.setColumnStretch(1, 1)
        main.addLayout(bottom)

        footer = QHBoxLayout()
        self.connection_label = QLabel("● WebRTC: Bekliyor")
        self.youtube_label = QLabel("● YouTube: Bekliyor")
        self.stop = QPushButton("YAYINI DURDUR  ■")
        self.stop.setObjectName("DangerButton")
        self.stop.setEnabled(False)
        footer.addWidget(self.connection_label)
        footer.addSpacing(20)
        footer.addWidget(self.youtube_label)
        footer.addStretch()
        footer.addWidget(self.stop)
        main.addLayout(footer)

        self.clear_offer.clicked.connect(self.offer.clear)
        self.generate.clicked.connect(self.start_stream)
        self.stop.clicked.connect(self.stop_stream)
        self.copy_answer.clicked.connect(lambda: QApplication.clipboard().setText(self.answer_code))
        self.reveal.toggled.connect(lambda checked: self.rtmp.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password))

    def _field(self, label: str, widget):
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        lay.addWidget(self._label(label))
        if isinstance(widget, QLayout):
            lay.addLayout(widget)
        else:
            lay.addWidget(widget)
        return box

    def _label(self, text):
        l = QLabel(text.upper())
        l.setObjectName("FieldLabel")
        return l

    def _connect_process(self):
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_error)
        self.process.started.connect(lambda: self._log("Motor başlatıldı."))
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(lambda _: self._log(f"Process hatası: {self.process.errorString()}"))

    def _apply_style(self):
        self.setStyleSheet("""
        QWidget { background: #080a0f; color: #edf2f7; font-family: "Segoe UI"; font-size: 13px; }
        QMainWindow { background: #080a0f; }
        #Card { background: #10141c; border: 1px solid #202837; border-radius: 18px; }
        #CardTitle { color: #f8fafc; font-size: 15px; font-weight: 700; letter-spacing: 1px; }
        #AppTitle { font-size: 27px; font-weight: 800; color: #ffffff; }
        #Subtitle { color: #7e8ba3; }
        #FieldLabel { color: #7e8ba3; font-size: 10px; font-weight: 800; }
        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background: #0a0e15; border: 1px solid #273244; border-radius: 10px;
            padding: 9px 11px; color: #f8fafc; selection-background-color: #7f1d2d;
        }
        QTextEdit { padding: 10px; }
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #9b1c31; }
        QPushButton {
            border: 1px solid #293548; border-radius: 10px; padding: 10px 15px;
            font-weight: 700; background: #171d28; color: #e5e7eb;
        }
        QPushButton:hover { background: #222b3a; border-color: #56657d; }
        QPushButton:pressed { padding-top: 11px; padding-bottom: 9px; }
        #PrimaryButton { background: #8f142b; border: 1px solid #bd304c; color: white; padding: 12px 22px; border-radius: 11px; }
        #PrimaryButton:hover { background: #ad1b37; }
        #SecondaryButton { background: #073f68; border-color: #0d6da8; }
        #SecondaryButton:hover { background: #0b527f; }
        #DangerButton { background: #5b1222; border-color: #9b2944; color: #ffdce3; }
        #DangerButton:hover { background: #7c1730; }
        #GhostButton { background: transparent; color: #aeb9ca; }
        #StatusDot { border-radius: 10px; padding: 7px 12px; font-weight: 800; background: #17202d; color: #9aa8bc; border: 1px solid #2a3648; }
        #StatusDot[status="running"] { background: #103323; color: #74e5a0; border-color: #1d6b43; }
        #StatusDot[status="error"] { background: #3a111b; color: #ff91a7; border-color: #7d2438; }
        QCheckBox { color: #aeb9ca; spacing: 8px; }
        QCheckBox::indicator { width: 18px; height: 18px; }
        """)

    def _set_idle(self):
        self.status.set_status("idle", "SİSTEM HAZIR")
        self.connection_label.setText("● WebRTC: Bekliyor")
        self.youtube_label.setText("● YouTube: Bekliyor")

    def _log(self, text: str):
        if text:
            self.log.append(text.rstrip())

    def read_output(self):
        data = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        self.buffer += data
        self._consume_buffer()

    def read_error(self):
        data = bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace")
        if data.strip():
            self._log(data.strip())

    def _consume_buffer(self):
        lines = self.buffer.splitlines()
        if self.buffer and not self.buffer.endswith(("\n", "\r")):
            self.buffer = lines[-1] if lines else self.buffer
            lines = lines[:-1]
        else:
            self.buffer = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            self._log(line)
            if "[WebRTC] Bağlantı durumu: connected" in line:
                self.connection_label.setText("● WebRTC: Bağlı")
                self.status.set_status("running", "WEBRTC BAĞLI")
            elif "[WebRTC] Bağlantı durumu:" in line:
                self.connection_label.setText(f"● WebRTC: {line.split(':', 1)[-1].strip()}")
            elif "[Aktarım] Başladı" in line:
                self.youtube_label.setText("● YouTube: Yayın aktif")
                self.status.set_status("running", "YAYIN AKTİF")
            elif "[Hazır]" in line:
                self.status.set_status("running", "ANSWER HAZIR")

            if len(line) > 80 and all(c.isalnum() or c in "+/=_-" for c in line) and not line.startswith("["):
                try:
                    import base64, json
                    obj = json.loads(base64.b64decode(line).decode("utf-8"))
                    if "sdp" in obj:
                        self.answer_code = line
                        self.answer.setPlainText(line)
                        self.copy_answer.setEnabled(True)
                        self.status.set_status("running", "ANSWER HAZIR")
                except Exception:
                    pass

    def start_stream(self):
        if self.process.state() != QProcess.NotRunning:
            return
        offer = self.offer.toPlainText().strip()
        rtmp = self.rtmp.text().strip()
        if not offer:
            QMessageBox.warning(self, "Offer gerekli", "WebRTC Offer / davet kodunu gir.")
            return
        if not rtmp:
            QMessageBox.warning(self, "RTMP gerekli", "YouTube RTMP adresini gir.")
            return
        if not Path(self.ffmpeg.text().strip()).is_file():
            QMessageBox.warning(self, "FFmpeg bulunamadı", "FFmpeg yolunu kontrol et.")
            return

        logo = self.logo_path.text().strip()
        if logo.lower().endswith(".svg"):
            try:
                logo = str(ensure_logo_png())
            except Exception as exc:
                QMessageBox.warning(self, "Logo", f"Logo hazırlanamadı: {exc}")
                return

        args = [
            "-u", str(CORE), "--rtmp", rtmp, "--ffmpeg", self.ffmpeg.text().strip(),
            "--resolution", self.resolution.currentText(), "--fps", str(self.fps.value()),
            "--bitrate", self.bitrate.text().strip(), "--maxrate", self.maxrate.text().strip(),
            "--logo", logo, "--logo-width", str(self.logo_width.value()),
            "--logo-opacity", str(self.logo_opacity.value()), "--logo-position", self.logo_position.currentText(),
        ]
        if self.reencode.isChecked():
            args.append("--reencode")

        self.answer.clear()
        self.answer_code = ""
        self.copy_answer.setEnabled(False)
        self.log.clear()
        self._log("Bağlantı hazırlanıyor…")
        self.generate.setEnabled(False)
        self.stop.setEnabled(True)
        self.status.set_status("running", "BAĞLANIYOR…")
        self.connection_label.setText("● WebRTC: Bağlanıyor")
        self.youtube_label.setText("● YouTube: Hazırlanıyor")

        python_exec = Path(sys.executable)
        if python_exec.name.lower() == "python.exe":
            pythonw = python_exec.with_name("pythonw.exe")
            if pythonw.exists():
                python_exec = pythonw
        self.process.setWorkingDirectory(str(ROOT))
        self.process.start(str(python_exec), args)
        if not self.process.waitForStarted(3000):
            self._set_idle()
            self.generate.setEnabled(True)
            self.stop.setEnabled(False)
            QMessageBox.critical(self, "Başlatılamadı", self.process.errorString())
            return
        QTimer.singleShot(500, lambda: self.process.write((offer + "\n").encode("utf-8")))

    def stop_stream(self):
        if self.process.state() == QProcess.NotRunning:
            return
        self._log("Yayın durduruluyor…")
        if os.name == "nt":
            import subprocess
            subprocess.run(["taskkill", "/PID", str(int(self.process.processId())), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            self.process.kill()

    def process_finished(self):
        self._log("Motor durdu.")
        self.generate.setEnabled(True)
        self.stop.setEnabled(False)
        self._set_idle()

    def choose_ffmpeg(self):
        path, _ = QFileDialog.getOpenFileName(self, "FFmpeg seç", "", "Executable (*.exe);;All files (*)")
        if path:
            self.ffmpeg.setText(path)

    def choose_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Logo seç", str(ASSETS), "Görseller (*.png *.jpg *.jpeg *.svg);;Tüm dosyalar (*)")
        if path:
            self.logo_path.setText(path)

    def closeEvent(self, event):
        if self.process.state() != QProcess.NotRunning:
            self.stop_stream()
            self.process.waitForFinished(2500)
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
