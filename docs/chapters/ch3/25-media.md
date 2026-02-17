# Глава 25. Медиа-форматы: изображения, аудио, видео

## Введение

Медиа-файлы — это бинарные данные, представляющие изображения, звук или видео. Ключевое различие:

- **Контейнер** — формат файла (MP4, MKV, FLAC)
- **Кодек** — алгоритм сжатия (H.264, VP9, Opus)

```
┌──────────────────────────────────────────────────┐
│  MP4 (контейнер)                                 │
│  ┌────────────────────────────────────────────┐  │
│  │  Видео: H.264 (кодек)                      │  │
│  │  - 1920x1080, 24 fps                       │  │
│  └────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────┐  │
│  │  Аудио: AAC (кодек)                        │  │
│  │  - 48 kHz, stereo                          │  │
│  └────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────┐  │
│  │  Субтитры: SRT                             │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

!!! note "Важно"
    Один контейнер может содержать разные кодеки. MP4 может иметь H.264, H.265, AV1 видео и AAC, MP3, Opus аудио.

---

## 25.1 Изображения

### PNG: без потерь

**PNG** (Portable Network Graphics, 1996) — сжатие без потерь, alpha-канал.

#### Структура

```
┌────────────────────────────────────────────┐
│  Signature: 89 50 4E 47 0D 0A 1A 0A        │
│             \x89 P  N  G  \r \n ^Z \n      │
├────────────────────────────────────────────┤
│  IHDR chunk (Image Header)                 │
│    - ширина, высота                        │
│    - bit depth (8, 16)                     │
│    - color type (grayscale, RGB, RGBA)     │
├────────────────────────────────────────────┤
│  IDAT chunks (Image Data)                  │
│    - сжатые данные (DEFLATE)               │
├────────────────────────────────────────────┤
│  IEND chunk (конец)                        │
└────────────────────────────────────────────┘
```

```bash
# Информация о PNG
$ file image.png
image.png: PNG image data, 800 x 600, 8-bit/color RGB, non-interlaced

$ identify image.png
image.png PNG 800x600 800x600+0+0 8-bit sRGB 125KB 0.000u 0:00.000

# Оптимизация PNG
$ optipng image.png
OptiPNG: 125KB → 98KB (21.6% decrease)

# Pngcrush
$ pngcrush image.png image_opt.png
```

**Применение:**
- Графика с чёткими границами (логотипы, скриншоты)
- Прозрачность (alpha-канал)
- Без потерь

### JPEG: с потерями

**JPEG** (Joint Photographic Experts Group, 1992) — сжатие с потерями для фотографий.

#### Структура

```
┌────────────────────────────────────────────┐
│  SOI (Start Of Image): FF D8               │
├────────────────────────────────────────────┤
│  APP0 (JFIF marker): FF E0                 │
│    - JFIF version                          │
│    - pixel density                         │
├────────────────────────────────────────────┤
│  APP1 (EXIF): FF E1                        │
│    - метаданные камеры                     │
│    - GPS координаты                        │
│    - дата съёмки                           │
├────────────────────────────────────────────┤
│  DQT (Quantization Tables): FF DB          │
│  SOF0 (Start Of Frame): FF C0              │
│  DHT (Huffman Tables): FF C4               │
├────────────────────────────────────────────┤
│  SOS (Start Of Scan): FF DA                │
│    - сжатые данные изображения             │
├────────────────────────────────────────────┤
│  EOI (End Of Image): FF D9                 │
└────────────────────────────────────────────┘
```

```bash
# Информация
$ file photo.jpg
photo.jpg: JPEG image data, JFIF standard 1.01, ...

$ identify photo.jpg
photo.jpg JPEG 4032x3024 4032x3024+0+0 8-bit sRGB 2.1MB

# EXIF метаданные
$ exiftool photo.jpg
File Name                       : photo.jpg
File Size                       : 2.1 MB
Camera Model Name               : iPhone 13 Pro
Date/Time Original              : 2025:02:04 10:00:00
GPS Latitude                    : 40.7128 N
GPS Longitude                   : 74.0060 W
Focal Length                    : 5.7 mm
F Number                        : 1.5
ISO                             : 64
```

**Качество vs размер:**

```bash
# Максимальное качество (почти без потерь)
$ convert input.png -quality 95 output.jpg

# Оптимальное (обычно незаметно)
$ convert input.png -quality 85 output.jpg

# Агрессивное сжатие
$ convert input.png -quality 60 output.jpg
```

```bash
$ ls -lh
-rw-r--r-- 1 user user 1.2M Feb  4 10:00 photo_q95.jpg
-rw-r--r-- 1 user user 450K Feb  4 10:00 photo_q85.jpg
-rw-r--r-- 1 user user 180K Feb  4 10:00 photo_q60.jpg
```

### WebP: современный формат

**WebP** (Google, 2010) — как PNG (без потерь), так и JPEG (с потерями).

```bash
# Конвертация PNG → WebP (без потерь)
$ cwebp -lossless input.png -o output.webp

# JPEG → WebP (с потерями, качество 80)
$ cwebp -q 80 input.jpg -o output.webp

# Сравнение размеров
$ ls -lh
-rw-r--r-- 1 user user 450K Feb  4 10:00 photo.jpg
-rw-r--r-- 1 user user 320K Feb  4 10:00 photo.webp    # ~30% меньше
```

**Преимущества:**
- Меньше размер при том же качестве
- Поддержка alpha-канала (в отличие от JPEG)
- Анимация (альтернатива GIF)

**Недостатки:**
- Поддержка браузеров (старые IE, Safari < 14)

### GIF: анимация

**GIF** (1987) — 256 цветов, простая анимация.

```bash
# Создать GIF из PNG
$ convert -delay 10 -loop 0 frame*.png animation.gif
#          ^^^^^^^^  ^^^^^^
#          10×1/100 = 0.1s между кадрами
#                    бесконечный цикл

# GIF → MP4 (меньше размер!)
$ ffmpeg -i animation.gif -movflags faststart \
         -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
         animation.mp4

$ ls -lh
-rw-r--r-- 1 user user 5.2M Feb  4 10:00 animation.gif
-rw-r--r-- 1 user user 890K Feb  4 10:00 animation.mp4   # ~83% меньше
```

!!! tip "Альтернативы GIF"
    - **WebP animated**: меньше размер, лучше качество
    - **APNG**: PNG анимация (поддержка хуже)
    - **MP4/WebM**: для сложных анимаций

### AVIF: будущее

**AVIF** (2019) — основан на AV1 видеокодеке.

```bash
# Конвертация
$ avifenc -s 0 input.jpg output.avif
#         ^^^^
#         скорость (0=медленно/лучше, 10=быстро/хуже)

$ ls -lh
-rw-r--r-- 1 user user 450K Feb  4 10:00 photo.jpg
-rw-r--r-- 1 user user 320K Feb  4 10:00 photo.webp
-rw-r--r-- 1 user user 180K Feb  4 10:00 photo.avif   # ~60% меньше JPEG
```

---

## 25.2 Аудио

### WAV: без сжатия

**WAV** (Microsoft, 1991) — несжатый аудио (PCM).

```
┌────────────────────────────────────────────┐
│  RIFF header: 'RIFF' + size                │
├────────────────────────────────────────────┤
│  WAVE header: 'WAVE'                       │
├────────────────────────────────────────────┤
│  fmt chunk: формат                         │
│    - sample rate (44100, 48000 Hz)         │
│    - bit depth (16, 24 bit)                │
│    - channels (1=mono, 2=stereo)           │
├────────────────────────────────────────────┤
│  data chunk: сырые PCM данные              │
└────────────────────────────────────────────┘
```

```bash
# Информация
$ file audio.wav
audio.wav: RIFF (little-endian) data, WAVE audio, 
           Microsoft PCM, 16 bit, stereo 44100 Hz

$ ffprobe audio.wav
Input #0, wav, from 'audio.wav':
  Duration: 00:03:45.00
    Stream #0:0: Audio: pcm_s16le, 44100 Hz, stereo, s16, 1411 kb/s
                        ^^^^^^^^^^  ^^^^^      ^^^^^^
                        PCM 16-bit  частота    каналы
```

**Расчёт размера:**

```
Размер (байт) = sample_rate × bit_depth/8 × channels × duration

44100 Hz × 16 bit / 8 × 2 channels × 225 seconds = 39,690,000 байт ≈ 38 МБ
```

### MP3: классический lossy

**MP3** (MPEG-1 Audio Layer III, 1993) — популярный формат с потерями.

```bash
# Информация
$ ffprobe audio.mp3
Input #0, mp3, from 'audio.mp3':
  Duration: 00:03:45.00
    Stream #0:0: Audio: mp3, 44100 Hz, stereo, fltp, 320 kb/s

# Конвертация WAV → MP3
$ lame -b 320 audio.wav audio.mp3
#       ^^^^^^
#       битрейт 320 kbps (максимальное качество)

$ lame -V 2 audio.wav audio.mp3
#       ^^^
#       переменный битрейт (VBR), качество 2 (0=лучше, 9=хуже)

$ ls -lh
-rw-r--r-- 1 user user  38M Feb  4 10:00 audio.wav
-rw-r--r-- 1 user user 9.0M Feb  4 10:00 audio_320.mp3
-rw-r--r-- 1 user user 5.8M Feb  4 10:00 audio_v2.mp3
```

### ID3-теги: метаданные в MP3

MP3-файлы хранят метаданные (исполнитель, альбом, обложка) в **ID3-тегах** — бинарных блоках в начале (ID3v2) или конце (ID3v1) файла. Это аналог EXIF для изображений.

```bash
# Просмотр тегов
$ id3v2 -l audio.mp3
id3v2 tag info for audio.mp3:
TIT2 (Title): Bohemian Rhapsody
TPE1 (Artist): Queen
TALB (Album): A Night at the Opera
TRCK (Track): 11
TDRC (Year): 1975

# Установка тегов
$ id3v2 -t "Bohemian Rhapsody" -a "Queen" -A "A Night at the Opera" audio.mp3

# Или через ffprobe
$ ffprobe -show_format audio.mp3 2>/dev/null | grep TAG
TAG:title=Bohemian Rhapsody
TAG:artist=Queen
```

```python
# Python: чтение/запись через mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB

# Чтение
audio = MP3("audio.mp3")
print(audio.tags.get("TIT2"))  # Title
print(audio.info.length)       # Длительность в секундах

# Запись
audio.tags.add(TIT2(encoding=3, text=["New Title"]))
audio.tags.add(TPE1(encoding=3, text=["New Artist"]))
audio.save()
```

!!! info "EXIF vs ID3 vs xattr"
    Все три — метаданные, но хранятся по-разному:
    
    | Механизм | Где хранится | Привязан к |
    |----------|-------------|------------|
    | **EXIF** | Внутри JPEG (сегмент APP1) | Формату файла |
    | **ID3** | Внутри MP3 (начало/конец файла) | Формату файла |
    | **xattr** | В файловой системе (inode) | ОС/ФС, не формату |
    
    EXIF и ID3 — часть **содержимого файла** (копируются при `cp`).
    xattr — часть **файловой системы** (могут потеряться при копировании, см. главу 9).

### FLAC: lossless сжатие

**FLAC** (Free Lossless Audio Codec, 2001) — сжатие без потерь.

```bash
# WAV → FLAC
$ flac audio.wav -o audio.flac

# FLAC → WAV (полное восстановление)
$ flac -d audio.flac -o audio_restored.wav

$ ls -lh
-rw-r--r-- 1 user user  38M Feb  4 10:00 audio.wav
-rw-r--r-- 1 user user  22M Feb  4 10:00 audio.flac    # ~42% меньше

# Проверка идентичности
$ diff audio.wav audio_restored.wav
# (пусто = идентичны)
```

| Формат | Тип | Размер (3:45) | Качество |
|--------|-----|---------------|----------|
| **WAV** | Несжатый | 38 МБ | 🎵🎵🎵🎵🎵 |
| **FLAC** | Lossless | 22 МБ | 🎵🎵🎵🎵🎵 |
| **MP3 320k** | Lossy | 9 МБ | 🎵🎵🎵🎵 |
| **MP3 VBR** | Lossy | 6 МБ | 🎵🎵🎵🎵 |
| **Opus 128k** | Lossy | 3.6 МБ | 🎵🎵🎵 |

### Opus: современный lossy

**Opus** (2012) — лучшее качество/битрейт.

```bash
# WAV → Opus
$ opusenc --bitrate 128 audio.wav audio.opus

$ ls -lh
-rw-r--r-- 1 user user  38M Feb  4 10:00 audio.wav
-rw-r--r-- 1 user user 3.6M Feb  4 10:00 audio.opus    # сопоставимо с MP3 VBR

# Качество Opus 128 kbps ≈ MP3 192 kbps
```

**Применение:**
- VoIP (голосовые звонки)
- Стриминг музыки
- YouTube, Discord

### AAC: Apple & Android

**AAC** (Advanced Audio Coding, 1997) — используется в MP4, Apple Music.

```bash
# WAV → AAC (внутри M4A контейнера)
$ ffmpeg -i audio.wav -c:a aac -b:a 256k audio.m4a

$ ls -lh
-rw-r--r-- 1 user user  38M Feb  4 10:00 audio.wav
-rw-r--r-- 1 user user 7.2M Feb  4 10:00 audio.m4a
```

---

## 25.3 Видео

### Контейнер vs Кодек (углублённо)

```
┌─────────────────────────────────────────────────────────┐
│  MP4 (контейнер)                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Video Track                                      │  │
│  │  Codec: H.264 (AVC)                               │  │
│  │  Resolution: 1920x1080                            │  │
│  │  Frame rate: 24 fps                               │  │
│  │  Bitrate: 5000 kbps                               │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Audio Track 1 (English)                          │  │
│  │  Codec: AAC                                       │  │
│  │  Channels: 5.1 (surround)                         │  │
│  │  Sample rate: 48000 Hz                            │  │
│  │  Bitrate: 256 kbps                                │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Audio Track 2 (Russian)                          │  │
│  │  Codec: AAC, Stereo, 48000 Hz, 192 kbps           │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Subtitle Track (SRT)                             │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### H.264 (AVC): стандарт индустрии

**H.264** (2003) — самый популярный видеокодек.

```bash
# Информация
$ ffprobe video.mp4
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'video.mp4':
  Duration: 00:05:30.00
    Stream #0:0: Video: h264 (High) (avc1), yuv420p, 1920x1080, 5000 kb/s, 24 fps
    Stream #0:1: Audio: aac (LC) (mp4a), 48000 Hz, stereo, 256 kb/s

# Перекодировка
$ ffmpeg -i input.mkv -c:v libx264 -preset slow -crf 22 \
         -c:a aac -b:a 192k output.mp4
#                 ^^^^           ^^^
#                 preset         CRF (0=lossless, 51=worst)
#                 slower = лучше сжатие
```

**Presets:**

| Preset | Скорость | Качество/Размер |
|--------|----------|-----------------|
| **ultrafast** | ⭐⭐⭐⭐⭐ | ⭐ (большой) |
| **fast** | ⭐⭐⭐⭐ | ⭐⭐ |
| **medium** (default) | ⭐⭐⭐ | ⭐⭐⭐ |
| **slow** | ⭐⭐ | ⭐⭐⭐⭐ |
| **veryslow** | ⭐ | ⭐⭐⭐⭐⭐ (меньше) |

**CRF (Constant Rate Factor):**
- 0 = lossless (огромный размер)
- 18-22 = visually lossless
- 23-28 = хорошее качество
- 28+ = заметные артефакты

### H.265 (HEVC): улучшенное сжатие

**H.265** (2013) — на 25-50% лучше сжимает, чем H.264.

```bash
# Перекодировка в HEVC
$ ffmpeg -i input.mp4 -c:v libx265 -preset medium -crf 28 \
         -c:a copy output_hevc.mp4
#                                              ^^^^
#                                              копировать аудио без перекодирования

$ ls -lh
-rw-r--r-- 1 user user 1.2G Feb  4 10:00 input.mp4 (H.264)
-rw-r--r-- 1 user user 650M Feb  4 10:00 output_hevc.mp4 (H.265)   # ~46% меньше
```

**Применение:**
- 4K видео (меньше битрейт)
- Стриминг-сервисы (Netflix, Apple TV+)

**Недостатки:**
- Медленное кодирование
- Требовательно к декодированию (CPU/GPU)

### VP9: открытый кодек (Google)

**VP9** (2013) — открытый аналог H.265.

```bash
# Перекодировка в VP9 (WebM контейнер)
$ ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 \
         -c:a libopus -b:a 128k output.webm
```

**Применение:**
- YouTube (по умолчанию для >1080p)
- Без лицензионных отчислений

### AV1: будущее

**AV1** (2018) — на 30% лучше VP9, на 50% лучше H.264.

```bash
# Перекодировка в AV1 (очень медленно!)
$ ffmpeg -i input.mp4 -c:v libaom-av1 -crf 30 -b:v 0 \
         -c:a libopus output.av1.mp4

# Или SVT-AV1 (быстрее)
$ ffmpeg -i input.mp4 -c:v libsvtav1 -crf 35 -preset 6 \
         -c:a libopus output.av1.mp4

$ ls -lh
-rw-r--r-- 1 user user 1.2G Feb  4 10:00 input.mp4 (H.264)
-rw-r--r-- 1 user user 650M Feb  4 10:00 hevc.mp4 (H.265)
-rw-r--r-- 1 user user 580M Feb  4 10:00 vp9.webm (VP9)
-rw-r--r-- 1 user user 420M Feb  4 10:00 av1.mp4 (AV1)    # ~65% меньше H.264
```

**Применение:**
- Netflix (постепенный переход)
- YouTube (для новых видео)

**Недостатки:**
- Очень медленное кодирование
- Декодирование требует hardware support

---

## 25.4 Практические задачи

### Извлечение кадра из видео

```bash
# Извлечь кадр на 1:23.5
$ ffmpeg -ss 00:01:23.5 -i video.mp4 -frames:v 1 thumbnail.jpg

# Извлечь каждый 10-й кадр
$ ffmpeg -i video.mp4 -vf "select='not(mod(n\,10))'" -vsync vfr frames_%04d.png
```

### Изменение разрешения

```bash
# 1080p → 720p
$ ffmpeg -i input.mp4 -vf scale=1280:720 output_720p.mp4

# 4K → 1080p (сохранить пропорции)
$ ffmpeg -i input_4k.mp4 -vf scale=1920:-1 output_1080p.mp4
#                                      ^^
#                                      автоматическая высота
```

### Вырезка фрагмента

```bash
# Вырезать с 1:00 до 2:30
$ ffmpeg -i input.mp4 -ss 00:01:00 -to 00:02:30 -c copy output.mp4
#                                                ^^^^^^
#                                                копировать без перекодирования (быстро)
```

### Склеивание видео

```bash
# Создать список
$ echo "file 'part1.mp4'" > list.txt
$ echo "file 'part2.mp4'" >> list.txt
$ echo "file 'part3.mp4'" >> list.txt

# Склеить
$ ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
```

### Добавление аудио

```bash
# Заменить аудио
$ ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4
#                                                      ^^^^^^^^^^  ^^^^^^^^^^
#                                                      видео из 1-го, аудио из 2-го
```

---

## Резюме

### Сравнительная таблица: изображения

| Формат | Сжатие | Прозрачность | Анимация | Размер (относительный) |
|--------|--------|--------------|----------|------------------------|
| **PNG** | Lossless | ✅ | ❌ | 100% |
| **JPEG** | Lossy | ❌ | ❌ | 35% |
| **WebP** | Оба | ✅ | ✅ | 25% (lossy), 70% (lossless) |
| **AVIF** | Lossy | ✅ | ✅ | 15% |
| **GIF** | Lossless | ⚠️ (1 bit) | ✅ | 150% (для фото) |

### Сравнительная таблица: аудио

| Формат | Тип | Битрейт | Размер (3:45) | Качество |
|--------|-----|---------|---------------|----------|
| **WAV** | Несжатый | 1411 kbps | 38 МБ | 🎵🎵🎵🎵🎵 |
| **FLAC** | Lossless | ~850 kbps | 22 МБ | 🎵🎵🎵🎵🎵 |
| **MP3 320** | Lossy | 320 kbps | 9 МБ | 🎵🎵🎵🎵 |
| **AAC 256** | Lossy | 256 kbps | 7.2 МБ | 🎵🎵🎵🎵 |
| **Opus 128** | Lossy | 128 kbps | 3.6 МБ | 🎵🎵🎵 |

### Сравнительная таблица: видео кодеки

| Кодек | Год | Сжатие vs H.264 | Скорость кодирования | Применение |
|-------|-----|-----------------|----------------------|------------|
| **H.264** | 2003 | 1.0x (baseline) | ⭐⭐⭐⭐ | Универсальный |
| **H.265** | 2013 | 1.5-2x лучше | ⭐⭐ | 4K, стриминг |
| **VP9** | 2013 | 1.5-2x лучше | ⭐⭐ | YouTube, WebM |
| **AV1** | 2018 | 2x лучше | ⭐ | Будущее (Netflix, YouTube) |

### Команды

| Команда | Назначение |
|---------|-----------|
| `identify image.png` | Информация об изображении |
| `exiftool photo.jpg` | EXIF метаданные |
| `ffprobe video.mp4` | Информация о видео |
| `ffmpeg -i in.mp4 -c:v libx264 out.mp4` | Перекодировка видео |
| `ffmpeg -i in.wav -b:a 320k out.mp3` | Конвертация аудио |

!!! tip "Выбор формата"
    - **Изображения**: JPEG для фото, PNG для графики, WebP для web
    - **Аудио**: FLAC для архива, Opus для стриминга, MP3 для совместимости
    - **Видео**: H.264 для совместимости, H.265/VP9 для стриминга, AV1 для будущего


??? question "Упражнения"
    **Задание 1.** Определите кодек и контейнер видеофайла через `ffprobe video.mp4` (или `mediainfo`). Перекодируйте в другой формат через `ffmpeg`.
    
    **Задание 2.** Сравните размер PNG и JPEG для одной и той же фотографии. Конвертируйте в WebP — какой выигрыш? Используйте `cwebp` или Python Pillow.
    
    **Задание 3.** Извлеките EXIF-метаданные из JPEG-фото через Python (`Pillow` или `exifread`). Какие данные там хранятся (GPS, камера, дата)?

---

## Troubleshooting: типичные проблемы Части III

!!! bug "JSON не парсится: trailing comma, комментарии"
    Стандартный JSON **не поддерживает** комментарии и trailing commas:
    ```json
    // ЭТО НЕ ВАЛИДНЫЙ JSON:
    {
        "key": "value",
        "list": [1, 2, 3,]
    }
    ```
    Решения: используйте JSON5, JSONC (VS Code) или YAML вместо JSON. Для валидации: `python -m json.tool file.json`.

!!! bug "YAML: строка превратилась в boolean / число"
    YAML автоматически интерпретирует значения:
    ```yaml
    country: NO      # → boolean False (Norway стала False!)
    version: 3.10    # → float 3.1 (не строка "3.10"!)
    password: 'yes'  # → строка "yes" (кавычки спасают)
    ```
    **Правило**: всегда оборачивайте неоднозначные значения в кавычки.

!!! bug "CSV: неправильный разделитель / кодировка"
    ```python
    import csv
    
    # Автоопределение разделителя:
    with open('file.csv', newline='') as f:
        dialect = csv.Sniffer().sniff(f.read(4096))
        f.seek(0)
        reader = csv.reader(f, dialect)
    ```
    Excel на Windows сохраняет CSV в CP1251 с разделителем `;`. Указывайте явно: `encoding='cp1251'`, `delimiter=';'`.

!!! bug "Повреждённый архив: 'unexpected end of file'"
    ```bash
    # Проверить целостность:
    gzip -t file.gz
    zip -T file.zip
    tar -tzf file.tar.gz > /dev/null
    
    # Попытка частичного извлечения:
    tar --ignore-zeros -xzf broken.tar.gz
    ```
    Причина: обрыв загрузки, битый диск, перезапись файла до окончания записи.

!!! tip "Следующая глава"
    Рассмотрели медиа-данные. Теперь перейдём к **практической работе с файлами** → [Потоки данных](../ch4/26-streams.md)
