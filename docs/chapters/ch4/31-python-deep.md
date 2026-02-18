---
title: Работа с файлами в Python — pathlib, io, mmap
description: Python глубокое погружение в файловые операции. pathlib vs os.path, модуль io, кодировки, буферизация, memory-mapped files.
---

# Глава 31. Python: глубокое погружение в файловые операции

## Введение

Python — один из самых популярных языков для работы с данными. В предыдущей главе мы рассмотрели итераторы и генераторы. Теперь погрузимся глубже: модули `pathlib`, `io`, работа с кодировками, memory-mapped files и лучшие практики.

---

## 31.1 Пути: pathlib vs os.path

### Старый способ: os.path

```python
import os

# Конкатенация путей
path = os.path.join("data", "2024", "sales.csv")

# Получение частей
dirname = os.path.dirname(path)    # "data/2024"
basename = os.path.basename(path)  # "sales.csv"
name, ext = os.path.splitext(basename)  # ("sales", ".csv")

# Проверки
os.path.exists(path)
os.path.isfile(path)
os.path.isdir(dirname)
```

### Современный способ: pathlib

```python
from pathlib import Path

# Конкатенация через /
path = Path("data") / "2024" / "sales.csv"

# Части пути — атрибуты
path.parent      # Path("data/2024")
path.name        # "sales.csv"
path.stem        # "sales"
path.suffix      # ".csv"
path.suffixes    # [".csv"] или [".tar", ".gz"]

# Проверки
path.exists()
path.is_file()
path.is_dir()

# Удобные методы
path.read_text(encoding="utf-8")
path.write_text("content", encoding="utf-8")
path.read_bytes()
path.write_bytes(b"content")
```

### Сравнение

| Задача | os.path | pathlib |
|--------|---------|---------|
| Соединить пути | `os.path.join(a, b)` | `Path(a) / b` |
| Имя файла | `os.path.basename(p)` | `path.name` |
| Расширение | `os.path.splitext(p)[1]` | `path.suffix` |
| Существует? | `os.path.exists(p)` | `path.exists()` |
| Прочитать | `open(p).read()` | `path.read_text()` |

!!! tip "Рекомендация"
    Используйте `pathlib` для нового кода. Он более читаемый и объектно-ориентированный. `os.path` оставьте для legacy-кода.

---

## 31.2 Открытие файлов: режимы и опции

### Режимы открытия

```python
# Основные режимы
open(path, "r")   # Чтение (по умолчанию)
open(path, "w")   # Запись (перезаписывает!)
open(path, "a")   # Добавление в конец
open(path, "x")   # Эксклюзивное создание (ошибка если существует)

# Модификаторы
open(path, "rb")  # Бинарный режим
open(path, "r+")  # Чтение и запись
open(path, "w+")  # Запись и чтение (создаёт/перезаписывает)
```

### Текст vs бинарный режим

```python
# Текстовый режим
with open("file.txt", "r", encoding="utf-8") as f:
    text = f.read()      # str
    lines = f.readlines() # List[str]

# Бинарный режим  
with open("file.bin", "rb") as f:
    data = f.read()      # bytes
    chunk = f.read(1024) # Прочитать N байт
```

!!! warning "Всегда указывайте encoding"
    ```python
    # ПЛОХО — зависит от системной локали
    open("file.txt", "r")
    
    # ХОРОШО — явная кодировка
    open("file.txt", "r", encoding="utf-8")
    ```

### Буферизация

```python
# buffering параметр
open(path, "r", buffering=1)      # Построчная (только текст)
open(path, "rb", buffering=0)     # Без буфера (только бинарный)
open(path, "r", buffering=8192)   # Буфер 8KB
open(path, "r", buffering=-1)     # Системный буфер (по умолчанию)
```

### Обработка ошибок кодировки

```python
# errors параметр
open(path, encoding="utf-8", errors="strict")   # Исключение (по умолчанию)
open(path, encoding="utf-8", errors="ignore")   # Пропустить
open(path, encoding="utf-8", errors="replace")  # Заменить на �
open(path, encoding="utf-8", errors="backslashreplace")  # \xNN
```

### Перевод строк

```python
# newline параметр
open(path, newline=None)   # Универсальный (по умолчанию)
open(path, newline="")     # Не преобразовывать
open(path, newline="\n")   # Только \n
open(path, newline="\r\n") # Только \r\n
```

### print() в файл

```python
# print() умеет писать в любой файловый объект
with open("output.txt", "w", encoding="utf-8") as f:
    print("Hello", file=f)
    print("World", file=f)
    print(1, 2, 3, sep=", ", file=f)  # "1, 2, 3"

# Удобно для логирования
import sys
print("Error!", file=sys.stderr)

# В StringIO
from io import StringIO
buffer = StringIO()
print("captured", file=buffer)
result = buffer.getvalue()  # "captured\n"
```

!!! tip "Когда использовать"
    `print(file=f)` удобен для простого вывода с автоматическим `\n`.  
    `f.write()` — когда нужен полный контроль над записью.

---

## 31.3 Context managers: with statement

### Зачем нужен with

```python
# БЕЗ with — нужно закрывать вручную
f = open("file.txt")
try:
    data = f.read()
finally:
    f.close()

# С with — закрытие автоматическое
with open("file.txt") as f:
    data = f.read()
# f.close() вызывается автоматически, даже при исключении
```

### Несколько файлов

```python
# Один with для нескольких файлов
with open("input.txt") as fin, open("output.txt", "w") as fout:
    for line in fin:
        fout.write(line.upper())

# Python 3.10+: скобки для многострочности
with (
    open("input.txt") as fin,
    open("output.txt", "w") as fout,
    open("log.txt", "a") as flog,
):
    ...
```

### Свой context manager

```python
from contextlib import contextmanager

@contextmanager
def open_with_backup(path, mode="w"):
    """Создаёт бэкап перед записью."""
    from pathlib import Path
    import shutil
    
    p = Path(path)
    backup = None
    
    if p.exists() and "w" in mode:
        backup = p.with_suffix(p.suffix + ".bak")
        shutil.copy(p, backup)
    
    f = open(path, mode)
    try:
        yield f
    except Exception:
        # При ошибке восстанавливаем
        if backup:
            shutil.move(backup, p)
        raise
    finally:
        f.close()
        if backup and backup.exists():
            backup.unlink()
```

---

## 31.4 Потоковая обработка больших файлов

### Построчное чтение

```python
# Файл — итератор строк
with open("huge.log", encoding="utf-8") as f:
    for line in f:
        process(line)  # Одна строка в памяти
```

### Чтение чанками (бинарный)

```python
def process_in_chunks(path, chunk_size=1024*1024):
    """Обрабатывает файл по 1MB."""
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

for chunk in process_in_chunks("huge.bin"):
    # chunk — bytes длиной до chunk_size
    hash_update(chunk)
```

### iter() с sentinel

```python
# Альтернативный способ чтения чанками
with open("file.bin", "rb") as f:
    for chunk in iter(lambda: f.read(8192), b""):
        process(chunk)
```

### Параллельная обработка строк

```python
from concurrent.futures import ProcessPoolExecutor
import itertools

def process_batch(lines):
    """Обрабатывает пачку строк."""
    return [transform(line) for line in lines]

def batched(iterable, n):
    """Группирует по n элементов."""
    it = iter(iterable)
    while batch := list(itertools.islice(it, n)):
        yield batch

with open("huge.txt") as f:
    with ProcessPoolExecutor() as executor:
        for result in executor.map(process_batch, batched(f, 10000)):
            for item in result:
                print(item)
```

---

## 31.5 Memory-mapped files (mmap)

### Что такое mmap

Memory-mapped файл отображается напрямую в память, позволяя работать с файлом как с байтовым массивом без явного чтения/записи.

```python
import mmap

# Чтение через mmap
with open("data.bin", "rb") as f:
    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        # mm ведёт себя как bytes
        print(mm[0:10])          # Первые 10 байт
        print(mm.find(b"pattern"))  # Поиск паттерна
        
        # Можно slice'ить
        chunk = mm[1000:2000]
```

### Запись через mmap

```python
# Изменение файла на месте
with open("data.bin", "r+b") as f:
    with mmap.mmap(f.fileno(), 0) as mm:
        # Заменить байты
        mm[0:5] = b"HELLO"
        
        # Поиск и замена
        pos = mm.find(b"old")
        if pos != -1:
            mm[pos:pos+3] = b"new"
```

### Когда использовать mmap

| Сценарий | mmap подходит? |
|----------|---------------|
| Случайный доступ к большому файлу | ✅ Да |
| Последовательное чтение | ❌ Обычный read() быстрее |
| Файл больше RAM | ⚠️ Осторожно с 32-bit |
| Изменение файла на месте | ✅ Да |
| Несколько процессов читают файл | ✅ Да (shared memory) |

---

## 31.6 Модуль io

### Файловые дескрипторы (низкоуровневый доступ)

Каждый открытый файл в Python имеет числовой дескриптор — тот самый, что использует ОС.

```python
import os

# Получить дескриптор из файлового объекта
with open("file.txt", "r") as f:
    fd = f.fileno()  # Числовой дескриптор (например, 3)
    print(f"Descriptor: {fd}")

# Стандартные дескрипторы
import sys
print(sys.stdin.fileno())   # 0
print(sys.stdout.fileno())  # 1  
print(sys.stderr.fileno())  # 2
```

### Низкоуровневые операции (os модуль)

```python
import os

# Открытие через os.open() — возвращает дескриптор
fd = os.open("file.txt", os.O_RDONLY)
try:
    data = os.read(fd, 100)  # Читаем до 100 байт
    print(data)
finally:
    os.close(fd)

# Запись через дескриптор
fd = os.open("out.txt", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
os.write(fd, b"Hello\n")
os.close(fd)
```

### os.fdopen(): дескриптор → файловый объект

```python
import os

# Создаём дескриптор низкоуровнево
fd = os.open("file.txt", os.O_RDWR | os.O_CREAT)

# Оборачиваем в файловый объект Python
with os.fdopen(fd, "r+", encoding="utf-8") as f:
    f.write("Hello")  # Можем использовать методы файла
    f.seek(0)
    print(f.read())
# fd автоматически закрыт при выходе из with
```

!!! warning "fd закрывается вместе с файлом"
    После `os.fdopen(fd, ...)` дескриптор принадлежит файловому объекту.  
    При закрытии файла дескриптор тоже закрывается.

### Когда нужны дескрипторы?

| Задача | Решение |
|--------|---------|
| Передать файл в subprocess | `subprocess.run(..., stdin=fd)` |
| Memory-mapped files | `mmap.mmap(f.fileno(), ...)` |
| Дублирование потоков | `os.dup()`, `os.dup2()` |
| Атомарное создание файла | `os.open(..., O_CREAT \| O_EXCL)` |
| Неблокирующий I/O | `fcntl.fcntl(fd, F_SETFL, O_NONBLOCK)` |

### StringIO и BytesIO

```python
from io import StringIO, BytesIO

# StringIO — файлоподобный объект для строк
sio = StringIO()
sio.write("Hello\n")
sio.write("World\n")
print(sio.getvalue())  # "Hello\nWorld\n"

# Использование как файла
sio.seek(0)
for line in sio:
    print(line)

# BytesIO — для байт
bio = BytesIO()
bio.write(b"\x00\x01\x02")
data = bio.getvalue()
```

### Применение: тестирование

```python
def process_file(f):
    """Функция принимает file-like object."""
    return sum(1 for line in f if "ERROR" in line)

# В тестах — используем StringIO
from io import StringIO

def test_process_file():
    fake_file = StringIO("OK\nERROR: fail\nOK\nERROR: crash\n")
    assert process_file(fake_file) == 2
```

### TextIOWrapper

```python
from io import TextIOWrapper
import sys

# Перенастройка stdout с другой кодировкой
sys.stdout = TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Чтение бинарного потока как текста
with open("file.bin", "rb") as f:
    text_stream = TextIOWrapper(f, encoding="utf-8")
    for line in text_stream:
        print(line)
```

---

## 31.7 Работа с кодировками

### Определение кодировки

```python
# Библиотека chardet
import chardet

with open("mystery.txt", "rb") as f:
    raw = f.read(10000)
result = chardet.detect(raw)
# {'encoding': 'utf-8', 'confidence': 0.99, 'language': ''}

with open("mystery.txt", encoding=result["encoding"]) as f:
    text = f.read()
```

### Перекодирование файла

```python
def convert_encoding(src, dst, from_enc, to_enc):
    """Конвертирует файл из одной кодировки в другую."""
    with open(src, encoding=from_enc) as fin:
        with open(dst, "w", encoding=to_enc) as fout:
            for line in fin:
                fout.write(line)

convert_encoding("old.txt", "new.txt", "cp1251", "utf-8")
```

### BOM (Byte Order Mark)

```python
# UTF-8 с BOM
with open("file.txt", "w", encoding="utf-8-sig") as f:
    f.write("Hello")

# Чтение файла с BOM
with open("file.txt", encoding="utf-8-sig") as f:
    text = f.read()  # BOM автоматически удаляется
```

---

## 31.8 Временные файлы

```python
import tempfile

# Временный файл (автоудаление)
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=True) as f:
    f.write("temporary data")
    f.flush()
    # Файл существует пока открыт
    print(f.name)  # /tmp/tmpXXXXXX.txt
# Файл удалён

# Временная директория
with tempfile.TemporaryDirectory() as tmpdir:
    path = Path(tmpdir) / "data.txt"
    path.write_text("hello")
# Директория и содержимое удалены
```

---

## 31.9 Атомарная запись

```python
import tempfile
import os
from pathlib import Path

def atomic_write(path, content, encoding="utf-8"):
    """Атомарная запись: либо полностью, либо никак."""
    path = Path(path)
    
    # Пишем во временный файл в той же директории
    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=".tmp_",
        suffix=path.suffix
    )
    
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(content)
        # Атомарное переименование
        os.replace(tmp_path, path)
    except:
        os.unlink(tmp_path)
        raise
```

---

## 31.10 Практические рецепты

### Подсчёт строк эффективно

```python
def count_lines(path):
    """Быстрый подсчёт строк."""
    with open(path, "rb") as f:
        return sum(1 for _ in f)

# Ещё быстрее с буфером
def count_lines_fast(path, buffer_size=1024*1024):
    with open(path, "rb") as f:
        return sum(chunk.count(b"\n") for chunk in iter(lambda: f.read(buffer_size), b""))
```

### Tail -f на Python

```python
import time

def tail_f(path):
    """Следит за файлом как tail -f."""
    with open(path) as f:
        f.seek(0, 2)  # В конец файла
        while True:
            line = f.readline()
            if line:
                yield line.rstrip()
            else:
                time.sleep(0.1)

for line in tail_f("/var/log/syslog"):
    print(line)
```

### Чтение CSV потоково

```python
import csv

def process_large_csv(path):
    """Обрабатывает большой CSV построчно."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row  # Один словарь за раз

for row in process_large_csv("huge.csv"):
    print(row["name"], row["value"])
```

---

## 31.8 Встроенные хранилища: dbm и shelve

Python имеет **встроенные** модули для файлового хранения «ключ-значение» — без установки внешних зависимостей.

### dbm — простой key-value store

```python
import dbm

# Создание/открытие БД (файл data.db + индекс)
with dbm.open("mydata", "c") as db:  # 'c' = создать если нет
    # Запись (ключи и значения — bytes или str)
    db["user:1"] = "Alice"
    db["user:2"] = "Bob"
    db["counter"] = "42"
    
    # Чтение
    print(db["user:1"])     # b'Alice'
    print("user:3" in db)   # False
    
    # Итерация
    for key in db.keys():
        print(key, db[key])
```

**Ограничения dbm**: ключи и значения — только строки/байты. Нет типизации, нет вложенных структур.

### shelve — «полка» для Python-объектов

`shelve` оборачивает `dbm`, добавляя сериализацию через `pickle`:

```python
import shelve

with shelve.open("myshelf") as shelf:
    # Можно хранить ЛЮБЫЕ Python-объекты
    shelf["config"] = {"debug": True, "version": "1.2.3"}
    shelf["users"] = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
    shelf["counter"] = 42
    
    # Чтение
    config = shelf["config"]
    print(config["debug"])  # True
    
    # Внимание: мутация вложенных объектов
    # shelf["users"].append({"name": "Charlie"})  # ❌ НЕ сохранится!
    users = shelf["users"]
    users.append({"name": "Charlie", "age": 28})
    shelf["users"] = users  # ✅ Нужно перезаписать
```

### Когда использовать

| Задача | dbm | shelve | SQLite | JSON-файл |
|--------|-----|--------|--------|-----------|
| Простой кэш | ✅ | ✅ | Избыточно | ✅ |
| Сложные объекты | ❌ | ✅ | ❌ | ⚠️ (нужна сериализация) |
| Конкурентный доступ | ❌ | ❌ | ✅ | ❌ |
| Запросы/фильтрация | ❌ | ❌ | ✅ | ❌ |
| Переносимость | ⚠️ | ❌ (pickle) | ✅ | ✅ |

!!! warning "Безопасность shelve"
    `shelve` использует `pickle`, который **исполняет произвольный код** при десериализации. Никогда не открывайте shelf-файлы из **недоверенных источников**.

---

## Резюме

| Модуль | Назначение |
|--------|-----------|
| `pathlib` | Работа с путями (современный способ) |
| `io` | StringIO, BytesIO, TextIOWrapper |
| `mmap` | Memory-mapped файлы |
| `tempfile` | Временные файлы и директории |
| `shutil` | Высокоуровневые операции (copy, move) |
| `os` | Низкоуровневые операции |


??? question "Упражнения"
    **Задание 1.** Напишите функцию `atomic_write(path, data)`, которая записывает данные во временный файл и атомарно заменяет оригинал через `os.replace()`.
    
    **Задание 2.** Откройте большой файл через `mmap` и найдите в нём подстроку без загрузки в память. Сравните скорость с обычным `f.read().find()`.
    
    **Задание 3.** Используя `pathlib`, напишите скрипт, который находит все дубликаты файлов в директории (по MD5-хешу) и выводит пары.

!!! tip "Следующая глава"
    Теперь мы знаем Python досконально. Время познакомиться с современными инструментами для работы с данными → [Современные инструменты](32-modern-tools.md)
