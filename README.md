# EBS WebRTC to YouTube

EBS Live üzerinden gelen WebRTC görüntü ve ses akışını Python + aiortc ile alıp FFmpeg üzerinden YouTube Live RTMP'ye aktaran köprü uygulaması.

Bu proje, tarayıcıdaki EBS Live yayınını bir WebRTC izleyicisi gibi karşılar. Yayıncı tarafından oluşturulan davet kodunu alır, cevap kodu üretir ve bağlantı kurulduktan sonra gelen medya akışını YouTube Live'a yönlendirir.

## Özellikler

- WebRTC yayınını Python tarafında alma
- `aiortc` ile gerçek WebRTC peer bağlantısı
- FFmpeg üzerinden YouTube Live RTMP çıkışı
- Logo / watermark bindirme
- Logo konumu seçimi
- Logo genişliği ve saydamlığı ayarı
- 1080p yeniden ölçekleme
- Ayarlanabilir bitrate, maxrate, buffer ve FPS
- Logo kullanılmadığında düşük CPU tüketimi için `-c copy`
- Logo kullanıldığında otomatik H.264 yeniden kodlama
- `.env` desteği
- Windows odaklı varsayılan FFmpeg yolu
- Stream key'in kaynak koduna gömülmesini gerektirmez

## Mimari

```text
EBS Live / Browser
       |
       | WebRTC P2P
       v
Python + aiortc
       |
       | MPEG-TS pipe
       v
     FFmpeg
       |
       | RTMP
       v
 YouTube Live
```

## Gereksinimler

- Python 3.10+
- FFmpeg
- WebRTC destekli EBS Live yayıncısı
- YouTube Live RTMP adresi / stream key

## Kurulum

Repoyu klonlayın:

```bash
git clone https://github.com/ebubekirbastama/ebs-webrtc-to-youtube.git
cd ebs-webrtc-to-youtube
```

Sanal ortam oluşturmanız önerilir:

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

## FFmpeg

Windows'ta script varsayılan olarak:

```text
C:\ffmpeg.exe
```

yolunu kullanır.

Başka bir konum kullanıyorsanız:

```bash
python src/webrtc_to_youtube.py --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe" --rtmp "RTMP_ADRESI"
```

## Kullanım

### Temel kullanım

```bash
python src/webrtc_to_youtube.py --rtmp "rtmp://a.rtmp.youtube.com/live2/XXXX-XXXX-XXXX-XXXX"
```

Script başladıktan sonra:

1. EBS Live yayınını başlatın.
2. `+ Yeni İzleyici Davet Et` butonuna basın.
3. Oluşan davet kodunu Python konsoluna yapıştırın.
4. Python tarafından üretilen cevap kodunu kopyalayın.
5. EBS Live içindeki ilgili izleyici kartına cevap kodunu yapıştırın.
6. `Bağlan` butonuna basın.
7. WebRTC bağlantısı kurulduğunda yayın YouTube'a aktarılmaya başlar.

## Logo ile yayın

`assets/logo.png` içerisine kendi logonuzu koyabilirsiniz.

```bash
python src/webrtc_to_youtube.py ^
  --rtmp "rtmp://a.rtmp.youtube.com/live2/XXXX-XXXX-XXXX-XXXX" ^
  --logo "assets/logo.png"
```

Linux/macOS:

```bash
python3 src/webrtc_to_youtube.py \
  --rtmp "rtmp://a.rtmp.youtube.com/live2/XXXX-XXXX-XXXX-XXXX" \
  --logo "assets/logo.png"
```

Logo kullanıldığında video filtrelenmesi gerektiği için FFmpeg otomatik olarak H.264 yeniden kodlama moduna geçer.

## Logo seçenekleri

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

## Yayın kalitesi seçenekleri

Varsayılan değerler:

```text
Çözünürlük : 1920x1080
FPS        : 30
Bitrate    : 5500k
Maxrate    : 6500k
Buffer     : 12000k
Audio      : AAC 128 kbps / 44.1 kHz / Stereo
```

Örnek:

```bash
python src/webrtc_to_youtube.py \
  --rtmp "RTMP_ADRESI" \
  --logo "assets/logo.png" \
  --resolution 1920x1080 \
  --fps 30 \
  --bitrate 5500k \
  --maxrate 6500k \
  --bufsize 12000k
```

## .env kullanımı

Önce:

```bash
copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Sonra `.env`:

```env
YOUTUBE_RTMP=rtmp://a.rtmp.youtube.com/live2/XXXX-XXXX-XXXX-XXXX
```

Böylece:

```bash
python src/webrtc_to_youtube.py --logo "assets/logo.png"
```

şeklinde çalıştırabilirsiniz.

> `.env` dosyası `.gitignore` içindedir. Stream key'inizi GitHub'a göndermeyin.

## `-c copy` ve logo modu

Logo kullanılmadığında script mümkün olduğunda:

```text
-c copy
```

kullanır. Bu yöntem yeniden video kodlama yapmadığı için daha az CPU tüketir.

Logo eklendiğinde FFmpeg görüntüyü değiştirmek zorunda olduğundan video:

```text
libx264
```

ile yeniden kodlanır.

## Klasör yapısı

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

## Güvenlik

YouTube stream key bir parola gibi değerlendirilmelidir.

- Kaynak koduna stream key yazmayın.
- `.env` dosyasını GitHub'a yüklemeyin.
- Yanlışlıkla yayınlanan stream key'i YouTube Studio üzerinden yenileyin.
- Ekran görüntüsü veya terminal çıktısı paylaşırken RTMP adresindeki anahtarı gizleyin.

## EBS Live

Bu araç EBS Live WebRTC yayın sistemiyle birlikte kullanılmak üzere geliştirilmiştir.

WebRTC offer/answer kodları Base64 içinde JSON biçiminde taşınır ve Python istemcisi EBS Live'ın kod formatıyla uyumludur.

## Lisans

MIT License. Ayrıntılar için `LICENSE` dosyasına bakın.
