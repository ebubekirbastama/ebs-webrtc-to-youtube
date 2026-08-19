from __future__ import annotations
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

ROOT=Path(__file__).resolve().parents[1]
SCOPES=['https://www.googleapis.com/auth/youtube.force-ssl']
SECRET=ROOT/'client_secret.json'
TOKEN=ROOT/'config'/'youtube_token.json'

def credentials(interactive=True):
    creds=None
    if TOKEN.exists():
        try: creds=Credentials.from_authorized_user_file(str(TOKEN),SCOPES)
        except Exception: creds=None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if (not creds or not creds.valid) and interactive:
        if not SECRET.exists():
            raise FileNotFoundError(f'client_secret.json bulunamadı: {SECRET}')
        flow=InstalledAppFlow.from_client_secrets_file(str(SECRET),SCOPES)
        creds=flow.run_local_server(port=0,open_browser=True,authorization_prompt_message='YouTube yetkilendirmesi için tarayıcı açılıyor...')
    if creds and creds.valid:
        TOKEN.parent.mkdir(parents=True,exist_ok=True)
        TOKEN.write_text(creds.to_json(),encoding='utf-8')
    return creds

def disconnect():
    if TOKEN.exists(): TOKEN.unlink()
