"""
webrtc_to_youtube.py
=====================
EBS Live (sunucusuz WebRTC) sitesinden gelen görüntü/sesi, headless bir
Python "izleyici" olarak yakalayıp ffmpeg üzerinden YouTube RTMP'ye basar.

MİMARİ
------
Site tarayıcıdan tarayıcıya (P2P) çalışır; Python bir tarayıcı olmadığı için
WebRTC "konuşamaz". Bu script, aiortc kütüphanesi ile gerçek bir WebRTC
istemcisi (izleyici) rolü üstlenir:

  1) Yayıncı tarayıcıda "+ Yeni İzleyici Davet Et" ile bir davet kodu üretir.
  2) O kod bu scriptin konsoluna yapıştırılır.
  3) Script bir CEVAP kodu üretir; bu kod yayıncıya geri gönderilip onun
     "Bağlan" kutusuna yapıştırılır.
  4) WebRTC bağlantısı kurulunca gelen video/ses, aiortc içinde otomatik
     olarak H.264 / AAC'ye kodlanıp bir ffmpeg alt sürecine "mpegts" formatında
     pipe üzerinden akıtılır; ffmpeg bunu (mümkünse yeniden kodlamadan,
     -c copy ile) YouTube RTMP adresine basar.

Kod değişim formatı, web sitesindeki encodeCode/decodeCode ile BİREBİR
uyumludur (base64(JSON({"sdp": {...}}))) — yani siteyle doğrudan konuşabilir.

KURULUM
-------
    pip install aiortc av

Not (Windows): aiortc bazı platformlarda derleme araçları isteyebilir.
Sorun yaşarsan güncel bir Python (3.10+) ve güncel pip ile tekrar dene;
çoğu Windows sürümü için hazır "wheel" paketleri mevcuttur.

KULLANIM
--------
    python webrtc_to_youtube.py --rtmp "rtmp://a.rtmp.youtube.com/live2/XXXX-XXXX-XXXX-XXXX"

Logo ile:
    python webrtc_to_youtube.py --rtmp "rtmp://a.rtmp.youtube.com/live2/XXXX-XXXX-XXXX-XXXX" --logo "logo.png"

Varsayılan ffmpeg yolu C:\\ffmpeg.exe olarak ayarlıdır (mevcut scriptinizle
aynı), --ffmpeg parametresiyle değiştirebilirsiniz.
"""

import argparse
import asyncio
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
from aiortc.contrib.media import MediaRecorder

# =========================
# Sabitler
# =========================
DEFAULT_FFMPEG_PATH = r"C:\ffmpeg.exe"

# Web sitesindeki ICE_SERVERS ile aynı — sadece IP keşfi için, signaling burada geçmez.
ICE_SERVERS = [
    RTCIceServer(urls=["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"]),
    RTCIceServer(urls=["stun:global.stun.twilio.com:3478"]),
]


# =========================
# Site ile uyumlu kod kodlama/çözme
# =========================
def encode_code(obj: dict) -> str:
    raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def decode_code(text: str) -> dict:
    clean = "".join(text.split())  # boşluk/satır sonlarını temizle
    raw = base64.b64decode(clean)
    return json.loads(raw.decode("utf-8"))


# =========================
# ICE toplama tamamlanana kadar bekle (web tarafındaki mantığın aynısı)
# =========================
async def wait_ice_gathering_complete(pc: RTCPeerConnection, timeout: float = 8.0):
    if pc.iceGatheringState == "complete":
        return
    done = asyncio.Event()

    @pc.on("icegatheringstatechange")
    def _on_change():
        if pc.iceGatheringState == "complete":
            done.set()

    try:
        await asyncio.wait_for(done.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        print("[WebRTC] ICE toplama zaman aşımına uğradı, mevcut adaylarla devam ediliyor.")


def _logo_overlay_xy(position: str, margin_x: int, margin_y: int) -> str:
    positions = {
        "top-left": f"{margin_x}:{margin_y}",
        "top-right": f"W-w-{margin_x}:{margin_y}",
        "bottom-left": f"{margin_x}:H-h-{margin_y}",
        "bottom-right": f"W-w-{margin_x}:H-h-{margin_y}",
    }
    return positions[position]


def build_ffmpeg_cmd(
    ffmpeg_path: str,
    rtmp_url: str,
    reencode: bool,
    logo: str | None = None,
    logo_width: int = 200,
    logo_opacity: float = 1.0,
    logo_position: str = "top-left",
    logo_margin_x: int = 50,
    logo_margin_y: int = 50,
    resolution: str = "1920x1080",
    bitrate: str = "5500k",
    maxrate: str = "6500k",
    bufsize: str = "12000k",
    fps: int = 30,
):
    """
    Girdi: aiortc'nin ürettiği mpegts akışı, stdin'den (pipe:0).
    Çıktı: YouTube RTMP.

    Logo yok ve reencode=False:
      -c copy ile yeniden kodlamadan aktarım yapılır.

    Logo verilirse:
      Video filtrelenmek zorunda olduğu için otomatik olarak libx264 ile
      yeniden kodlanır ve logo bindirilir.
    """
    base = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel", "warning",
        "-fflags", "+genpts",
        "-f", "mpegts",
        "-i", "pipe:0",
    ]

    force_encode = reencode or bool(logo)

    if logo:
        if not Path(logo).is_file():
            raise FileNotFoundError(f"Logo dosyası bulunamadı: {logo}")

        base += ["-loop", "1", "-i", logo]

        try:
            out_w, out_h = resolution.lower().split("x", 1)
            out_w, out_h = int(out_w), int(out_h)
        except Exception as exc:
            raise ValueError("Çözünürlük 1920x1080 biçiminde olmalı.") from exc

        opacity = max(0.0, min(1.0, float(logo_opacity)))
        xy = _logo_overlay_xy(logo_position, logo_margin_x, logo_margin_y)

        filter_complex = (
            f"[0:v]scale={out_w}:{out_h}:force_original_aspect_ratio=decrease,"
            f"pad={out_w}:{out_h}:(ow-iw)/2:(oh-ih)/2:black,"
            f"fps={fps}[base];"
            f"[1:v]scale={logo_width}:-1,format=rgba,"
            f"colorchannelmixer=aa={opacity}[logo];"
            f"[base][logo]overlay={xy}:format=auto[vout]"
        )

        out = [
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "0:a:0?",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-tune", "zerolatency",
            "-profile:v", "high",
            "-pix_fmt", "yuv420p",
            "-b:v", bitrate,
            "-maxrate", maxrate,
            "-bufsize", bufsize,
            "-g", str(max(1, fps * 2)),
            "-sc_threshold", "0",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-ac", "2",
            "-shortest",
        ]
    elif force_encode:
        out = [
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-tune", "zerolatency",
            "-profile:v", "high",
            "-pix_fmt", "yuv420p",
            "-b:v", bitrate,
            "-maxrate", maxrate,
            "-bufsize", bufsize,
            "-g", str(max(1, fps * 2)),
            "-sc_threshold", "0",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-ac", "2",
        ]
    else:
        out = ["-c", "copy"]

    tail = [
        "-max_muxing_queue_size", "1024",
        "-f", "flv",
        "-rtmp_live", "live",
        rtmp_url,
    ]
    return base + out + tail


async def run(args):
    pc = RTCPeerConnection(configuration=RTCConfiguration(iceServers=ICE_SERVERS))
    received_tracks = []
    ffmpeg_proc = None
    recorder = None
    started = asyncio.Event()

    @pc.on("track")
    def on_track(track):
        print(f"[WebRTC] Kanal alındı: {track.kind}")
        received_tracks.append(track)

    @pc.on("connectionstatechange")
    async def on_state_change():
        print(f"[WebRTC] Bağlantı durumu: {pc.connectionState}")
        if pc.connectionState == "connected" and not started.is_set():
            started.set()
        elif pc.connectionState in ("failed", "disconnected", "closed"):
            await shutdown()

    async def shutdown():
        print("[Sistem] Kapatılıyor...")
        try:
            if recorder:
                await recorder.stop()
        except Exception:
            pass
        try:
            await pc.close()
        except Exception:
            pass
        if ffmpeg_proc and ffmpeg_proc.stdin:
            try:
                ffmpeg_proc.stdin.close()
            except Exception:
                pass
        if ffmpeg_proc:
            try:
                ffmpeg_proc.wait(timeout=5)
            except Exception:
                ffmpeg_proc.kill()

    # 1) Yayıncının davet kodunu al
    print("\n=== EBS Live -> YouTube Aktarıcı (headless) ===")
    print("Yayıncı tarayıcıda '+ Yeni İzleyici Davet Et' ile bir kod üretsin.")
    offer_code = input("Davet kodunu buraya yapıştır ve Enter'a bas:\n> ").strip()
    try:
        decoded = decode_code(offer_code)
        offer_sdp = decoded["sdp"]
    except Exception as e:
        print(f"[Hata] Kod okunamadı: {e}")
        return

    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp["sdp"], type=offer_sdp["type"]))

    # 2) ffmpeg alt sürecini, cevabı üretmeden önce hazırla (stdin pipe'ı bekliyor olacak)
    ffmpeg_cmd = build_ffmpeg_cmd(
        args.ffmpeg,
        args.rtmp,
        args.reencode,
        logo=args.logo,
        logo_width=args.logo_width,
        logo_opacity=args.logo_opacity,
        logo_position=args.logo_position,
        logo_margin_x=args.logo_margin_x,
        logo_margin_y=args.logo_margin_y,
        resolution=args.resolution,
        bitrate=args.bitrate,
        maxrate=args.maxrate,
        bufsize=args.bufsize,
        fps=args.fps,
    )
    print("[FFmpeg] Komut:", " ".join(ffmpeg_cmd))
    ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    # 3) MediaRecorder, gelen kareleri mpegts (H.264/AAC) olarak ffmpeg'in stdin'ine yazacak
    recorder = MediaRecorder(ffmpeg_proc.stdin, format="mpegts")

    # 4) Cevabı oluştur
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await wait_ice_gathering_complete(pc)

    code = encode_code({"sdp": {"type": pc.localDescription.type, "sdp": pc.localDescription.sdp}})
    print("\n[Hazır] Bu CEVAP kodunu kopyala ve yayıncıya gönder:\n")
    print(code)
    print("\nYayıncı bu kodu ilgili izleyici davet kartındaki kutuya yapıştırıp 'Bağlan' dediğinde")
    print("bağlantı kurulacak ve aktarım otomatik başlayacak. (Ctrl+C ile durdurabilirsin)\n")

    # 5) Bağlantı kurulmasını bekle, sonra kayıt/aktarımı başlat
    await started.wait()
    for t in received_tracks:
        recorder.addTrack(t)
    await recorder.start()
    print("[Aktarım] Başladı — YouTube'a basılıyor.")

    # 6) Bağlantı kesilene / Ctrl+C'ye kadar bekle
    try:
        while pc.connectionState not in ("failed", "disconnected", "closed"):
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[Sistem] Kullanıcı durdurdu.")
    finally:
        await shutdown()


def main():
    if load_dotenv:
        load_dotenv()
    parser = argparse.ArgumentParser(description="EBS Live WebRTC akışını YouTube RTMP'ye aktarır (sunucusuz, headless).")
    parser.add_argument("--rtmp", default=os.getenv("YOUTUBE_RTMP"), help="YouTube RTMP + akış anahtarı. --rtmp verilmezse YOUTUBE_RTMP ortam değişkeni kullanılır.")
    parser.add_argument("--ffmpeg", default=DEFAULT_FFMPEG_PATH, help=f"ffmpeg yürütülebilir dosya yolu (varsayılan: {DEFAULT_FFMPEG_PATH})")
    parser.add_argument("--reencode", action="store_true", help="YouTube kodek/profil hatası verirse yeniden kodlamayı zorla (daha yavaş, daha fazla CPU)")
    parser.add_argument("--logo", help="Yayına bindirilecek PNG/JPG logo dosyası. Verilirse video otomatik yeniden kodlanır.")
    parser.add_argument("--logo-width", type=int, default=200, help="Logonun piksel cinsinden genişliği (varsayılan: 200)")
    parser.add_argument("--logo-opacity", type=float, default=1.0, help="Logo saydamlığı 0.0-1.0 (varsayılan: 1.0)")
    parser.add_argument("--logo-position", choices=["top-left", "top-right", "bottom-left", "bottom-right"], default="top-left", help="Logo konumu")
    parser.add_argument("--logo-margin-x", type=int, default=50, help="Logonun yatay kenar boşluğu (varsayılan: 50)")
    parser.add_argument("--logo-margin-y", type=int, default=50, help="Logonun dikey kenar boşluğu (varsayılan: 50)")
    parser.add_argument("--resolution", default="1920x1080", help="Logo/reencode modunda çıkış çözünürlüğü (varsayılan: 1920x1080)")
    parser.add_argument("--bitrate", default="5500k", help="Video bitrate (varsayılan: 5500k)")
    parser.add_argument("--maxrate", default="6500k", help="Maksimum video bitrate (varsayılan: 6500k)")
    parser.add_argument("--bufsize", default="12000k", help="VBV buffer boyutu (varsayılan: 12000k)")
    parser.add_argument("--fps", type=int, default=30, help="Hedef FPS / GOP hesabı (varsayılan: 30)")
    args = parser.parse_args()

    if not args.rtmp:
        parser.error("RTMP adresi gerekli. --rtmp kullan veya .env içinde YOUTUBE_RTMP tanımla.")

    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
