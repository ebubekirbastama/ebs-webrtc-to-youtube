from __future__ import annotations
import argparse, asyncio, base64, json, os, subprocess, sys
from pathlib import Path
from dotenv import load_dotenv
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
from aiortc.contrib.media import MediaRecorder

ICE_SERVERS=[RTCIceServer(urls=['stun:stun.l.google.com:19302','stun:stun1.l.google.com:19302']),RTCIceServer(urls=['stun:global.stun.twilio.com:3478'])]

def encode_code(obj): return base64.b64encode(json.dumps(obj,ensure_ascii=False).encode()).decode('ascii')
def decode_code(text): return json.loads(base64.b64decode(''.join(text.split())).decode('utf-8'))
async def wait_ice(pc,timeout=8.0):
    if pc.iceGatheringState=='complete': return
    done=asyncio.Event()
    @pc.on('icegatheringstatechange')
    def _():
        if pc.iceGatheringState=='complete': done.set()
    try: await asyncio.wait_for(done.wait(),timeout)
    except asyncio.TimeoutError: print('[WebRTC] ICE toplama zaman aşımı; mevcut adaylarla devam.',flush=True)

def overlay_xy(pos,mx,my):
    return {'top-left':f'{mx}:{my}','top-right':f'W-w-{mx}:{my}','bottom-left':f'{mx}:H-h-{my}','bottom-right':f'W-w-{mx}:H-h-{my}'}[pos]

def build_ffmpeg_cmd(ffmpeg,rtmp,reencode,logo=None,logo_width=220,logo_opacity=.9,logo_position='top-right',logo_margin_x=40,logo_margin_y=40,resolution='1920x1080',bitrate='5500k',maxrate='6500k',bufsize='12000k',fps=30):
    base=[ffmpeg,'-hide_banner','-loglevel','warning','-fflags','+genpts','-f','mpegts','-i','pipe:0']
    if logo:
        if not Path(logo).is_file(): raise FileNotFoundError(f'Logo dosyası bulunamadı: {logo}')
        base += ['-loop','1','-i',logo]
        ow,oh=map(int,resolution.lower().split('x',1)); opacity=max(0,min(1,float(logo_opacity)))
        filt=(f'[0:v]scale={ow}:{oh}:force_original_aspect_ratio=decrease,pad={ow}:{oh}:(ow-iw)/2:(oh-ih)/2:black,fps={fps}[base];'
              f'[1:v]scale={logo_width}:-1,format=rgba,colorchannelmixer=aa={opacity}[logo];'
              f'[base][logo]overlay={overlay_xy(logo_position,logo_margin_x,logo_margin_y)}:format=auto[vout]')
        out=['-filter_complex',filt,'-map','[vout]','-map','0:a:0?','-c:v','libx264','-preset','veryfast','-tune','zerolatency','-profile:v','high','-pix_fmt','yuv420p','-b:v',bitrate,'-maxrate',maxrate,'-bufsize',bufsize,'-g',str(max(1,fps*2)),'-sc_threshold','0','-c:a','aac','-b:a','128k','-ar','44100','-ac','2','-shortest']
    elif reencode:
        out=['-c:v','libx264','-preset','veryfast','-tune','zerolatency','-profile:v','high','-pix_fmt','yuv420p','-b:v',bitrate,'-maxrate',maxrate,'-bufsize',bufsize,'-g',str(max(1,fps*2)),'-sc_threshold','0','-c:a','aac','-b:a','128k','-ar','44100','-ac','2']
    else: out=['-c','copy']
    return base+out+['-max_muxing_queue_size','1024','-f','flv','-rtmp_live','live',rtmp]

async def run(args):
    pc=RTCPeerConnection(configuration=RTCConfiguration(iceServers=ICE_SERVERS)); tracks=[]; recorder=None; ffmpeg_proc=None
    @pc.on('track')
    def on_track(track): tracks.append(track); print(f'[WebRTC] Kanal alındı: {track.kind}',flush=True)
    try:
        print('[Sistem] Offer bekleniyor...',flush=True); offer=input().strip(); decoded=decode_code(offer); sdp=decoded['sdp']
        await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp['sdp'],type=sdp['type']))
        cmd=build_ffmpeg_cmd(args.ffmpeg,args.rtmp,args.reencode,args.logo,args.logo_width,args.logo_opacity,args.logo_position,args.logo_margin_x,args.logo_margin_y,args.resolution,args.bitrate,args.maxrate,args.bufsize,args.fps)
        print('[FFmpeg] Başlatılıyor...',flush=True); ffmpeg_proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        recorder=MediaRecorder(ffmpeg_proc.stdin,format='mpegts')
        answer=await pc.createAnswer(); await pc.setLocalDescription(answer); await wait_ice(pc)
        code=encode_code({'sdp':{'type':pc.localDescription.type,'sdp':pc.localDescription.sdp}})
        print('EBS_ANSWER_CODE:'+code,flush=True)
        print('[WebRTC] Answer hazır. Yayıncıya gönderin.',flush=True)
        while not tracks: await asyncio.sleep(.1)
        for t in tracks: recorder.addTrack(t)
        await recorder.start(); print('[YouTube] Medya akışı başladı.',flush=True)
        while pc.connectionState not in ('failed','closed','disconnected'):
            await asyncio.sleep(1)
    finally:
        if recorder:
            try: await recorder.stop()
            except Exception: pass
        try: await pc.close()
        except Exception: pass
        if ffmpeg_proc:
            try:
                if ffmpeg_proc.stdin: ffmpeg_proc.stdin.close()
                ffmpeg_proc.wait(timeout=4)
            except Exception:
                try: ffmpeg_proc.kill()
                except Exception: pass

def parser():
    p=argparse.ArgumentParser(); p.add_argument('--rtmp'); p.add_argument('--ffmpeg',required=True); p.add_argument('--logo'); p.add_argument('--reencode',action='store_true'); p.add_argument('--logo-width',type=int,default=220); p.add_argument('--logo-opacity',type=float,default=.9); p.add_argument('--logo-position',choices=['top-left','top-right','bottom-left','bottom-right'],default='top-right'); p.add_argument('--logo-margin-x',type=int,default=40); p.add_argument('--logo-margin-y',type=int,default=40); p.add_argument('--resolution',default='1920x1080'); p.add_argument('--bitrate',default='5500k'); p.add_argument('--maxrate',default='6500k'); p.add_argument('--bufsize',default='12000k'); p.add_argument('--fps',type=int,default=30); return p
if __name__=='__main__':
    load_dotenv(); a=parser().parse_args(); a.rtmp=a.rtmp or os.getenv('YOUTUBE_RTMP','')
    if not a.rtmp: raise SystemExit('RTMP adresi gerekli.')
    try: asyncio.run(run(a))
    except KeyboardInterrupt: pass
    except Exception as exc: print('[Hata]',exc,flush=True); raise
