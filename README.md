# EBS WebRTC to YouTube

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![WebRTC](https://img.shields.io/badge/WebRTC-aiortc-333333?style=for-the-badge)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Pipeline-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)
![YouTube Live](https://img.shields.io/badge/YouTube-Live%20RTMP-FF0000?style=for-the-badge&logo=youtube&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

> EBS Live üzerinden gelen WebRTC video/ses akışını Python + `aiortc` ile gerçek bir WebRTC izleyicisi olarak alan, FFmpeg üzerinden işleyip YouTube Live RTMP'ye aktaran headless yayın köprüsü.

## 📌 Proje Hakkında

**EBS WebRTC to YouTube**, tarayıcı tabanlı EBS Live yayınını ayrı bir yayın sunucusuna ihtiyaç duymadan YouTube Live'a aktarmak için hazırlanmıştır.

Uygulama bir tarayıcı otomasyonu değildir. Python tarafında `aiortc` kullanarak gerçek bir `RTCPeerConnection` oluşturur, EBS Live'ın kullandığı Base64 + JSON tabanlı SDP offer/answer kodlarını işler ve WebRTC üzerinden gelen medya track'lerini alır. Gelen medya `MediaRecorder` ile MPEG-TS biçiminde FFmpeg stdin'ine aktarılır; FFmpeg de bunu YouTube RTMP endpoint'ine gönderir. fileciteturn262file0turn264file0

## 🧰 Teknoloji Kartları

| Teknoloji | Rol |
|---|---|
| 🐍 **Python 3.10+** | Uygulama ve WebRTC kontrol katmanı |
| 📡 **aiortc** | WebRTC peer connection ve medya track yönetimi |
| 🎞️ **PyAV / av** | Medya işleme altyapısı |
| ⚙️ **FFmpeg** | MPEG-TS alma, filtreleme/encoding ve RTMP çıkışı |
| ▶️ **YouTube Live** | RTMP yayın hedefi |
| 🔐 **python-dotenv** | RTMP bilgilerinin `.env` üzerinden yönetimi |
| 🌐 **STUN** | ICE bağlantı adaylarının keşfi |

Bağımlılıklar repository'deki `requirements.txt` içerisinde `aiortc>=1.9.0`, `av>=12.0.0` ve `python-dotenv>=1.0.1` olarak tanımlıdır. fileciteturn263file0

## ✨ Özellikler

- 📡 EBS Live WebRTC yayınını alma
- 🤝 SDP offer/answer kodlarını Base64 + JSON olarak işleme
- 🌐 Google/Twilio STUN sunucuları üzerinden ICE candidate keşfi
- 🎥 Video ve 🔊 ses track'lerini alma
- 🔄 `aiortc → MediaRecorder → MPEG-TS → FFmpeg → RTMP` pipeline'ı
- ⚡ Logo yokken mümkün olduğunda `-c copy` ile düşük CPU'lu aktarım
- 🖼️ Logo/watermark bindirme
- 📐 1080p yeniden ölçekleme ve aspect-ratio koruma
- 🎛️ Logo konumu, genişliği ve saydamlığı ayarlama
- 🎞️ Logo/re-encode modunda H.264 `libx264`
- 📊 Bitrate, maxrate, buffer ve FPS ayarları
- 🔊 AAC 128 kbps / 44.1 kHz / stereo çıkış
- 🪟 Windows için varsayılan `C:\ffmpeg.exe`
- 🔐 YouTube stream key'i kaynak koduna yazmadan `.env` kullanabilme
- 🧹 Bağlantı kapanırken recorder, WebRTC peer ve FFmpeg sürecini kapatma

## 🏗️ Mimari

```text
┌───────────────────────┐
│      EBS Live         │
│  Browser / Publisher  │
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
           │ Video + Audio tracks
           ▼
┌───────────────────────┐
│ aiortc MediaRecorder  │
│ MPEG-TS               │
└──────────┬────────────┘
           │ stdin pipe
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

Kaynak kodunda FFmpeg stdin'i `MediaRecorder(..., format="mpegts")` ile beslenmekte ve çıktı `-f flv` + `-rtmp_live live` ile verilen RTMP adresine gönderilmektedir. fileciteturn264file0

## 🔁 WebRTC Signaling Akışı

Bu proje signaling sunucusu çalıştırmaz. EBS Live yayıncısının oluşturduğu davet kodu elle Python konsoluna aktarılır.

```text
EBS Live Publisher
       │
       │ 1. Invite / Offer Code
       ▼
Python
       │
       │ 2. decode Base64 + JSON
       ▼
aiortc RTCPeerConnection
       │
       │ 3. createAnswer()
       │ 4. ICE gathering
       ▼
Python
       │
       │ 5. Answer Code
       ▼
EBS Live Publisher
       │
       │ 6. Connect
       ▼
WebRTC Media
       │
       ▼
YouTube RTMP
```

Kodlama/çözme tarafında `base64.b64encode`, `base64.b64decode` ve JSON kullanılır; SDP nesnesi `{ "sdp": {...} }` yapısında taşınır. fileciteturn262file0

## 📦 Gereksinimler

- **Python 3.10 veya üzeri**
- **FFmpeg**
- WebRTC destekli EBS Live yayıncısı
- YouTube Live RTMP endpoint'i ve stream key
- İnternet erişimi

Python paketleri:

```text
aiortc>=1.9.0
av>=12.0.0
python-dotenv>=1.0.1
```

fileciteturn263file0

## 🚀 Kurulum

Repository'yi klonlayın:

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

## ⚙️ FFmpeg Kurulumu

Windows'ta mevcut uygulama varsayılan olarak:

```text
C:\ffmpeg.exe
```

yolunu kullanır. Bu değer kaynak kodunda `DEFAULT_FFMPEG_PATH` olarak tanımlıdır. İsterseniz `--ffmpeg` ile farklı bir executable belirtebilirsiniz. fileciteturn262file0

Örnek:

```powershell
python src/webrtc_to_youtube.py `
  --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe" `
  --rtmp "RTMP_ADRESI"
```

## ▶️ Temel Kullanım

```bash
python src/webrtc_to_youtube.py --rtmp "rtmp://a.rtmp.youtube.com/live2/STREAM_KEY"
```

Ardından:

1. EBS Live yayınını başlatın.
2. **+ Yeni İzleyici Davet Et** seçeneğini kullanın.
3. Oluşturulan davet/offer kodunu Python konsoluna yapıştırın.
4. Python'un ürettiği cevap/answer kodunu kopyalayın.
5. Bu kodu EBS Live'daki ilgili izleyici alanına yapıştırın.
6. **Bağlan** seçeneğini kullanın.
7. WebRTC bağlantısı kurulduğunda medya FFmpeg pipeline'ına ve ardından YouTube Live'a aktarılır.

Kaynak kodunda bağlantı `connected` durumuna geçtiğinde alınan track'ler `MediaRecorder`'a eklenerek aktarım başlatılmaktadır. fileciteturn264file0

## 🖼️ Logo / Watermark

Repository'deki mevcut `assets/logo.png` yolunu kullanabilir veya kendi görselinizi belirtebilirsiniz.

```bash
python src/webrtc_to_youtube.py \
  --rtmp "RTMP_ADRESI" \
  --logo "assets/logo.png"
```

Logo kullanıldığında video filtrelenmek zorunda olduğu için FFmpeg otomatik olarak `libx264` ile yeniden kodlama moduna geçer. Logo; ölçeklenir, saydamlığı ayarlanır ve seçilen konuma bindirilir. fileciteturn262file0

### Logo seçenekleri

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

Örnek:

```bash
python src/webrtc_to_youtube.py \
  --rtmp "RTMP_ADRESI" \
  --logo "assets/logo.png" \
  --logo-position top-right \
  --logo-width 180 \
  --logo-opacity 0.90
```

## 🎥 Yayın Kalitesi

Logo/re-encode modunda mevcut varsayılanlar:

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
| Audio sample rate | `44100 Hz` |
| Channels | Stereo |

Kaynak kodundaki FFmpeg komutu H.264 için `yuv420p`, `high` profile ve `zerolatency` tuning kullanır. GOP değeri FPS'in iki katı olacak şekilde oluşturulur. fileciteturn264file0

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

## ⚡ Copy Modu vs Re-Encode

### Logo yoksa

Mümkün olduğunda:

```text
-c copy
```

kullanılır. Bu durumda video yeniden kodlanmadığı için CPU tüketimi daha düşüktür.

### Logo varsa

Video üzerinde filtre uygulanması gerektiğinden:

```text
libx264 + AAC
```

ile yeniden kodlama yapılır.

Ayrıca YouTube/codec uyumluluğu için gerektiğinde:

```bash
--reencode
```

parametresiyle yeniden kodlama zorlanabilir. Bu mod daha fazla CPU kullanır. fileciteturn262file0

## 🔐 Stream Key Güvenliği

YouTube stream key'i **parola gibi** değerlendirin.

Önerilen yöntem:

```env
YOUTUBE_RTMP=rtmp://a.rtmp.youtube.com/live2/STREAM_KEY
```

Ardından:

```bash
python src/webrtc_to_youtube.py
```

`python-dotenv` kullanıldığında `.env` dosyası yüklenebilir ve `--rtmp` verilmezse `YOUTUBE_RTMP` ortam değişkeni kullanılabilir. fileciteturn262file0

**Asla:**

- Stream key'i Python kaynak koduna yazmayın.
- `.env` dosyasını Git'e commit etmeyin.
- Terminal çıktısındaki RTMP URL'sini herkese açık şekilde paylaşmayın.
- Sızmış bir stream key'i kullanmaya devam etmeyin; YouTube üzerinden yenileyin.

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

### `ffmpeg` bulunamıyor

Windows'ta varsayılan yolun doğru olduğundan emin olun veya:

```bash
--ffmpeg "C:\ffmpeg\bin\ffmpeg.exe"
```

kullanın.

### WebRTC bağlantısı kurulmuyor

- EBS Live'daki offer kodunun tamamını kopyaladığınızdan emin olun.
- Answer kodunu değiştirmeden geri gönderin.
- STUN erişiminin engellenmediğini kontrol edin.
- NAT/firewall ortamını kontrol edin.
- Konsoldaki `[WebRTC] Bağlantı durumu:` mesajlarını inceleyin.

ICE gathering belirlenen sürede tamamlanmazsa uygulama mevcut adaylarla devam eder; kaynak kodunda timeout varsayılanı **8 saniyedir**. fileciteturn262file0

### YouTube codec/format hatası

Önce:

```bash
--reencode
```

ile deneyin. Bu, FFmpeg tarafında H.264/AAC çıkışını zorlar.

### Logo görünmüyor

- Logo dosya yolunun doğru olduğundan emin olun.
- PNG/JPG dosyasının gerçekten mevcut olduğunu kontrol edin.
- `--logo-position`, `--logo-width` ve margin değerlerini kontrol edin.

Kaynak kodu logo dosyası bulunamazsa `FileNotFoundError` üretir. fileciteturn262file0

## ⚠️ Teknik Sınırlamalar

Bu proje **headless yayın köprüsü** olarak tasarlanmıştır; tam özellikli bir yayın otomasyon platformu değildir.

Mevcut implementasyonda:

- Signaling kodları kullanıcı tarafından manuel olarak kopyalanır.
- Kalıcı bir signaling sunucusu bulunmaz.
- Otomatik yeniden bağlanma/reconnect mekanizması bulunmaz.
- Tek bir WebRTC oturumu üzerinden çalışır.
- FFmpeg işlemi yerel makinede çalışır.
- Re-encode modu CPU yükünü önemli ölçüde artırabilir.
- RTMP bağlantısının başarısı YouTube ve ağ durumuna bağlıdır.

## 🛠️ Gelecek Geliştirmeler

- Web tabanlı signaling / QR kod ile eşleştirme
- Otomatik reconnect
- Birden fazla WebRTC kaynağı
- YouTube yayın durumunun API üzerinden izlenmesi
- Otomatik stream başlatma/durdurma
- FFmpeg health monitoring
- Bitrate düşürme / adaptive fallback
- WebRTC bağlantı ve medya istatistiklerinin gösterilmesi
- Windows için tek dosya executable paketleme
- Docker/Linux deployment profili
- Yapılandırılabilir yayın profilleri

## 📄 Lisans

MIT License. Ayrıntılar için repository'deki `LICENSE` dosyasına bakın.

## 👤 Geliştirici

**Ebubekir Bastama**  
GitHub: [@ebubekirbastama](https://github.com/ebubekirbastama)

---

⭐ Projeyi faydalı bulduysanız repository'ye yıldız bırakabilirsiniz.
