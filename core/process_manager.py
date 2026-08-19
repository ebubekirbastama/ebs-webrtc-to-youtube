from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import QObject, QProcess, Signal
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'core'/'webrtc_engine.py'
class BridgeProcess(QObject):
    log=Signal(str); answer=Signal(str); state=Signal(str)
    def __init__(self,parent=None):
        super().__init__(parent); self.p=QProcess(self); self.buf=''
        self.p.setProcessChannelMode(QProcess.MergedChannels)
        self.p.readyReadStandardOutput.connect(self._read); self.p.finished.connect(lambda *_: self.state.emit('stopped'))
    def start(self, python_exe, args, offer):
        if self.p.state()!=QProcess.NotRunning: self.stop()
        self.p.setProgram(python_exe); self.p.setArguments([str(ENGINE),*args]); self.p.start()
        if not self.p.waitForStarted(8000): raise RuntimeError(self.p.errorString())
        self.p.write((offer.strip()+'\n').encode('utf-8')); self.p.waitForBytesWritten(3000); self.state.emit('running')
    def stop(self):
        if self.p.state()==QProcess.NotRunning: return
        self.p.terminate()
        if not self.p.waitForFinished(5000): self.p.kill(); self.p.waitForFinished(2000)
    def _read(self):
        text=bytes(self.p.readAllStandardOutput()).decode('utf-8','replace')
        self.buf += text
        while '\n' in self.buf:
            line,self.buf=self.buf.split('\n',1); self.log.emit(line)
            if line.startswith('EBS_ANSWER_CODE:'): self.answer.emit(line.split(':',1)[1].strip())
