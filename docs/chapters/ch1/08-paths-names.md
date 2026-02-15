# Глава 8. Пути и имена файлов

## Введение

Мы разобрались с устройством файловой системы, метаданными, правами доступа. Теперь поговорим о том, **как обращаться к файлам** — о путях и именах.

Казалось бы, простая тема, но здесь много подводных камней: разделители, регистр, Unicode, зарезервированные имена...

!!! note "Путь ≠ имя файла"
    - **Имя файла** (filename, basename) — последний компонент пути: `report.txt`
    - **Путь** (path, pathname) — полный адрес файла: `/home/user/docs/report.txt`
    - **Расширение** (extension) — часть имени после последней точки: `.txt`

---

## 8.1 Абсолютные и относительные пути (Absolute vs Relative)

### Абсолютный путь (Absolute Path)

Начинается от **корня** файловой системы:

```bash
# Unix/Linux/macOS
/home/user/documents/report.txt
/etc/nginx/nginx.conf
/var/log/syslog

# Windows
C:\Users\Alice\Documents\report.txt
D:\Projects\app\config.ini
\\server\share\file.txt    # UNC path (сетевой)
```

### Относительный путь

Начинается от **текущей директории**:

```bash
$ pwd
/home/user

# Относительные пути от /home/user:
documents/report.txt      # = /home/user/documents/report.txt
./script.sh               # = /home/user/script.sh
../alice/file.txt         # = /home/alice/file.txt
../../etc/passwd          # = /etc/passwd
```

### Специальные обозначения

| Символ | Значение | Пример |
|--------|----------|--------|
| `/` | Корень (Unix) | `/etc/passwd` |
| `~` | Домашняя директория | `~/Documents` → `/home/user/Documents` |
| `.` | Текущая директория | `./script.sh` |
| `..` | Родительская директория | `../config` |
| `-` | Предыдущая директория (cd) | `cd -` |

```bash
# ~ раскрывается shell'ом
$ echo ~
/home/user

$ echo ~alice
/home/alice

# В программах ~ не работает автоматически!
$ python -c "print(open('~/file.txt'))"
# FileNotFoundError: No such file or directory: '~/file.txt'

# Нужно раскрывать явно
$ python -c "import os; print(os.path.expanduser('~/file.txt'))"
/home/user/file.txt
```

---

## 8.2 Разделители путей

### Unix vs Windows

| ОС | Разделитель | Пример |
|----|-------------|--------|
| Unix/Linux/macOS | `/` | `/home/user/file.txt` |
| Windows | `\` | `C:\Users\Alice\file.txt` |
| Windows (альтернатива) | `/` | `C:/Users/Alice/file.txt` |

```python
import os

# os.sep — разделитель текущей ОС
print(os.sep)  # '/' на Unix, '\\' на Windows

# os.path.join — правильный способ соединять пути
path = os.path.join('home', 'user', 'file.txt')
# Unix: 'home/user/file.txt'
# Windows: 'home\\user\\file.txt'

# pathlib — современный способ (Python 3.4+)
from pathlib import Path
path = Path('home') / 'user' / 'file.txt'
```

### Нормализация путей

```python
import os.path

# Убрать лишние разделители и . / ..
os.path.normpath('/home/user/../alice/./docs//file.txt')
# '/home/alice/docs/file.txt'

# Получить абсолютный путь
os.path.abspath('docs/file.txt')
# '/home/user/docs/file.txt'

# Разрешить symlinks
os.path.realpath('link_to_file')
# '/actual/path/to/file.txt'
```

---

## 8.3 Ограничения имён файлов

### Запрещённые символы

| ОС | Запрещённые символы |
|----|---------------------|
| **Unix/Linux** | `/` и `NUL` (0x00) |
| **Windows** | `< > : " / \ | ? *` и NUL, символы 1-31 |
| **macOS (HFS+/APFS)** | `/` и `:` (двоеточие показывается как `/` в Finder) |

```bash
# Unix позволяет почти всё
$ touch "file with spaces.txt"      # ОК
$ touch "file'with'quotes.txt"      # ОК
$ touch $'file\nwith\nnewlines'     # ОК (!)
$ touch "file:with:colons.txt"      # ОК на Linux, проблема на macOS

# Не работает
$ touch "path/with/slash.txt"       # Ошибка: это путь, а не имя
```

!!! note "ANSI-C Quoting: `$'...'`"
    Синтаксис `$'...'` в Bash — это **ANSI-C Quoting**, позволяющий использовать escape-последовательности:
    ```bash
    $ echo 'hello\nworld'     # Буквально: hello\nworld
    $ echo $'hello\nworld'    # С переносом: hello↵world
    ```
    Так `$'file\nwith\nnewlines'` создаёт файл с **реальными переносами строк** в имени.

### Ограничения длины

| Компонент | Лимит |
|-----------|-------|
| Имя файла (Unix) | 255 байт |
| Имя файла (Windows) | 255 символов UTF-16 |
| Полный путь (Unix) | ~4096 байт (PATH_MAX) |
| Полный путь (Windows) | 260 символов (можно увеличить) |

```bash
# Проверить лимит ФС
$ getconf NAME_MAX /
255

$ getconf PATH_MAX /
4096
```

!!! warning "Байты vs символы"
    В Linux лимит 255 **байт**, не символов! UTF-8 символ может занимать до 4 байт:
    ```bash
    # 255 ASCII символов — ОК
    $ touch $(python3 -c "print('a'*255)")
    
    # 255 эмодзи — ошибка (255×4 = 1020 байт)
    $ touch $(python3 -c "print('😀'*255)")
    touch: cannot touch '😀😀😀...': File name too long
    
    # Максимум ~63 четырёхбайтных символа
    $ touch $(python3 -c "print('😀'*63)")  # ОК
    ```

### Зарезервированные имена (Windows)

Windows имеет исторические зарезервированные имена:

```
CON, PRN, AUX, NUL
COM1, COM2, ..., COM9
LPT1, LPT2, ..., LPT9
```

```powershell
# Эти имена нельзя использовать
PS> New-Item CON.txt
# Ошибка!

# Даже с расширением
PS> New-Item CON.txt.bak
# Ошибка!
```

---

## 8.4 Регистрозависимость

### Сравнение ОС

| ОС / ФС | Регистрозависимость |
|---------|---------------------|
| Linux (ext4, XFS) | ✅ Да (case-sensitive) |
| macOS (APFS default) | ❌ Нет (case-insensitive) |
| macOS (APFS case-sensitive) | ✅ Да |
| Windows (NTFS) | ❌ Нет (case-insensitive) |
| Windows (WSL) | ✅ Да |

```bash
# Linux: разные файлы
$ touch File.txt file.txt FILE.txt
$ ls
File.txt  file.txt  FILE.txt

# macOS/Windows: один файл
$ touch File.txt
$ touch file.txt    # Не создаёт новый файл!
$ ls
File.txt
```

### Проблемы с Git

```bash
# Частая проблема: переименование регистра на macOS/Windows
$ git mv File.txt file.txt
# Может не сработать!

# Решение: двухэтапное переименование
$ git mv File.txt temp.txt
$ git mv temp.txt file.txt
```

---

## 8.5 Unicode в именах файлов

### Кодировки в разных ОС

| ОС | Кодировка имён | Особенности |
|----|----------------|-------------|
| Linux | Байты (обычно UTF-8) | Ядро не проверяет валидность |
| macOS | UTF-8 (NFD) | Автоматическая нормализация |
| Windows | UTF-16 | Внутреннее представление |

### Проблема: имена в Linux — просто байты

```bash
# Linux позволяет невалидный UTF-8
$ touch $'\xff\xfe'    # Невалидная последовательность
$ ls
??

# Python не сможет прочитать
$ python3 -c "import os; print(os.listdir('.'))"
# UnicodeDecodeError или surrogateescape
```

```python
# Работа с "битыми" именами в Python
import os

# surrogateescape для обработки невалидного UTF-8
for name in os.listdir('.'):
    # name может содержать surrogate characters
    print(name.encode('utf-8', 'surrogateescape'))
```

### Нормализация Unicode (NFC vs NFD)

Один и тот же символ может быть представлен по-разному:

```python
import unicodedata

# "é" — два способа представления
nfc = "é"                    # U+00E9 (1 codepoint)
nfd = "e\u0301"              # U+0065 + U+0301 (2 codepoints)

print(len(nfc))  # 1
print(len(nfd))  # 2
print(nfc == nfd)  # False!

# Но выглядят одинаково
print(nfc, nfd)  # é é

# Нормализация
unicodedata.normalize('NFC', nfd) == nfc  # True
```

!!! warning "macOS автоматически нормализует в NFD"
    ```bash
    # На macOS
    $ touch "café"
    $ python3 -c "import os; print([repr(n) for n in os.listdir('.')])"
    ["'cafe\\u0301'"]  # NFD!
    
    # На Linux
    $ touch "café"  
    $ python3 -c "import os; print([repr(n) for n in os.listdir('.')])"
    ["'café'"]  # NFC (как ввели)
    ```

### Практические проблемы

```bash
# Файл создан на macOS (NFD)
$ ls
café

# При копировании на Linux и обратно могут появиться "дубликаты"
$ ls
café   # NFC версия
café   # NFD версия (выглядят одинаково!)
```

---

## 8.6 Работа с путями в программировании

### Python: os.path vs pathlib

```python
# Старый способ (os.path)
import os.path

path = os.path.join('/home', 'user', 'file.txt')
dirname = os.path.dirname(path)      # '/home/user'
basename = os.path.basename(path)    # 'file.txt'
name, ext = os.path.splitext(basename)  # ('file', '.txt')
exists = os.path.exists(path)

# Современный способ (pathlib, Python 3.4+)
from pathlib import Path

path = Path('/home/user/file.txt')
path.parent        # PosixPath('/home/user')
path.name          # 'file.txt'
path.stem          # 'file'
path.suffix        # '.txt'
path.exists()      # True/False

# Создание путей
new_path = path.parent / 'other.txt'
config = Path.home() / '.config' / 'app.ini'

# Итерация по директории
for f in Path('.').glob('*.py'):
    print(f)

# Рекурсивный поиск
for f in Path('.').rglob('*.txt'):
    print(f)
```

### Shell: работа с путями

```bash
# dirname и basename
$ dirname /home/user/file.txt
/home/user

$ basename /home/user/file.txt
file.txt

$ basename /home/user/file.txt .txt
file

# Parameter expansion в Bash
path="/home/user/file.txt"
echo ${path%/*}      # /home/user  (dirname)
echo ${path##*/}     # file.txt    (basename)
echo ${path%.txt}    # /home/user/file  (без расширения)
echo ${path##*.}     # txt         (только расширение)
```

### Кроссплатформенность

```python
from pathlib import Path, PurePosixPath, PureWindowsPath

# Работа с путями другой ОС
win_path = PureWindowsPath('C:\\Users\\Alice\\file.txt')
print(win_path.parts)  # ('C:\\', 'Users', 'Alice', 'file.txt')

unix_path = PurePosixPath('/home/alice/file.txt')
print(unix_path.parts)  # ('/', 'home', 'alice', 'file.txt')

# Конвертация (осторожно!)
# Нет надёжного способа конвертировать пути между ОС
```

---

## 8.7 Частые ошибки

### 1. Пробелы в путях

```bash
# ❌ Плохо: word splitting
path="/home/user/my file.txt"
cat $path
# cat: /home/user/my: No such file or directory
# cat: file.txt: No such file or directory

# ✅ Хорошо: кавычки
cat "$path"

# ✅ Хорошо: в циклах
for f in *.txt; do
    cat "$f"
done
```

### 2. Начинается с дефиса

```bash
# ❌ Файл воспринимается как опция
$ rm -rf.txt
rm: invalid option -- 'r'

# ✅ Решение 1: ./
$ rm ./-rf.txt

# ✅ Решение 2: --
$ rm -- -rf.txt
```

### 3. Newline в имени

```bash
# Файл с newline в имени
$ touch $'file\nwith\nnewlines.txt'

# find -print0 и xargs -0 для безопасной обработки
$ find . -name "*.txt" -print0 | xargs -0 rm
```

### 4. Конкатенация путей

```python
# ❌ Плохо: ручная конкатенация
path = directory + "/" + filename  # Проблемы с //

# ✅ Хорошо: os.path.join или pathlib
path = os.path.join(directory, filename)
path = Path(directory) / filename
```

---

## 8.8 Специальные случаи

### Symlinks и realpath

```bash
$ ls -l /usr/bin/python
/usr/bin/python -> python3.11

$ readlink /usr/bin/python
python3.11

$ readlink -f /usr/bin/python
/usr/bin/python3.11

$ realpath /usr/bin/python
/usr/bin/python3.11
```

### Canonicalization

```python
import os

# Разные пути к одному файлу
paths = [
    '/home/user/./file.txt',
    '/home/user/../user/file.txt',
    '/home/user/link.txt',  # symlink
]

# Канонический путь — единственный "правильный"
for p in paths:
    print(os.path.realpath(p))
# Все выведут: /home/user/file.txt
```

### Относительный путь между файлами

```python
import os.path
from pathlib import Path

# os.path.relpath
os.path.relpath('/home/user/docs/file.txt', '/home/user/projects')
# '../docs/file.txt'

# pathlib
Path('/home/user/docs/file.txt').relative_to('/home/user')
# PosixPath('docs/file.txt')
```

---

## Резюме

| Понятие | Описание |
|---------|----------|
| **Абсолютный путь** | От корня: `/home/user/file.txt` |
| **Относительный путь** | От текущей директории: `./file.txt` |
| **Разделитель** | `/` (Unix), `\` (Windows) |
| **Нормализация** | Удаление `..`, `.`, лишних `/` |
| **Канонический путь** | Абсолютный + resolved symlinks |

| Лимит | Значение |
|-------|----------|
| Имя файла (Unix) | 255 байт |
| Полный путь (Unix) | 4096 байт |
| Имя файла (Windows) | 255 UTF-16 |
| Полный путь (Windows) | 260 символов (по умолчанию) |

!!! tip "Безопасная работа с путями"
    - Всегда используйте `os.path.join()` или `pathlib`
    - В shell всегда заключайте пути в кавычки: `"$path"`
    - Используйте `find -print0 | xargs -0` для файлов с пробелами/newlines
    - Проверяйте Unicode нормализацию при кроссплатформенной работе

!!! tip "Связь с Главой 2"
    Unicode в именах файлов тесно связан с кодировками текста, которые мы подробно разберём в Главе 2.4.


??? question "Упражнения"
    **Задание 1.** Создайте файл с пробелами, кавычками и Unicode в имени: `touch "мой файл (копия).txt"`. Обработайте его в bash-скрипте без ошибок.
    
    **Задание 2.** Напишите Python-скрипт, который преобразует абсолютный путь в относительный (от текущей директории) используя только `pathlib`.
    
    **Задание 3.** Создайте файл с именем длиной ровно 255 символов (максимум для ext4). Проверьте, что 256 символов не работает. Какой лимит на macOS (APFS)?

!!! tip "Следующая глава"
    Помимо стандартных прав, существуют **расширенные атрибуты, ACL, SELinux** → [Расширенные атрибуты и безопасность](09-extended-attrs.md)
