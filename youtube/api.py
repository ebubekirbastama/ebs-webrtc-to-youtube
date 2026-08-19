from __future__ import annotations
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from .auth import credentials

class YouTubeLive:
    def __init__(self, interactive=True):
        creds=credentials(interactive=interactive)
        if not creds: raise RuntimeError('YouTube yetkilendirmesi yok.')
        self.api=build('youtube','v3',credentials=creds,cache_discovery=False)
    def channel(self):
        r=self.api.channels().list(part='snippet',mine=True).execute()
        items=r.get('items',[])
        if not items: return {'title':'Bilinmiyor','id':''}
        x=items[0]; return {'title':x['snippet']['title'],'id':x['id']}
    def list_broadcasts(self):
        r=self.api.liveBroadcasts().list(part='id,snippet,status,contentDetails',broadcastStatus='all',broadcastType='all',mine=True,maxResults=50).execute()
        out=[]
        for x in r.get('items',[]):
            out.append({'id':x['id'],'title':x['snippet'].get('title',''),'status':x.get('status',{}).get('lifeCycleStatus',''),'boundStreamId':x.get('contentDetails',{}).get('boundStreamId','')})
        return out
    def list_streams(self):
        r=self.api.liveStreams().list(part='id,snippet,cdn,status',mine=True,maxResults=50).execute()
        return [self._stream_info(x) for x in r.get('items',[])]
    def stream(self, stream_id):
        r=self.api.liveStreams().list(part='id,snippet,cdn,status',id=stream_id).execute()
        items=r.get('items',[])
        if not items: raise RuntimeError('YouTube stream bulunamadı.')
        return self._stream_info(items[0])
    def _stream_info(self,x):
        ing=x.get('cdn',{}).get('ingestionInfo',{})
        base=ing.get('rtmpsIngestionAddress') or ing.get('ingestionAddress') or ''
        key=ing.get('streamName','')
        return {'id':x['id'],'title':x.get('snippet',{}).get('title',''),'status':x.get('status',{}).get('streamStatus',''), 'ingestion':base,'stream_name':key,'rtmp_url':f'{base.rstrip("/")}/{key}' if base and key else ''}
    def create_broadcast_and_stream(self,title,description='',privacy='unlisted',resolution='1080p',fps='30fps',latency='low',auto_start=True,auto_stop=True,reusable=True):
        start=(datetime.now(timezone.utc)+timedelta(minutes=2)).isoformat().replace('+00:00','Z')
        broadcast=self.api.liveBroadcasts().insert(part='snippet,status,contentDetails',body={
            'snippet':{'title':title,'description':description,'scheduledStartTime':start},
            'status':{'privacyStatus':privacy,'selfDeclaredMadeForKids':False},
            'contentDetails':{'enableAutoStart':auto_start,'enableAutoStop':auto_stop,'latencyPreference':latency}
        }).execute()
        stream=self.api.liveStreams().insert(part='snippet,cdn,contentDetails',body={
            'snippet':{'title':title+' Stream'},
            'cdn':{'frameRate':fps,'ingestionType':'rtmp','resolution':resolution},
            'contentDetails':{'isReusable':reusable}
        }).execute()
        self.api.liveBroadcasts().bind(part='id,contentDetails',id=broadcast['id'],streamId=stream['id']).execute()
        return {'broadcast_id':broadcast['id'],'stream':self._stream_info(stream)}
