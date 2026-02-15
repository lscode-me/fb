# Глава 14. Unicode и UTF-8: Единый стандарт

## Введение

**Unicode** — это не кодировка, а **универсальный каталог всех символов мира**. Каждому символу присвоен уникальный номер (code point), а различные кодировки (UTF-8, UTF-16, UTF-32) определяют, как эти номера хранятся в байтах.

```
Символ:     П
Название:   CYRILLIC CAPITAL LETTER PE
Code point: U+041F (десятичное: 1055)

В разных кодировках:
  UTF-8:    D0 9F (2 байта)
  UTF-16:   04 1F (2 байта)
  UTF-32:   00 00 04 1F (4 байта)
```

---

## 14.1 Что такое Unicode

### Основные концепции

```
┌─────────────────────────────────────────────────────────────┐
│                        UNICODE                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CODE POINT — уникальный номер символа                      │
│  Диапазон: U+0000 до U+10FFFF (1,114,112 позиций)           │
│                                                             │
│  Примеры:                                                   │
│    U+0041   A          (Latin Capital Letter A)             │
│    U+0410   А          (Cyrillic Capital Letter A)          │
│    U+4E2D   中         (CJK Unified Ideograph)               │
│    U+1F600  😀         (Grinning Face)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Unicode ≠ UTF-8

Это важное различие:

| Концепция | Что это | Пример |
|-----------|---------|--------|
| **Unicode** | Каталог символов | A = U+0041 |
| **UTF-8** | Способ хранения | A = 0x41 (1 байт) |
| **UTF-16** | Другой способ хранения | A = 0x0041 (2 байта) |
| **UTF-32** | Ещё один способ | A = 0x00000041 (4 байта) |

```python
char = "A"
print(f"Unicode: U+{ord(char):04X}")    # Unicode: U+0041
print(f"UTF-8:   {char.encode('utf-8').hex()}")    # UTF-8:   41
print(f"UTF-16:  {char.encode('utf-16-be').hex()}")  # UTF-16:  0041
print(f"UTF-32:  {char.encode('utf-32-be').hex()}")  # UTF-32:  00000041
```

### Структура Unicode

```
┌─────────────────────────────────────────────────────────────┐
│              17 ПЛОСКОСТЕЙ (Planes)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Plane 0: BMP (Basic Multilingual Plane)                    │
│           U+0000 - U+FFFF (65,536 символов)                 │
│           Основные языки, знаки препинания                  │
│                                                             │
│  Plane 1: SMP (Supplementary Multilingual Plane)            │
│           U+10000 - U+1FFFF                                 │
│           Эмодзи 😀, исторические письменности              │
│                                                             │
│  Plane 2: SIP (Supplementary Ideographic Plane)             │
│           U+20000 - U+2FFFF                                 │
│           Редкие китайские иероглифы                        │
│                                                             │
│  Planes 3-13: Зарезервированы                               │
│                                                             │
│  Plane 14: SSP (Supplementary Special-purpose Plane)        │
│           Теги, variation selectors                         │
│                                                             │
│  Planes 15-16: Private Use Areas                            │
│           Для пользовательских символов                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Статистика Unicode 15.0 (2022)

| Категория | Количество |
|-----------|------------|
| Всего code points | 1,114,112 |
| Присвоено символов | 149,186 |
| Письменности (scripts) | 161 |
| Эмодзи | 3,664 |
| CJK-иероглифы | ~92,000 |

---

## 14.2 UTF-8: Кодировка-победитель

**UTF-8** (Unicode Transformation Format — 8-bit) — переменной длины кодировка, разработанная Кеном Томпсоном и Робом Пайком в 1992 году.

### Почему UTF-8 победил

```
┌─────────────────────────────────────────────────────────────┐
│               ПРЕИМУЩЕСТВА UTF-8                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ ASCII-совместимость (байты 0x00-0x7F идентичны)         │
│  ✅ Самосинхронизация (можно найти начало символа)          │
│  ✅ Нет проблем с порядком байтов (endianness)              │
│  ✅ Компактен для латиницы (1 байт)                         │
│  ✅ Нет нулевых байтов в середине (C-строки работают)       │
│  ✅ Сортировка байтов = сортировка code points              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Алгоритм кодирования UTF-8

```
┌─────────────────────────────────────────────────────────────┐
│  Code Point Range         │ Байты │ Шаблон                  │
├─────────────────────────────────────────────────────────────┤
│ U+0000   - U+007F         │   1   │ 0xxxxxxx                │
│ U+0080   - U+07FF         │   2   │ 110xxxxx 10xxxxxx       │
│ U+0800   - U+FFFF         │   3   │ 1110xxxx 10xxxxxx ×2    │
│ U+10000  - U+10FFFF       │   4   │ 11110xxx 10xxxxxx ×3    │
└─────────────────────────────────────────────────────────────┘
```

### Примеры кодирования

```python
def show_utf8(char):
    """Показать UTF-8 кодирование символа"""
    cp = ord(char)
    utf8 = char.encode('utf-8')
    binary = ' '.join(f'{b:08b}' for b in utf8)
    
    print(f"Символ:     {char}")
    print(f"Code point: U+{cp:04X} (десятичное: {cp})")
    print(f"UTF-8 hex:  {utf8.hex(' ')}")
    print(f"UTF-8 bin:  {binary}")
    print()

show_utf8('A')
# Символ:     A
# Code point: U+0041 (десятичное: 65)
# UTF-8 hex:  41
# UTF-8 bin:  01000001

show_utf8('П')
# Символ:     П
# Code point: U+041F (десятичное: 1055)
# UTF-8 hex:  d0 9f
# UTF-8 bin:  11010000 10011111

show_utf8('中')
# Символ:     中
# Code point: U+4E2D (десятичное: 20013)
# UTF-8 hex:  e4 b8 ad
# UTF-8 bin:  11100100 10111000 10101101

show_utf8('😀')
# Символ:     😀
# Code point: U+1F600 (десятичное: 128512)
# UTF-8 hex:  f0 9f 98 80
# UTF-8 bin:  11110000 10011111 10011000 10000000
```

### Ручное кодирование UTF-8

```python
def encode_utf8_manual(code_point):
    """Ручное кодирование code point в UTF-8"""
    if code_point <= 0x7F:
        # 1 байт: 0xxxxxxx
        return bytes([code_point])
    
    elif code_point <= 0x7FF:
        # 2 байта: 110xxxxx 10xxxxxx
        b1 = 0xC0 | (code_point >> 6)
        b2 = 0x80 | (code_point & 0x3F)
        return bytes([b1, b2])
    
    elif code_point <= 0xFFFF:
        # 3 байта: 1110xxxx 10xxxxxx 10xxxxxx
        b1 = 0xE0 | (code_point >> 12)
        b2 = 0x80 | ((code_point >> 6) & 0x3F)
        b3 = 0x80 | (code_point & 0x3F)
        return bytes([b1, b2, b3])
    
    else:
        # 4 байта: 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx
        b1 = 0xF0 | (code_point >> 18)
        b2 = 0x80 | ((code_point >> 12) & 0x3F)
        b3 = 0x80 | ((code_point >> 6) & 0x3F)
        b4 = 0x80 | (code_point & 0x3F)
        return bytes([b1, b2, b3, b4])

# Проверка
assert encode_utf8_manual(0x41) == 'A'.encode('utf-8')
assert encode_utf8_manual(0x41F) == 'П'.encode('utf-8')
assert encode_utf8_manual(0x4E2D) == '中'.encode('utf-8')
assert encode_utf8_manual(0x1F600) == '😀'.encode('utf-8')
```

### Декодирование UTF-8

```python
def decode_utf8_manual(data):
    """Ручное декодирование UTF-8"""
    result = []
    i = 0
    
    while i < len(data):
        b = data[i]
        
        if b <= 0x7F:
            # 1 байт
            result.append(chr(b))
            i += 1
            
        elif b <= 0xDF:
            # 2 байта
            cp = ((b & 0x1F) << 6) | (data[i+1] & 0x3F)
            result.append(chr(cp))
            i += 2
            
        elif b <= 0xEF:
            # 3 байта
            cp = ((b & 0x0F) << 12) | \
                 ((data[i+1] & 0x3F) << 6) | \
                 (data[i+2] & 0x3F)
            result.append(chr(cp))
            i += 3
            
        else:
            # 4 байта
            cp = ((b & 0x07) << 18) | \
                 ((data[i+1] & 0x3F) << 12) | \
                 ((data[i+2] & 0x3F) << 6) | \
                 (data[i+3] & 0x3F)
            result.append(chr(cp))
            i += 4
    
    return ''.join(result)

# Проверка
test = "Hello, Мир! 😀"
encoded = test.encode('utf-8')
decoded = decode_utf8_manual(encoded)
assert decoded == test
```

---

## 14.3 UTF-16 и UTF-32

### UTF-16

UTF-16 использует 2 или 4 байта на символ.

```
┌─────────────────────────────────────────────────────────────┐
│  BMP (U+0000 - U+FFFF):     2 байта напрямую                │
│  Вне BMP (U+10000+):        4 байта (surrogate pairs)       │
└─────────────────────────────────────────────────────────────┘
```

```python
text = "Hello, Мир! 😀"

# UTF-16 с BOM
utf16 = text.encode('utf-16')
print(utf16.hex(' '))
# ff fe 48 00 65 00 6c 00 6c 00 6f 00 ...
# ^^^^^ BOM (Little Endian)

# Явный порядок байтов
utf16_le = text.encode('utf-16-le')  # Little Endian
utf16_be = text.encode('utf-16-be')  # Big Endian

print(f"UTF-16 LE: {utf16_le[:10].hex(' ')}")  # 48 00 65 00 6c 00 ...
print(f"UTF-16 BE: {utf16_be[:10].hex(' ')}")  # 00 48 00 65 00 6c ...
```

### Surrogate Pairs для эмодзи

```python
# Эмодзи 😀 (U+1F600) в UTF-16
emoji = "😀"

# Code point > 0xFFFF требует surrogate pair
cp = ord(emoji)
print(f"Code point: U+{cp:X}")  # U+1F600

# Вычисление surrogate pair
adjusted = cp - 0x10000
high = 0xD800 + (adjusted >> 10)
low = 0xDC00 + (adjusted & 0x3FF)
print(f"High surrogate: U+{high:04X}")  # U+D83D
print(f"Low surrogate:  U+{low:04X}")   # U+DE00

# В UTF-16
utf16_be = emoji.encode('utf-16-be')
print(utf16_be.hex(' '))  # d8 3d de 00
```

### UTF-32

UTF-32 — фиксированные 4 байта на символ.

```python
text = "AПБ😀"

utf32 = text.encode('utf-32-be')
# Каждый символ = 4 байта
for i in range(0, len(utf32), 4):
    cp = int.from_bytes(utf32[i:i+4], 'big')
    print(f"U+{cp:04X} = {chr(cp)}")

# U+0041 = A
# U+041F = П
# U+0411 = Б
# U+1F600 = 😀
```

### Сравнение UTF кодировок

| Характеристика | UTF-8 | UTF-16 | UTF-32 |
|----------------|-------|--------|--------|
| Размер ASCII | 1 байт | 2 байта | 4 байта |
| Размер кириллицы | 2 байта | 2 байта | 4 байта |
| Размер китайского | 3 байта | 2 байта | 4 байта |
| Размер эмодзи | 4 байта | 4 байта | 4 байта |
| ASCII-совместим | ✅ | ❌ | ❌ |
| Фиксированная длина | ❌ | ❌ | ✅ |
| Endianness | N/A | Да (BE/LE) | Да (BE/LE) |
| Нулевые байты | ❌ | ✅ | ✅ |

### Когда что использовать

```
┌─────────────────────────────────────────────────────────────┐
│  UTF-8:   Веб, файлы, Unix, API                             │
│           Стандарт для обмена данными                       │
│                                                             │
│  UTF-16:  Windows API, Java, JavaScript (внутренне)         │
│           .NET, Objective-C                                  │
│                                                             │
│  UTF-32:  Редко. Когда нужна O(1) индексация                │
│           Внутреннее представление в некоторых БД           │
└─────────────────────────────────────────────────────────────┘
```

---

## 14.4 BOM (Byte Order Mark)

BOM — специальный символ U+FEFF в начале файла, указывающий кодировку и порядок байтов.

### BOM сигнатуры

```python
BOMS = {
    b'\xef\xbb\xbf': 'UTF-8',
    b'\xff\xfe': 'UTF-16 LE',
    b'\xfe\xff': 'UTF-16 BE',
    b'\xff\xfe\x00\x00': 'UTF-32 LE',
    b'\x00\x00\xfe\xff': 'UTF-32 BE',
}

def detect_bom(path):
    with open(path, 'rb') as f:
        start = f.read(4)
    
    # Проверяем от длинных к коротким
    for bom, encoding in sorted(BOMS.items(), key=lambda x: -len(x[0])):
        if start.startswith(bom):
            return encoding, len(bom)
    
    return None, 0
```

### Проблемы с BOM

```python
# BOM в UTF-8 — источник проблем!

# Создаём файл с BOM
with open('with_bom.txt', 'w', encoding='utf-8-sig') as f:
    f.write('Hello')

# Читаем как обычный UTF-8
with open('with_bom.txt', 'rb') as f:
    data = f.read()
    print(data)  # b'\xef\xbb\xbfHello'
    #               ^^^^^^^^^ BOM — "мусор" в начале!

# Правильное чтение
with open('with_bom.txt', 'r', encoding='utf-8-sig') as f:
    text = f.read()
    print(text)  # Hello (без BOM)
```

```bash
# Проблема с shebang
$ cat script.py
#!/usr/bin/env python3  # Если перед # стоит BOM...
print("Hello")

$ ./script.py
./script.py: line 1: #!/usr/bin/env: No such file or directory
# BOM сломал shebang!
```

### Рекомендации по BOM

```
┌─────────────────────────────────────────────────────────────┐
│  UTF-8:   НЕ ИСПОЛЬЗУЙТЕ BOM                                │
│           Исключение: файлы для старых Windows-программ     │
│                                                             │
│  UTF-16:  BOM ОБЯЗАТЕЛЕН (или явно указывайте BE/LE)        │
│                                                             │
│  UTF-32:  BOM ОБЯЗАТЕЛЕН (или явно указывайте BE/LE)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 14.5 Нормализация Unicode

Один и тот же визуальный символ может иметь разные представления!

### Проблема

```python
# Буква "й" — два способа представления:

# 1. Precomposed (NFC): один code point
composed = "й"  # U+0439 CYRILLIC SMALL LETTER SHORT I
print(len(composed))  # 1
print([hex(ord(c)) for c in composed])  # ['0x439']

# 2. Decomposed (NFD): буква + combining character
decomposed = "й"  # U+0438 + U+0306 (combining breve)
print(len(decomposed))  # 2
print([hex(ord(c)) for c in decomposed])  # ['0x438', '0x306']

# Визуально идентичны, но:
print(composed == decomposed)  # False!
```

### Формы нормализации

```
┌─────────────────────────────────────────────────────────────┐
│  NFC  — Canonical Decomposition + Composition               │
│         Компактная форма (precomposed)                      │
│         "é" → U+00E9                                        │
│                                                             │
│  NFD  — Canonical Decomposition                             │
│         Разложенная форма                                   │
│         "é" → U+0065 U+0301 (e + ´)                         │
│                                                             │
│  NFKC — Compatibility Decomposition + Composition           │
│         + замена совместимых символов                       │
│         "ﬁ" → "fi"                                          │
│                                                             │
│  NFKD — Compatibility Decomposition                         │
│         Максимальное разложение                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Python и нормализация

```python
import unicodedata

# Нормализация
text_nfd = "й"  # decomposed
text_nfc = unicodedata.normalize('NFC', text_nfd)

print(len(text_nfd))  # 2
print(len(text_nfc))  # 1
print(text_nfd == text_nfc)  # False
print(unicodedata.normalize('NFC', text_nfd) == 
      unicodedata.normalize('NFC', text_nfc))  # True

# Безопасное сравнение строк
def safe_compare(s1, s2):
    return unicodedata.normalize('NFC', s1) == \
           unicodedata.normalize('NFC', s2)
```

### Практический пример: имена файлов

```python
import os
import unicodedata

# macOS использует NFD для имён файлов!
# Windows и Linux используют NFC

filename = "Документ.txt"

# На macOS файл может быть сохранён как NFD
nfd_name = unicodedata.normalize('NFD', filename)
nfc_name = unicodedata.normalize('NFC', filename)

print(f"NFC length: {len(nfc_name)}")  # 12
print(f"NFD length: {len(nfd_name)}")  # 13 (о + combining ̆)

# Безопасный поиск файла
def find_file(directory, target_name):
    target_nfc = unicodedata.normalize('NFC', target_name)
    
    for name in os.listdir(directory):
        name_nfc = unicodedata.normalize('NFC', name)
        if name_nfc == target_nfc:
            return os.path.join(directory, name)
    
    return None
```

!!! warning "Проблема имён файлов при переносе"
    Файл, созданный на macOS (NFD), может "не найтись" на Linux (NFC), хотя имя выглядит одинаково:
    
    ```bash
    # На macOS создали файл
    $ touch "Документ.txt"
    
    # Скопировали на Linux через ZIP
    $ unzip archive.zip
    $ ls
    Документ.txt   # Имя выглядит нормально
    
    $ python -c "open('Документ.txt')"  # Ошибка!
    # Потому что байты имени разные (NFD vs NFC)
    ```
    
    См. также: [Пути и имена файлов](../ch1/08-paths-names.md) в Главе 1.

---

## 14.6 Grapheme Clusters

**Grapheme cluster** — это то, что пользователь воспринимает как один символ.

```python
# Эмодзи "семья" — это ОДИН grapheme cluster
family = "👨‍👩‍👧‍👦"

print(len(family))  # 11 code points!
print([hex(ord(c)) for c in family])
# ['0x1f468', '0x200d', '0x1f469', '0x200d', '0x1f467', '0x200d', '0x1f466']
# 👨 + ZWJ + 👩 + ZWJ + 👧 + ZWJ + 👦

# Флаги — два Regional Indicator Symbols
flag = "🇷🇺"
print(len(flag))  # 2 code points
# U+1F1F7 (R) + U+1F1FA (U)
```

### Правильный подсчёт символов

```python
# pip install regex (не стандартный re!)
import regex

def grapheme_length(text):
    """Количество видимых символов (grapheme clusters)"""
    return len(regex.findall(r'\X', text))

text = "Привет 👨‍👩‍👧‍👦! 🇷🇺"

print(f"len():           {len(text)}")           # 21
print(f"grapheme_length: {grapheme_length(text)}")  # 11
```

---

## 14.7 Python и Unicode

### Строки в Python 3

```python
# Python 3: str — это Unicode (code points)
text = "Привет"
print(type(text))  # <class 'str'>

# bytes — это байты
data = text.encode('utf-8')
print(type(data))  # <class 'bytes'>

# Конвертация
text2 = data.decode('utf-8')
assert text == text2
```

### Работа с code points

```python
# ord() — символ → code point
print(ord('A'))   # 65
print(ord('П'))   # 1055
print(ord('😀'))  # 128512

# chr() — code point → символ
print(chr(65))     # A
print(chr(1055))   # П
print(chr(128512)) # 😀

# Escape-последовательности
print("\u0041")      # A (4 hex digits)
print("\u041F")      # П
print("\U0001F600")  # 😀 (8 hex digits для code points > FFFF)
print("\N{GRINNING FACE}")  # 😀 (по имени)
```

### Обработка ошибок кодирования

```python
text = "Привет 😀"

# strict (по умолчанию) — исключение
try:
    text.encode('ascii')
except UnicodeEncodeError as e:
    print(f"Ошибка: {e}")

# ignore — пропустить
print(text.encode('ascii', errors='ignore'))  # b'  '

# replace — заменить на ?
print(text.encode('ascii', errors='replace'))  # b'?????? ????'

# xmlcharrefreplace — HTML entities
print(text.encode('ascii', errors='xmlcharrefreplace'))
# b'&#1055;&#1088;&#1080;&#1074;&#1077;&#1090; &#128512;'

# backslashreplace — escape
print(text.encode('ascii', errors='backslashreplace'))
# b'\\u041f\\u0440\\u0438\\u0432\\u0435\\u0442 \\U0001f600'
```

### unicodedata module

```python
import unicodedata

char = 'П'

print(unicodedata.name(char))      # CYRILLIC CAPITAL LETTER PE
print(unicodedata.category(char))  # Lu (Letter, uppercase)

# Поиск по имени
print(unicodedata.lookup('CYRILLIC CAPITAL LETTER PE'))  # П

# Категории символов
categories = {
    'Lu': 'Uppercase Letter',
    'Ll': 'Lowercase Letter',
    'Nd': 'Decimal Number',
    'Po': 'Punctuation, Other',
    'Sm': 'Symbol, Math',
    'So': 'Symbol, Other',
}
```

---

## 14.8 Доминирование UTF-8

### Статистика веба

```
┌─────────────────────────────────────────────────────────────┐
│              ИСПОЛЬЗОВАНИЕ КОДИРОВОК В ВЕБЕ                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  UTF-8      ████████████████████████████████████  98.2%     │
│  ISO-8859-1 █                                     1.0%      │
│  Windows-1251 ▏                                    0.2%      │
│  Другие     ▏                                      0.6%      │
│                                                             │
│  Источник: W3Techs, 2024                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Рекомендации

```python
# ВСЕГДА указывайте кодировку явно!

# Файлы
with open('file.txt', 'w', encoding='utf-8') as f:
    f.write(content)

# HTTP
response.headers['Content-Type'] = 'application/json; charset=utf-8'

# HTML
# <meta charset="utf-8">

# Python source files (по умолчанию UTF-8 в Python 3)
# -*- coding: utf-8 -*-
```

---

## 14.9 Частые проблемы и решения

### Mojibake в UTF-8

```python
# Данные были в CP1251, но прочитаны как UTF-8
broken = "Ð\x9fÑ\x80Ð¸Ð²ÐµÑ\x82"

# Восстановление
fixed = broken.encode('latin-1').decode('utf-8')
print(fixed)  # Привет
```

### Double encoding

```python
# Текст был закодирован дважды
double_encoded = "Ð\x9fÑ\x80Ð¸Ð²ÐµÑ\x82"

# Шаг 1: "Привет" → UTF-8 bytes
# Шаг 2: bytes интерпретированы как Latin-1 → string
# Шаг 3: string → UTF-8 bytes снова

# Исправление
step1 = double_encoded.encode('latin-1')  # Вернуть в bytes
step2 = step1.decode('utf-8')             # Правильно декодировать
print(step2)  # Привет
```

### Проверка валидности UTF-8

```python
def is_valid_utf8(data: bytes) -> bool:
    try:
        data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

# Или с использованием codecs
import codecs

def is_valid_utf8_strict(data: bytes) -> bool:
    try:
        codecs.decode(data, 'utf-8', errors='strict')
        return True
    except UnicodeDecodeError:
        return False
```

---

## Резюме

**Unicode и UTF-8:**

| Концепция | Описание |
|-----------|----------|
| **Unicode** | Каталог символов (1.1M позиций) |
| **Code point** | Уникальный номер символа (U+XXXX) |
| **UTF-8** | Кодировка 1-4 байта, ASCII-совместимая |
| **UTF-16** | Кодировка 2-4 байта, используется в Windows/Java |
| **UTF-32** | Фиксированные 4 байта |
| **BOM** | Маркер порядка байтов |
| **Нормализация** | NFC/NFD для сравнения строк |

**Ключевые правила:**

1. **UTF-8 — стандарт** для файлов, API, веба
2. **Всегда указывайте кодировку** явно
3. **Нормализуйте** строки перед сравнением
4. **Не используйте BOM** в UTF-8
5. **Помните о grapheme clusters** при работе с эмодзи

---

## Дополнительные ресурсы

- [The Absolute Minimum Every Developer Must Know About Unicode](https://tonsky.me/blog/unicode/)
- [UTF-8 Everywhere Manifesto](http://utf8everywhere.org/)
- [Unicode Standard](https://unicode.org/standard/standard.html)
- [Python Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)
- [Unicode Character Database](https://unicode.org/ucd/)


??? question "Упражнения"
    **Задание 1.** Закодируйте символ "€" (U+20AC) в UTF-8 вручную. Проверьте через `python3 -c "print('€'.encode('utf-8'))"`.
    
    **Задание 2.** Продемонстрируйте разницу NFC и NFD: символ "é" — один code point (U+00E9) или два (U+0065 + U+0301)? Покажите через `unicodedata.normalize()`.
    
    **Задание 3.** Найдите эмодзи, занимающий 4 байта в UTF-8 (например, 🎉). Докажите это через `len('🎉'.encode('utf-8'))`. Почему `len('🎉')` == 1 в Python 3?

!!! tip "Следующая глава"
    Разобрались с Unicode и UTF-8. Теперь посмотрим, как работать с кодировками в **Python** → [Кодировки в Python](15-python-encodings.md)
