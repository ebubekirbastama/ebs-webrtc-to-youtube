# EBS WebRTC to YouTube

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![WebRTC](https://img.shields.io/badge/WebRTC-aiortc-333333?style=for-the-badge)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Pipeline-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)
![YouTube Live](https://img.shields.io/badge/YouTube-Live%20RTMP-FF0000?style=for-the-badge&logo=youtube&logoColor=white)
![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)

> EBS Live üzerinden gelen WebRTC video/ses akışını Python + `aiortc` ile alan, FFmpeg üzerinden işleyip YouTube Live RTMP'ye aktaran headless yayın köprüsü.

## 📌 Proje Hakkında

**EBS WebRTC to YouTube**, tarayıcı tabanlı EBS Live yayınını YouTube Live'a aktarmak için hazırlanmış bir WebRTC → FFmpeg → RTMP bridge uygulamasıdır.

Uygulama Python tarafında `aiortc` ile `RTCPeerConnection` oluşturur, Base64 + JSON biçimindeki SDP offer/answer verilerini işler ve WebRTC üzerinden gelen video/ses track'lerini alır. Medya FFmpeg pipeline'ına aktarılır ve YouTube Live RTMP endpoint'ine gönderilir.

## 🧰 Teknoloji Kartları

| Teknoloji | Rol |
|---|---|
| 🐍 **Python 3.10+** | Uygulama ve WebRTC kontrol katmanı |
| 📡 **aiortc** | WebRTC peer connection ve medya track yönetimi |
| 🎞️ **PyAV / av** | Medya işleme altyapısı |
| ⚙️ **FFmpeg** | Medya işleme, encoding ve RTMP çıkışı |
| ▶️ **YouTube Live** | RTMP yayın hedefi |
| 🔐 **python-dotenv** | Ortam değişkenleri ve yayın yapılandırması |
| 🌐 **STUN / ICE** | WebRTC bağlantı kurulumu |

## ✨ Özellikler

- 📡 EBS Live WebRTC yayınını alma
- 🤝 SDP offer/answer kodlarını Base64 + JSON olarak işleme
- 🌐 STUN / ICE bağlantı desteği
- 🎥 Video ve ses track'lerini alma
- 🔄 WebRTC → MPEG-TS → FFmpeg → RTMP pipeline'ı
- ⚡ Logo yokken mümkün olduğunda düşük CPU'lu aktarım
- 🖼️ Logo / watermark bindirme
- 📐 1080p yeniden ölçekleme
- 🎛️ Logo konumu, genişliği ve saydamlığını ayarlama
- 🎞️ Logo kullanımında H.264 `libx264` encoding
- 📊 Bitrate, maxrate, buffer ve FPS ayarları
- 🔊 AAC ses çıkışı
- 🪟 Windows FFmpeg yolu desteği
- 🔐 `.env` üzerinden YouTube RTMP yapılandırması
- 🧹 Bağlantı kapanırken medya ve FFmpeg kaynaklarını temizleme

## 🏗️ Mimari

```text
┌───────────────────────┐
│      EBS Live         │
│  WebRTC Publisher     │
└──────────┬────────────┘
           │ SDP Offer / Answer
           ▼
┌───────────────────────┐
│ Python + aiortc       │
│ RTCPeerConnection     │
│ STUN / ICE            │
└──────────┬────────────┘
           │ Video + Audio
           ▼
┌───────────────────────┐
│ Media / MPEG-TS       │
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

## 📦 Gereksinimler

- Python 3.10 veya üzeri
- FFmpeg
- EBS Live WebRTC yayıncısı
- YouTube Live RTMP endpoint'i ve stream key
- İnternet bağlantısı

Python bağımlılıkları:

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

Windows ortamında varsayılan FFmpeg yolu:

```text
C:\ffmpeg.exe
```

Farklı bir executable belirtmek için:

```powershell
python src/webrtc_to_youtube.py --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe" --rtmp "RTMP_ADRESI"
```

## ▶️ Temel Kullanım

```bash
python src/webrtc_to_youtube.py --rtmp "rtmp://a.rtmp.youtube.com/live2/STREAM_KEY"
```

Ardından EBS Live üzerinden yayıncı davet/offer kodunu alın, Python uygulamasına girin ve oluşturulan answer kodunu EBS Live'a geri gönderin.

WebRTC bağlantısı kurulduktan sonra medya FFmpeg pipeline'ına aktarılır ve YouTube Live RTMP endpoint'ine gönderilir.

## 🖼️ Logo / Watermark

Mevcut `assets/logo.png` dosyasını veya kendi görselinizi kullanabilirsiniz:

```bash
python src/webrtc_to_youtube.py \
  --rtmp "RTMP_ADRESI" \
  --logo "assets/logo.png" \
  --logo-position top-right \
  --logo-width 180 \
  --logo-opacity 0.90
```

Desteklenen konumlar:

```text
top-left
top-right
bottom-left
bottom-right
```

## 🎥 Yayın Kalitesi

Logo/re-encode modunda kullanılabilen temel ayarlar:

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

## ⚡ Copy Modu ve Re-Encode

Logo kullanılmadığında mümkün olan durumlarda medya yeniden encode edilmeden aktarılabilir.

Logo veya başka video filtresi kullanıldığında yeniden encoding gerekir:

```text
libx264 + AAC
```

Codec uyumluluğunu zorlamak için:

```bash
--reencode
```

kullanılabilir.

## 🔐 Stream Key Güvenliği

YouTube stream key'i parola gibi korunmalıdır.

Önerilen yöntem `.env` kullanmaktır:

```env
YOUTUBE_RTMP=rtmp://a.rtmp.youtube.com/live2/STREAM_KEY
```

Ardından:

```bash
python src/webrtc_to_youtube.py
```

### Dikkat

- Stream key'i kaynak koda yazmayın.
- `.env` dosyasını Git'e göndermeyin.
- Stream key'i herkese açık şekilde paylaşmayın.
- Sızan bir key'i YouTube üzerinden yenileyin.

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

FFmpeg yolunu kontrol edin veya `--ffmpeg` ile tam yolu belirtin.

### WebRTC bağlantısı kurulmuyor

- Offer kodunun tamamını kopyalayın.
- Answer kodunu değiştirmeden EBS Live'a gönderin.
- STUN/ICE bağlantısını kontrol edin.
- NAT ve firewall kısıtlamalarını kontrol edin.
- Konsoldaki WebRTC bağlantı durumunu inceleyin.

### YouTube yayın başlamıyor

- RTMP adresini kontrol edin.
- Stream key'in geçerli olduğundan emin olun.
- YouTube Live yayınının hazır olduğunu kontrol edin.
- Gerekirse `--reencode` ile deneyin.

### Logo görünmüyor

- Logo yolunun doğru olduğunu kontrol edin.
- Dosyanın gerçekten mevcut olduğundan emin olun.
- Logo genişliği, opacity ve konum parametrelerini kontrol edin.

## ⚠️ Teknik Sınırlamalar

Bu proje tam teşekküllü bir yayın yönetim platformu değildir. Temel amacı WebRTC medya akışını alıp YouTube Live RTMP'ye aktarmaktır.

Üretim ortamında aşağıdaki geliştirmeler değerlendirilebilir:

- Daha gelişmiş reconnect mekanizması
- WebRTC signaling otomasyonu
- Çoklu yayın hedefleri
- Health check ve monitoring
- FFmpeg restart supervision
- Yapılandırma dosyası desteği
- Daha ayrıntılı logging
- Docker desteği
- Web tabanlı yönetim paneli

## 📄 Lisans

Bu proje **Apache License 2.0** altında lisanslanmıştır.

Lisans metni için repository'deki [`LICENSE`](./LICENSE) dosyasına bakabilirsiniz.

## 👤 Geliştirici

**Ebubekir Bastama**

[GitHub profili](https://github.com/ebubekirbastama)

---

⭐ Projeyi faydalı bulduysanız repository'ye yıldız bırakabilirsiniz.
