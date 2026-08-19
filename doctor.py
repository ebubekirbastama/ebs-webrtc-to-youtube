from pathlib import Path
import sys
from bootstrap import find_ffmpeg

ROOT=Path(__file__).resolve().parent
checks={
    'Python >= 3.10': sys.version_info >= (3,10),
    'ui/main_window.py': (ROOT/'ui'/'main_window.py').is_file(),
    'youtube/auth.py': (ROOT/'youtube'/'auth.py').is_file(),
    'youtube/api.py': (ROOT/'youtube'/'api.py').is_file(),
    'logo.png': (ROOT/'logo.png').is_file(),
    'FFmpeg': bool(find_ffmpeg()),
}
for name, ok in checks.items():
    print(f"[{'OK' if ok else 'EKSİK'}] {name}")
print('[BİLGİ] client_secret.json:', 'hazır' if (ROOT/'client_secret.json').is_file() else 'GUI içinden seçilebilir')
raise SystemExit(0 if all(v for k,v in checks.items() if k!='FFmpeg') else 1)
