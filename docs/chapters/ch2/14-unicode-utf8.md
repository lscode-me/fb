---
description: "Как работает Unicode и UTF-8. Code points, плоскости BMP и SMP, байтовое представление символов. Практические примеры на Python."
---

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

!!! info "Все три кодировки покрывают весь Unicode"
    UTF-8, UTF-16 и UTF-32 — это три **равноценных** способа записи одних и тех же символов. Каждая из них способна закодировать **любой** code point Unicode (от U+0000 до U+10FFFF). Разница только в том, сколько байтов и каких используется для представления. Ни одна из кодировок не расширяет и не ограничивает набор доступных символов — это всегда один и тот же каталог Unicode.

```python
char = "A"
print(f"Unicode: U+{ord(char):04X}")    # Unicode: U+0041
print(f"UTF-8:   {char.encode('utf-8').hex()}")    # UTF-8:   41
print(f"UTF-16:  {char.encode('utf-16-be').hex()}")  # UTF-16:  0041
print(f"UTF-32:  {char.encode('utf-32-be').hex()}")  # UTF-32:  00000041
```

### Алфавиты и Unicode: общие и уникальные символы

Разные алфавиты — это просто **подмножества** каталога Unicode. Многие символы совпадают, но у каждого языка есть свои уникальные буквы:

**Латиница: английский (EN), немецкий (DE), турецкий (TR)**

| Символ | Code point | EN | DE | TR | Название |
|:------:|:----------:|:--:|:--:|:--:|----------|
| A | U+0041 | ✅ | ✅ | ✅ | Latin Capital Letter A |
| B | U+0042 | ✅ | ✅ | ✅ | Latin Capital Letter B |
| C | U+0043 | ✅ | ✅ | ✅ | Latin Capital Letter C |
| Ç | U+00C7 | — | — | ✅ | Latin Capital Letter C with Cedilla |
| D | U+0044 | ✅ | ✅ | ✅ | Latin Capital Letter D |
| E | U+0045 | ✅ | ✅ | ✅ | Latin Capital Letter E |
| F | U+0046 | ✅ | ✅ | ✅ | Latin Capital Letter F |
| G | U+0047 | ✅ | ✅ | ✅ | Latin Capital Letter G |
| Ğ | U+011E | — | — | ✅ | Latin Capital Letter G with Breve |
| H | U+0048 | ✅ | ✅ | ✅ | Latin Capital Letter H |
| I | U+0049 | ✅ | ✅ | ✅ | Latin Capital Letter I |
| İ | U+0130 | — | — | ✅ | Latin Capital Letter I with Dot Above |
| ı | U+0131 | — | — | ✅ | Latin Small Letter Dotless I |
| J | U+004A | ✅ | ✅ | ✅ | Latin Capital Letter J |
| K | U+004B | ✅ | ✅ | ✅ | Latin Capital Letter K |
| L | U+004C | ✅ | ✅ | ✅ | Latin Capital Letter L |
| M | U+004D | ✅ | ✅ | ✅ | Latin Capital Letter M |
| N | U+004E | ✅ | ✅ | ✅ | Latin Capital Letter N |
| O | U+004F | ✅ | ✅ | ✅ | Latin Capital Letter O |
| Ö | U+00D6 | — | ✅ | ✅ | Latin Capital Letter O with Diaeresis |
| P | U+0050 | ✅ | ✅ | ✅ | Latin Capital Letter P |
| Q | U+0051 | ✅ | ✅ | — | Latin Capital Letter Q |
| R | U+0052 | ✅ | ✅ | ✅ | Latin Capital Letter R |
| S | U+0053 | ✅ | ✅ | ✅ | Latin Capital Letter S |
| Ş | U+015E | — | — | ✅ | Latin Capital Letter S with Cedilla |
| T | U+0054 | ✅ | ✅ | ✅ | Latin Capital Letter T |
| U | U+0055 | ✅ | ✅ | ✅ | Latin Capital Letter U |
| Ü | U+00DC | — | ✅ | ✅ | Latin Capital Letter U with Diaeresis |
| V | U+0056 | ✅ | ✅ | ✅ | Latin Capital Letter V |
| W | U+0057 | ✅ | ✅ | — | Latin Capital Letter W |
| X | U+0058 | ✅ | ✅ | — | Latin Capital Letter X |
| Y | U+0059 | ✅ | ✅ | ✅ | Latin Capital Letter Y |
| Z | U+005A | ✅ | ✅ | ✅ | Latin Capital Letter Z |
| Ä | U+00C4 | — | ✅ | — | Latin Capital Letter A with Diaeresis |
| ß | U+00DF | — | ✅ | — | Latin Small Letter Sharp S |

Все эти символы живут в блоках **Latin Basic** (U+0000–U+007F) и **Latin Extended** (U+0080–U+024F) — это общая латиница, из которой каждый язык берёт нужные символы. Заметьте: турецкий не использует Q, W, X, зато добавляет Ç, Ğ, İ/ı, Ö, Ş, Ü. А немецкий расширяет базовый набор буквами Ä, Ö, Ü и лигатурой ß.

**Кириллица: русский (RU), украинский (UA), сербский (SR)**

| Символ | Code point | RU | UA | SR | Название |
|:------:|:----------:|:--:|:--:|:--:|----------|
| А | U+0410 | ✅ | ✅ | ✅ | Cyrillic Capital Letter A |
| Б | U+0411 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Be |
| В | U+0412 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Ve |
| Г | U+0413 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Ghe |
| Ґ | U+0490 | — | ✅ | — | Cyrillic Capital Letter Ghe with Upturn |
| Д | U+0414 | ✅ | ✅ | ✅ | Cyrillic Capital Letter De |
| Ђ | U+0402 | — | — | ✅ | Cyrillic Capital Letter Dje |
| Е | U+0415 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Ie |
| Є | U+0404 | — | ✅ | — | Cyrillic Capital Letter Ukrainian Ie |
| Ё | U+0401 | ✅ | — | — | Cyrillic Capital Letter Io |
| Ж | U+0416 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Zhe |
| З | U+0417 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Ze |
| И | U+0418 | ✅ | ✅ | ✅ | Cyrillic Capital Letter I |
| І | U+0406 | — | ✅ | — | Cyrillic Capital Letter Byelorussian-Ukrainian I |
| Ї | U+0407 | — | ✅ | — | Cyrillic Capital Letter Yi |
| Й | U+0419 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Short I |
| Ј | U+0408 | — | — | ✅ | Cyrillic Capital Letter Je |
| К | U+041A | ✅ | ✅ | ✅ | Cyrillic Capital Letter Ka |
| Л | U+041B | ✅ | ✅ | ✅ | Cyrillic Capital Letter El |
| Љ | U+0409 | — | — | ✅ | Cyrillic Capital Letter Lje |
| М | U+041C | ✅ | ✅ | ✅ | Cyrillic Capital Letter Em |
| Н | U+041D | ✅ | ✅ | ✅ | Cyrillic Capital Letter En |
| Њ | U+040A | — | — | ✅ | Cyrillic Capital Letter Nje |
| О | U+041E | ✅ | ✅ | ✅ | Cyrillic Capital Letter O |
| П | U+041F | ✅ | ✅ | ✅ | Cyrillic Capital Letter Pe |
| Р | U+0420 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Er |
| С | U+0421 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Es |
| Т | U+0422 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Te |
| Ћ | U+040B | — | — | ✅ | Cyrillic Capital Letter Tshe |
| У | U+0423 | ✅ | ✅ | ✅ | Cyrillic Capital Letter U |
| Ф | U+0424 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Ef |
| Х | U+0425 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Ha |
| Ц | U+0426 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Tse |
| Ч | U+0427 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Che |
| Џ | U+040F | — | — | ✅ | Cyrillic Capital Letter Dzhe |
| Ш | U+0428 | ✅ | ✅ | ✅ | Cyrillic Capital Letter Sha |
| Щ | U+0429 | ✅ | ✅ | — | Cyrillic Capital Letter Shcha |
| Ъ | U+042A | ✅ | — | — | Cyrillic Capital Letter Hard Sign |
| Ы | U+042B | ✅ | — | — | Cyrillic Capital Letter Yeru |
| Ь | U+042C | ✅ | ✅ | — | Cyrillic Capital Letter Soft Sign |
| Э | U+042D | ✅ | — | — | Cyrillic Capital Letter E |
| Ю | U+042E | ✅ | ✅ | — | Cyrillic Capital Letter Yu |
| Я | U+042F | ✅ | ✅ | ✅ | Cyrillic Capital Letter Ya |
| Ӏ | U+04C0 | — | — | — | Cyrillic Letter Palochka (кавказские языки) |

Кириллический блок (U+0400–U+04FF) содержит буквы для **всех** языков, использующих кириллицу. Русский (33 буквы), украинский (33 буквы) или сербский (30 букв) — это лишь выборки из этого общего блока. Видно, что большинство букв общие, но у каждого языка есть свои: Ё/Ъ/Ы/Э только в русском, Ґ/Є/І/Ї — в украинском, Ђ/Ј/Љ/Њ/Ћ/Џ — в сербском. А есть символы, которых нет ни в одном из этих трёх алфавитов — например, **Палочка** (Ӏ, U+04C0), используемая в кавказских языках: аварском, чеченском, ингушском, даргинском, лакском и других. Она тоже живёт в кириллическом блоке Unicode, подтверждая: блок содержит гораздо больше символов, чем любой отдельный алфавит.

!!! tip "Алфавит ≠ блок Unicode"
    Алфавит конкретного языка — это **подмножество** символов из Unicode-блока. Сам Unicode не привязан к языкам: он просто хранит все символы, а какие из них составляют алфавит — определяется языковой нормой.

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

### Статистика Unicode 16.0 (2024)

| Категория | Количество |
|-----------|------------|
| Всего code points | 1,114,112 |
| Присвоено символов | 154,998 |
| Письменности (scripts) | 168 |
| Эмодзи | 3,790 |
| CJK-иероглифы | ~97,000 |
| Зарезервировано (не присвоено) | ~821,000 |

```
┌─────────────────────────────────────────────────────────────┐
│          ЗАПОЛНЕННОСТЬ UNICODE (v16.0)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Общий размер пространства:      1,114,112 code points      │
│                                                             │
│  ██░░░░░░░░░░░░░░░░░░  Присвоено символов:  154,998 (14%)   │
│  ██░░░░░░░░░░░░░░░░░░  Private Use Area:    137,468 (12%)   │
│  ██░░░░░░░░░░░░░░░░░░  Суррогаты (UTF-16):   2,048  (0.2%)  │
│  ░░░░░░░░░░░░░░░░░░░░  Noncharacters:           66  (<0.1%) │
│  ████████████████░░░░  Свободно:            ~819,530 (74%)  │
│                                                             │
│  → ~74% пространства Unicode ещё не занято                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Три четверти пространства Unicode свободно. Места хватит ещё на ~819 000 символов — это в 5 раз больше, чем уже присвоено. При текущем темпе добавления (~5 000–7 000 символов за версию) пространства хватит ещё на столетия.

### Как добавить новый символ в Unicode

Unicode — **живой стандарт**. Новые символы добавляются в каждой версии. Любой человек или организация может подать заявку:

**Процесс**

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. Proposal │───▶│  2. Комитет  │───▶│ 3. Синхрони- │───▶│ 4. Публика-  │
│  (заявка)    │    │  UTC         │    │ зация с ISO  │    │ ция версии   │
│              │    │  4 раза/год  │    │ 10646        │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

1. **Подготовка заявки (proposal).** Документ (обычно PDF) для Unicode Consortium, где нужно обосновать:
    - зачем нужен символ (лингвистические свидетельства, примеры текстов)
    - где он уже используется (книги, документы, вывески)
    - чем он отличается от существующих символов
    - предлагаемые свойства (категория, направление письма)

2. **Рассмотрение UTC** (Unicode Technical Committee). Комитет собирается 4 раза в год, заявка проходит несколько раундов обсуждения.

3. **Синхронизация с ISO 10646.** Unicode синхронизирован со стандартом ISO/IEC 10646, поэтому одобрение проходит и через ISO.

4. **Публикация** в очередной версии Unicode (выходит примерно раз в год).

**Сложность зависит от того, что добавляется**

| Ситуация | Сложность | Сроки |
|----------|-----------|-------|
| Новый эмодзи | Средняя | 1–2 года |
| Буквы для живого языка с незадокументированной письменностью | Высокая | 2–4 года |
| Историческая письменность (клинопись, руны) | Высокая | 2–5 лет |
| Символ, дублирующий существующий | Отклоняется | — |

**Главные трудности:**

- **Доказательная база.** Недостаточно сказать «нам нужна буква». Нужны опубликованные тексты, словари, грамматики. Для бесписьменных языков — академические работы лингвистов.
- **Необратимость.** Символ, добавленный в Unicode, **нельзя удалить** — стандарт гарантирует стабильность. Поэтому комитет осторожен.
- **Политика.** Иногда вопрос «это отдельная буква или вариант существующей?» — предмет споров между лингвистами и национальными органами стандартизации.

!!! example "Примеры успешных добавлений"
    - **Адлам** (U+1E900–U+1E95F) — письменность для языка фула (Западная Африка), изобретена в 1989 г. двумя подростками из Гвинеи, добавлена в Unicode 9.0 (2016)
    - **Ваи** (U+A500–U+A63F) — слоговое письмо Либерии, создано в 1830-х, добавлено в Unicode 5.1 (2008)
    - **Строчная Палочка ӏ** (U+04CF) — заглавная Палочка Ӏ (U+04C0) попала в Unicode ещё в 1993 (v1.1), но без строчной пары. 13 лет кавказские языки не имели строчной формы, пока её не добавили в Unicode 5.0 (2006)
    - **Символ рубля ₽** (U+20BD) — добавлен в Unicode 7.0 (2014) по заявке Банка России
    - **Символ биткоина ₿** (U+20BF) — добавлен в Unicode 10.0 (2017) после многолетних обсуждений о том, является ли криптовалюта достаточно «устоявшейся»

!!! tip "Private Use Area — временное решение"
    Пока символ не принят официально, можно использовать code points из **Private Use Area** (U+E000–U+F8FF, а также Planes 15–16). Так делает, например, SIL International для редких африканских письменностей. Но PUA-символы не стандартизированы — их значение известно только тем, кто заранее договорился.

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

### Surrogate Pairs: как UTF-16 кодирует символы вне BMP

UTF-16 изначально задумывался как кодировка **фиксированной длины** — ровно 2 байта на символ. Этого хватает для 65 536 значений (BMP, U+0000–U+FFFF), и в 1990-х казалось, что этого хватит. Но Unicode вырос за пределы BMP — появились символы с code points от U+10000 (эмодзи, исторические письменности, редкие иероглифы). Как их уместить в 2-байтовые единицы?

Решение — **суррогатные пары** (surrogate pairs). Unicode зарезервировал 2 048 code points (U+D800–U+DFFF), **запретив** присваивать им символы. Этот диапазон разделён на две половины:

```
┌─────────────────────────────────────────────────────────────┐
│  СУРРОГАТНЫЙ ДИАПАЗОН (U+D800–U+DFFF)                      │
│  2 048 code points, НЕ являются символами                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  High surrogates:  U+D800 – U+DBFF  (1 024 значения)       │
│  Low surrogates:   U+DC00 – U+DFFF  (1 024 значения)       │
│                                                             │
│  Пара (high + low) кодирует один символ вне BMP:            │
│  1 024 × 1 024 = 1 048 576 комбинаций                       │
│  → ровно столько, сколько code points в Planes 1–16         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Алгоритм кодирования:**

Чтобы закодировать code point `cp` (где `cp >= 0x10000`) в surrogate pair:

```
1. adjusted = cp - 0x10000        (получаем 20-битное число: 0x00000–0xFFFFF)
2. high = 0xD800 + (adjusted >> 10)   (старшие 10 бит → high surrogate)
3. low  = 0xDC00 + (adjusted & 0x3FF) (младшие 10 бит → low surrogate)
```

Каждый суррогат — 16-битное значение, записывается как обычная 2-байтовая единица UTF-16. Итого: 4 байта на символ вне BMP.

```python
# Эмодзи 😀 (U+1F600) в UTF-16
emoji = "😀"

# Code point > 0xFFFF требует surrogate pair
cp = ord(emoji)
print(f"Code point: U+{cp:X}")  # U+1F600

# Вычисление surrogate pair
adjusted = cp - 0x10000          # 0xF600
high = 0xD800 + (adjusted >> 10) # 0xD800 + 0x3D = 0xD83D
low = 0xDC00 + (adjusted & 0x3FF) # 0xDC00 + 0x200 = 0xDE00
print(f"High surrogate: U+{high:04X}")  # U+D83D
print(f"Low surrogate:  U+{low:04X}")   # U+DE00

# В UTF-16BE: high и low записываются подряд
utf16_be = emoji.encode('utf-16-be')
print(utf16_be.hex(' '))  # d8 3d de 00
```

**Декодирование обратно:**

```
cp = 0x10000 + (high - 0xD800) × 0x400 + (low - 0xDC00)
   = 0x10000 + (0xD83D - 0xD800) × 0x400 + (0xDE00 - 0xDC00)
   = 0x10000 + 0x3D × 0x400 + 0x200
   = 0x10000 + 0xF400 + 0x200
   = 0x1F600 → 😀
```

!!! warning "Суррогаты — это НЕ символы"
    Code points U+D800–U+DFFF **не являются символами**. Им не соответствует никакая буква, знак или эмодзи — это **технический механизм** UTF-16. Стандарт Unicode запрещает присваивать им символы, и этот диапазон никогда не будет использован для чего-то другого.

    Из этого следуют важные правила:

    - **UTF-8 и UTF-32** запрещают кодирование суррогатных code points — они им не нужны
    - **UTF-16** использует суррогаты только парами (high + low) — непарный суррогат в валидном UTF-16 невозможен
    - Если вы видите суррогат в данных вне контекста UTF-16 — это **ошибка** (или нестандартная кодировка вроде MUTF-8/WTF-8)

!!! note "Почему именно U+D800–U+DFFF?"
    Этот диапазон был зарезервирован **до** появления символов вне BMP. Когда Unicode Consortium осознал, что 65 536 позиций не хватит, нужен был способ расширить UTF-16 без полной смены формата. Выбор пал на «дырку» в BMP — 2 048 неиспользуемых позиций, которые навечно отданы под суррогатный механизм.

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

### Modified UTF-8 (MUTF-8)

**Modified UTF-8** — нестандартный вариант UTF-8, используемый в экосистеме Java. Он отличается от стандартного UTF-8 в двух ключевых моментах:

**1. Нулевой символ (U+0000) → два байта**

В стандартном UTF-8 нулевой символ кодируется одним байтом `0x00`. Это проблема для C-строк и JNI, где `0x00` означает конец строки. MUTF-8 кодирует `U+0000` как два байта `0xC0 0x80` — overlong encoding, запрещённое в стандартном UTF-8:

```
Стандартный UTF-8:   U+0000 → 00
Modified UTF-8:      U+0000 → C0 80

Почему C0 80?
  110 00000  10 000000     (шаблон 2-байтовой последовательности)
   C0          80          = overlong encoding для нуля
```

**2. Символы вне BMP → 6 байтов через суррогатные пары**

Стандартный UTF-8 кодирует символы `U+10000–U+10FFFF` напрямую в 4 байта. MUTF-8 сначала разбивает code point на **суррогатную пару** (как в UTF-16), затем кодирует **каждый суррогат отдельно** в 3 байта — итого 6 байтов:

```
Символ: 😀 (U+1F600)

Стандартный UTF-8 (4 байта):
  U+1F600 → F0 9F 98 80

Modified UTF-8 (6 байтов):
  U+1F600 → surrogate pair: U+D83D U+DE00
  U+D83D  → ED A0 BD      (3 байта, high surrogate)
  U+DE00  → ED B8 80      (3 байта, low surrogate)
  Итого:    ED A0 BD ED B8 80
```

!!! warning "Суррогаты в UTF-8 — это ошибка"
    Стандартный UTF-8 **запрещает** кодирование суррогатных code points (U+D800–U+DFFF). Валидный UTF-8 декодер должен отклонить такие последовательности. MUTF-8 намеренно нарушает это правило.

**Сравнение:**

| Символ | Code point | UTF-8 | MUTF-8 |
|:------:|:----------:|:-----:|:------:|
| A | U+0041 | `41` | `41` |
| NUL | U+0000 | `00` | `C0 80` |
| П | U+041F | `D0 9F` | `D0 9F` |
| 中 | U+4E2D | `E4 B8 AD` | `E4 B8 AD` |
| 😀 | U+1F600 | `F0 9F 98 80` (4 Б) | `ED A0 BD ED B8 80` (6 Б) |

Для символов BMP (кроме `U+0000`) кодировки идентичны. Различия проявляются только на нулевом символе и символах за пределами BMP.

**Где используется MUTF-8:**

| Контекст | Детали |
|----------|--------|
| **JVM `.class` файлы** | Все строковые константы в байткоде хранятся в MUTF-8 (CONSTANT_Utf8) |
| **`DataInput/DataOutput`** | Методы `readUTF()` / `writeUTF()` в Java используют MUTF-8 |
| **Java Object Serialization** | Строки в сериализованных объектах |
| **Android DEX** | Формат `.dex` (Dalvik Executable) использует MUTF-8 для строк |
| **JNI** | `GetStringUTFChars()` возвращает MUTF-8, а не UTF-8 |

```python
# Демонстрация разницы UTF-8 и MUTF-8 на Python

def encode_mutf8(text: str) -> bytes:
    """Кодирование строки в Modified UTF-8"""
    result = bytearray()
    for char in text:
        cp = ord(char)
        
        if cp == 0x0000:
            # NUL → overlong 2-байтовая последовательность
            result.extend(b'\xC0\x80')
        elif cp <= 0x7F:
            result.append(cp)
        elif cp <= 0x7FF:
            result.append(0xC0 | (cp >> 6))
            result.append(0x80 | (cp & 0x3F))
        elif cp <= 0xFFFF:
            result.append(0xE0 | (cp >> 12))
            result.append(0x80 | ((cp >> 6) & 0x3F))
            result.append(0x80 | (cp & 0x3F))
        else:
            # Вне BMP: суррогатная пара, каждый суррогат → 3 байта
            adjusted = cp - 0x10000
            high = 0xD800 + (adjusted >> 10)
            low = 0xDC00 + (adjusted & 0x3FF)
            for surrogate in (high, low):
                result.append(0xE0 | (surrogate >> 12))
                result.append(0x80 | ((surrogate >> 6) & 0x3F))
                result.append(0x80 | (surrogate & 0x3F))
    
    return bytes(result)


# Сравнение
for char, name in [('A', 'Latin A'), ('\x00', 'NUL'), ('П', 'Cyrillic'),
                    ('😀', 'Emoji')]:
    utf8 = char.encode('utf-8')
    mutf8 = encode_mutf8(char)
    match = "✅" if utf8 == mutf8 else "❌"
    print(f"{name:10s}  UTF-8: {utf8.hex(' '):20s}  "
          f"MUTF-8: {mutf8.hex(' '):20s}  совпадают: {match}")

# Latin A    UTF-8: 41                    MUTF-8: 41                    совпадают: ✅
# NUL        UTF-8: 00                    MUTF-8: c0 80                 совпадают: ❌
# Cyrillic   UTF-8: d0 9f                 MUTF-8: d0 9f                 совпадают: ✅
# Emoji      UTF-8: f0 9f 98 80           MUTF-8: ed a0 bd ed b8 80    совпадают: ❌
```

!!! note "CESU-8 — ещё один вариант"
    **CESU-8** (Compatibility Encoding Scheme for UTF-16: 8-Bit) кодирует символы вне BMP через суррогатные пары (как MUTF-8), но **не** модифицирует нулевой символ. CESU-8 описан в [Unicode Technical Report #26](https://www.unicode.org/reports/tr26/). MUTF-8 = CESU-8 + overlong NUL.

!!! tip "Практическое правило"
    Если вы работаете с Java-файлами (`.class`, сериализация, JNI) и видите 6-байтовые последовательности с `0xED` вместо ожидаемых 4-байтовых — это MUTF-8. Стандартный Python-декодер UTF-8 выбросит `UnicodeDecodeError` на таких данных. Для корректного чтения нужна конвертация MUTF-8 → UTF-8.

### WTF-8 (Wobbly Transformation Format)

**WTF-8** — ещё одно расширение UTF-8, но с другой целью: он допускает **непарные суррогаты** (isolated surrogates). Зачем это нужно?

Windows хранит имена файлов в UTF-16, но не проверяет корректность — файл может иметь имя с непарным суррогатом (например, `U+D800` без соответствующего low surrogate). Стандартный UTF-8 не может представить такие данные, потому что суррогаты (U+D800–U+DFFF) запрещены. WTF-8 снимает это ограничение:

```
Стандартный UTF-8:
  U+D800 (непарный суррогат) → ❌ ОШИБКА, запрещено

WTF-8:
  U+D800 → ED A0 80  (3 байта, допустимо)
```

Отличия WTF-8 от UTF-8 и MUTF-8:

| Свойство | UTF-8 | MUTF-8 | WTF-8 |
|----------|-------|--------|-------|
| Непарные суррогаты | ❌ | ❌ (только пары) | ✅ |
| Парные суррогаты | ❌ | ✅ (для символов вне BMP) | ❌ (конвертируются в 4-байтовую форму) |
| Overlong NUL | ❌ | ✅ (`C0 80`) | ❌ |
| Символы вне BMP | 4 байта напрямую | 6 байтов через пару суррогатов | 4 байта напрямую |

Важное свойство: WTF-8 **запрещает парные суррогаты** — если суррогаты образуют валидную пару, они должны быть заменены на 4-байтовое представление code point. Это гарантирует, что любая валидная UTF-8 строка остаётся валидной WTF-8 строкой.

**Где используется:**

| Контекст | Детали |
|----------|--------|
| **Rust `OsString`/`OsStr`** | На Windows пути хранятся во внутреннем представлении, совместимом с WTF-8 (`Wtf8Buf`) |
| **Firefox** | Внутреннее представление строк при работе с Windows API |
| **Python `os.fsencode()`** | На Windows использует `surrogatepass` error handler — аналогичная идея |

```python
# Python: работа с «грязными» путями Windows через surrogatepass

# Имитация непарного суррогата
surrogate = '\ud800'  # Непарный high surrogate

# Стандартный UTF-8 отказывается
try:
    surrogate.encode('utf-8')
except UnicodeEncodeError as e:
    print(f"UTF-8: {e}")  # surrogates not allowed

# surrogatepass разрешает — аналог WTF-8
wtf8_bytes = surrogate.encode('utf-8', errors='surrogatepass')
print(f"WTF-8 (surrogatepass): {wtf8_bytes.hex(' ')}")  # ed a0 80

# Декодирование обратно
decoded = wtf8_bytes.decode('utf-8', errors='surrogatepass')
print(f"Decoded: {decoded!r}")  # '\ud800'
```

!!! info "Спецификация WTF-8"
    WTF-8 описан Саймоном Сапиным (Simon Sapin) в [неофициальной спецификации](https://simonsapin.github.io/wtf-8/). Название «Wobbly» — ирония над тем, что формат намеренно ослабляет строгие правила UTF-8.

### UTF-7: 7-битный Unicode

**UTF-7** (RFC 2152) — кодировка Unicode, использующая только 7-битные ASCII-символы. Разработана для передачи Unicode через каналы, пропускающие только 7 бит (email-шлюзы 1990-х).

Основная идея: ASCII-символы передаются как есть, а не-ASCII кодируются через **Modified Base64** в блоках, обрамлённых `+` и `-`:

```
Текст:    "Привет, мир!"
UTF-7:    +BBgEQAQ4BDIENQRCLCAEPARYBEAAIQ-

          +           — начало Base64-блока
          BBgEQ...    — Modified Base64 кодирование UTF-16 байтов
          -           — конец блока (или переход к ASCII)

Текст:    "Hello, мир!"
UTF-7:    Hello, +BDwEWARAACE-

          Hello,      — ASCII часть (as-is)
          +BDwEWARAACE- — не-ASCII часть в Base64
```

Сам символ `+` кодируется как `+-`:

```
Текст:   "2+2=4"
UTF-7:   2+-2=4
```

```python
# Python поддерживает UTF-7
text = "Hello, мир!"

encoded = text.encode('utf-7')
print(encoded)  # b'Hello, +BDAEOAQ4ACE-'
print(len(encoded))  # больше, чем UTF-8

# Декодирование
decoded = encoded.decode('utf-7')
assert decoded == text

# Чистый ASCII → UTF-7 идентичен
ascii_text = "Hello, World!"
assert ascii_text.encode('utf-7') == ascii_text.encode('ascii')
```

**Где до сих пор используется:**

| Контекст | Детали |
|----------|--------|
| **IMAP** | Имена почтовых папок кодируются в Modified UTF-7 (RFC 3501, не совсем тот же UTF-7) |
| **Легаси-системы** | Старые email-шлюзы, которые отбрасывают 8-й бит |

!!! danger "UTF-7 и XSS-атаки"
    UTF-7 стал вектором **XSS-атак** в браузерах. Если сервер не указывал `charset` в `Content-Type`, браузер мог автоматически определить кодировку как UTF-7. Атакующий вставлял:

    ```
    +ADw-script+AD4-alert(1)+ADw-/script+AD4-
    ```

    Браузер декодировал это как UTF-7 и получал:

    ```html
    <script>alert(1)</script>
    ```

    **Защита:** современные браузеры полностью запретили автодетект UTF-7. HTML5 спецификация явно исключает UTF-7 из списка допустимых кодировок. **Всегда указывайте `charset=utf-8`** в заголовках.

!!! tip "В новых проектах UTF-7 не нужен"
    Сегодня email использует MIME с `Content-Transfer-Encoding: base64` или `quoted-printable` для передачи 8-битных данных. UTF-7 — исторический артефакт. Единственное живое применение — IMAP с его Modified UTF-7 для имён папок.

### Punycode и IDNA: Unicode в доменных именах

**Punycode** (RFC 3492) — алгоритм кодирования Unicode в ограниченный набор ASCII-символов (`a-z`, `0-9`, `-`), предназначенный для **интернационализированных доменных имён** (IDN).

DNS-система работает только с ASCII. Чтобы домены вроде `münchen.de` или `пример.рф` могли существовать, придумали **IDNA** (Internationalized Domain Names in Applications) — стандарт, который конвертирует Unicode-домены через Punycode с префиксом `xn--`:

```
Unicode домен:      münchen.de
Punycode-метка:     mnchen-3ya
IDNA (ACE-форма):   xn--mnchen-3ya.de

Unicode домен:      пример.рф
IDNA:               xn--e1afmapc.xn--p1ai

Unicode домен:      食狮.中国
IDNA:               xn--85x722f.xn--fiqs8s
```

Каждая метка (часть домена между точками) кодируется отдельно. Если метка содержит только ASCII — она остаётся без изменений.

```python
# Python: работа с Punycode и IDNA

# Кодирование Punycode
domain = "münchen"
punycode = domain.encode('punycode')
print(punycode)  # b'mnchen-3ya'

# Декодирование
print(punycode.decode('punycode'))  # münchen

# IDNA через встроенный модуль
domain_full = "münchen.de"

# Кодирование в IDNA
idna_encoded = domain_full.encode('idna')
print(idna_encoded)  # b'xn--mnchen-3ya.de'

# Декодирование из IDNA
print(idna_encoded.decode('idna'))  # münchen.de

# Кириллический пример
print("пример.рф".encode('idna'))  # b'xn--e1afmapc.xn--p1ai'
```

**Как работает Punycode (упрощённо):**

Алгоритм разделяет символы на ASCII (basic) и не-ASCII (non-basic), затем кодирует позиции и code points не-ASCII символов в компактную строку:

```
Вход: "münchen"

1. Извлечь ASCII-символы (сохраняя порядок): mnchen
2. Добавить разделитель: mnchen-
3. Закодировать позицию и code point 'ü' (U+00FC): 3ya
4. Результат: mnchen-3ya
```

!!! danger "Гомографические атаки (IDN homograph attack)"
    Punycode и IDN открывают вектор **фишинг-атак**. Многие Unicode-символы визуально неотличимы от ASCII:

    ```
    apple.com          — настоящий (латинские буквы)
    аpple.com          — фейк! (первая 'а' — кириллическая U+0430)

    Punycode фейка:    xn--pple-43d.com
    ```

    Человек не видит разницы в адресной строке, но DNS ведёт на разные серверы.

    **Защита в браузерах:**

    - Chrome, Firefox, Safari показывают Punycode (`xn--...`) вместо Unicode, если домен содержит символы из **разных скриптов** (mixed-script detection)
    - Некоторые TLD (`.рф`, `.中国`) считаются безопасными, т.к. используют один скрипт
    - Реестры доменов ограничивают допустимые символы для каждого TLD

### GB18030: Обязательный стандарт Китая

**GB18030** — это китайский национальный стандарт кодирования символов, **обязательный** для всего программного обеспечения, продаваемого в Китае. Это единственная кодировка помимо UTF-*, которая покрывает **все** code points Unicode.

**Эволюция китайских кодировок:**

```
1980  GB2312     6,763 иероглифов, 2 байта
  │
  └─→ 1993  GBK        21,886 иероглифов, 2 байта (расширение GB2312)
        │
        └─→ 2000  GB18030    Все Unicode + совместимость с GBK
              │
              └─→ 2005  GB18030-2005  Обновление (обязательный стандарт)
                    │
                    └─→ 2022  GB18030-2022  Актуальная версия
```

GB18030 использует переменную длину: 1, 2 или 4 байта:

```
┌─────────────────────────────────────────────────────────────┐
│  Длина  │ Диапазон байтов        │ Что покрывает            │
├─────────────────────────────────────────────────────────────┤
│ 1 байт  │ 0x00-0x7F              │ ASCII (идентичен)        │
│ 2 байта │ 0x8140-0xFEFE          │ Китайские иероглифы,     │
│         │                        │ символы CJK              │
│ 4 байта │ 0x81308130-0xFE39FE39  │ Все остальные Unicode    │
│         │                        │ (line by line mapping)   │
└─────────────────────────────────────────────────────────────┘
```

```python
# Python: работа с GB18030
text = "Hello, 你好世界! 😀"

# Кодирование
gb = text.encode('gb18030')
utf8 = text.encode('utf-8')

print(f"GB18030: {len(gb)} байтов  {gb.hex(' ')}")
print(f"UTF-8:   {len(utf8)} байтов  {utf8.hex(' ')}")

# Сравнение размера для разных символов
for char, name in [('A', 'ASCII'), ('Я', 'Cyrillic'), ('你', 'Chinese'),
                    ('😀', 'Emoji')]:
    gb_bytes = char.encode('gb18030')
    utf8_bytes = char.encode('utf-8')
    print(f"{name:10s}  GB18030: {gb_bytes.hex(' '):12s} ({len(gb_bytes)}Б)  "
          f"UTF-8: {utf8_bytes.hex(' '):12s} ({len(utf8_bytes)}Б)")

# ASCII      GB18030: 41           (1Б)  UTF-8: 41           (1Б)
# Cyrillic   GB18030: a7 d1        (2Б)  UTF-8: d0 af        (2Б)
# Chinese    GB18030: c4 e3        (2Б)  UTF-8: e4 bd a0      (3Б)
# Emoji      GB18030: 94 39 fc 37  (4Б)  UTF-8: f0 9f 98 80   (4Б)
```

**Сравнение GB18030 и UTF-8:**

| Характеристика | GB18030 | UTF-8 |
|----------------|---------|-------|
| Покрытие Unicode | Полное | Полное |
| ASCII-совместимость | ✅ | ✅ |
| Размер китайского текста | 2 байта | 3 байта |
| Размер кириллицы | 2 байта | 2 байта |
| Размер эмодзи | 4 байта | 4 байта |
| Совместимость с GBK/GB2312 | ✅ | ❌ |
| Самосинхронизация | ❌ | ✅ |
| Распространённость | Китай | Весь мир |

GB18030 компактнее UTF-8 для китайского текста (2 байта vs 3), но не самосинхронизируется — нельзя определить начало символа, начав с произвольного байта.

!!! info "Обязательность GB18030"
    С 2006 года **все** программное обеспечение и операционные системы, продаваемые в Китае, обязаны поддерживать GB18030. Это касается ОС, браузеров, офисных пакетов и баз данных. Поэтому GB18030 поддерживается в Windows, macOS, Linux, Python, Java и большинстве языков программирования.

!!! tip "Практическое применение"
    Если вы разрабатываете ПО для китайского рынка или работаете с данными из китайских систем, вам может встретиться GB18030 (или его подмножества GBK/GB2312). Python обрабатывает его из коробки: `'gb18030'`, `'gbk'`, `'gb2312'` — валидные имена кодировок для `encode()`/`decode()`.

### Сводная таблица: варианты и альтернативы UTF-8

| Кодировка | Отношение к UTF-8 | Ключевая особенность | Где встречается |
|-----------|-------------------|----------------------|------------------|
| **UTF-8** | Стандарт | — | Везде |
| **CESU-8** | Нестандартный вариант | Суррогатные пары для символов вне BMP | Oracle DB, некоторые XML-парсеры |
| **MUTF-8** | CESU-8 + overlong NUL | + нулевой символ → `C0 80` | JVM, Android DEX, JNI |
| **WTF-8** | Расширение | Допускает непарные суррогаты | Rust `OsString`, Firefox |
| **UTF-7** | 7-битная альтернатива | Только ASCII-байты на выходе | IMAP (legacy) |
| **GB18030** | Независимая кодировка | Полное покрытие Unicode, компактен для CJK | Китай (обязательный стандарт) |

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

### BOM в реальном мире: подводные грабли

BOM в UTF-8 — это всего 3 байта (`EF BB BF`), но они ломают удивительно много вещей:

| Жертва | Что происходит | Решение |
|--------|---------------|---------|
| **JSON** | RFC 8259 запрещает BOM. Многие парсеры отвергают файл | Не использовать `utf-8-sig` для JSON |
| **CSV** | Excel на Windows **требует** BOM для корректного UTF-8. Другие программы — ломаются | Для Excel: `utf-8-sig`. Для остальных: `utf-8` |
| **Shebang** (`#!`) | Ядро не распознаёт `#!` с BOM перед ним | Никогда не добавлять BOM в скрипты |
| **Git diff** | BOM отображается как изменение, хотя текст не менялся | `.gitattributes`: `* text=auto` |
| **YAML** | Спецификация разрешает BOM, но некоторые парсеры его не ждут | Лучше не добавлять |
| **`cat file1 file2`** | BOM окажется в середине объединённого файла | Удалить BOM перед конкатенацией |

### Обнаружение и удаление BOM

```bash
# Обнаружить файлы с BOM
grep -rl $'\xef\xbb\xbf' *.py *.json

# Или через file
file --mime document.txt
# document.txt: text/plain; charset=utf-8 (с BOM → "utf-8-bom")

# Удалить BOM (sed)
sed -i '1s/^\xEF\xBB\xBF//' file.txt

# Удалить BOM (Python)
python3 -c "
import pathlib
p = pathlib.Path('file.txt')
data = p.read_bytes()
if data.startswith(b'\xef\xbb\xbf'):
    p.write_bytes(data[3:])
    print('BOM удалён')
"
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

### SIMD-ускорение валидации UTF-8

Наивная проверка UTF-8 обрабатывает **по одному байту** за такт. Современные процессоры имеют **SIMD**-инструкции (Single Instruction, Multiple Data), которые обрабатывают **16-64 байта одновременно**:

```text
Наивная валидация:     1 байт / такт  →  ~1 ГБ/с
SIMD (SSE4/AVX2):    32 байта / такт  →  ~20-30 ГБ/с
SIMD (ARM NEON):     16 байт / такт   →  ~12-15 ГБ/с
```

Библиотека **simdjson** (Daniel Lemire) использует этот подход для парсинга JSON с валидацией UTF-8 на скорости, близкой к пропускной способности памяти. Аналогичные идеи применяются в:

- **simdutf** — библиотека для транскодирования Unicode (используется в Node.js)
- **Rust**: крейт `simdutf8` — валидация UTF-8 через SIMD
- **Go 1.22+**: оптимизированная проверка UTF-8 в стандартной библиотеке

!!! tip "Как это работает (упрощённо)"
    UTF-8 имеет жёсткие правила: первый байт определяет длину последовательности, продолжающие байты начинаются с `10xxxxxx`. SIMD-алгоритм загружает 32 байта разом, применяет серию **битовых масок и сдвигов** и за несколько инструкций определяет, нарушены ли правила. Классический подход с конечным автоматом (state machine) обрабатывает данные в ~20 раз медленнее.

---

## Резюме

**Unicode и UTF-8:**

| Концепция | Описание |
|-----------|----------|
| **Unicode** | Каталог символов (1.1M позиций) |
| **Code point** | Уникальный номер символа (U+XXXX) |
| **UTF-8** | Кодировка 1-4 байта, ASCII-совместимая |
| **MUTF-8** | Вариант UTF-8 для Java: overlong NUL, суррогатные пары для символов вне BMP |
| **WTF-8** | Расширение UTF-8 для непарных суррогатов (Rust, Firefox) |
| **UTF-7** | 7-битная кодировка Unicode (IMAP, legacy email) |
| **Punycode/IDNA** | Unicode в доменных именах (`xn--...`) |
| **GB18030** | Китайский стандарт, полное покрытие Unicode |
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
