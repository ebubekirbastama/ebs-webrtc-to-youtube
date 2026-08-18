# EBS WebRTC to YouTube

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![WebRTC](https://img.shields.io/badge/WebRTC-aiortc-333333?style=for-the-badge)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Pipeline-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)
![YouTube Live](https://img.shields.io/badge/YouTube-Live%20RTMP-FF0000?style=for-the-badge&logo=youtube&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

> EBS Live üzerinden gelen WebRTC video/ses akışını Python + `aiortc` ile alan, FFmpeg üzerinden işleyip YouTube Live RTMP'ye aktaran headless yayın köprüsü.

## 📌 Proje Hakkında

**EBS WebRTC to YouTube**, EBS Live yayınını WebRTC üzerinden alıp YouTube Live'a RTMP olarak aktarmak için hazırlanmıştır.

Uygulama tarayıcı otomasyonu yerine Python tarafında gerçek bir `RTCPeerConnection` oluşturur. SDP offer/answer verilerini Base64 + JSON formatında işler, WebRTC video/ses track'lerini alır ve medya akışını FFmpeg üzerinden YouTube RTMP endpoint'ine gönderir.

## 🧰 Teknoloji Kartları

| Teknoloji | Rol |
|---|---|
| 🐍 **Python 3.10+** | Uygulama ve kontrol katmanı |
| 📡 **aiortc** | WebRTC bağlantısı ve medya track yönetimi |
| 🎞️ **PyAV / av** | Medya işleme altyapısı |
| ⚙️ **FFmpeg** | MPEG-TS, encoding ve RTMP çıkışı |
| ▶️ **YouTube Live** | RTMP yayın hedefi |
| 🔐 **python-dotenv** | `.env` tabanlı yapılandırma |
| 🌐 **STUN / ICE** | WebRTC bağlantı adaylarının keşfi |

## ✨ Özellikler

- 📡 EBS Live WebRTC yayınını alma
- 🤝 Base64 + JSON SDP offer/answer işleme
- 🌐 STUN/ICE desteği
- 🎥 Video ve ses track'lerini alma
- 🔄 `aiortc → MediaRecorder → MPEG-TS → FFmpeg → RTMP` pipeline'ı
- ⚡ Logo olmadan mümkün olduğunda düşük CPU'lu `-c copy` aktarımı
- 🖼️ Logo/watermark bindirme
- 📐 1080p yeniden ölçekleme
- 🎛️ Logo konumu, genişliği ve opacity ayarı
- 🎞️ Logo/re-encode modunda H.264 `libx264`
- 📊 Bitrate, maxrate, buffer ve FPS ayarları
- 🔊 AAC 128 kbps / 44.1 kHz / stereo çıkış
- 🪟 Windows'ta özel FFmpeg yolu belirleme
- 🔐 YouTube stream key'i `.env` üzerinden kullanabilme
- 🧹 WebRTC, recorder ve FFmpeg süreçlerinin kontrollü kapatılması

## 🏗️ Mimari

```text
┌───────────────────────┐
│       EBS Live        │
│ Browser / Publisher   │
└──────────┬────────────┘
           │
           │ SDP Offer / Answer
           │ Base64(JSON)
           ▼
┌───────────────────────┐
│ Python + aiortc       │
│ RTCPeerConnection     │
│ STUN / ICE            │
└──────────┬────────────┘
           │
           │ Video + Audio
           ▼
┌───────────────────────┐
│ aiortc MediaRecorder  │
│ MPEG-TS               │
└──────────┬────────────┘
           │ stdin
           ▼
┌───────────────────────┐
│        FFmpeg         │
│ copy / H.264 + AAC    │
│ optional logo filter  │
└──────────┬────────────┘
           │ RTMP / FLV
           ▼
┌───────────────────────┐
│     YouTube Live      │
└───────────────────────┘
```

## 🔁 WebRTC Signaling Akışı

Proje ayrı bir signaling sunucusu çalıştırmaz. EBS Live tarafından oluşturulan davet/offer kodu Python uygulamasına aktarılır.

```text
EBS Live Publisher
       │
       │ Offer Code
       ▼
Python
       │
       │ Base64 + JSON decode
       ▼
aiortc RTCPeerConnection
       │
       │ createAnswer + ICE
       ▼
Python
       │
       │ Answer Code
       ▼
EBS Live Publisher
       │
       ▼
WebRTC Media
       │
       ▼
FFmpeg
       │
       ▼
YouTube Live
```

## 📦 Gereksinimler

- Python **3.10 veya üzeri**
- FFmpeg
- WebRTC destekli EBS Live yayıncısı
- YouTube Live RTMP endpoint'i
- YouTube Live stream key
- İnternet erişimi

`requirements.txt` temel olarak şu paketleri içerir:

```text
aiortc>=1.9.0
av>=12.0.0
python-dotenv>=1.0.1
```

## 🚀 Kurulum

```bash
git clone https://github.com/ebubekirbastama/ebs-webrtc-to-youtube.git
cd ebs-webrtc-to-youtube
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ⚙️ FFmpeg

Windows'ta uygulamanın varsayılan FFmpeg yolu:

```text
C:\ffmpeg.exe
```

Farklı bir FFmpeg executable kullanmak için:

```powershell
python src/webrtc_to_youtube.py --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe" --rtmp "RTMP_ADRESI"
```

## ▶️ Temel Kullanım

```bash
python src/webrtc_to_youtube.py --rtmp "rtmp://a.rtmp.youtube.com/live2/STREAM_KEY"
```

Ardından:

1. EBS Live yayınını başlatın.
2. **Yeni İzleyici Davet Et** seçeneğini kullanın.
3. Oluşturulan offer/davet kodunu Python konsoluna yapıştırın.
4. Python tarafından oluşturulan answer kodunu kopyalayın.
5. Answer kodunu EBS Live tarafındaki ilgili alana gönderin.
6. WebRTC bağlantısının kurulmasını bekleyin.
7. Medya FFmpeg üzerinden YouTube Live'a aktarılır.

## 🖼️ Logo / Watermark

Mevcut asset yapısını koruyarak `assets/logo.png` kullanılabilir.

```bash
python src/webrtc_to_youtube.py \
  --rtmp "RTMP_ADRESI" \
  --logo "assets/logo.png"
```

Logo seçenekleri:

```text
--logo FILE
--logo-width 200
--logo-opacity 1.0
--logo-position top-left
--logo-margin-x 50
--logo-margin-y 50
```

Desteklenen konumlar:

```text
top-left
top-right
bottom-left
bottom-right
```

Logo kullanıldığında video filtresi gerektiği için FFmpeg yeniden encode moduna geçer ve `libx264` kullanır.

## 🎥 Yayın Kalitesi

Logo/re-encode modundaki temel ayarlar:

| Ayar | Varsayılan |
|---|---:|
| Çözünürlük | `1920x1080` |
| FPS | `30` |
| Video bitrate | `5500k` |
| Maxrate | `6500k` |
| Buffer | `12000k` |
| Video codec | `libx264` |
| Preset | `veryfast` |
| Audio codec | `AAC` |
| Audio bitrate | `128k` |
| Sample rate | `44100 Hz` |
| Channels | Stereo |

Örnek:

```bash
python src/webrtc_to_youtube.py \
  --rtmp "RTMP_ADRESI" \
  --resolution 1920x1080 \
  --fps 30 \
  --bitrate 5500k \
  --maxrate 6500k \
  --bufsize 12000k
```

## ⚡ Copy Modu ve Re-Encode

### Logo yoksa

Mümkün olduğunda:

```text
-c copy
```

kullanılarak yeniden encode gerektirmeyen düşük CPU'lu aktarım yapılabilir.

### Logo veya filtre varsa

Video üzerinde işlem yapılması gerektiği için:

```text
libx264 + AAC
```

ile yeniden kodlama kullanılır.

YouTube/codec uyumluluğu için yeniden kodlamayı zorlamak isterseniz:

```bash
--reencode
```

kullanabilirsiniz.

## 🔐 Stream Key Güvenliği

YouTube stream key'i parola gibi korunmalıdır.

`.env` örneği:

```env
YOUTUBE_RTMP=rtmp://a.rtmp.youtube.com/live2/STREAM_KEY
```

Ardından:

```bash
python src/webrtc_to_youtube.py
```

### Güvenlik kuralları

- Stream key'i kaynak koda yazmayın.
- `.env` dosyasını Git'e göndermeyin.
- Stream key'i README, issue veya ekran görüntülerinde paylaşmayın.
- Sızmış bir key'i YouTube üzerinden yenileyin.

## 📁 Proje Yapısı

```text
ebs-webrtc-to-youtube/
├── src/
│   └── webrtc_to_youtube.py
├── assets/
│   └── README.md
├── examples/
│   ├── windows-logo.bat
│   └── linux-logo.sh
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## 🧪 Sorun Giderme

### FFmpeg bulunamıyor

FFmpeg yolunu açıkça belirtin:

```bash
--ffmpeg "C:\ffmpeg\bin\ffmpeg.exe"
```

### WebRTC bağlantısı kurulmuyor

- Offer kodunun tamamını kopyalayın.
- Answer kodunu değiştirmeden geri gönderin.
- STUN erişimini kontrol edin.
- NAT/firewall kısıtlamalarını kontrol edin.
- WebRTC bağlantı durumunu konsoldan takip edin.

### YouTube codec/format problemi

Şunu deneyin:

```bash
--reencode
```

Bu mod H.264/AAC çıkışını zorlar.

### Logo görünmüyor

- Dosya yolunu kontrol edin.
- `assets/logo.png` dosyasının mevcut olduğundan emin olun.
- `--logo-position` değerini kontrol edin.
- Logo genişliği ve opacity değerlerini kontrol edin.

## ⚠️ Teknik Sınırlamalar

Bu proje **headless yayın köprüsü / araştırma projesi** niteliğindedir.

- Signaling işlemi otomatik bir merkezi sunucu üzerinden yapılmaz.
- WebRTC bağlantısı EBS Live'ın kullandığı offer/answer akışına bağlıdır.
- FFmpeg sistem üzerinde ayrıca bulunmalıdır.
- Logo/re-encode modu CPU kullanımını artırır.
- Ağ/NAT/firewall koşulları WebRTC bağlantısını etkileyebilir.
- YouTube yayın kotası, codec gereksinimleri ve RTMP erişimi YouTube tarafındaki koşullara bağlıdır.

## 🛠️ Geliştirme Yol Haritası

- Otomatik signaling servisi
- Web tabanlı kontrol paneli
- Birden fazla yayın desteği
- Otomatik reconnect
- Yayın sağlık/bitrate monitörü
- FFmpeg stderr log paneli
- Docker desteği
- Sistem servisi olarak çalışma
- YouTube API entegrasyonu
- Çoklu RTMP çıkışı

## 📄 Lisans

Bu repository'deki `LICENSE` dosyasına bakınız.

## 👤 Geliştirici

**Ebubekir Bastama**  
GitHub: https://github.com/ebubekirbastama

---

⭐ Projeyi faydalı bulduysanız repository'ye yıldız bırakabilirsiniz.
