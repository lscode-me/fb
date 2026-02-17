# Глава 50. Токенизация: как текст превращается в числа для LLM

## Введение

В главах 11–15 мы изучили, как текст превращается в байты: символы → кодовые точки Unicode → байты UTF-8. Но для языковых моделей (GPT, Claude, LLaMA, Gemini) этого недостаточно. Модели работают не с байтами и не с символами, а с **токенами** — фрагментами текста, сконвертированными в числа через специальный словарь.

Токенизация — это **ещё один слой кодирования**, надстройка над Unicode:

```
Текст          "Файловая система"
    │
    ▼  Unicode (глава 14)
Кодовые точки  [1060, 1072, 1081, 1083, 1086, 1074, 1072, 1103, ...]
    │
    ▼  UTF-8 (глава 14)
Байты          [d0 a4, d0 b0, d0 b9, d0 bb, d0 be, d0 b2, d0 b0, ...]
    │
    ▼  Токенизация (эта глава)
Токены         [41084, 11209, 7894]     ← 3 числа вместо 17 символов
```

Понимание токенизации критично: от неё зависит **стоимость**, **скорость** и **качество** работы LLM.

---

## 50.1 Зачем нужны токены

### Почему не символы?

Кажется логичным подавать модели текст посимвольно. Но:

| Подход | Словарь | Проблемы |
|--------|---------|----------|
| **Символы** | ~150 000 (Unicode) | Слишком длинные последовательности, модель «не видит» слова |
| **Слова** | ~500 000+ (словарь языка) | Не обработает новые слова, опечатки, код |
| **Байты** | 256 | Ещё длиннее, 1 символ кириллицы = 2 байта |
| **Токены (subword)** | 32 000–200 000 | Баланс: короткие последовательности + любой текст |

### Что такое токен

Токен — это фрагмент текста от одного символа до целого слова (иногда нескольких слов):

```
Текст:   "Tokenization is fascinating"
Токены:  ["Token", "ization", " is", " fascin", "ating"]
ID:      [3404,     2065,      318,    매혹,      1723]
```

Частые слова → один токен. Редкие слова → несколько токенов. Это позволяет:

- Ограниченным словарём (~100K записей) кодировать **любой** текст
- Частые слова обрабатывать **быстро** (один токен)
- Редкие слова всё равно обработать, разбив на части

!!! note "Аналогия с кодировками"
    Вспомните UTF-8 (глава 14): частые символы (ASCII) — 1 байт, редкие — 2-4 байта.
    Токенизация делает то же самое на уровне слов: частые слова — 1 токен, редкие — 2-5 токенов.

---

## 50.2 Byte Pair Encoding (BPE)

### Алгоритм

BPE — основной алгоритм токенизации в GPT, LLaMA, Mistral. Он **обучается** на корпусе текста:

**Шаг 1.** Начинаем со словаря из 256 отдельных байтов.

**Шаг 2.** Находим самую частую пару соседних токенов в корпусе.

**Шаг 3.** Объединяем эту пару в новый токен, добавляем в словарь.

**Шаг 4.** Повторяем шаги 2–3, пока словарь не достигнет нужного размера.

### Пример обучения BPE

```
Корпус: "aabaabaab"

Шаг 0: Словарь = {a, b}         Текст = [a, a, b, a, a, b, a, a, b]
                                 Частоты пар: (a,a)=3  (a,b)=3  (b,a)=2

Шаг 1: Объединяем (a,a) → "aa"  Словарь = {a, b, aa}
        Текст = [aa, b, aa, b, aa, b]
                                 Частоты пар: (aa,b)=3  (b,aa)=2

Шаг 2: Объединяем (aa,b) → "aab" Словарь = {a, b, aa, aab}
        Текст = [aab, aab, aab]
                                 Готово: весь текст = 3 токена
```

### Реализация на Python

```python
from collections import Counter

def train_bpe(text: str, vocab_size: int) -> dict:
    """Обучение BPE-токенизатора."""
    # Начальные токены — отдельные символы
    tokens = list(text)
    merges = {}  # (пара) → новый токен

    while len(set(tokens)) < vocab_size:
        # Считаем пары
        pairs = Counter(zip(tokens, tokens[1:]))
        if not pairs:
            break

        # Самая частая пара
        best_pair = pairs.most_common(1)[0][0]
        new_token = best_pair[0] + best_pair[1]

        # Заменяем пару на новый токен
        merged = []
        i = 0
        while i < len(tokens):
            if i < len(tokens) - 1 and \
               (tokens[i], tokens[i+1]) == best_pair:
                merged.append(new_token)
                i += 2
            else:
                merged.append(tokens[i])
                i += 1

        tokens = merged
        merges[best_pair] = new_token
        print(f"Merge: {best_pair!r} → {new_token!r}  "
              f"(tokens: {len(tokens)})")

    return merges

# Пример
merges = train_bpe("aabaabaab", vocab_size=5)
# Merge: ('a', 'a') → 'aa'  (tokens: 6)
# Merge: ('aa', 'b') → 'aab'  (tokens: 3)
```

---

## 50.3 Токенизаторы популярных моделей

### Сравнение

| Модель | Токенизатор | Размер словаря | Особенности |
|--------|-------------|---------------|-------------|
| GPT-2 | BPE | 50 257 | Byte-level BPE |
| GPT-3.5/4 | BPE (cl100k) | 100 256 | Лучше для кода и не-латиницы |
| GPT-4o | BPE (o200k) | 200 000 | Ещё экономнее для не-английских языков |
| LLaMA 2 | SentencePiece (BPE) | 32 000 | Byte-fallback |
| LLaMA 3 | tiktoken-compatible | 128 256 | Расширенный словарь |
| Claude | BPE | ~100 000 | Byte-level |
| Gemini | SentencePiece | 256 000 | Очень большой словарь |
| BERT | WordPiece | 30 522 | Subword, `##` для продолжений |

### tiktoken — токенизатор OpenAI

```python
import tiktoken

# Загрузить токенизатор GPT-4o
enc = tiktoken.encoding_for_model("gpt-4o")

# Токенизация
text = "Файловая система ext4"
tokens = enc.encode(text)
print(tokens)        # [41084, 11209, 7894, 1759, 4132, 19]
print(len(tokens))   # 6 токенов из 21 символа

# Декодирование обратно
print(enc.decode(tokens))  # "Файловая система ext4"

# Посмотреть каждый токен
for t in tokens:
    print(f"  {t:>6d} → {enc.decode([t])!r}")
#   41084 → 'Файл'
#   11209 → 'овая'
#    7894 → ' система'
#    1759 → ' ext'
#    4132 → '4'
```

### SentencePiece — токенизатор Google/Meta

```python
import sentencepiece as spm

# Обучение на своём корпусе
spm.SentencePieceTrainer.train(
    input='corpus.txt',
    model_prefix='my_tokenizer',
    vocab_size=32000,
    model_type='bpe',           # или 'unigram'
    character_coverage=0.9995,  # Покрытие символов (для CJK, кириллицы)
    byte_fallback=True          # Неизвестные символы → байты
)

# Использование
sp = spm.SentencePieceProcessor(model_file='my_tokenizer.model')
tokens = sp.encode("Файловая система ext4", out_type=str)
print(tokens)  # ['▁Файл', 'ов', 'ая', '▁система', '▁ext', '4']
#                  ▁ = пробел (специальный символ)
```

---

## 50.4 Как токенизация влияет на всё

### Стоимость API

LLM-API тарифицируются **за токены**, не за символы:

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

texts = {
    "English": "The file system manages files on disk",
    "Русский": "Файловая система управляет файлами на диске",
    "Python":  "with open('file.txt', 'r') as f:\n    data = f.read()",
    "JSON":    '{"name": "test", "size": 1024, "type": "file"}',
}

for lang, text in texts.items():
    tokens = enc.encode(text)
    ratio = len(text) / len(tokens)
    print(f"{lang:10s}: {len(text):3d} символов → {len(tokens):2d} токенов "
          f"(~{ratio:.1f} символов/токен)")

# English   :  38 символов →  8 токенов (~4.8 символов/токен)
# Русский   :  43 символов → 11 токенов (~3.9 символов/токен)
# Python    :  52 символов → 18 токенов (~2.9 символов/токен)
# JSON      :  49 символов → 18 токенов (~2.7 символов/токен)
```

!!! warning "Русский текст дороже английского"
    Английский текст кодируется эффективнее (~4-5 символов/токен), потому что токенизаторы обучены
    преимущественно на английском корпусе. Русский — ~3-4 символа/токен. Китайский — ~1-2.
    Это значит: **тот же текст на русском стоит в 1.5-2 раза больше** при использовании LLM API.

### Контекстное окно

«128K контекст» означает 128 000 **токенов**, не символов:

```python
# Сколько текста помещается в 128K контекст?
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

# Приблизительно:
# Английский: 128K токенов ≈ 500K символов ≈ 96K слов ≈ 350 страниц
# Русский:    128K токенов ≈ 400K символов ≈ 65K слов ≈ 250 страниц
# Код:        128K токенов ≈ 300K символов ≈ 10K строк кода
```

### Влияние на качество

Токенизация определяет, как модель «видит» текст:

```python
enc = tiktoken.encoding_for_model("gpt-4o")

# Частое слово → один токен (модель «знает» его целиком)
print(enc.encode("function"))   # [1857]         — 1 токен

# Редкое слово → несколько токенов (модель собирает по частям)
print(enc.encode("дефрагментация"))  # [несколько]  — 3-5 токенов

# Опечатка → непредсказуемая токенизация
print(enc.encode("functiom"))   # [func, ti, om]  — 3 токена
print(enc.encode("function"))   # [function]      — 1 токен
# Модель видит опечатку совсем иначе!
```

---

## 50.5 Byte-level BPE: от байтов к токенам

### Проблема с символами

Классический BPE работает с символами, но Unicode содержит ~150 000 символов. Если каждый — отдельный начальный токен, словарь раздувается.

### Решение: начинаем с байтов

GPT-2 и последующие модели используют **byte-level BPE**: начальный словарь — 256 байтов, а не символы. Любой текст на любом языке — это просто последовательность байтов:

```
Текст:     "Файл"
UTF-8:     [0xD0, 0xA4, 0xD0, 0xB0, 0xD0, 0xB9, 0xD0, 0xBB]
Byte BPE:  [Ф, а, й, л]  ← байты объединены в знакомые подпоследовательности
```

Преимущества:
- **Нет OOV** (out-of-vocabulary): любой байт = валидный токен
- Компактный базовый словарь: 256 vs 150 000
- Одна модель для всех языков и бинарных данных

### Byte-fallback в SentencePiece

SentencePiece (LLaMA) использует гибридный подход: символы + байт-fallback для неизвестных:

```
Известные символы → токены
Неизвестный символ → <0xD0> <0xA4>  (UTF-8 байты как токены)
```

---

## 50.6 WordPiece и Unigram — альтернативы BPE

### WordPiece (BERT, DistilBERT)

Похож на BPE, но при слиянии выбирает пару, максимизирующую **likelihood** корпуса:

```
Текст:   "tokenization"
Токены:  ["token", "##ization"]
          ^^^^      ^^ = продолжение слова

# "##" означает, что токен — продолжение предыдущего (не начало слова)
```

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
tokens = tokenizer.tokenize("tokenization is useful")
print(tokens)
# ['token', '##ization', 'is', 'useful']

ids = tokenizer.encode("tokenization is useful")
print(ids)
# [101, 19204, 6590, 2003, 6179, 102]
#  ^^^                             ^^^
#  [CLS]                          [SEP]  — специальные токены BERT
```

### Unigram (SentencePiece)

Обратный подход: начинает с **большого** словаря и **удаляет** наименее полезные токены:

1. Создать огромный словарь (все подстроки до длины N)
2. Для каждого токена вычислить вклад в likelihood корпуса
3. Удалить 10-20% наименее полезных токенов
4. Повторять, пока словарь не уменьшится до нужного размера

```python
# Unigram даёт вероятностную сегментацию:
# Один текст может быть разбит несколькими способами
"unrelated" → ["un", "related"]      p = 0.7
             → ["unrel", "ated"]     p = 0.2
             → ["u", "n", "related"] p = 0.1
# Выбирается разбиение с максимальной вероятностью
```

### Сравнение алгоритмов

| | BPE | WordPiece | Unigram |
|---|---|---|---|
| Направление | bottom-up (слияние) | bottom-up (слияние) | top-down (удаление) |
| Критерий | Частота пары | Likelihood | Likelihood |
| Детерминизм | Да | Да | Вероятностный |
| Используется в | GPT, LLaMA, Mistral | BERT, DistilBERT | T5, mBART, ALBERT |
| Маркер продолжения | Нет (пробел = часть токена) | `##` | `▁` (начало слова) |

---

## 50.7 Специальные токены

У каждого токенизатора есть **специальные токены** — метаданные, невидимые пользователю:

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

# Специальные токены GPT
special = {
    "<|endoftext|>":  200018,   # Конец текста
    "<|im_start|>":   200019,   # Начало сообщения
    "<|im_end|>":     200020,   # Конец сообщения
}

# Как выглядит чат для модели:
# <|im_start|>system
# You are a helpful assistant.<|im_end|>
# <|im_start|>user
# Что такое файл?<|im_end|>
# <|im_start|>assistant
```

```python
# BERT
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("bert-base-uncased")

print(tok.special_tokens_map)
# {
#   'unk_token': '[UNK]',     # Неизвестный токен
#   'sep_token': '[SEP]',     # Разделитель предложений
#   'pad_token': '[PAD]',     # Заполнитель (выравнивание длины)
#   'cls_token': '[CLS]',     # Начало последовательности
#   'mask_token': '[MASK]'    # Маскированный токен (для обучения)
# }
```

---

## 50.8 Токенизация и файлы

### Чтение файла для LLM

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

# Посчитать токены в файле
with open("document.txt", "r", encoding="utf-8") as f:
    text = f.read()

tokens = enc.encode(text)
print(f"Файл: {len(text)} символов, {len(tokens)} токенов")
print(f"Средняя длина токена: {len(text)/len(tokens):.1f} символов")

# Проверить, помещается ли в контекст
MAX_CONTEXT = 128_000
if len(tokens) > MAX_CONTEXT:
    print(f"⚠ Файл не помещается! Нужно {len(tokens) - MAX_CONTEXT} токенов отрезать")
```

### Разбиение длинных файлов (chunking)

Для RAG (Retrieval-Augmented Generation) файлы разбивают на чанки по токенам:

```python
def chunk_by_tokens(text: str, enc, chunk_size: int = 512,
                    overlap: int = 50) -> list[str]:
    """Разбить текст на чанки по токенам с перекрытием."""
    tokens = enc.encode(text)
    chunks = []

    for i in range(0, len(tokens), chunk_size - overlap):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)

    return chunks

enc = tiktoken.encoding_for_model("gpt-4o")
with open("large_document.txt") as f:
    text = f.read()

chunks = chunk_by_tokens(text, enc, chunk_size=512, overlap=50)
print(f"{len(chunks)} чанков по ~512 токенов")
```

### Разные форматы — разная эффективность

```python
import tiktoken, json, csv, io

enc = tiktoken.encoding_for_model("gpt-4o")

# Одни и те же данные в разных форматах
data = [
    {"name": "report.pdf", "size": 1048576, "type": "application/pdf"},
    {"name": "photo.jpg", "size": 2097152, "type": "image/jpeg"},
    {"name": "data.csv", "size": 524288, "type": "text/csv"},
]

# JSON
json_text = json.dumps(data, indent=2)
json_tokens = len(enc.encode(json_text))

# CSV
csv_buf = io.StringIO()
w = csv.DictWriter(csv_buf, fieldnames=["name", "size", "type"])
w.writeheader()
w.writerows(data)
csv_text = csv_buf.getvalue()
csv_tokens = len(enc.encode(csv_text))

# Markdown table
md_text = "| name | size | type |\n|---|---|---|\n"
for d in data:
    md_text += f"| {d['name']} | {d['size']} | {d['type']} |\n"
md_tokens = len(enc.encode(md_text))

print(f"JSON:     {json_tokens:3d} токенов ({len(json_text):3d} символов)")
print(f"CSV:      {csv_tokens:3d} токенов ({len(csv_text):3d} символов)")
print(f"Markdown: {md_tokens:3d} токенов ({len(md_text):3d} символов)")
# CSV обычно эффективнее JSON на 20-40% по токенам!
```

!!! tip "Практический совет"
    При работе с LLM API предпочитайте **компактные форматы** (CSV, TSV) вместо JSON для табличных данных — это экономит токены и деньги. Убирайте лишние пробелы, переносы, комментарии.

---

## 50.9 Проблемы токенизации

### Проблема с арифметикой

```python
enc = tiktoken.encoding_for_model("gpt-4o")

# Числа токенизируются непредсказуемо:
for n in ["123", "1234", "12345", "123456"]:
    tokens = enc.encode(n)
    parts = [enc.decode([t]) for t in tokens]
    print(f"{n:>8s} → {parts}")

#      123 → ['123']           — 1 токен
#     1234 → ['1234']          — 1 токен
#    12345 → ['123', '45']     — 2 токена! Граница внутри числа
#   123456 → ['123', '456']    — 2 токена
# Модель «видит» 12345 как два отдельных числа
```

### Проблема с пробелами и форматированием

```python
# Пробел В НАЧАЛЕ слова — часть токена!
enc = tiktoken.encoding_for_model("gpt-4o")

print(enc.encode("hello"))    # [15339]
print(enc.encode(" hello"))   # [24748]     ← ДРУГОЙ токен!
print(enc.encode("  hello"))  # [256, 24748] ← пробел + " hello"

# Поэтому " the" и "the" — разные токены
# Модель знает, что " the" обычно идёт после пробела
```

### Проблема с не-латинскими языками

```python
# Английский — очень эффективен
en = "The quick brown fox jumps over the lazy dog"
# Русский — менее эффективен
ru = "Быстрая коричневая лиса прыгает через ленивую собаку"

en_tokens = len(enc.encode(en))
ru_tokens = len(enc.encode(ru))
print(f"EN: {en_tokens} токенов, {len(en)/en_tokens:.1f} chars/token")
print(f"RU: {ru_tokens} токенов, {len(ru)/ru_tokens:.1f} chars/token")
# EN: ~10 токенов, ~4.4 chars/token
# RU: ~15 токенов, ~3.5 chars/token
```

### Проблема с кодом

```python
# Код токенизируется по-разному в зависимости от языка
code_python = "def read_file(path: str) -> bytes:"
code_rust = "fn read_file(path: &str) -> Vec<u8> {"

py_tokens = len(enc.encode(code_python))
rs_tokens = len(enc.encode(code_rust))
print(f"Python: {py_tokens} токенов")
print(f"Rust:   {rs_tokens} токенов")
# Python обычно эффективнее — больше Python-кода в обучающих данных
```

---

## 50.10 Обучение своего токенизатора

Когда стандартные токенизаторы неэффективны (специализированный домен, язык), можно обучить свой:

```python
# Вариант 1: SentencePiece (Google)
import sentencepiece as spm

spm.SentencePieceTrainer.train(
    input='my_corpus.txt',         # Ваш корпус
    model_prefix='my_tokenizer',
    vocab_size=32000,
    model_type='bpe',               # 'bpe' или 'unigram'
    character_coverage=0.9995,       # 99.95% символов покрыто
    num_threads=8,
    max_sentence_length=16384,
    byte_fallback=True,              # Неизвестные → байты
    split_digits=True,               # Цифры — отдельные токены
    allow_whitespace_only_pieces=True
)

# Результат: my_tokenizer.model + my_tokenizer.vocab
sp = spm.SentencePieceProcessor(model_file='my_tokenizer.model')
print(sp.encode("Файловая система ext4", out_type=str))
```

```python
# Вариант 2: tokenizers (Hugging Face) — быстрее
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel

tokenizer = Tokenizer(BPE())
tokenizer.pre_tokenizer = ByteLevel()

trainer = BpeTrainer(
    vocab_size=32000,
    special_tokens=["<pad>", "<unk>", "<s>", "</s>"]
)

tokenizer.train(files=["corpus.txt"], trainer=trainer)
tokenizer.save("my_tokenizer.json")

# Использование
output = tokenizer.encode("Файловая система ext4")
print(output.tokens)
```

---

## 50.11 Визуализация токенизации

### Онлайн-инструменты

- **[tiktokenizer.vercel.app](https://tiktokenizer.vercel.app)** — интерактивная визуализация tiktoken
- **[platform.openai.com/tokenizer](https://platform.openai.com/tokenizer)** — официальный токенизатор OpenAI

### Своя визуализация

```python
import tiktoken

def visualize_tokens(text: str, model: str = "gpt-4o"):
    """Визуализация токенизации с цветами."""
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)

    colors = [
        '\033[42m', '\033[43m', '\033[44m',
        '\033[45m', '\033[46m', '\033[41m'
    ]
    reset = '\033[0m'

    result = ""
    for i, token_id in enumerate(tokens):
        token_text = enc.decode([token_id])
        color = colors[i % len(colors)]
        # Заменяем пробелы на видимый символ для наглядности
        display = token_text.replace(' ', '␣')
        result += f"{color}{display}{reset}"

    print(f"Текст:   {text}")
    print(f"Токены:  {result}")
    print(f"Кол-во:  {len(tokens)} токенов")
    print(f"ID:      {tokens}")
    print()

visualize_tokens("Файловая система управляет файлами")
visualize_tokens("def open(path: str) -> IO:")
visualize_tokens("Hello, world! 你好世界")
```

---

## 50.12 Полный путь: от файла до нейросети

```
                        Файл на диске
                             │
                    ┌────────┴────────┐
                    │   bytes on disk  │ ← Глава 11
                    └────────┬────────┘
                             │  decode (UTF-8)
                    ┌────────┴────────┐
                    │   Unicode text   │ ← Глава 14
                    └────────┬────────┘
                             │  tokenize (BPE)
                    ┌────────┴────────┐
                    │   token IDs      │ ← Эта глава
                    │  [41084, 11209]  │
                    └────────┬────────┘
                             │  embedding lookup
                    ┌────────┴────────┐
                    │   vectors        │ ← Нейросеть
                    │  [0.12, -0.34,  │
                    │   0.56, ...]     │
                    └────────┬────────┘
                             │  transformer layers
                    ┌────────┴────────┐
                    │   output logits  │
                    │  → next token    │
                    └─────────────────┘
```

Токенизация — это **интерфейс** между миром файлов/текста и миром нейросетей. Файл → байты → текст → токены → векторы → внимание → предсказание.

---

## 50.13 Упражнения

!!! example "Практика"
    **Задание 1.** Установите `tiktoken` и посчитайте количество токенов в нескольких файлах вашего проекта. Какие файлы самые «дорогие» для LLM?
    ```bash
    pip install tiktoken
    ```

    **Задание 2.** Сравните токенизацию одного и того же текста на русском и английском (tiktoken, модель `gpt-4o`). Во сколько раз русский «дороже»?

    **Задание 3.** Реализуйте BPE с нуля (раздел 50.2). Обучите на тексте нескольких страниц книги. Сравните результат с tiktoken.

    **Задание 4.** Напишите утилиту, которая считает стоимость обработки файла через GPT-4o API:
    ```python
    # Формула: input_tokens * $2.50/1M + output_tokens * $10.00/1M
    ```

    **Задание 5.** Сравните «стоимость» одних и тех же данных в JSON vs CSV vs Markdown-таблице (раздел 50.8). Какой формат самый токен-эффективный?

    **Задание 6.** Обучите свой SentencePiece-токенизатор на русскоязычном корпусе (32K словарь). Сравните эффективность на русском тексте с tiktoken (должен быть эффективнее!).

---

## Troubleshooting: типичные проблемы Части V

!!! bug "Disk full, но файлы занимают меньше, чем показывает `df`"
    Возможные причины:
    
    - **Зарезервированное пространство**: ext4 резервирует 5% для root. Уменьшить: `tune2fs -m 1 /dev/sdX`.
    - **Удалённые, но открытые файлы**: `lsof +L1` — процесс держит удалённый файл.
    - **Снапшоты**: ZFS/Btrfs снапшоты удерживают старые данные. `zfs list -t snapshot` / `btrfs subvolume list /`.

!!! bug "Файловая система read-only после ошибки"
    ```bash
    # Проверить состояние:
    mount | grep /dev/sdX
    dmesg | tail -20  # ищите "I/O error" или "remounting read-only"
    
    # Восстановить (ОТМОНТИРУЙТЕ СНАЧАЛА!):
    umount /dev/sdX
    fsck -y /dev/sdX
    mount /dev/sdX /mnt
    ```
    Ядро автоматически переключает ФС в read-only при обнаружении ошибок. Это защита от дальнейшего повреждения данных.

!!! bug "SMART предупреждение: диск скоро выйдет из строя"
    ```bash
    # Проверить здоровье диска:
    smartctl -H /dev/sdX
    smartctl -A /dev/sdX | grep -E 'Reallocated|Pending|Uncorrectable'
    
    # Критические атрибуты:
    # Reallocated_Sector_Ct > 0  → диск переназначает сектора
    # Current_Pending_Sector > 0 → есть нечитаемые сектора
    ```
    **Немедленно создайте резервную копию**. SMART предупреждения — серьёзный сигнал.

!!! bug "NFS: stale file handle / permission denied"
    ```bash
    # Stale handle — сервер перезагрузился или экспорт изменился:
    umount -f /mnt/nfs
    mount -t nfs server:/share /mnt/nfs
    
    # Permission denied — проверьте:
    # 1. /etc/exports на сервере (IP-адрес клиента разрешён?)
    # 2. UID/GID совпадают на клиенте и сервере
    # 3. root_squash (root на клиенте → nobody на сервере)
    ```

!!! success "Книга завершена!"
    Вы прошли путь от **определения файла** до **токенизации для LLM** — через кодировки, форматы, инструменты и инфраструктуру хранения.
    
    → [Глоссарий](../../glossary.md) · [О проекте](../../about.md)
