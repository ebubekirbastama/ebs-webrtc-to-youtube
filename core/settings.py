from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'config'/'settings.json'
DEFAULTS={
 'ffmpeg_path':'','resolution':'1920x1080','fps':30,'bitrate':'5500k','maxrate':'6500k','bufsize':'12000k',
 'logo_width':220,'logo_opacity':0.90,'logo_position':'top-right','reencode':True,'rtmp_manual':''
}
def load_settings():
    if not PATH.exists(): return DEFAULTS.copy()
    try:
        data=json.loads(PATH.read_text(encoding='utf-8')); return {**DEFAULTS,**data}
    except Exception: return DEFAULTS.copy()
def save_settings(data):
    PATH.parent.mkdir(parents=True,exist_ok=True)
    safe={**DEFAULTS,**data}; safe.pop('stream_key',None)
    PATH.write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding='utf-8')
