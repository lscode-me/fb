# Глава 15. Кодировки в Python

## Введение

После изучения Unicode и UTF-8 пришло время применить эти знания на практике. Python — один из самых популярных языков для работы с текстом, и понимание того, как он обрабатывает кодировки, критически важно для любого разработчика.

---

## 15.1 Python 2 vs Python 3: революция в работе с текстом

### Проблема Python 2

В Python 2 существовало фундаментальное смешение понятий:

```python
# Python 2
>>> type("hello")
<type 'str'>          # Это байты!

>>> type(u"hello")
<type 'unicode'>      # Это текст

>>> "привет"          # Байты в кодировке терминала
'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82'

>>> u"привет"         # Unicode строка
u'\u043f\u0440\u0438\u0432\u0435\u0442'
```

Это приводило к бесконечным ошибкам:

```python
# Python 2 — типичная ошибка
>>> "hello" + u"мир"
Traceback (most recent call last):
UnicodeDecodeError: 'ascii' codec can't decode byte 0xd0
```

### Решение в Python 3

Python 3 чётко разделил понятия:

| Тип | Содержит | Литерал |
|-----|----------|---------|
| `str` | Unicode текст (code points) | `"hello"`, `"привет"` |
| `bytes` | Сырые байты | `b"hello"`, `b"\xd0\xbf"` |

```python
# Python 3
>>> type("привет")
<class 'str'>         # Это текст (Unicode)

>>> type(b"hello")
<class 'bytes'>       # Это байты

>>> "привет"
'привет'              # Читаемый текст

>>> "привет".encode('utf-8')
b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82'
```

### Практическое последствие: сетевое программирование

Разделение `str`/`bytes` особенно важно при работе с **сетью**. Сетевые протоколы (HTTP, SMTP, FTP) передают **байты**, а не текст:

```python
# Python 2 — работало случайно
import socket
s = socket.socket()
s.connect(("example.com", 80))
s.send("GET / HTTP/1.0\r\n\r\n")  # str = байты, «повезло»

# Python 3 — явное преобразование
import socket
s = socket.socket()
s.connect(("example.com", 80))
s.send(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")  # bytes!
response = s.recv(4096)  # → bytes
text = response.decode("utf-8", errors="replace")  # → str
```

```bash
# Аналог в shell — telnet отправляет байты «как есть»
$ echo -e "GET / HTTP/1.0\r\nHost: example.com\r\n\r\n" | nc example.com 80
```

!!! warning "Правило Python 3"
    Всё, что уходит в **сеть, файл или процесс** — должно быть `bytes`.
    Всё, что показывается **пользователю** — должно быть `str`.
    Граница между ними — `encode()`/`decode()`.

---

## 15.2 str и bytes: два разных мира

### str — это текст

`str` в Python 3 — это последовательность **Unicode code points**:

```python
text = "Привет, 世界! 👋"

# Длина — количество символов (code points)
>>> len(text)
14

# Индексация по символам
>>> text[0]
'П'
>>> text[8]
'世'
>>> text[13]
'👋'

# Итерация по символам
>>> list(text)
['П', 'р', 'и', 'в', 'е', 'т', ',', ' ', '世', '界', '!', ' ', '👋']
```

### bytes — это байты

`bytes` — это последовательность **целых чисел от 0 до 255**:

```python
data = b"Hello"

>>> len(data)
5

>>> data[0]      # Не 'H', а число!
72

>>> list(data)
[72, 101, 108, 108, 111]
```

Для не-ASCII символов нужно кодирование:

```python
>>> b"привет"
SyntaxError: bytes can only contain ASCII literal characters

>>> "привет".encode('utf-8')
b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82'
```

---

## 15.3 encode() и decode(): мост между мирами

### Кодирование: str → bytes

```python
text = "Привет"

# UTF-8 (по умолчанию)
>>> text.encode()
b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82'

>>> text.encode('utf-8')
b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82'

# UTF-16
>>> text.encode('utf-16')
b'\xff\xfe?\x04@\x048\x042\x045\x04B\x04'

# UTF-32
>>> text.encode('utf-32')
b'\xff\xfe\x00\x00?\x04\x00\x00@\x04\x00\x008\x04\x00\x002\x04\x00\x005\x04\x00\x00B\x04\x00\x00'

# Windows-1251
>>> text.encode('cp1251')
b'\xcf\xf0\xe8\xe2\xe5\xf2'

# KOI8-R
>>> text.encode('koi8-r')
b'\xf0\xd2\xc9\xd7\xc5\xd4'
```

### Декодирование: bytes → str

```python
data = b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82'

>>> data.decode('utf-8')
'Привет'

>>> data.decode()  # UTF-8 по умолчанию
'Привет'

# Неправильная кодировка — кракозябры или ошибка
>>> data.decode('cp1251')
'Ð¿Ñ\x80Ð¸Ð²ÐµÑ\x82'

>>> data.decode('ascii')
UnicodeDecodeError: 'ascii' codec can't decode byte 0xd0
```

### Обработка ошибок

```python
text = "Привет"

# strict (по умолчанию) — исключение при ошибке
>>> text.encode('ascii')
UnicodeEncodeError: 'ascii' codec can't encode characters

# ignore — пропустить некодируемые символы
>>> text.encode('ascii', errors='ignore')
b''

# replace — заменить на ?
>>> text.encode('ascii', errors='replace')
b'??????'

# xmlcharrefreplace — XML-сущности
>>> text.encode('ascii', errors='xmlcharrefreplace')
b'&#1055;&#1088;&#1080;&#1074;&#1077;&#1090;'

# backslashreplace — escape-последовательности
>>> text.encode('ascii', errors='backslashreplace')
b'\\u043f\\u0440\\u0438\\u0432\\u0435\\u0442'
```

---

## 15.4 Работа с файлами: режимы открытия

### Текстовый режим (по умолчанию)

```python
# Чтение текста
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()     # str
    
# Запись текста
with open('file.txt', 'w', encoding='utf-8') as f:
    f.write('Привет')   # str
    
# Добавление текста
with open('file.txt', 'a', encoding='utf-8') as f:
    f.write('\nМир')    # str
```

### Бинарный режим

```python
# Чтение байтов
with open('file.bin', 'rb') as f:
    data = f.read()     # bytes
    
# Запись байтов
with open('file.bin', 'wb') as f:
    f.write(b'\x00\x01\x02')  # bytes
    
# Добавление байтов
with open('file.bin', 'ab') as f:
    f.write(b'\x03\x04')      # bytes
```

### Все режимы открытия файлов

| Режим | Описание | Тип данных |
|-------|----------|------------|
| `'r'` | Чтение текста | str |
| `'w'` | Запись текста (перезапись) | str |
| `'a'` | Добавление текста | str |
| `'x'` | Создание и запись (ошибка если существует) | str |
| `'rb'` | Чтение байтов | bytes |
| `'wb'` | Запись байтов (перезапись) | bytes |
| `'ab'` | Добавление байтов | bytes |
| `'xb'` | Создание и запись байтов | bytes |
| `'r+'` | Чтение и запись текста | str |
| `'w+'` | Чтение и запись текста (перезапись) | str |
| `'rb+'` | Чтение и запись байтов | bytes |
| `'wb+'` | Чтение и запись байтов (перезапись) | bytes |

### Важность указания кодировки

```python
# ПЛОХО — зависит от системной локали!
with open('file.txt', 'r') as f:
    text = f.read()
    
# ХОРОШО — явное указание кодировки
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()
```

!!! warning "Кодировка по умолчанию"
    Если не указать `encoding`, Python использует `locale.getpreferredencoding()`:
    - Linux/macOS: обычно UTF-8
    - Windows: cp1251, cp1252 или другая системная

---

## 15.5 UTF-8, UTF-16, UTF-32: когда что использовать

### UTF-8

```python
text = "Hello, мир! 👋"

encoded = text.encode('utf-8')
>>> len(encoded)
20

>>> encoded
b'Hello, \xd0\xbc\xd0\xb8\xd1\x80! \xf0\x9f\x91\x8b'
```

**Характеристики:**
- Переменная длина: 1–4 байта на символ
- ASCII-совместим (первые 128 символов — 1 байт)
- Нет проблем с порядком байтов (endianness)
- **Рекомендуется для большинства случаев**

### UTF-16

```python
text = "Hello, мир! 👋"

# С BOM (Byte Order Mark)
>>> text.encode('utf-16')
b'\xff\xfeH\x00e\x00l\x00l\x00o\x00,\x00 \x00<\x044\x048\x04!\x00 \x00=\xd8K\xde'

# Little-endian без BOM
>>> text.encode('utf-16-le')
b'H\x00e\x00l\x00l\x00o\x00,\x00 \x00<\x044\x048\x04!\x00 \x00=\xd8K\xde'

# Big-endian без BOM
>>> text.encode('utf-16-be')
b'\x00H\x00e\x00l\x00l\x00o\x00,\x00 \x04<\x044\x048\x00!\x00 \xd8=\xdeK'
```

**Характеристики:**
- Переменная длина: 2 или 4 байта на символ
- Используется в Windows API, Java, JavaScript (внутренне)
- Требует указания порядка байтов (BOM или явно LE/BE)

### UTF-32

```python
text = "Hello, мир! 👋"

>>> text.encode('utf-32')
b'\xff\xfe\x00\x00H\x00\x00\x00e\x00\x00\x00l\x00\x00\x00...'

>>> len(text.encode('utf-32'))
52  # 4 байта × 12 символов + 4 байта BOM
```

**Характеристики:**
- Фиксированная длина: 4 байта на символ
- Простая индексация, но большой размер
- Редко используется для хранения

### Сравнение размеров

```python
text = "Hello, мир! 👋"

print(f"UTF-8:  {len(text.encode('utf-8')):3} байт")
print(f"UTF-16: {len(text.encode('utf-16')):3} байт")
print(f"UTF-32: {len(text.encode('utf-32')):3} байт")

# Вывод:
# UTF-8:   20 байт
# UTF-16:  28 байт
# UTF-32:  52 байт
```

---

## 15.6 Практические примеры

### Чтение файла с автоопределением кодировки

```python
import chardet

def read_file_auto(path):
    """Читает файл, автоматически определяя кодировку."""
    with open(path, 'rb') as f:
        raw = f.read()
    
    detected = chardet.detect(raw)
    encoding = detected['encoding']
    confidence = detected['confidence']
    
    print(f"Detected: {encoding} (confidence: {confidence:.0%})")
    return raw.decode(encoding)
```

### Конвертация файла между кодировками

```python
def convert_encoding(input_path, output_path, 
                     from_encoding='cp1251', 
                     to_encoding='utf-8'):
    """Конвертирует файл из одной кодировки в другую."""
    with open(input_path, 'r', encoding=from_encoding) as f:
        content = f.read()
    
    with open(output_path, 'w', encoding=to_encoding) as f:
        f.write(content)

# Использование
convert_encoding('old_file.txt', 'new_file.txt', 
                 from_encoding='cp1251', to_encoding='utf-8')
```

### Работа с BOM

```python
import codecs

# Чтение файла с BOM
with open('file_with_bom.txt', 'r', encoding='utf-8-sig') as f:
    text = f.read()  # BOM автоматически удаляется

# Запись файла с BOM (для совместимости с Excel)
with open('for_excel.csv', 'w', encoding='utf-8-sig') as f:
    f.write('Имя,Возраст\n')
    f.write('Иван,30\n')
```

### Безопасная работа с неизвестной кодировкой

```python
def safe_decode(data: bytes, encodings=None) -> str:
    """Пытается декодировать байты, перебирая кодировки."""
    if encodings is None:
        encodings = ['utf-8', 'cp1251', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # Fallback: декодируем с заменой ошибок
    return data.decode('utf-8', errors='replace')
```

---

## 15.7 Типичные ошибки и их решения

### Ошибка 1: Смешивание str и bytes

```python
# ОШИБКА
>>> "Hello " + b"World"
TypeError: can only concatenate str (not "bytes") to str

# РЕШЕНИЕ
>>> "Hello " + b"World".decode('utf-8')
'Hello World'
```

### Ошибка 2: Забыли указать кодировку

```python
# ОШИБКА — непредсказуемое поведение
with open('file.txt') as f:
    text = f.read()

# РЕШЕНИЕ
with open('file.txt', encoding='utf-8') as f:
    text = f.read()
```

### Ошибка 3: Двойное кодирование

```python
text = "Привет"

# ОШИБКА — закодировали дважды
>>> text.encode('utf-8').decode('latin-1').encode('utf-8')
b'\xc3\x90\xc2\xbf\xc3\x91\xc2\x80...'  # Мусор

# Распознать: decode + encode с правильными кодировками
>>> b'\xc3\x90\xc2\xbf...'.decode('utf-8').encode('latin-1').decode('utf-8')
'Привет'
```

### Ошибка 4: Чтение бинарного файла в текстовом режиме

```python
# ОШИБКА
with open('image.png', 'r') as f:
    data = f.read()  # UnicodeDecodeError!

# РЕШЕНИЕ
with open('image.png', 'rb') as f:
    data = f.read()  # bytes
```

### Ошибка 5: Regex по байтовым строкам с кириллицей

Эта ловушка характерна для Python 2, но иллюстрирует фундаментальную проблему смешения байтов и текста:

```python
# Python 2, терминал в UTF-8
>>> import re
>>> re.search('м', 'жаба')     # Ничего — ожидаемо
>>> re.search('м|н', 'жаба')   # Ничего — тоже ожидаемо
>>> re.search('[мн]', 'жаба')  # Нашли! Почему?!
<_sre.SRE_Match object at 0x7f04f2d46308>
>>> re.findall('[мн]', 'жаба')
['\xd0', '\xd0', '\xd0', '\xd0']
```

Причина: буква `м` в UTF-8 — это два байта `\xd0\xbc`. Когда regex видит символьный класс `[мн]`, он разбивает байтовые последовательности на **отдельные байты**: `[\xd0\xbc\xd0\xbd]`. Байт `\xd0` — общий префикс почти всех кириллических символов в UTF-8, поэтому он находится в каждом символе строки `'жаба'`.

В Python 3 эта проблема не возникает, потому что `str` — это всегда Unicode, а `bytes` и `str` нельзя смешивать:

```python
# Python 3
>>> import re
>>> re.findall('[мн]', 'жаба')  # Работает корректно с символами
[]
>>> re.findall(b'[\xd0]', 'жаба'.encode())  # Нужно явно работать с байтами
[b'\xd0', b'\xd0', b'\xd0', b'\xd0']
```

!!! warning "Мораль"
    Если вы работаете с текстом — используйте `str`, а не `bytes`. Regex-паттерны и строки должны быть одного типа.

---

## 15.8 Доступные кодировки в Python

### Как получить список всех кодировок

Python поставляется с модулем `encodings`, содержащим все поддерживаемые кодировки:

```python
import pkgutil
import encodings

# Список всех доступных кодировок
all_encodings = sorted([name for _, name, _ in pkgutil.iter_modules(encodings.__path__)])
print(all_encodings)
```

Результат (Python 3.12):

```python
['aliases', 'ascii', 'base64_codec', 'big5', 'big5hkscs', 'bz2_codec', 
'charmap', 'cp037', 'cp1006', 'cp1026', 'cp1125', 'cp1140', 'cp1250', 
'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 
'cp1258', 'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775', 
'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 
'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 
'cp932', 'cp949', 'cp950', 'euc_jis_2004', 'euc_jisx0213', 'euc_jp', 
'euc_kr', 'gb18030', 'gb2312', 'gbk', 'hex_codec', 'hp_roman8', 'hz', 
'idna', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 
'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'iso8859_1', 'iso8859_10', 
'iso8859_11', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16', 
'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 
'iso8859_7', 'iso8859_8', 'iso8859_9', 'johab', 'koi8_r', 'koi8_t', 
'koi8_u', 'kz1048', 'latin_1', 'mac_arabic', 'mac_croatian', 'mac_cyrillic', 
'mac_farsi', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 
'mac_romanian', 'mac_turkish', 'mbcs', 'oem', 'palmos', 'ptcp154', 
'punycode', 'quopri_codec', 'raw_unicode_escape', 'rot_13', 'shift_jis', 
'shift_jis_2004', 'shift_jisx0213', 'tis_620', 'undefined', 
'unicode_escape', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_32', 
'utf_32_be', 'utf_32_le', 'utf_7', 'utf_8', 'utf_8_sig', 'uu_codec', 
'zlib_codec']
```

### Фильтрация по типу

```python
# Только UTF кодировки
>>> [e for e in all_encodings if "utf" in e]
['utf_16', 'utf_16_be', 'utf_16_le', 'utf_32', 'utf_32_be', 
 'utf_32_le', 'utf_7', 'utf_8', 'utf_8_sig']

# Кириллические кодировки
>>> [e for e in all_encodings if any(x in e for x in ['1251', 'koi8', '866', 'cyrillic'])]
['cp1251', 'cp866', 'koi8_r', 'koi8_t', 'koi8_u', 'mac_cyrillic']

# Японские кодировки
>>> [e for e in all_encodings if any(x in e for x in ['jp', 'jis', 'shift'])]
['euc_jis_2004', 'euc_jisx0213', 'euc_jp', 'iso2022_jp', 'iso2022_jp_1',
 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
 'shift_jis', 'shift_jis_2004', 'shift_jisx0213']
```

### Откуда берутся кодировки?

Кодировки в Python — это **часть стандартной библиотеки CPython**, а не системные. Они хранятся в директории `Lib/encodings/` исходников Python:

```python
import encodings
import os

# Путь к модулю encodings
>>> encodings.__path__
['/usr/lib/python3.12/encodings']

# Файлы кодировок
>>> os.listdir(encodings.__path__[0])[:10]
['cp1251.py', 'utf_8.py', 'ascii.py', 'iso8859_1.py', ...]
```

Каждый файл — это Python-модуль, реализующий кодек:

```python
# Пример: упрощённая структура cp1251.py
import codecs

class Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        return codecs.charmap_encode(input, errors, encoding_table)
    
    def decode(self, input, errors='strict'):
        return codecs.charmap_decode(input, errors, decoding_table)

# Таблица соответствия байт → символ
decoding_table = (
    '\x00'    # 0x00 -> NULL
    '\x01'    # 0x01 -> ...
    # ... 256 символов ...
)
```

### Создание собственной кодировки

Можно зарегистрировать свой кодек через `codecs.register()`:

```python
import codecs

def rot13_encode(text):
    """ROT13 — сдвиг букв на 13 позиций."""
    return codecs.encode(text, 'rot_13'), len(text)

def rot13_decode(data):
    return codecs.decode(data, 'rot_13'), len(data)

class Rot13Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        return rot13_encode(input)
    def decode(self, input, errors='strict'):
        return rot13_decode(input)

def find_rot13(encoding):
    if encoding == 'my_rot13':
        return codecs.CodecInfo(
            name='my_rot13',
            encode=Rot13Codec().encode,
            decode=Rot13Codec().decode,
        )
    return None

# Регистрация
codecs.register(find_rot13)

# Использование
>>> "Hello".encode('my_rot13')
b'Uryyb'
>>> b'Uryyb'.decode('my_rot13')
'Hello'
```

---

## 15.9 Сводная таблица кодировок

### Unicode кодировки (UTF)

| Кодировка | Байт/символ | BOM | Описание |
|-----------|-------------|-----|----------|
| `utf_8` | 1–4 | Нет | Универсальный стандарт, ASCII-совместим |
| `utf_8_sig` | 1–4 | Да (EF BB BF) | UTF-8 с BOM для Excel и Windows |
| `utf_7` | 1–5+ | Нет | Для email (7-bit safe), устарел |
| `utf_16` | 2–4 | Да | С BOM, определяет порядок байтов |
| `utf_16_le` | 2–4 | Нет | Little-endian без BOM |
| `utf_16_be` | 2–4 | Нет | Big-endian без BOM |
| `utf_32` | 4 | Да | С BOM |
| `utf_32_le` | 4 | Нет | Little-endian без BOM |
| `utf_32_be` | 4 | Нет | Big-endian без BOM |

### Кириллические кодировки

| Кодировка | Байт/символ | Описание |
|-----------|-------------|----------|
| `cp1251` | 1 | Windows Cyrillic (Россия, Украина, Болгария) |
| `cp866` | 1 | DOS Cyrillic (OEM) |
| `koi8_r` | 1 | KOI8-R (Русский, UNIX legacy) |
| `koi8_u` | 1 | KOI8-U (Украинский) |
| `iso8859_5` | 1 | ISO Latin/Cyrillic |
| `mac_cyrillic` | 1 | Mac OS Cyrillic |

### Западноевропейские кодировки

| Кодировка | Байт/символ | Описание |
|-----------|-------------|----------|
| `ascii` | 1 | 7-bit ASCII (0–127) |
| `latin_1` / `iso8859_1` | 1 | ISO Latin-1 (Западная Европа) |
| `cp1252` | 1 | Windows Western (надмножество latin-1) |
| `iso8859_15` | 1 | Latin-9 (с символом €) |
| `mac_roman` | 1 | Mac OS Roman |

### Восточноазиатские кодировки

| Кодировка | Байт/символ | Описание |
|-----------|-------------|----------|
| `gb2312` | 1–2 | Китайский (упрощённый, базовый) |
| `gbk` | 1–2 | Китайский (расширенный GBK) |
| `gb18030` | 1–4 | Китайский (полный Unicode-совместимый) |
| `big5` | 1–2 | Китайский (традиционный, Тайвань) |
| `shift_jis` | 1–2 | Японский (Windows) |
| `euc_jp` | 1–3 | Японский (UNIX) |
| `euc_kr` | 1–2 | Корейский (UNIX) |
| `cp949` | 1–2 | Корейский (Windows) |

### Специальные кодеки (не кодировки текста)

| Кодек | Описание |
|-------|----------|
| `base64_codec` | Base64 кодирование |
| `hex_codec` | Шестнадцатеричное представление |
| `bz2_codec` | Сжатие bzip2 |
| `zlib_codec` | Сжатие zlib |
| `quopri_codec` | Quoted-printable (email) |
| `uu_codec` | Uuencode (UNIX-to-UNIX) |
| `rot_13` | ROT13 шифрование |
| `unicode_escape` | Python Unicode escape (`\uXXXX`) |
| `raw_unicode_escape` | Raw Unicode escape |
| `punycode` | Punycode для IDN (домены) |
| `idna` | IDNA кодирование доменов |

---

## 15.10 Особые кодировки: подробности

### utf_8_sig — UTF-8 с BOM

**BOM** (Byte Order Mark) — это специальная последовательность в начале файла:

```python
# При записи — добавляет BOM
>>> "Привет".encode('utf-8-sig')
b'\xef\xbb\xbfПривет'

# При чтении — автоматически удаляет BOM
>>> b'\xef\xbb\xbf\xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82'.decode('utf-8-sig')
'Привет'
```

**Когда использовать:**
- CSV файлы для Excel (иначе Excel не распознает UTF-8)
- Файлы для Windows-программ, ожидающих BOM

```python
# CSV для Excel
with open('data.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Имя', 'Возраст'])
    writer.writerow(['Пётр', 30])
```

### utf_7 — для email (7-bit safe)

UTF-7 кодирует Unicode, используя только ASCII-символы. Нужен для старых email-систем:

```python
>>> "Привет, мир!".encode('utf-7')
b'Привет, мир!'  # Кириллица как +BDAEQARLBDUEQgQ-...

>>> "Привет".encode('utf-7')
b'+BDAEPAQ4BDIENQRC-'

# ASCII остаётся как есть
>>> "Hello".encode('utf-7')
b'Hello'
```

**Не используйте** — устарел, заменён MIME и base64.

### unicode_escape и raw_unicode_escape

Превращает текст в Python escape-последовательности:

```python
>>> "Привет 👋".encode('unicode_escape')
b'\\u043f\\u0440\\u0438\\u0432\\u0435\\u0442 \\U0001f44b'

>>> b'\\u043f\\u0440\\u0438\\u0432\\u0435\\u0442'.decode('unicode_escape')
'привет'

# raw_unicode_escape — не экранирует \n, \t и т.д.
>>> "Tab:\tNewline:\n".encode('unicode_escape')
b'Tab:\\tNewline:\\n'

>>> "Tab:\tNewline:\n".encode('raw_unicode_escape')
b'Tab:\tNewline:\n'
```

### punycode и idna — для интернационализированных доменов

```python
# Punycode — кодирование IDN
>>> "münchen".encode('punycode')
b'mnchen-3ya'

>>> "москва".encode('punycode')
b'80aafi6cg'

# IDNA — полное преобразование домена
>>> "münchen.de".encode('idna')
b'xn--mnchen-3ya.de'

>>> "почта.рф".encode('idna')
b'xn--80a1acny.xn--p1ai'
```

### mbcs и oem — Windows-специфичные

```python
# mbcs — Multi-Byte Character Set текущей локали Windows
# Недоступен на Linux/macOS

# oem — OEM кодовая страница Windows (обычно cp437 или cp866)
```

### undefined — специальный кодек

Всегда вызывает исключение — для тестирования:

```python
>>> "test".encode('undefined')
UnicodeEncodeError: 'undefined' codec can't encode characters
```

---

## 15.11 Кодировка исходного кода (PEP 263)

В Python 2 если исходный файл содержит не-ASCII символы (например, кириллицу в строковых литералах или комментариях), необходимо явно указать кодировку файла в первой или второй строке:

```python
# -*- coding: utf-8 -*-
# или короче:
# coding: utf-8

приветствие = u'Привет, мир!'
```

Без этой декларации Python 2 выдаёт `SyntaxError`:

```bash
$ echo 'print u"жаба"' | python2
  File "<stdin>", line 1
SyntaxError: Non-ASCII character '\xd0' in file <stdin> on line 1,
  but no encoding declared; see http://python.org/dev/peps/pep-0263/
```

В **Python 3** кодировка по умолчанию — UTF-8 ([PEP 3120](https://peps.python.org/pep-3120/)), поэтому декларация `# coding: utf-8` больше не нужна. Однако она всё ещё часто встречается в кодовых базах, мигрированных с Python 2, и не вредит.

!!! note "Формат декларации"
    Python ищет паттерн `coding[=:]\s*([-\w.]+)` в первой или второй строке файла (вторая — если первая строка — shebang `#!/usr/bin/env python`). Все эти варианты валидны:
    
    ```python
    # coding: utf-8
    # -*- coding: utf-8 -*-
    # vim: set fileencoding=utf-8 :
    ```

---

## 15.12 Кодировки потоков ввода-вывода

### sys.stdin.encoding и sys.stdout.encoding

Python знает кодировку терминала через атрибуты `encoding` стандартных потоков:

```python
import sys
print(sys.stdin.encoding)   # например: 'utf-8'
print(sys.stdout.encoding)  # например: 'utf-8'
print(sys.stderr.encoding)  # например: 'utf-8'
```

Эти значения определяются из **локали** операционной системы (`LC_CTYPE`, `LANG`).

### Поведение при перенаправлении (pipes)

Критически важный нюанс: поведение зависит от того, **куда** идёт ввод/вывод.

**Python 2** — при перенаправлении кодировка сбрасывается в `None`:

```bash
# Python 2
$ python2 -c 'import sys; print(sys.stdin.encoding, sys.stdout.encoding)'
('UTF-8', 'UTF-8')

$ echo test | python2 -c 'import sys; print(sys.stdin.encoding, sys.stdout.encoding)'
(None, 'UTF-8')

$ python2 -c 'import sys; print(sys.stdin.encoding, sys.stdout.encoding)' | cat
('UTF-8', None)

$ echo test | python2 -c 'import sys; print(sys.stdin.encoding, sys.stdout.encoding)' | cat
(None, None)
```

Это означает, что `print(u'кириллица')` в Python 2 при перенаправлении в pipe вызывает `UnicodeEncodeError`, потому что Python не знает, в какой кодировке кодировать вывод, и использует `ascii`.

**Python 3** — кодировка берётся из локали даже при перенаправлении:

```bash
# Python 3
$ python3 -c 'import sys; print(sys.stdout.encoding)' | cat
utf-8

$ echo test | python3 -c 'import sys; print(sys.stdin.encoding)'
utf-8
```

### PYTHONIOENCODING

Переменная окружения `PYTHONIOENCODING` позволяет явно задать кодировку для stdin/stdout/stderr:

```bash
# Задать кодировку для всех потоков
$ PYTHONIOENCODING=utf-8 python3 -c 'import sys; print(sys.stdout.encoding)' | cat
utf-8

# Формат: encoding[:errors]
$ PYTHONIOENCODING=utf-8:surrogateescape python3 script.py

# Полезно для скриптов в пайплайнах
$ cat data.txt | PYTHONIOENCODING=utf-8 python3 process.py | sort
```

### PYTHONUTF8 (Python 3.7+)

Начиная с Python 3.7 ([PEP 540](https://peps.python.org/pep-0540/)) можно включить **UTF-8 Mode**, который переключает все стандартные потоки и `open()` по умолчанию на UTF-8, игнорируя системную локаль:

```bash
# Включить UTF-8 Mode
$ PYTHONUTF8=1 python3 script.py

# Или через флаг
$ python3 -X utf8 script.py
```

Что меняет UTF-8 Mode:

| Аспект | Без UTF-8 Mode | С UTF-8 Mode |
|--------|----------------|---------------|
| `open()` без encoding | `locale.getpreferredencoding()` | `'utf-8'` |
| `sys.stdin.encoding` | Из локали | `'utf-8'` |
| `sys.stdout.encoding` | Из локали | `'utf-8'` |
| `sys.stderr.encoding` | Из локали | `'utf-8'` |

!!! tip "Когда использовать UTF-8 Mode"
    - На системах с не-UTF-8 локалью (старые серверы, Windows с cp1251)
    - В Docker-контейнерах, где локаль не настроена
    - В CI/CD пайплайнах
    
    Начиная с Python 3.15 UTF-8 Mode будет **включён по умолчанию** ([PEP 686](https://peps.python.org/pep-0686/)).

---

## 15.13 Кодировка файловой системы

Кроме кодировки текстовых данных, Python должен знать, в какой кодировке хранятся **имена файлов** и **переменные окружения** операционной системы.

### sys.getfilesystemencoding()

```python
import sys

print(sys.getfilesystemencoding())
# Linux/macOS: 'utf-8'
# Windows:     'utf-8' (Python 3.6+, ранее — 'mbcs')
```

Эта кодировка используется для:

- Декодирования имён файлов, полученных от ОС (`os.listdir()`, `os.scandir()`)
- Кодирования путей, передаваемых системным вызовам (`open()`, `os.stat()`)
- Декодирования аргументов командной строки (`sys.argv`)
- Декодирования переменных окружения (`os.environ`)

### os.listdir() и тип аргумента

`os.listdir()` возвращает **разный тип** в зависимости от типа аргумента:

```python
import os

# Передаём str → получаем str (имена декодируются)
os.listdir('.')         # ['файл.txt', 'data.bin']
os.listdir('/tmp')      # ['test.txt', 'café.md']

# Передаём bytes → получаем bytes (сырые байты от ОС)
os.listdir(b'.')        # [b'\xd1\x84\xd0\xb0\xd0\xb9\xd0\xbb.txt', b'data.bin']
os.listdir(b'/tmp')     # [b'test.txt', b'caf\xc3\xa9.md']
```

### surrogateescape: работа с невалидными именами файлов

В Linux имена файлов — это произвольные последовательности байтов (кроме `/` и `\0`). Ядро **не проверяет** валидность UTF-8. Это значит, что можно создать файл с именем, которое не является валидным UTF-8:

```bash
# Создаём файл с невалидным UTF-8 именем
$ touch $'\xff\xfe.txt'
$ ls
??.txt
```

Python 3 использует обработчик ошибок **surrogateescape** ([PEP 383](https://peps.python.org/pep-0383/)) для таких случаев. Невалидные байты заменяются на «суррогатные» code points в диапазоне U+DC80–U+DCFF:

```python
import os

# Имя файла содержит невалидный UTF-8
names = os.listdir('.')  # str с surrogate characters
for name in names:
    try:
        print(name)
    except UnicodeEncodeError:
        # Имя содержит surrogate — не может быть напечатано
        raw = name.encode('utf-8', 'surrogateescape')
        print(f'Невалидное имя: {raw}')
```

Механизм surrogateescape позволяет **lossless round-trip**: декодировать байты в str и обратно в исходные байты без потерь:

```python
# bytes → str (с surrogateescape)
>>> b'\xff\xfe.txt'.decode('utf-8', 'surrogateescape')
'\udcff\udcfe.txt'

# str → bytes (обратно)
>>> '\udcff\udcfe.txt'.encode('utf-8', 'surrogateescape')
b'\xff\xfe.txt'
```

!!! note "Windows: UTF-8 по умолчанию"
    Начиная с Python 3.6 ([PEP 529](https://peps.python.org/pep-0529/)) на Windows `sys.getfilesystemencoding()` возвращает `'utf-8'` вместо `'mbcs'`, а для работы с файловой системой используются Wide API (`*W` функции), которые оперируют UTF-16 напрямую.

---

## 15.14 Сортировка Unicode-строк (collation)

Python сортирует строки по **code points** — то есть по числовым значениям символов:

```python
>>> sorted(['б', 'а', 'в'])
['а', 'б', 'в']  # Совпадает с алфавитным — повезло

>>> sorted(['ё', 'е', 'ж'])
['е', 'ж', 'ё']  # Неправильно! «ё» (U+0451) после «ж» (U+0436)
```

Это происходит потому, что Unicode code point буквы «ё» (U+0451) больше, чем у «ж» (U+0436). Для правильной сортировки нужно учитывать **лингвистические правила** (collation).

### locale.strxfrm — системная локаль

Функция `locale.strxfrm()` преобразует строку так, чтобы побайтовое сравнение давало правильный порядок для текущей локали:

```python
import locale

locale.setlocale(locale.LC_COLLATE, 'ru_RU.UTF-8')

>>> sorted(['ё', 'е', 'ж'], key=locale.strxfrm)
['е', 'ё', 'ж']  # Правильный алфавитный порядок
```

!!! warning "Ограничения locale"
    - Зависит от установленных в системе локалей (`locale -a`)
    - Глобальное состояние — `setlocale` влияет на весь процесс
    - Может отличаться между ОС

### pyuca — Unicode Collation Algorithm

Библиотека [pyuca](https://github.com/jtauber/pyuca) реализует Unicode Collation Algorithm (UCA) без зависимости от системной локали:

```python
from pyuca import Collator

collator = Collator()

>>> sorted(['ё', 'е', 'ж'], key=collator.sort_key)
['е', 'ё', 'ж']  # Правильно

>>> sorted(['Straße', 'Strasse', 'Strava'], key=collator.sort_key)
['Straße', 'Strasse', 'Strava']  # Немецкий порядок
```

### babel — интернационализация

Для более сложных задач (форматирование дат, чисел, валют по локали) используется [babel](https://babel.pocoo.org/):

```python
from babel import Locale
from babel.numbers import format_decimal

# Форматирование числа по правилам локали
format_decimal(1234567.89, locale='ru_RU')  # '1 234 567,89'
format_decimal(1234567.89, locale='en_US')  # '1,234,567.89'
format_decimal(1234567.89, locale='de_DE')  # '1.234.567,89'
```

!!! note "Регулярные выражения и Unicode"
    Стандартный модуль `re` в Python не поддерживает поиск по Unicode-свойствам (например, `\p{Cyrillic}`). Для этого есть библиотека [regex](https://pypi.org/project/regex/), которая поддерживает Unicode properties, вычитание множеств символов и другие расширения:
    
    ```python
    import regex  # pip install regex
    
    # Найти все кириллические символы
    regex.findall(r'\p{Cyrillic}+', 'Hello мир world')
    # ['мир']
    
    # Вычитание множеств: все буквы кроме ASCII
    regex.findall(r'[\p{L}--\p{ASCII}]+', 'Hello мир 世界')
    # ['мир', '世界']
    ```

---

## Резюме

| Концепция | Python 2 | Python 3 |
|-----------|----------|----------|
| Текст | `unicode` | `str` |
| Байты | `str` | `bytes` |
| Литерал текста | `u"текст"` | `"текст"` |
| Литерал байтов | `"bytes"` | `b"bytes"` |
| Кодировка по умолчанию | ASCII | UTF-8 |
| Кодировка исходного кода | Нужна декларация | UTF-8 по умолчанию |
| Кодировка stdout в pipe | `None` | Из локали |

**Правила работы с кодировками в Python 3:**

1. **Всегда указывайте `encoding`** при открытии текстовых файлов
2. **Используйте UTF-8** если нет особых требований
3. **Не смешивайте `str` и `bytes`** — явно конвертируйте
4. **Декодируйте на входе, кодируйте на выходе** — внутри программы работайте с `str`
5. **Используйте `PYTHONIOENCODING`** или UTF-8 Mode для скриптов в пайплайнах
6. **Учитывайте `surrogateescape`** при работе с именами файлов в Linux


??? question "Упражнения"
    **Задание 1.** Напишите функцию `safe_read(path)`, которая пытается прочитать файл в UTF-8, при ошибке — в CP1251, при ошибке — в latin-1 (всегда работает). Используйте `errors='strict'`.
    
    **Задание 2.** Откройте один и тот же файл с `encoding='utf-8'` и `encoding='utf-8-sig'`. В чём разница? Когда нужен `-sig`?
    
    **Задание 3.** Создайте файл, содержащий `b'\xff\xfe'` в начале. Откройте его с `encoding='utf-16'`. Что произошло? Это BOM — объясните механизм.

---

## Troubleshooting: типичные проблемы Части II

!!! bug "Кракозябры (mojibake) при чтении файла"
    Файл читается не в той кодировке, в которой был записан.
    
    ```python
    # Шаг 1: определите реальную кодировку
    import chardet
    with open('file', 'rb') as f:
        result = chardet.detect(f.read())
    print(result)  # {'encoding': 'Windows-1251', 'confidence': 0.99}
    
    # Шаг 2: перекодируйте
    with open('file', encoding=result['encoding']) as f:
        text = f.read()
    ```
    
    На уровне терминала: `file --mime-encoding file.txt` покажет предположительную кодировку.

!!! bug "UnicodeDecodeError в Python"
    ```python
    # Быстрое исправление — пропустить ошибки:
    text = data.decode('utf-8', errors='replace')  # замена на �
    
    # Лучшее решение — найти правильную кодировку:
    for enc in ['utf-8', 'cp1251', 'latin-1']:
        try:
            text = data.decode(enc)
            print(f"Сработало: {enc}")
            break
        except UnicodeDecodeError:
            continue
    ```

!!! bug "BOM (EF BB BF) ломает JSON / shebang / CSV"
    ```bash
    # Проверить наличие BOM:
    xxd file.txt | head -1
    # 00000000: efbb bf7b...  ← BOM перед { в JSON
    
    # Удалить BOM:
    sed -i '1s/^\xEF\xBB\xBF//' file.txt
    ```
    В Python используйте `encoding='utf-8-sig'` для автоматической обработки BOM.

!!! bug "Терминал показывает мусор вместо Unicode"
    Проверьте:
    
    - `echo $LANG` — должно содержать `UTF-8` (например, `en_US.UTF-8`)
    - `locale charmap` — должно вывести `UTF-8`
    - Шрифт терминала должен поддерживать нужные символы (попробуйте Nerd Font или JetBrains Mono)

!!! tip "Следующая глава"
    Разобрались с кодировками в Python. Теперь перейдём к **форматам файлов** — начнём с JSON → [JSON](../ch3/16-json.md)
