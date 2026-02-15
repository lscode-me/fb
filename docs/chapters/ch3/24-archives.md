# Глава 24. Архивы и контейнеры

## Введение

**Архив** — файл, содержащий другие файлы (часто со сжатием).

**Контейнер** — файл, объединяющий несколько потоков данных (аудио + видео + субтитры).

Разница тонкая: архив — это "хранилище файлов", контейнер — "композиция потоков".

!!! note "Многозадачность"
    - ZIP — и архив, и контейнер (JAR, DOCX, APK)
    - MP4 — контейнер, но может содержать множество дорожек
    - TAR — только упаковка, сжатие добавляется сверху (gzip, bzip2)

---

## 24.1 Архивы: упаковка и сжатие

### TAR: Tape ARchive

**tar** — старейший формат (1979), изначально для магнитных лент.

#### Структура

```
┌──────────────────────────────────────────────────────┐
│  Header 1 (512 байт)                                 │
│    - имя файла                                       │
│    - права (mode)                                    │
│    - uid/gid                                         │
│    - размер                                          │
│    - timestamp                                       │
├──────────────────────────────────────────────────────┤
│  Data 1 (выровнено по 512 байт)                      │
├──────────────────────────────────────────────────────┤
│  Header 2 (512 байт)                                 │
├──────────────────────────────────────────────────────┤
│  Data 2                                              │
├──────────────────────────────────────────────────────┤
│  ...                                                 │
├──────────────────────────────────────────────────────┤
│  EOF: 2 блока по 512 нулей                           │
└──────────────────────────────────────────────────────┘
```

#### Практика

```bash
# Создать архив
$ tar -cvf archive.tar docs/
docs/
docs/file1.txt
docs/file2.txt

# Просмотр содержимого
$ tar -tvf archive.tar
-rw-r--r-- user/user  1234 2025-02-04 10:00 docs/file1.txt
-rw-r--r-- user/user  5678 2025-02-04 10:01 docs/file2.txt

# Извлечь
$ tar -xvf archive.tar

# Извлечь один файл
$ tar -xvf archive.tar docs/file1.txt
```

#### TAR + сжатие

```bash
# gzip (быстро)
$ tar -czf archive.tar.gz docs/
# или
$ tar -cf - docs/ | gzip > archive.tar.gz

# bzip2 (лучше сжимает)
$ tar -cjf archive.tar.bz2 docs/

# xz (максимальное сжатие)
$ tar -cJf archive.tar.xz docs/

# zstd (современный, быстрый)
$ tar --zstd -cf archive.tar.zst docs/
```

**Сравнение:**

```bash
$ ls -lh docs/
total 100M

$ tar -czf docs.tar.gz docs/    # gzip
$ tar -cjf docs.tar.bz2 docs/   # bzip2
$ tar -cJf docs.tar.xz docs/    # xz
$ tar --zstd -cf docs.tar.zst docs/  # zstd

$ ls -lh docs.tar.*
-rw-r--r-- 1 user user  45M Feb  4 10:00 docs.tar.gz
-rw-r--r-- 1 user user  42M Feb  4 10:01 docs.tar.bz2
-rw-r--r-- 1 user user  38M Feb  4 10:02 docs.tar.xz
-rw-r--r-- 1 user user  44M Feb  4 10:03 docs.tar.zst
```

| Алгоритм | Скорость сжатия | Скорость распаковки | Степень сжатия |
|----------|----------------|---------------------|----------------|
| **gzip** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **bzip2** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **xz** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **zstd** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

#### Solid Compression: TAR + gzip vs ZIP

**Ключевое архитектурное различие:**

```
ZIP: Каждый файл сжимается отдельно
┌────────────┐ ┌────────────┐ ┌────────────┐
│file1 → zip │ │file2 → zip │ │file3 → zip │
└────────────┘ └────────────┘ └────────────┘
      ↓              ↓              ↓
  [сжатые данные 1][сжатые данные 2][сжатые данные 3]

TAR.GZ: Все файлы сжимаются как один поток (solid)
┌────────────────────────────────────────┐
│file1 + file2 + file3 → один поток     │
└────────────────────────────────────────┘
                    ↓
            [единый сжатый поток]
```

**Следствия:**

| Аспект | ZIP | TAR.GZ (solid) |
|--------|-----|----------------|
| Извлечь 1 файл | ✅ Быстро | ❌ Нужно распаковать всё до него |
| Сжатие похожих файлов | ⚠️ Плохо | ✅ Отлично (LZ77 видит повторы) |
| Повреждение архива | ⚠️ Теряем 1 файл | ❌ Теряем всё после |
| Стриминг | ❌ Нужен Central Directory | ✅ Можно распаковывать на лету |

**Пример: 1000 похожих логов:**

```bash
# ZIP — каждый файл сжимается отдельно
$ zip -r logs.zip logs/
Archive size: 450 MB

# TAR.GZ — solid compression, видит повторы между файлами
$ tar -czf logs.tar.gz logs/
Archive size: 120 MB   # В ~4 раза меньше!
```

!!! tip "Когда что использовать"
    - **ZIP:** нужен произвольный доступ к файлам, Windows-совместимость
    - **TAR.GZ:** максимальное сжатие для бэкапов, похожие файлы

#### Особенности TAR

```bash
# TAR сохраняет метаданные
$ tar -xvf archive.tar --numeric-owner
# --numeric-owner: сохранить UID/GID как есть

# Исключить файлы
$ tar -czf backup.tar.gz --exclude='*.log' --exclude='node_modules' app/

# Добавить файлы в существующий архив
$ tar -rvf archive.tar newfile.txt

# Инкрементальный бэкап
$ tar -czf backup-full.tar.gz --listed-incremental=snapshot.file /data
$ tar -czf backup-incr.tar.gz --listed-incremental=snapshot.file /data
```

---

### ZIP: универсальный формат

**ZIP** — самый распространённый формат (Phil Katz, 1989).

#### Структура

```
┌────────────────────────────────────────────┐
│  Local File Header 1                       │
│    - signature: 0x04034b50 (PK\x03\x04)    │
│    - версия, флаги, метод сжатия           │
│    - CRC32, размеры                        │
│    - имя файла                             │
├────────────────────────────────────────────┤
│  Compressed Data 1                         │
├────────────────────────────────────────────┤
│  Local File Header 2                       │
├────────────────────────────────────────────┤
│  Compressed Data 2                         │
├────────────────────────────────────────────┤
│  ...                                       │
├────────────────────────────────────────────┤
│  Central Directory                         │
│    - список всех файлов                    │
│    - смещения к Local Headers              │
├────────────────────────────────────────────┤
│  End of Central Directory                  │
│    - signature: 0x06054b50 (PK\x05\x06)    │
│    - количество файлов                     │
│    - смещение к Central Directory          │
└────────────────────────────────────────────┘
```

**Ключевое отличие от TAR:** Central Directory в конце позволяет **быстрый произвольный доступ**.

```bash
# Создать ZIP
$ zip -r archive.zip docs/

# Просмотр
$ unzip -l archive.zip
Archive:  archive.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     1234  02-04-2025 10:00   docs/file1.txt
     5678  02-04-2025 10:01   docs/file2.txt
---------                     -------
     6912                     2 files

# Извлечь
$ unzip archive.zip

# Извлечь один файл
$ unzip archive.zip docs/file1.txt

# Добавить файл
$ zip archive.zip newfile.txt

# Удалить файл
$ zip -d archive.zip docs/file2.txt
```

#### Степень сжатия

```bash
# Без сжатия (store)
$ zip -0 -r archive.zip docs/

# Максимальное сжатие
$ zip -9 -r archive.zip docs/

# По умолчанию: -6
```

#### ZIP как контейнер

```bash
# JAR (Java ARchive)
$ unzip -l app.jar
Archive:  app.jar
  Length      Date    Time    Name
---------  ---------- -----   ----
      ...
       42  02-04-2025 10:00   META-INF/MANIFEST.MF
     1234  02-04-2025 10:00   com/example/Main.class

# APK (Android Package)
$ unzip -l app.apk
Archive:  app.apk
  ...
  AndroidManifest.xml
  classes.dex
  resources.arsc

# DOCX (Word документ)
$ unzip -l document.docx
Archive:  document.docx
  ...
  word/document.xml
  word/styles.xml
  [Content_Types].xml
```

---

### 7z: максимальное сжатие

**7-Zip** (Igor Pavlov, 1999) — открытый формат с LZMA/LZMA2 сжатием.

```bash
# Создать архив
$ 7z a archive.7z docs/

# Просмотр
$ 7z l archive.7z

# Извлечь
$ 7z x archive.7z

# Максимальное сжатие
$ 7z a -mx=9 archive.7z docs/
```

**Сравнение:**

```bash
$ ls -lh docs/
total 100M

$ zip -9 -r docs.zip docs/
$ 7z a -mx=9 docs.7z docs/

$ ls -lh docs.*
-rw-r--r-- 1 user user  48M Feb  4 10:00 docs.zip
-rw-r--r-- 1 user user  36M Feb  4 10:01 docs.7z
```

| Формат | Размер | Скорость | Поддержка |
|--------|--------|----------|-----------|
| **ZIP** | 48 МБ | ⭐⭐⭐⭐⭐ | Везде |
| **7z** | 36 МБ | ⭐⭐⭐ | Нужна утилита |

---

### Другие форматы

#### RAR

```bash
# Создать (нужен WinRAR/rar)
$ rar a archive.rar docs/

# Распаковать (unrar — open source)
$ unrar x archive.rar
```

!!! warning "Проприетарность"
    RAR — проприетарный формат. Утилита `unrar` может только распаковывать, `rar` для создания — платная.

#### CAB (Windows)

```bash
# Создать (Windows)
C:\> makecab file.txt file.cab

# Распаковать (Linux)
$ cabextract file.cab
```

#### ar (статические библиотеки)

```bash
# .a файлы — это ar архивы
$ ar -t libexample.a
file1.o
file2.o

$ ar -x libexample.a file1.o
```

---

## 24.2 Контейнеры: мультимедиа

### MP4: видео контейнер

**MP4** (MPEG-4 Part 14) — контейнер для аудио/видео.

```bash
# Информация о контейнере
$ ffprobe video.mp4
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'video.mp4':
  Metadata:
    major_brand     : isom
    minor_version   : 512
  Duration: 00:05:30.00
  Stream #0:0: Video: h264 (High) (avc1), yuv420p, 1920x1080
  Stream #0:1: Audio: aac (LC) (mp4a), 48000 Hz, stereo
  Stream #0:2: Subtitle: mov_text (tx3g)
```

**Структура MP4:**

```
┌───────────────────────────────────────────────────┐
│  ftyp (File Type Box)                             │
│    - major_brand: isom                            │
├───────────────────────────────────────────────────┤
│  moov (Movie Box) — метаданные                    │
│    ├─ mvhd (Movie Header)                         │
│    ├─ trak (Video Track)                          │
│    │   ├─ tkhd (Track Header)                     │
│    │   └─ mdia (Media)                            │
│    └─ trak (Audio Track)                          │
├───────────────────────────────────────────────────┤
│  mdat (Media Data) — сжатые видео/аудио фреймы    │
└───────────────────────────────────────────────────┘
```

```bash
# Извлечь видео поток
$ ffmpeg -i video.mp4 -vcodec copy -an video_only.mp4
#                                   ^^
#                                   без аудио

# Извлечь аудио
$ ffmpeg -i video.mp4 -acodec copy -vn audio.m4a
#                                   ^^
#                                   без видео
```

### MKV: Matroska

**MKV** — открытый контейнер, поддерживает больше кодеков.

```bash
$ ffprobe video.mkv
Input #0, matroska,webm, from 'video.mkv':
  Duration: 01:30:00.00
  Stream #0:0: Video: hevc (Main 10), 3840x2160, 23.98 fps
  Stream #0:1(eng): Audio: opus, 48000 Hz, 5.1
  Stream #0:2(rus): Audio: opus, 48000 Hz, stereo
  Stream #0:3(eng): Subtitle: ass
  Stream #0:4(rus): Subtitle: ass
```

```bash
# Извлечь субтитры
$ ffmpeg -i video.mkv -map 0:s:0 subtitles.srt

# Смена контейнера без перекодирования
$ ffmpeg -i video.mkv -c copy video.mp4
```

### OGG: аудио контейнер

```bash
$ ogginfo audio.ogg
Vorbis stream 1:
    Total data length: 5245123 bytes
    Playback length: 3m:45s
    Average bitrate: 186.234567 kb/s
```

---

## 24.3 ISO: образы дисков

**ISO 9660** — стандарт для CD/DVD образов.

```bash
# Создать ISO из директории
$ mkisofs -o image.iso -R -J /path/to/files
#                         ^^
#                         R = Rock Ridge (Unix права)
#                         J = Joliet (длинные имена Windows)

# Современная альтернатива:
$ genisoimage -o image.iso -R -J /path/to/files

# Монтировать ISO
$ sudo mount -o loop image.iso /mnt/cdrom

# Просмотр без монтирования
$ isoinfo -l -i image.iso
Directory listing of /
d---------   0    0    0         2048 Feb  4 10:00 [     23 02] .
d---------   0    0    0         2048 Feb  4 10:00 [     23 02] ..
----------   0    0    0         1234 Feb  4 10:00 [     24 00] FILE.TXT;1
```

### Гибридные ISO

```bash
# Создать загрузочный USB/CD
$ isohybrid image.iso

# Теперь можно:
$ dd if=image.iso of=/dev/sdX bs=4M
# И использовать как USB, и записать на CD
```

---

## 24.4 Произвольный доступ vs Потоковое чтение

### TAR: последовательный

```bash
# Извлечь последний файл = читать весь архив
$ tar -xf huge.tar --wildcards '*/last_file.txt'
# Нужно прочитать весь архив!
```

### ZIP: произвольный доступ

```bash
# Central Directory в конце → быстрый доступ
$ unzip archive.zip last_file.txt
# Читается только Central Directory + нужный файл
```

### Streaming архивы

```bash
# TAR идеален для pipe
$ tar -czf - /data | ssh remote "tar -xzf -"

# ZIP не подходит (Central Directory в конце)
$ zip -r - /data | ssh remote "unzip -"
# ❌ Не работает: zip нужен seek
```

---

## 24.5 Метаданные и проверка целостности

### CRC32 в ZIP

```bash
$ unzip -v archive.zip
Archive:  archive.zip
 Length   Method    Size  Cmpr    Date    Time   CRC-32   Name
--------  ------  ------- ---- ---------- ----- --------  ----
    1234  Defl:N      890  28% 2025-02-04 10:00 a3b5c7d9  file.txt
                                                  ^^^^^^^^
                                                  CRC32 checksum
```

### SHA256 для целостности

```bash
# Создать архив + checksum
$ tar -czf backup.tar.gz /data
$ sha256sum backup.tar.gz > backup.tar.gz.sha256

# Проверка
$ sha256sum -c backup.tar.gz.sha256
backup.tar.gz: OK
```

### PAR2: восстановление повреждений

```bash
# Создать файлы восстановления (10%)
$ par2 create -r10 archive.zip

$ ls
archive.zip
archive.zip.par2
archive.zip.vol0+1.par2
archive.zip.vol1+2.par2

# Проверка и восстановление
$ par2 verify archive.zip.par2
$ par2 repair archive.zip.par2
```

---

## 24.6 Специализированные форматы

### Исходный код: tgz, xz

```bash
# Linux kernel
$ wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.7.tar.xz
$ tar -xJf linux-6.7.tar.xz

# Python package
$ pip download numpy --no-binary :all:
$ ls
numpy-1.26.4.tar.gz
$ tar -xzf numpy-1.26.4.tar.gz
```

### Системные пакеты

```bash
# Debian: .deb = ar + tar.gz
$ ar -t package.deb
debian-binary
control.tar.xz
data.tar.xz

$ ar -x package.deb
$ tar -xJf data.tar.xz  # Файлы для установки
$ tar -xJf control.tar.xz  # Метаданные пакета

# RPM: cpio внутри
$ rpm2cpio package.rpm | cpio -idmv
```

### Бэкапы: squashfs, borgbackup

```bash
# SquashFS (read-only сжатая ФС)
$ mksquashfs /data backup.sqfs
$ sudo mount backup.sqfs /mnt -o loop

# BorgBackup (дедупликация)
$ borg init --encryption=repokey /backup/repo
$ borg create /backup/repo::archive1 /data
$ borg create /backup/repo::archive2 /data  # Только изменения!
```

---

## Резюме

### Сравнительная таблица

| Формат | Сжатие | Произвольный доступ | Метаданные | Применение |
|--------|--------|---------------------|------------|------------|
| **TAR** | ❌ (внешнее) | ❌ | ✅ (Unix) | Бэкапы, исходники |
| **ZIP** | ✅ | ✅ | ⚠️ (ограничено) | Дистрибуция, контейнеры |
| **7z** | ✅✅ | ✅ | ✅ | Максимальное сжатие |
| **RAR** | ✅ | ✅ | ✅ | Windows, recovery records |
| **MP4** | N/A | ✅ | ✅ | Видео/аудио |
| **MKV** | N/A | ✅ | ✅✅ | Видео (больше кодеков) |
| **ISO** | ❌ | ✅ | ⚠️ | Образы дисков |

### Команды

| Команда | Назначение |
|---------|-----------|
| `tar -czf a.tar.gz dir/` | Создать tar.gz |
| `tar -xzf a.tar.gz` | Распаковать |
| `zip -r a.zip dir/` | Создать ZIP |
| `unzip a.zip` | Распаковать ZIP |
| `7z a a.7z dir/` | Создать 7z |
| `7z x a.7z` | Распаковать 7z |
| `ffprobe video.mp4` | Информация о контейнере |
| `isoinfo -l -i image.iso` | Содержимое ISO |

!!! tip "Выбор формата"
    - **TAR+gzip**: бэкапы, передача по сети
    - **ZIP**: совместимость, Windows
    - **7z**: когда важен размер
    - **MP4**: видео с хорошей поддержкой
    - **MKV**: видео с максимальной гибкостью


??? question "Упражнения"
    **Задание 1.** Создайте tar.gz и zip из одной директории. Сравните размер, скорость создания и скорость распаковки. Попробуйте `zstd` — что быстрее?
    
    **Задание 2.** Извлеките один файл из tar.gz без распаковки всего архива: `tar xzf archive.tar.gz path/to/file`. Возможно ли то же с ZIP? С 7z?
    
    **Задание 3.** Напишите Python-скрипт, создающий zip-архив с паролем, используя модуль `zipfile`. Какие ограничения у встроенного шифрования ZIP?

!!! tip "Следующая глава"
    Разобрались с контейнерами. Теперь углубимся в **форматы медиа-данных** → [Медиа-форматы](25-media.md)
