# Глава 10. Бинарные данные и уровни абстракции

## Введение

В части I мы разобрались с файлами как элементами файловой системы. Теперь заглянем внутрь: **что находится в файле?**

Любой файл — это последовательность **байтов**. Но интерпретация этих байтов зависит от контекста: это может быть текст, изображение, архив или исполняемый код.

!!! note "Всё есть байты"
    На самом низком уровне не существует "текстовых" или "бинарных" файлов. Есть только последовательность байтов `0x48 0x65 0x6C 0x6C 0x6F`, которую мы можем интерпретировать как ASCII текст "Hello" или как пять чисел 72, 101, 108, 108, 111.

---

## 10.1 Байт — основная единица

### Что такое байт?

**Байт** — 8 бит, число от 0 до 255 (0x00 до 0xFF в hex).

```
Бит:   0 1 0 1 1 0 1 0
       │ │ │ │ │ │ │ │
Биты: 128 64 32 16 8 4 2 1
       └─┴─┴─┴─┴─┴─┴─┘
          = 90 (decimal)
          = 0x5A (hex)
```

### Просмотр байтов: hexdump

```bash
$ echo "Hello" > test.txt

$ hexdump -C test.txt
00000000  48 65 6c 6c 6f 0a                                 |Hello.|
00000006

# Расшифровка:
# 0x48 = 72 = 'H'
# 0x65 = 101 = 'e'
# 0x6c = 108 = 'l'
# 0x6c = 108 = 'l'
# 0x6f = 111 = 'o'
# 0x0a = 10 = '\n' (newline)
```

**Другие hex-утилиты:**

```bash
# xxd — популярная альтернатива
$ xxd test.txt
00000000: 4865 6c6c 6f0a                           Hello.

# od — POSIX стандарт
$ od -A x -t x1z test.txt
000000 48 65 6c 6c 6f 0a                          >Hello.<
000006

# hexyl — современная утилита с подсветкой
$ hexyl test.txt
```

### Python: работа с байтами

```python
# Чтение как байты
with open('test.txt', 'rb') as f:
    data = f.read()
    print(type(data))  # <class 'bytes'>
    print(data)        # b'Hello\n'
    print(list(data))  # [72, 101, 108, 108, 111, 10]

# Запись байтов
with open('binary.dat', 'wb') as f:
    f.write(b'\x48\x65\x6c\x6c\x6f')  # 'Hello'
    f.write(bytes([72, 101, 108, 108, 111]))  # То же самое
```

---

## 10.2 Endianness: порядок байтов

### Проблема многобайтовых чисел

Число `0x12345678` (305419896 в decimal) занимает 4 байта. В каком порядке их записывать?

**Big-endian** (BE, network byte order):
```
Адрес:  0x00    0x01    0x02    0x03
Байт:   0x12    0x34    0x56    0x78
        ^^^^                    ^^^^
        старший байт            младший байт
```

**Little-endian** (LE, Intel x86):
```
Адрес:  0x00    0x01    0x02    0x03
Байт:   0x78    0x56    0x34    0x12
        ^^^^                    ^^^^
        младший байт            старший байт
```

### Проверка endianness системы

```python
import sys
print(sys.byteorder)  # 'little' или 'big'

# Через struct
import struct
data = struct.pack('i', 1)  # native byte order
print(data.hex())
# little-endian: 01000000
# big-endian:    00000001
```

### Практическое значение

```python
import struct

# Чтение 32-битного числа из файла
with open('data.bin', 'rb') as f:
    bytes_data = f.read(4)  # b'\x78\x56\x34\x12'
    
    # Little-endian
    num_le = struct.unpack('<I', bytes_data)[0]
    print(hex(num_le))  # 0x12345678
    
    # Big-endian (тот же файл!)
    num_be = struct.unpack('>I', bytes_data)[0]
    print(hex(num_be))  # 0x78563412
```

**Форматы:**
- `<` — little-endian
- `>` — big-endian
- `=` — native (системный)
- `!` — network (= big-endian)

### Примеры форматов

| Формат | Endianness |
|--------|------------|
| **ELF** (Linux executables) | Little-endian (x86/x86_64) |
| **Mach-O** (macOS executables) | Little-endian (x86_64), Big-endian (PowerPC legacy) |
| **PNG** | Big-endian |
| **JPEG** | Big-endian (JFIF), Little-endian (EXIF может быть оба) |
| **TIFF** | Оба (указывается в заголовке: II=LE, MM=BE) |
| **Network protocols** | Big-endian |

### Network Byte Order

Сетевые протоколы (TCP/IP) используют **big-endian** — это называется **Network Byte Order**:

```python
import socket

# Преобразование host ↔ network byte order
port = 8080
print(hex(port))                     # 0x1f90
print(socket.htons(port).to_bytes(2, 'big').hex())  # 1f90 (network)

ip = 0x7F000001  # 127.0.0.1
print(socket.inet_ntoa(socket.htonl(ip).to_bytes(4, 'big')))  # 127.0.0.1
```

**Почему важно:** Если вы парсите сетевой пакет или формат файла (WAV, BMP), нужно знать endianness:

```python
import struct

# Разбор WAV заголовка (little-endian)
with open('audio.wav', 'rb') as f:
    riff = f.read(4)         # b'RIFF'
    size = struct.unpack('<I', f.read(4))[0]  # LE!
    wave = f.read(4)         # b'WAVE'
    fmt = f.read(4)          # b'fmt '
    # ...

# Разбор PNG (big-endian)
with open('image.png', 'rb') as f:
    magic = f.read(8)        # \x89PNG\r\n\x1a\n
    length = struct.unpack('>I', f.read(4))[0]  # BE!
    chunk_type = f.read(4)   # b'IHDR'
    # ...
```

---

## 10.3 Уровни структур: от байтов к смыслу

Файл можно рассматривать на разных уровнях абстракции:

```
┌────────────────────────────────────────────────────────┐
│  Уровень 5: Приложение                                 │
│  "Фотография кота на пляже"                            │
├────────────────────────────────────────────────────────┤
│  Уровень 4: Структура данных                           │
│  "JPEG с EXIF метаданными"                             │
├────────────────────────────────────────────────────────┤
│  Уровень 3: Формат контейнера                          │
│  "JFIF с маркерами 0xFFD8...0xFFD9"                    │
├────────────────────────────────────────────────────────┤
│  Уровень 2: Бинарное представление                     │
│  "Последовательность байтов FF D8 FF E0..."            │
├────────────────────────────────────────────────────────┤
│  Уровень 1: Биты на диске                              │
│  "Магнитные домены / заряды в ячейках SSD"             │
└────────────────────────────────────────────────────────┘
```

### Пример: ZIP-файл

```bash
$ xxd archive.zip | head -5
00000000: 504b 0304 1400 0000 0800 b875 5766 4c27  PK.........uWfL'
00000010: a34b 1a00 0000 1800 0000 0800 1c00 746f  .K............to
00000020: 7761 722e 7478 7455 5409 0003 67ce 7567  war.txtUT...g.ug
```

**Разбор:**
- `50 4B 03 04` — magic number ("PK", от Phil Katz, автор ZIP)
- `14 00` — версия формата
- `00 00` — флаги
- `08 00` — метод сжатия (deflate)
- ...

### Magic numbers

**Magic number** — первые байты файла, идентифицирующие формат:

| Формат | Magic | Hex |
|--------|-------|-----|
| PNG | `\x89PNG` | `89 50 4E 47` |
| JPEG | `ÿØÿà` | `FF D8 FF E0` (JFIF) |
| GIF | `GIF89a` | `47 49 46 38 39 61` |
| PDF | `%PDF-` | `25 50 44 46 2D` |
| ZIP | `PK\x03\x04` | `50 4B 03 04` |
| ELF | `\x7FELF` | `7F 45 4C 46` |
| Gzip | `\x1f\x8b` | `1F 8B` |

```bash
# file использует magic numbers
$ file test.png
test.png: PNG image data, 800 x 600, 8-bit/color RGB, non-interlaced

$ file --mime-type test.png
test.png: image/png
```

### База данных magic numbers

```bash
# Где хранятся magic numbers
$ file -v
file-5.45
magic file from /usr/share/misc/magic

# Просмотр базы
$ less /usr/share/misc/magic
# или
$ less /usr/share/file/magic
```

---

## 10.4 Текст vs Бинарные данные

### Текстовый файл

**Текстовый файл** — файл, содержащий символы, закодированные в определённой кодировке (ASCII, UTF-8, и т.д.).

```bash
$ echo "Hello" > text.txt
$ file text.txt
text.txt: ASCII text

$ hexdump -C text.txt
00000000  48 65 6c 6c 6f 0a        |Hello.|
```

Характеристики:
- Читаем человеком
- Байты соответствуют символам
- Переносы строк: `\n` (Unix), `\r\n` (Windows)

### Бинарный файл

**Бинарный файл** — файл, содержащий данные, не предназначенные для прямого чтения человеком.

```bash
$ file /bin/ls
/bin/ls: ELF 64-bit LSB executable, x86-64

$ hexdump -C /bin/ls | head -3
00000000  7f 45 4c 46 02 01 01 00  00 00 00 00 00 00 00 00  |.ELF............|
00000010  03 00 3e 00 01 00 00 00  50 5f 00 00 00 00 00 00  |..>.....P_......|
00000020  40 00 00 00 00 00 00 00  88 e0 01 00 00 00 00 00  |@...............|
```

Характеристики:
- Структурированные данные
- Специфический формат
- Нужны инструменты для чтения

!!! note "Всё относительно"
    HTML — это текст для человека, но бинарные данные для браузера (нужен парсер). JPEG — бинарные данные, но можно извлечь текстовые EXIF метаданные.

---

## 10.5 Sparse Files: эффективность хранения

### Что такое sparse file?

**Sparse file** (разреженный файл) — файл, содержащий длинные последовательности нулей, которые **не занимают место на диске**.

```python
# Создаём файл 1 ГБ, но на диске — почти 0
import os

with open('sparse.dat', 'wb') as f:
    f.seek(1024**3 - 1)  # 1 ГБ - 1 байт
    f.write(b'\0')       # Записываем 1 байт

# Логический размер: 1 ГБ
# Физический размер: 4 КБ (один блок)
```

```bash
$ ls -lh sparse.dat
-rw-r--r-- 1 user user 1.0G Feb  4 10:00 sparse.dat
                       ^^^^
                       логический размер

$ du -h sparse.dat
4.0K    sparse.dat
^^^^
физический размер на диске
```

### Проверка sparse файлов

```bash
# stat показывает оба размера
$ stat sparse.dat
  Size: 1073741824      Blocks: 8
              ^^^^^^^^^^        ^
              байты             512-байтные блоки (8×512=4KB)

# Найти sparse файлы
$ find . -type f -printf "%S\t%p\n" | awk '$1 < 1.0'
0.000004    ./sparse.dat
# %S — sparseness (отношение Blocks к Size)
```

### Практическое применение

**1. Образы дисков**

```bash
# Создаём образ диска 10 ГБ
$ dd if=/dev/zero of=disk.img bs=1 count=0 seek=10G
0+0 records in
0+0 records out
0 bytes copied

$ ls -lh disk.img
-rw-r--r-- 1 user user 10G Feb  4 10:00 disk.img

$ du -h disk.img
0       disk.img    # Занимает 0!
```

**2. Виртуальные машины**

```bash
# QCOW2 (QEMU) использует sparse
$ qemu-img create -f qcow2 vm.qcow2 50G
Formatting 'vm.qcow2', fmt=qcow2 size=53687091200

$ ls -lh vm.qcow2
-rw-r--r-- 1 user user 50G Feb  4 10:00 vm.qcow2

$ du -h vm.qcow2
196K    vm.qcow2    # Реально занимает ~200 КБ
```

**3. Торренты**

Торрент-клиенты создают sparse файлы для резервирования места:

```bash
# Начинаем скачивать 10 ГБ файл
$ ls -lh movie.mkv
-rw-r--r-- 1 user user 10G Feb  4 10:00 movie.mkv

$ du -h movie.mkv
1.5G    movie.mkv    # Скачано 15%
```

### Копирование sparse файлов

```bash
# ❌ Плохо: cp по умолчанию заполняет дыры
$ cp sparse.dat sparse_copy.dat
$ du -h sparse_copy.dat
1.0G    sparse_copy.dat    # Занимает 1 ГБ!

# ✅ Хорошо: --sparse=always
$ cp --sparse=always sparse.dat sparse_copy.dat
$ du -h sparse_copy.dat
4.0K    sparse_copy.dat    # Остался sparse

# rsync сохраняет sparse по умолчанию
$ rsync -avS sparse.dat remote:/backup/
```

### Заполнение дыр

```bash
# Преобразовать sparse в обычный файл
$ dd if=sparse.dat of=dense.dat bs=4M

$ du -h dense.dat
1.0G    dense.dat    # Теперь занимает полный размер
```

---

## 10.6 Сжатие vs Sparse

### Разница

| Метод | Что делает | Размер на диске |
|-------|----------|-----------------|
| **Sparse** | Не хранит нули | Зависит от данных |
| **Сжатие** | Кодирует повторы | Всегда меньше |

```bash
# Sparse: нули не занимают место
$ truncate -s 1G sparse_zeros.dat
$ du -h sparse_zeros.dat
0       sparse_zeros.dat

# Сжатие: нули сжимаются отлично
$ truncate -s 1G full_zeros.dat
$ gzip full_zeros.dat
$ ls -lh full_zeros.dat.gz
-rw-r--r-- 1 user user 1.0M Feb  4 10:00 full_zeros.dat.gz
# 1 ГБ нулей → 1 МБ архив
```

### Комбинация

```bash
# tar может и sparse, и сжатие
$ tar -cSzf backup.tar.gz sparse_file
#       ^^
#       S = сохранить sparse
#       z = gzip сжатие
```

---

## Резюме

| Понятие | Описание |
|---------|----------|
| **Байт** | 8 бит, 0-255, основная единица |
| **Endianness** | Порядок байтов: LE (Intel) vs BE (network) |
| **Magic number** | Первые байты, идентифицирующие формат |
| **Sparse file** | Нули не занимают место на диске |
| **Текстовый файл** | Символы в кодировке (ASCII, UTF-8) |
| **Бинарный файл** | Структурированные данные |

| Команда | Назначение |
|---------|-----------|
| `hexdump -C file` | Hex-дамп с ASCII |
| `xxd file` | Альтернативный hex-дамп |
| `file file` | Определить тип файла |
| `du -h file` | Физический размер |
| `ls -lh file` | Логический размер |
| `stat file` | Полная информация о размере |

!!! tip "Инструменты для работы с бинарными данными"
    - **hexdump, xxd, od** — просмотр байтов
    - **file** — определение типа
    - **strings** — извлечение текста из бинарных файлов
    - **binwalk** — анализ и извлечение вложенных форматов
    - **010 Editor, ImHex** — hex-редакторы с шаблонами форматов


??? question "Упражнения"
    **Задание 1.** Выполните `xxd /bin/ls | head -5`. Определите magic number. Что за формат файла? Проверьте через `file /bin/ls`.
    
    **Задание 2.** Напишите Python-скрипт, который читает первые 16 байт файла и выводит их в hex, decimal и binary формате.
    
    **Задание 3.** Создайте файл с числом 0x12345678 в little-endian и big-endian порядке (используя `struct.pack`). Проверьте через `xxd`.

!!! tip "Следующая глава"
    Теперь мы понимаем байтовую структуру. Перейдём к **представлению данных** → [От битов к байтам](11-bytes-encoding.md)
