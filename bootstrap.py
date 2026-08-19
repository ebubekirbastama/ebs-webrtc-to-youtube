from __future__ import annotations
import importlib.util, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQ = ROOT / 'requirements.txt'
IMPORT_MAP = {
    'aiortc': 'aiortc', 'av': 'av', 'python-dotenv': 'dotenv', 'PySide6': 'PySide6',
    'google-api-python-client': 'googleapiclient', 'google-auth': 'google.auth',
    'google-auth-oauthlib': 'google_auth_oauthlib', 'google-auth-httplib2': 'google_auth_httplib2'
}

def _pkg_name(line: str) -> str:
    for sep in ('>=','==','<=','~=','>','<'):
        if sep in line: return line.split(sep,1)[0].strip()
    return line.strip()

def ensure_python_dependencies() -> None:
    lines = [x.strip() for x in REQ.read_text(encoding='utf-8').splitlines() if x.strip() and not x.startswith('#')]
    missing=[]
    for spec in lines:
        pkg=_pkg_name(spec); module=IMPORT_MAP.get(pkg,pkg.replace('-','_'))
        try:
            present=importlib.util.find_spec(module) is not None
        except Exception:
            present=False
        if not present: missing.append(spec)
    if not missing: return
    print('[Bootstrap] Eksik Python bağımlılıkları kuruluyor:', ', '.join(missing))
    subprocess.check_call([sys.executable,'-m','pip','install','--upgrade','pip'])
    subprocess.check_call([sys.executable,'-m','pip','install',*missing])

def find_ffmpeg() -> str | None:
    candidates=[ROOT/'ffmpeg.exe', ROOT/'bin'/'ffmpeg.exe', Path(r'C:\ffmpeg.exe'), Path(r'C:\ffmpeg\bin\ffmpeg.exe')]
    found=shutil.which('ffmpeg')
    if found: return found
    for p in candidates:
        if p.is_file(): return str(p)
    return None

def try_install_ffmpeg_windows() -> str | None:
    if os.name != 'nt': return None
    winget=shutil.which('winget')
    if not winget: return None
    print('[Bootstrap] FFmpeg bulunamadı. winget ile kurulum deneniyor...')
    try:
        subprocess.check_call([winget,'install','--id','Gyan.FFmpeg','-e','--accept-package-agreements','--accept-source-agreements'])
    except Exception as exc:
        print('[Bootstrap] FFmpeg otomatik kurulamadı:', exc)
        return None
    return find_ffmpeg()

def prepare_dirs() -> None:
    for name in ('config','logs','assets'):
        (ROOT/name).mkdir(parents=True,exist_ok=True)

def bootstrap() -> None:
    prepare_dirs()
    ensure_python_dependencies()

if __name__=='__main__':
    bootstrap()
    print('Python bağımlılıkları hazır.')
    print('FFmpeg:', find_ffmpeg() or 'Bulunamadı')
