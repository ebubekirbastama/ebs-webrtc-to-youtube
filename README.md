# EBS WebRTC → YouTube Live

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![WebRTC](https://img.shields.io/badge/WebRTC-aiortc-333333?style=for-the-badge)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Pipeline-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)
![YouTube Live](https://img.shields.io/badge/YouTube-Live%20RTMP-FF0000?style=for-the-badge&logo=youtube&logoColor=white)
![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)

> EBS Live üzerinden gelen WebRTC video/ses akışını Python + `aiortc` ile alan, FFmpeg üzerinden işleyip YouTube Live RTMP'ye aktaran; hem **modern masaüstü GUI** hem de **console/headless** kullanımını destekleyen yayın köprüsü.

## 📌 Proje Hakkında

**EBS WebRTC → YouTube Live**, tarayıcı tabanlı EBS Live yayınını YouTube Live'a aktarmak için geliştirilmiş bir WebRTC → FFmpeg → RTMP bridge uygulamasıdır.

Uygulama Python tarafında `aiortc` ile `RTCPeerConnection` oluşturur, Base64 + JSON biçimindeki SDP offer/answer verilerini işler ve WebRTC üzerinden gelen video/ses track'lerini alır. Medya FFmpeg pipeline'ına aktarılır ve YouTube Live RTMP endpoint'ine gönderilir.

Proje iki kullanım biçimine sahiptir:

- 🖥️ **Modern GUI:** PySide6 tabanlı, dark/modern masaüstü arayüz
- 💻 **Console / Headless:** Sunucu, otomasyon ve ileri seviye kullanıcılar için komut satırı motoru

GUI, yayın motorunun yerine geçmez; mevcut `src/webrtc_to_youtube.py` motorunu ayrı bir process olarak çalıştırır. Böylece GUI ile console kullanımının aynı çekirdek kodu kullanması sağlanır.

## ✨ Öne Çıkan Özellikler

### 🖥️ Modern GUI

- 🎨 Modern dark / premium arayüz
- 🪟 Responsive pencere düzeni ve kart tabanlı tasarım
- 🟢 WebRTC ve YouTube bağlantı durum göstergeleri
- ▶️ Yayını GUI üzerinden başlatma
- ⏹️ Yayını güvenli şekilde durdurma
- 📋 WebRTC Answer kodunu tek tıklamayla kopyalama
- 📝 Canlı FFmpeg / WebRTC log ekranı
- 🔐 YouTube RTMP / Stream Key alanı
- 👁️ Stream Key göster/gizle
- ⚙️ FFmpeg executable seçme
- 🖼️ Logo dosyası seçme
- 📍 Logo konumu seçme
- 📐 Logo genişliği ayarlama
- 🌫️ Logo opacity ayarlama
- 🎞️ Re-encode seçeneğini GUI'den kontrol etme
- 📺 Çözünürlük, FPS, bitrate ve maxrate ayarları
- 🔴 Yayın sırasında durum takibi
- 🧹 Uygulama kapanırken yayın process'ini temizleme

### 📡 WebRTC / FFmpeg

- EBS Live WebRTC yayınını alma
- SDP offer/answer kodlarını Base64 + JSON olarak işleme
- STUN / ICE bağlantı desteği
- Video ve ses track'lerini alma
- WebRTC → MPEG-TS → FFmpeg → RTMP pipeline'ı
- Logo yokken mümkün olduğunda düşük CPU'lu aktarım
- Logo / watermark bindirme
- 1080p yeniden ölçekleme
- H.264 `libx264` video encoding
- AAC ses çıkışı
- Bitrate, maxrate, buffer ve FPS ayarları
- Windows FFmpeg yolu desteği
- `.env` üzerinden YouTube RTMP yapılandırması
- Bağlantı kapanırken medya ve FFmpeg kaynaklarını temizleme

## 🖥️ GUI Kullanımı

GUI'yi proje klasöründen çalıştırın:

```bash
python gui.py
```

Uygulama açıldığında genel akış:

1. **WebRTC / Offer** alanına EBS Live yayıncısından alınan offer/davet kodunu girin.
2. **YouTube RTMP / Stream Key** bilgisini girin veya `.env` yapılandırmasını kullanın.
3. İsterseniz **FFmpeg** executable yolunu seçin.
4. Logo kullanacaksanız `assets/logo.svg` veya kendi görselinizi seçin.
5. Çözünürlük, FPS, bitrate, logo konumu ve diğer yayın ayarlarını belirleyin.
6. **YAYINI BAŞLAT** butonuna basın.
7. GUI'nin oluşturduğu **Answer** kodunu kopyalayıp EBS Live yayıncısındaki ilgili alana gönderin.
8. WebRTC ve YouTube durum göstergelerini ve canlı log ekranını takip edin.
9. Yayını bitirmek için **YAYINI DURDUR** butonunu kullanın.

> GUI, WebRTC yayın motorunu arka planda ayrı bir process olarak çalıştırır. Bu nedenle GUI donmadan logları okuyabilir ve yayın process'ini yönetebilir.

## 💻 Console / Headless Kullanımı

GUI kullanmak istemeyenler için çekirdek motor doğrudan çalıştırılabilir:

```bash
python src/webrtc_to_youtube.py --rtmp "rtmp://a.rtmp.youtube.com/live2/STREAM_KEY"
```

FFmpeg yolu belirtmek için:

```powershell
python src/webrtc_to_youtube.py --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe" --rtmp "RTMP_ADRESI"
```

Logo ile:

```powershell
python src/webrtc_to_youtube.py --rtmp "RTMP_ADRESI" --logo "assets/logo.svg" --logo-position top-right --logo-width 220 --logo-opacity 0.90
```

Console modu özellikle sunucu, otomasyon, script ve GUI gerektirmeyen kullanım senaryoları için korunmuştur.

## 🧰 Teknoloji Kartları

| Teknoloji | Rol |
|---|---|
| 🐍 **Python 3.10+** | Uygulama ve WebRTC kontrol katmanı |
| 🖥️ **PySide6** | Modern masaüstü GUI |
| 📡 **aiortc** | WebRTC peer connection ve medya track yönetimi |
| 🎞️ **PyAV / av** | Medya işleme altyapısı |
| ⚙️ **FFmpeg** | Medya işleme, encoding ve RTMP çıkışı |
| ▶️ **YouTube Live** | RTMP yayın hedefi |
| 🔐 **python-dotenv** | Ortam değişkenleri ve yayın yapılandırması |
| 🌐 **STUN / ICE** | WebRTC bağlantı kurulumu |

## 🏗️ Mimari

```text
┌───────────────────────┐
│      EBS Live         │
│  WebRTC Publisher     │
└──────────┬────────────┘
           │ SDP Offer / Answer
           ▼
┌───────────────────────┐
│   EBS WebRTC GUI      │
│      PySide6          │
└──────────┬────────────┘
           │ starts process
           ▼
┌───────────────────────┐
│ Python + aiortc       │
│ RTCPeerConnection     │
│ STUN / ICE             │
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
PySide6>=6.7.0
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
python gui.py
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python gui.py
```

Console motorunu doğrudan çalıştırmak için:

```bash
python src/webrtc_to_youtube.py --rtmp "RTMP_ADRESI"
```

## ⚙️ FFmpeg

Windows ortamında varsayılan FFmpeg yolu:

```text
C:\ffmpeg.exe
```

Farklı bir executable GUI üzerinden seçilebilir veya console kullanımında `--ffmpeg` ile belirtilebilir:

```powershell
python src/webrtc_to_youtube.py --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe" --rtmp "RTMP_ADRESI"
```

## 🖼️ Logo / Watermark

Projede varsayılan marka logosu:

```text
assets/logo.svg
```

GUI açıldığında bu logo uygulama ikonu ve marka görseli olarak kullanılır. Ayrıca GUI üzerinden farklı bir logo seçilebilir.

Console kullanımında:

```bash
python src/webrtc_to_youtube.py \
  --rtmp "RTMP_ADRESI" \
  --logo "assets/logo.svg" \
  --logo-position top-right \
  --logo-width 220 \
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

Codec uyumluluğunu zorlamak için console tarafında:

```bash
--reencode
```

kullanılabilir. Aynı seçenek GUI'deki **Re-Encode** kutusundan da kontrol edilebilir.

## 🔐 Stream Key Güvenliği

YouTube stream key'i parola gibi korunmalıdır.

Önerilen yöntem `.env` kullanmaktır:

```env
YOUTUBE_RTMP=rtmp://a.rtmp.youtube.com/live2/STREAM_KEY
```

Ardından console motorunu RTMP parametresi vermeden çalıştırabilirsiniz:

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
├── assets/
│   └── logo.svg
├── examples/
│   ├── windows-logo.bat
│   └── linux-logo.sh
├── src/
│   └── webrtc_to_youtube.py
├── .env.example
├── .gitignore
├── gui.py
├── LICENSE
├── README.md
└── requirements.txt
```

## 🧪 Sorun Giderme

### GUI açılmıyor

PySide6'nın kurulu olduğundan emin olun:

```bash
pip install PySide6
```

Ardından:

```bash
python gui.py
```

### FFmpeg bulunamıyor

FFmpeg yolunu GUI'deki **FFmpeg seç** alanından belirleyin veya console kullanımında `--ffmpeg` ile tam yolu belirtin.

### WebRTC bağlantısı kurulmuyor

- Offer kodunun tamamını kopyalayın.
- Answer kodunu değiştirmeden EBS Live'a gönderin.
- STUN/ICE bağlantısını kontrol edin.
- NAT ve firewall kısıtlamalarını kontrol edin.
- GUI'deki canlı log alanını veya console çıktısını inceleyin.

### YouTube yayın başlamıyor

- RTMP adresini kontrol edin.
- Stream key'in geçerli olduğundan emin olun.
- YouTube Live yayınının hazır olduğunu kontrol edin.
- Gerekirse `--reencode` ile deneyin.
- GUI'deki YouTube durum göstergesini ve log ekranını kontrol edin.

### Logo görünmüyor

- Logo yolunun doğru olduğunu kontrol edin.
- `assets/logo.svg` dosyasının mevcut olduğundan emin olun.
- Logo genişliği, opacity ve konum ayarlarını kontrol edin.
- FFmpeg'in logo filtreleriyle çalışabildiğini doğrulayın.

## ⚠️ Teknik Sınırlamalar

Bu proje tam teşekküllü bir yayın yönetim platformu değildir. Temel amacı WebRTC medya akışını alıp YouTube Live RTMP'ye aktarmaktır.

GUI, yayın motorunun kontrol katmanıdır; medya işleme yine `aiortc` + FFmpeg tarafından yapılır.

Gelecekte değerlendirilebilecek geliştirmeler:

- Daha gelişmiş reconnect mekanizması
- WebRTC signaling otomasyonu
- Çoklu yayın hedefleri
- Health check ve monitoring
- FFmpeg restart supervision
- Yapılandırma profilleri
- Ayrıntılı istatistik paneli
- Docker desteği
- Web tabanlı yönetim paneli
- Otomatik yayın planlama

## 📄 Lisans

Bu proje **Apache License 2.0** altında lisanslanmıştır.

Lisans metni için repository'deki [`LICENSE`](./LICENSE) dosyasına bakabilirsiniz.

## 👤 Geliştirici

**Ebubekir Bastama**

[GitHub profili](https://github.com/ebubekirbastama)

---

⭐ Projeyi faydalı bulduysanız repository'ye yıldız bırakabilirsiniz.
