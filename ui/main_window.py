from __future__ import annotations
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QLineEdit,QTextEdit,QComboBox,QCheckBox,QSpinBox,QDoubleSpinBox,QFileDialog,QMessageBox,QScrollArea,QInputDialog)
from .widgets import Card,ActionButton,StatusLabel
from core.process_manager import BridgeProcess
from core.settings import load_settings,save_settings
from bootstrap import find_ffmpeg,try_install_ffmpeg_windows
from youtube.api import YouTubeLive
from youtube.auth import disconnect

ROOT=Path(__file__).resolve().parents[1]
class Worker(QObject):
    done=Signal(object); fail=Signal(str)
    def __init__(self,fn): super().__init__(); self.fn=fn
    def run(self):
        try:self.done.emit(self.fn())
        except Exception as e:self.fail.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.s=load_settings(); self.yt=None; self.bridge=BridgeProcess(self); self.answer=''
        self.setWindowTitle('EBS WebRTC → YouTube Live v2'); self.resize(1380,900); self.setMinimumSize(980,700)
        self.bridge.log.connect(self.log); self.bridge.answer.connect(self._answer); self.bridge.state.connect(self._bridge_state)
        self._build(); self._load(); self._check_ffmpeg()
    def _build(self):
        root=QWidget(); root.setObjectName('Root'); outer=QVBoxLayout(root); outer.setContentsMargins(14,14,14,14)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); wrap=QWidget(); lay=QVBoxLayout(wrap); lay.setSpacing(14)
        top=Card(); top.setObjectName('TopBar'); r=QHBoxLayout(); title=QVBoxLayout(); a=QLabel('EBS LIVE BRIDGE'); a.setObjectName('Title'); b=QLabel('WebRTC → YouTube • Metallic Control Console'); b.setObjectName('SubTitle'); title.addWidget(a); title.addWidget(b); r.addLayout(title,1); self.sysstatus=StatusLabel(); self.sysstatus.set_state('idle','● SİSTEM KONTROL'); r.addWidget(self.sysstatus); top.body.addLayout(r); lay.addWidget(top)
        grid=QGridLayout(); grid.setSpacing(14)
        web=Card('① WEBRTC • GİRİŞ'); self.offer=QTextEdit(); self.offer.setPlaceholderText('Offer / davet kodunu buraya yapıştırın...'); self.offer.setMinimumHeight(120); web.body.addWidget(self.offer); row=QHBoxLayout(); clear=ActionButton('TEMİZLE','Grey'); clear.clicked.connect(self.offer.clear); start=ActionButton('▶ BAĞLANTIYI BAŞLAT','Green'); start.clicked.connect(self.start_bridge); row.addWidget(clear); row.addStretch(); row.addWidget(start); web.body.addLayout(row); grid.addWidget(web,0,0)
        yt=Card('② YOUTUBE • RTMP / API'); self.ytstatus=StatusLabel(); self.ytstatus.set_state('idle','● Bağlı değil'); yt.body.addWidget(self.ytstatus); mode=QHBoxLayout(); self.mode=QComboBox(); self.mode.addItems(['Manuel RTMP','YouTube API']); mode.addWidget(QLabel('Mod:')); mode.addWidget(self.mode); yt.body.addLayout(mode); self.rtmp=QLineEdit(); self.rtmp.setPlaceholderText('rtmps://.../STREAM_KEY'); self.rtmp.setEchoMode(QLineEdit.Password); yt.body.addWidget(self.rtmp); br=QHBoxLayout(); show=ActionButton('GÖSTER','Grey'); show.clicked.connect(lambda:self.rtmp.setEchoMode(QLineEdit.Normal if self.rtmp.echoMode()==QLineEdit.Password else QLineEdit.Password)); auth=ActionButton('YOUTUBE’A BAĞLAN','Purple'); auth.clicked.connect(self.youtube_connect); fetch=ActionButton('KEY’İ OTOMATİK AL','Blue'); fetch.clicked.connect(self.youtube_fetch); br.addWidget(show); br.addWidget(auth); br.addWidget(fetch); yt.body.addLayout(br); create=ActionButton('＋ YENİ YOUTUBE YAYINI OLUŞTUR','Orange'); create.clicked.connect(self.youtube_create); yt.body.addWidget(create); grid.addWidget(yt,0,1)
        settings=Card('③ YAYIN • GÖRÜNTÜ / LOGO / FFMPEG'); sg=QGridLayout(); self.res=QComboBox(); self.res.addItems(['1920x1080','1280x720','854x480']); self.fps=QComboBox(); self.fps.addItems(['30','60']); self.bitrate=QLineEdit(); self.maxrate=QLineEdit(); self.bufsize=QLineEdit(); self.pos=QComboBox(); self.pos.addItems(['top-right','top-left','bottom-right','bottom-left']); self.logo_w=QSpinBox(); self.logo_w.setRange(50,800); self.opacity=QDoubleSpinBox(); self.opacity.setRange(0.1,1.0); self.opacity.setSingleStep(.05); self.reencode=QCheckBox('H.264 yeniden encode');
        for i,(lab,w) in enumerate([('Çözünürlük',self.res),('FPS',self.fps),('Bitrate',self.bitrate),('Maxrate',self.maxrate),('Bufsize',self.bufsize),('Logo konumu',self.pos),('Logo genişliği',self.logo_w),('Logo opacity',self.opacity)]): sg.addWidget(QLabel(lab),0 if i<4 else 2,i%4); sg.addWidget(w,1 if i<4 else 3,i%4)
        self.logo=QLineEdit(str(ROOT/'logo.png')); lb=ActionButton('LOGO SEÇ','Blue'); lb.clicked.connect(self.pick_logo); self.ffmpeg=QLineEdit(); fb=ActionButton('FFMPEG SEÇ','Grey'); fb.clicked.connect(self.pick_ffmpeg); fi=ActionButton('FFMPEG OTOMATİK KUR','Orange'); fi.clicked.connect(self.install_ffmpeg); sg.addWidget(QLabel('Yayın logosu (ana klasör logo.png)'),4,0); sg.addWidget(self.logo,5,0,1,2); sg.addWidget(lb,5,2); sg.addWidget(self.reencode,5,3); sg.addWidget(QLabel('FFmpeg'),6,0); sg.addWidget(self.ffmpeg,7,0,1,2); sg.addWidget(fb,7,2); sg.addWidget(fi,7,3); settings.body.addLayout(sg); grid.addWidget(settings,1,0,1,2)
        ans=Card('④ ANSWER • YAYINCIYA GERİ GÖNDER'); self.answerbox=QTextEdit(); self.answerbox.setReadOnly(True); self.answerbox.setMinimumHeight(110); ans.body.addWidget(self.answerbox); cp=ActionButton('ANSWER KOPYALA','Blue'); cp.clicked.connect(lambda: QApplication.clipboard().setText(self.answerbox.toPlainText())); ans.body.addWidget(cp); grid.addWidget(ans,2,0)
        logc=Card('⑤ CANLI LOG'); self.logbox=QTextEdit(); self.logbox.setReadOnly(True); self.logbox.setMinimumHeight(160); logc.body.addWidget(self.logbox); grid.addWidget(logc,2,1); lay.addLayout(grid)
        foot=QHBoxLayout(); self.wstatus=StatusLabel(); self.wstatus.set_state('idle','● WebRTC bekliyor'); stop=ActionButton('■ YAYINI DURDUR','Red'); stop.clicked.connect(self.bridge.stop); save=ActionButton('AYARLARI KAYDET','Grey'); save.clicked.connect(self.save); foot.addWidget(self.wstatus); foot.addStretch(); foot.addWidget(save); foot.addWidget(stop); lay.addLayout(foot)
        scroll.setWidget(wrap); outer.addWidget(scroll); self.setCentralWidget(root)
    def _load(self):
        self.res.setCurrentText(self.s['resolution']); self.fps.setCurrentText(str(self.s['fps'])); self.bitrate.setText(self.s['bitrate']); self.maxrate.setText(self.s['maxrate']); self.bufsize.setText(self.s['bufsize']); self.pos.setCurrentText(self.s['logo_position']); self.logo_w.setValue(self.s['logo_width']); self.opacity.setValue(self.s['logo_opacity']); self.reencode.setChecked(self.s['reencode']); self.rtmp.setText(self.s.get('rtmp_manual','')); self.ffmpeg.setText(self.s.get('ffmpeg_path',''))
    def save(self):
        d={'ffmpeg_path':self.ffmpeg.text(),'resolution':self.res.currentText(),'fps':int(self.fps.currentText()),'bitrate':self.bitrate.text(),'maxrate':self.maxrate.text(),'bufsize':self.bufsize.text(),'logo_width':self.logo_w.value(),'logo_opacity':self.opacity.value(),'logo_position':self.pos.currentText(),'reencode':self.reencode.isChecked(),'rtmp_manual':self.rtmp.text() if self.mode.currentIndex()==0 else ''}; save_settings(d); self.log('[Ayar] Kaydedildi.')
    def _check_ffmpeg(self):
        f=self.ffmpeg.text().strip() or find_ffmpeg() or ''
        if f:self.ffmpeg.setText(f); self.sysstatus.set_state('ok','● SİSTEM HAZIR')
        else:self.sysstatus.set_state('bad','● FFMPEG EKSİK')
    def install_ffmpeg(self): self.log('[Bootstrap] FFmpeg kurulumu deneniyor...'); f=try_install_ffmpeg_windows(); self.ffmpeg.setText(f or ''); self._check_ffmpeg()
    def pick_logo(self):
        f,_=QFileDialog.getOpenFileName(self,'Yayın logosu seç',str(ROOT),'Görsel (*.png *.jpg *.jpeg *.webp)');
        if f:self.logo.setText(f)
    def pick_ffmpeg(self):
        f,_=QFileDialog.getOpenFileName(self,'ffmpeg.exe seç','','FFmpeg (ffmpeg.exe);;Tüm dosyalar (*)');
        if f:self.ffmpeg.setText(f); self._check_ffmpeg()
    def start_bridge(self):
        offer=self.offer.toPlainText().strip(); rtmp=self.rtmp.text().strip(); ff=self.ffmpeg.text().strip()
        if not offer or not rtmp or not ff: QMessageBox.warning(self,'Eksik bilgi','Offer, RTMP ve FFmpeg alanları zorunlu.'); return
        logo=self.logo.text().strip(); args=['--rtmp',rtmp,'--ffmpeg',ff,'--resolution',self.res.currentText(),'--fps',self.fps.currentText(),'--bitrate',self.bitrate.text(),'--maxrate',self.maxrate.text(),'--bufsize',self.bufsize.text(),'--logo-width',str(self.logo_w.value()),'--logo-opacity',str(self.opacity.value()),'--logo-position',self.pos.currentText()]
        if logo and Path(logo).is_file(): args += ['--logo',logo]
        if self.reencode.isChecked(): args += ['--reencode']
        try:self.bridge.start(sys.executable,args,offer); self.save()
        except Exception as e: QMessageBox.critical(self,'Başlatma hatası',str(e))
    def _answer(self,x): self.answer=x; self.answerbox.setPlainText(x); self.wstatus.set_state('ok','● Answer hazır')
    def _bridge_state(self,s): self.wstatus.set_state('ok' if s=='running' else 'idle','● WebRTC çalışıyor' if s=='running' else '● WebRTC bekliyor')
    def log(self,t): self.logbox.append(t)
    def _async(self,fn,ok):
        th=QThread(self); w=Worker(fn); w.moveToThread(th); th.started.connect(w.run); w.done.connect(ok); w.done.connect(th.quit); w.fail.connect(lambda e:(self.log('[YouTube Hata] '+e),QMessageBox.critical(self,'YouTube',e))); w.fail.connect(th.quit); th.finished.connect(w.deleteLater); th.finished.connect(th.deleteLater); th.start(); self._thread=th
    def youtube_connect(self):
        self._async(lambda: (YouTubeLive(True),), lambda r:self._youtube_connected(r[0]))
    def _youtube_connected(self,yt): self.yt=yt; ch=yt.channel(); self.ytstatus.set_state('ok','● '+ch['title']); self.mode.setCurrentText('YouTube API'); self.log('[YouTube] Hesap bağlandı: '+ch['title'])
    def youtube_fetch(self):
        def fn():
            y=self.yt or YouTubeLive(True); streams=y.list_streams(); return y,streams
        def ok(r):
            self.yt=r[0]; items=r[1]
            if not items: QMessageBox.information(self,'YouTube','Mevcut stream bulunamadı. Yeni yayın oluşturabilirsiniz.'); return
            labels=[f"{x['title']} [{x['status']}]" for x in items]; choice,yes=QInputDialog.getItem(self,'YouTube Stream','Stream seçin:',labels,0,False)
            if yes:
                x=items[labels.index(choice)]; self.rtmp.setText(x['rtmp_url']); self.mode.setCurrentText('YouTube API'); self.log('[YouTube] RTMP bilgisi alındı (key logda gizlidir).')
        self._async(fn,ok)
    def youtube_create(self):
        title,ok=QInputDialog.getText(self,'Yeni YouTube Yayını','Yayın başlığı:');
        if not ok or not title.strip(): return
        privacy,ok=QInputDialog.getItem(self,'Gizlilik','Gizlilik:',['unlisted','private','public'],0,False)
        if not ok:return
        resolution={'1920x1080':'1080p','1280x720':'720p','854x480':'480p'}[self.res.currentText()]; fps='60fps' if self.fps.currentText()=='60' else '30fps'
        def fn():
            y=self.yt or YouTubeLive(True); return y,y.create_broadcast_and_stream(title.strip(),privacy=privacy,resolution=resolution,fps=fps)
        def done(r): self.yt=r[0]; self.rtmp.setText(r[1]['stream']['rtmp_url']); self.mode.setCurrentText('YouTube API'); self.ytstatus.set_state('ok','● Yayın oluşturuldu'); self.log('[YouTube] Broadcast + stream oluşturuldu ve bind edildi.')
        self._async(fn,done)
    def closeEvent(self,e): self.bridge.stop(); self.save(); e.accept()
