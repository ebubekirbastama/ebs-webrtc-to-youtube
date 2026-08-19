# EBS WebRTC → YouTube Live v2

Modüler PySide6 masaüstü uygulaması. WebRTC offer/answer akışını `aiortc` ile alır, FFmpeg üzerinden YouTube RTMP/RTMPS hedefine iletir ve isteğe bağlı olarak YouTube Live Streaming API ile stream/broadcast oluşturup RTMP bilgisini otomatik alır.

## İlk çalıştırma (Windows)

1. ZIP'i çıkarın.
2. Google OAuth kullanacaksanız **Desktop app** tipindeki OAuth dosyanızı proje köküne `client_secret.json` adıyla koyun.
3. Yayına bindirilecek logoyu proje köküne `logo.png` adıyla koyun. İsterseniz GUI'den farklı bir PNG/JPG/WebP de seçebilirsiniz.
4. `start_windows.bat` çalıştırın veya `python app.py` kullanın.

`app.py` başlamadan önce eksik Python paketlerini `requirements.txt` üzerinden otomatik kurar. FFmpeg bulunamazsa arayüzde **FFMPEG OTOMATİK KUR** düğmesi Windows `winget` üzerinden Gyan.FFmpeg paketini kurmayı dener. Ayrıca `ffmpeg.exe` elle seçilebilir.

## YouTube API

Arayüzde **YOUTUBE’A BAĞLAN** ile tarayıcı tabanlı OAuth yetkilendirmesi açılır. Token `config/youtube_token.json` dosyasına kaydedilir ve `.gitignore` kapsamındadır.

**KEY’İ OTOMATİK AL** mevcut YouTube liveStream kaynaklarını listeler. **YENİ YOUTUBE YAYINI OLUŞTUR** yeni broadcast + stream oluşturur, ikisini bind eder ve YouTube'un verdiği RTMP/RTMPS ingestion adresi ile streamName bilgisini birleştirerek yayın URL'sini doldurur.

> Program rastgele stream key üretmez. Key YouTube tarafından API üzerinden verilir.

## Güvenlik

Şunları Git'e göndermeyin:
- `client_secret.json`
- `config/youtube_token.json`
- `.env`

Stream key uygulama ayarlarına API modunda kalıcı olarak yazılmaz. Manuel RTMP alanı istenirse `settings.json` içine kaydedilebilir; ortak bilgisayarlarda manuel adres kaydetmeyin.

## Klasörler

- `app.py`: başlangıç noktası
- `bootstrap.py`: bağımlılık/FFmpeg kontrolü
- `core/webrtc_engine.py`: WebRTC + FFmpeg yayın motoru
- `core/process_manager.py`: GUI arka plan process yönetimi
- `youtube/auth.py`: OAuth
- `youtube/api.py`: YouTube Live API
- `ui/main_window.py`: metallic-light GUI
- `ui/styles.py`: tema
- `logo.png`: yayın watermark dosyası
- `assets/`: uygulama görselleri
- `config/`: ayarlar ve OAuth token
- `logs/`: log klasörü

## Notlar

YouTube kanalının canlı yayın kullanımına uygun ve YouTube Data API v3 / Live Streaming API erişiminin etkin olması gerekir. OAuth consent screen ve Desktop App OAuth istemcisi Google Cloud Console tarafında yapılandırılmalıdır.

## v2.1 Paint-safe düzeltmesi

Bu paket arayüzde SVG -> QImage -> QPainter dönüşümü kullanmaz. Program ikonu ve yayın logosu PNG üzerinden çalışır. Ayrıca butonlarda QGraphicsDropShadowEffect kaldırılmıştır; böylece eski `QPainter::begin ... Painter not active` zincirini tetikleyen runtime paint yolları devre dışı bırakılmıştır.

Başlatma: `start_windows.bat` veya `python app.py`.
YouTube OAuth için `client_secret.json` dosyasını proje köküne koyabilir veya GUI'deki **CLIENT_SECRET SEÇ** düğmesiyle seçebilirsiniz. OAuth token `config/youtube_token.json` altında tutulur ve `.gitignore` tarafından GitHub'a gönderilmez.
