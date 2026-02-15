# Глава 4. Ссылки: жёсткие и символические

## Введение

В предыдущей главе мы узнали, что **директория — это таблица "имя → inode"**. Это ключевое понимание открывает важную возможность: один inode может иметь **несколько имён** в разных директориях.

Эта возможность реализуется через **ссылки** (links).

!!! note "Два типа ссылок"
    - **Hard link** (жёсткая ссылка) — дополнительное имя для существующего inode
    - **Symbolic link** (символическая ссылка, symlink, soft link) — отдельный файл, содержащий путь к другому файлу

---

## 4.1 Жёсткие ссылки (Hard Links)

### Что такое hard link?

**Жёсткая ссылка** (hard link) — это просто ещё одна **запись в директории** (directory entry), указывающая на тот же inode.

```
┌─────────────────────────────────────────────────────────────┐
│                    Директория /home/user                    │
├─────────────────────────────────────────────────────────────┤
│    Имя           │  inode                                   │
│   ──────────────────────────                                │
│    original.txt  │  131074  ──┐                             │
│    ...           │  ...       │                             │
└──────────────────────────────│─────────────────────────────┘
                               │
┌──────────────────────────────│─────────────────────────────┐
│                    Директория /tmp                          │
├──────────────────────────────│─────────────────────────────┤
│    Имя           │  inode    │                              │
│   ──────────────────────────                                │
│    hardlink.txt  │  131074  ──┤   ← Тот же inode!           │
│    notes.txt     │  131074  ──┤   ← И ещё одно имя!         │
│    report.txt    │  200001    │   ← Другой файл              │
│    ...           │  ...       │                             │
└──────────────────────────────│─────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     inode 131074    │
                    ├─────────────────────┤
                    │  size: 1234         │
                    │  links: 3  ← счётчик│
                    │  uid: 1000          │
                    │  data blocks: ...   │
                    └─────────────────────┘
```

Обратите внимание: три разных имени (`original.txt`, `hardlink.txt`, `notes.txt`) в двух разных директориях указывают на одни и те же данные. Имена могут быть совершенно разными — связь только через номер inode.

### Создание hard link

```bash
# Создаём обычный файл
$ echo "Hello, World!" > original.txt

# Проверяем inode и link count
$ ls -li original.txt
131074 -rw-r--r-- 1 user user 14 Feb  4 10:00 original.txt
                  ^
                  link count = 1

# Создаём hard link
$ ln original.txt hardlink.txt

# Оба файла указывают на один inode
$ ls -li original.txt hardlink.txt
131074 -rw-r--r-- 2 user user 14 Feb  4 10:00 hardlink.txt
131074 -rw-r--r-- 2 user user 14 Feb  4 10:00 original.txt
^^^^^^            ^
тот же inode      link count = 2
```

### Ключевые свойства hard links

**1. Нет "оригинала" и "копии"**

Оба имени абсолютно равноправны. Нельзя определить, какое имя было "первым":

```bash
$ stat original.txt hardlink.txt
# Показывают одинаковые метаданные, включая время создания
```

**2. Изменения видны через любое имя**

```bash
$ echo "New content" >> original.txt
$ cat hardlink.txt
Hello, World!
New content
```

**3. Удаление одного имени не удаляет данные**

```bash
$ rm original.txt
$ cat hardlink.txt      # Файл по-прежнему доступен!
Hello, World!
New content

$ ls -li hardlink.txt
131074 -rw-r--r-- 1 user user 26 Feb  4 10:00 hardlink.txt
                  ^
                  link count снова = 1
```

**4. Данные удаляются, когда link count = 0**

```bash
$ rm hardlink.txt       # Последняя ссылка удалена
# Теперь inode 131074 и его блоки данных освобождены
```

### Ограничения hard links

| Ограничение | Причина |
|-------------|---------|
| **Только в пределах одной ФС** | inode уникален только внутри файловой системы |
| **Нельзя для директорий** (обычно) | Предотвращение циклов в дереве каталогов |
| **Нельзя для несуществующего файла** | Должен существовать целевой inode |

```bash
# Hard link на другую файловую систему — ошибка
$ ln /home/user/file.txt /mnt/usb/link.txt
ln: failed to create hard link '/mnt/usb/link.txt': Invalid cross-device link

# Hard link на директорию — ошибка (EPERM)
$ ln /home/user/mydir /tmp/dirlink
ln: /home/user/mydir: hard link not allowed for directory
```

!!! warning "Hard links для директорий"
    Только root может создавать hard links для директорий (с флагом `ln -d`), и это **крайне не рекомендуется** — может сломать утилиты вроде `find`, `du`, `rm -r`.
    
    Исключение: `.` и `..` — это hard links на директории, создаваемые ядром автоматически.

### Практическое применение hard links

**1. Экономия места при бэкапах**

```bash
# rsync с --link-dest создаёт hard links на неизменённые файлы
$ rsync -av --link-dest=/backup/2026-02-03 /data/ /backup/2026-02-04/

# Каждый бэкап выглядит как полная копия, но занимает мало места
$ du -sh /backup/*
4.0G    /backup/2026-02-03    # Первый бэкап — полный
100M    /backup/2026-02-04    # Только изменённые файлы занимают место
```

**2. Атомарное обновление файлов**

```bash
# Обновляем конфиг без downtime
$ cp config.conf config.conf.new
$ vim config.conf.new           # Редактируем
$ ln -f config.conf.new config.conf  # Атомарная замена
```

---

## 4.2 Символические ссылки (Symbolic Links)

### Что такое symlink?

**Symbolic link** (symlink, soft link) — это **отдельный файл**, содержащий **путь** к другому файлу.

```
┌─────────────────────────────────────────────────────────────┐
│                    Директория /home/user                    │
├─────────────────────────────────────────────────────────────┤
│    Имя           │  inode                                   │
│   ──────────────────────────                                │
│    original.txt  │  131074  ────────────────────────────────┼──┐
│    symlink.txt   │  131075  ──┐                             │  │
└───────────────────────────────│────────────────────────────┘  │
                                │                               │
                                ▼                               │
                     ┌─────────────────────┐                    │
                     │    inode 131075     │                    │
                     │    (symlink)        │                    │
                     ├─────────────────────┤                    │
                     │ type: symbolic link │                    │
                     │ size: 12            │                    │
                     │ data: "original.txt"│───── путь ─────────┘
                     └─────────────────────┘
```

### Создание symlink

```bash
$ ln -s original.txt symlink.txt

$ ls -li original.txt symlink.txt
131074 -rw-r--r-- 1 user user 14 Feb  4 10:00 original.txt
131075 lrwxrwxrwx 1 user user 12 Feb  4 10:00 symlink.txt -> original.txt
^^^^^^ ^                      ^^
разные тип = l (link)         размер = длина пути (12 символов)
inode
```

### Чтение symlink vs чтение через symlink

```bash
# Читаем сам symlink (путь)
$ readlink symlink.txt
original.txt

# Читаем файл через symlink (содержимое original.txt)
$ cat symlink.txt
Hello, World!
```

### Абсолютные vs относительные пути

```bash
# Относительный symlink
$ ln -s ../data/file.txt link1.txt
$ readlink link1.txt
../data/file.txt

# Абсолютный symlink
$ ln -s /home/user/data/file.txt link2.txt
$ readlink link2.txt
/home/user/data/file.txt
```

!!! tip "Какой путь выбрать?"
    - **Относительный** — переносимый (работает при перемещении всей структуры)
    - **Абсолютный** — надёжный (работает из любой директории)
    
    ```bash
    # Относительный symlink ломается при перемещении самого symlink
    $ mv link1.txt /tmp/
    $ cat /tmp/link1.txt
    cat: /tmp/link1.txt: No such file or directory  # ../data/file.txt не существует из /tmp
    ```

### Dangling symlink (битая ссылка)

Symlink может указывать на **несуществующий файл**:

```bash
$ ln -s nonexistent.txt broken_link.txt
$ ls -l broken_link.txt
lrwxrwxrwx 1 user user 14 Feb  4 10:00 broken_link.txt -> nonexistent.txt

$ cat broken_link.txt
cat: broken_link.txt: No such file or directory

# Найти все битые symlinks
$ find . -xtype l
./broken_link.txt
```

### Symlinks на директории

В отличие от hard links, symlinks на директории — это **нормально**:

```bash
$ ln -s /var/log logs
$ ls -l logs
lrwxrwxrwx 1 user user 8 Feb  4 10:00 logs -> /var/log

$ ls logs/
# Показывает содержимое /var/log
```

### Цепочки symlinks

Symlink может указывать на другой symlink:

```bash
$ ln -s original.txt link1
$ ln -s link1 link2
$ ln -s link2 link3

$ cat link3           # Работает: link3 → link2 → link1 → original.txt
Hello, World!

$ readlink link3      # Показывает только непосредственную цель
link2

$ readlink -f link3   # Показывает конечный файл (резолвит всю цепочку)
/home/user/original.txt
```

!!! warning "Циклические symlinks"
    ```bash
    $ ln -s link_b link_a
    $ ln -s link_a link_b
    
    $ cat link_a
    cat: link_a: Too many levels of symbolic links
    ```
    
    Ядро ограничивает глубину разрешения symlinks (обычно 40 уровней в Linux).

---

## 4.3 Сравнение Hard Links и Symbolic Links

| Характеристика | Hard Link | Symbolic Link |
|----------------|-----------|---------------|
| **Свой inode** | Нет (тот же inode) | Да (отдельный inode) |
| **Размер** | 0 (только запись в директории) | Длина пути |
| **Кросс-ФС** | ❌ Нет | ✅ Да |
| **На директории** | ❌ Нет (обычно) | ✅ Да |
| **На несуществующий файл** | ❌ Нет | ✅ Да (dangling) |
| **При удалении оригинала** | Данные остаются | Становится битым |
| **Права доступа** | Права inode | Всегда `lrwxrwxrwx` (не используются) |
| **Отличим от оригинала** | Нет | Да (`ls -l`, `file`) |

### Визуальное сравнение

```bash
$ echo "Data" > original.txt
$ ln original.txt hard.txt
$ ln -s original.txt soft.txt

$ ls -li
131074 -rw-r--r-- 2 user user 5 Feb  4 10:00 hard.txt      # тот же inode
131074 -rw-r--r-- 2 user user 5 Feb  4 10:00 original.txt  # тот же inode
131075 lrwxrwxrwx 1 user user 12 Feb  4 10:00 soft.txt -> original.txt  # другой inode

# Удаляем оригинал
$ rm original.txt

$ cat hard.txt    # Работает!
Data

$ cat soft.txt    # Битая ссылка!
cat: soft.txt: No such file or directory

$ ls -l soft.txt
lrwxrwxrwx 1 user user 12 Feb  4 10:00 soft.txt -> original.txt  # Красным в терминале
```

---

## 4.4 Ссылки в разных ОС

### Linux

```bash
# Hard link
$ ln target link

# Symbolic link
$ ln -s target link

# Символическая ссылка на директорию
$ ln -s /path/to/dir link

# Принудительная перезапись существующей ссылки
$ ln -sf new_target existing_link
```

### FreeBSD / OpenBSD

Синтаксис идентичен Linux:

```bash
# FreeBSD
$ ln original.txt hardlink.txt
$ ln -s original.txt symlink.txt

# OpenBSD — то же самое
$ ln -s /var/log logs
```

Различия в поведении `stat`:

```bash
# FreeBSD: stat показывает тип ссылки
$ stat -f "%N: %HT" symlink.txt
symlink.txt: Symbolic Link

# Linux: stat показывает иначе
$ stat symlink.txt
  File: symlink.txt -> original.txt
  ...
```

### macOS

```bash
# Идентично FreeBSD/Linux
$ ln -s /Applications /tmp/apps_link

# Finder показывает symlinks как "aliases", но это разные вещи!
# Aliases — это проприетарный формат macOS, хранящий и путь, и file ID
```

!!! note "macOS Aliases vs Symlinks"
    | Свойство | Symlink | macOS Alias |
    |----------|---------|-------------|
    | Формат | Путь в файле | Бинарный файл с метаданными |
    | При перемещении оригинала | Ломается | Может найти по file ID |
    | Совместимость с Unix | ✅ Да | ❌ Только macOS |
    | Создание из терминала | `ln -s` | Только через Finder или API |

### Windows

Windows поддерживает несколько типов ссылок:

#### Symbolic Links (Vista+)

```powershell
# Требует права администратора (или Developer Mode в Win10+)

# Symlink на файл
PS> New-Item -ItemType SymbolicLink -Path "link.txt" -Target "C:\original.txt"

# Symlink на директорию
PS> New-Item -ItemType SymbolicLink -Path "link_dir" -Target "C:\original_dir"

# Через cmd
> mklink link.txt C:\original.txt
> mklink /D link_dir C:\original_dir
```

#### Hard Links (NTFS)

```powershell
# Hard link (только для файлов, только на том же томе)
PS> New-Item -ItemType HardLink -Path "hardlink.txt" -Target "C:\original.txt"

# Через cmd
> mklink /H hardlink.txt C:\original.txt

# Через fsutil
> fsutil hardlink create hardlink.txt C:\original.txt
```

#### Junction Points (NTFS, только директории)

```powershell
# Junction — как symlink, но только для директорий и только локальных путей
PS> New-Item -ItemType Junction -Path "junction_dir" -Target "C:\original_dir"

# Через cmd
> mklink /J junction_dir C:\original_dir
```

#### Сравнение ссылок в Windows

| Тип | Файлы | Директории | Кросс-том | Права |
|-----|-------|------------|-----------|-------|
| **Symbolic Link** | ✅ | ✅ | ✅ | Admin/DevMode |
| **Hard Link** | ✅ | ❌ | ❌ | User |
| **Junction** | ❌ | ✅ | ❌ (только локальные) | User |

```powershell
# Просмотр типа ссылки
PS> Get-Item link.txt | Select-Object LinkType, Target
LinkType       Target
--------       ------
SymbolicLink   C:\original.txt
```

---

## 4.5 Системные вызовы

### POSIX (Linux, BSD, macOS)

```c
#include <unistd.h>

// Создание hard link
int link(const char *oldpath, const char *newpath);

// Создание symbolic link
int symlink(const char *target, const char *linkpath);

// Чтение содержимого symbolic link
ssize_t readlink(const char *pathname, char *buf, size_t bufsiz);

// Удаление ссылки (и hard link, и symlink)
int unlink(const char *pathname);
```

### Python

```python
import os

# Hard link
os.link('original.txt', 'hardlink.txt')

# Symbolic link
os.symlink('original.txt', 'symlink.txt')

# Чтение symlink
target = os.readlink('symlink.txt')
print(target)  # 'original.txt'

# Проверка: это symlink?
os.path.islink('symlink.txt')  # True
os.path.islink('hardlink.txt')  # False

# Получить абсолютный путь, разрешив все symlinks
os.path.realpath('symlink.txt')  # '/home/user/original.txt'

# Количество hard links
stat_info = os.stat('original.txt')
print(stat_info.st_nlink)  # 2 (если есть один hard link)
```

### Разница между stat() и lstat()

```python
import os

# stat() следует по symlink (показывает информацию о целевом файле)
os.stat('symlink.txt').st_size  # Размер original.txt

# lstat() НЕ следует по symlink (показывает информацию о самом symlink)
os.lstat('symlink.txt').st_size  # Длина пути "original.txt" = 12

# То же самое в shell
$ stat symlink.txt      # Информация о original.txt
$ stat -L symlink.txt   # Явно следовать по symlink (то же самое)

# В BSD/macOS
$ stat -F symlink.txt   # Показывает @ для symlink
```

---

## 4.6 Практические сценарии

### Сценарий 1: Версионирование библиотек

```bash
$ ls -l /usr/lib/
libssl.so -> libssl.so.3        # Symlink на текущую версию
libssl.so.3 -> libssl.so.3.0.0  # Symlink на конкретную версию
libssl.so.3.0.0                 # Реальный файл

# При обновлении — только перенаправление symlink
$ ln -sf libssl.so.3.0.1 libssl.so.3
```

### Сценарий 2: Альтернативные команды

```bash
$ ls -l /usr/bin/python*
/usr/bin/python -> python3       # python вызывает python3
/usr/bin/python3 -> python3.11   # python3 вызывает python3.11
/usr/bin/python3.11              # Реальный исполняемый файл

# Система alternatives (Debian/Ubuntu)
$ update-alternatives --display python3
```

### Сценарий 3: Dotfiles management

```bash
# Храним dotfiles в Git-репозитории
$ tree ~/dotfiles/
/home/user/dotfiles/
├── .bashrc
├── .vimrc
└── .gitconfig

# Создаём symlinks в домашней директории
$ ln -s ~/dotfiles/.bashrc ~/.bashrc
$ ln -s ~/dotfiles/.vimrc ~/.vimrc
$ ln -s ~/dotfiles/.gitconfig ~/.gitconfig
```

### Сценарий 4: Объединение директорий (overlay)

```bash
# Плагины из разных источников в одной директории
$ mkdir -p ~/.vim/plugins
$ ln -s ~/my-vim-plugins/plugin1 ~/.vim/plugins/
$ ln -s /opt/shared-plugins/plugin2 ~/.vim/plugins/

$ ls ~/.vim/plugins/
plugin1 -> /home/user/my-vim-plugins/plugin1
plugin2 -> /opt/shared-plugins/plugin2
```

---

## 4.7 Подводные камни

### 1. Относительные symlinks и перемещение

```bash
$ mkdir dir1 dir2
$ echo "data" > dir1/file.txt
$ cd dir1 && ln -s file.txt link.txt && cd ..

$ ls -l dir1/
-rw-r--r-- 1 user user 5 Feb  4 10:00 file.txt
lrwxrwxrwx 1 user user 8 Feb  4 10:00 link.txt -> file.txt  # Работает

$ mv dir1/link.txt dir2/
$ cat dir2/link.txt
cat: dir2/link.txt: No such file or directory  # file.txt не существует в dir2
```

### 2. Tar и symlinks

```bash
# По умолчанию tar сохраняет symlinks как symlinks
$ tar -cvf archive.tar dir_with_symlinks/

# Чтобы архивировать содержимое (разыменовать symlinks):
$ tar -cvhf archive.tar dir_with_symlinks/
#       ^
#       -h = dereference symlinks
```

### 3. cp и symlinks

```bash
# По умолчанию cp копирует сам symlink
$ cp symlink.txt copy.txt
$ ls -l copy.txt
lrwxrwxrwx 1 user user 12 Feb  4 10:00 copy.txt -> original.txt

# Чтобы скопировать содержимое:
$ cp -L symlink.txt copy.txt
#    ^
#    -L = dereference
```

### 4. Права на symlink

```bash
$ ls -l symlink.txt
lrwxrwxrwx 1 user user 12 Feb  4 10:00 symlink.txt -> original.txt
^^^^^^^^^
Всегда 777 — права symlink игнорируются!

# chmod на symlink меняет права ЦЕЛЕВОГО файла
$ chmod 600 symlink.txt
$ ls -l original.txt
-rw------- 1 user user 5 Feb  4 10:00 original.txt  # Права изменились!
```

---

## 4.8 Дедупликация через hard links

### Экономия места при хранении одинаковых файлов

Если на диске множество **идентичных файлов** (копии медиа, дублирующиеся зависимости, повторные загрузки), их можно заменить hard links, экономя место:

```bash
# Найти файлы-дубликаты по хэшу содержимого
$ find /data -type f -exec sha256sum {} + | sort | uniq -d -w 64
# Первые 64 символа = хэш; дубликаты имеют одинаковый хэш
```

### Утилиты для автоматической дедупликации

```bash
# hardlink — заменяет дубликаты жёсткими ссылками
$ hardlink -v /data/photos/
# Comparing: 12,345 files
# Linked: 3,210 files
# Saved: 15.2 GiB

# fdupes — находит и опционально связывает дубликаты
$ fdupes -r /data/           # Найти рекурсивно
$ fdupes -r -L /data/        # Заменить hard links'ами (-L)

# jdupes — улучшенный fdupes (быстрее)
$ jdupes -r -L /data/

# rdfind — быстрый поиск дубликатов с разными стратегиями
$ rdfind -makehardlinks true /data/photos/
# rdfind сначала сравнивает размеры, потом первые/последние байты, потом полные хэши.
# Это делает его быстрее fdupes на больших деревьях.

$ rdfind -dryrun true /data/     # Только показать, что нашёл
$ rdfind -makesymlinks true /data/  # Заменить символическими ссылками вместо hard links
```

### Скрипт: рекурсивная оптимизация хранилища

```python
#!/usr/bin/env python3
"""Заменяет файлы-дубликаты жёсткими ссылками.
Сохраняет один оригинал, все копии → hard links на него.
"""
import os
import hashlib
from collections import defaultdict

def hash_file(path, block_size=65536):
    """SHA-256 хэш содержимого файла."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            h.update(block)
    return h.hexdigest()

def dedup_directory(root, dry_run=True):
    """Находит дубликаты и заменяет их hard links."""
    # Группируем по размеру (быстрый фильтр)
    by_size = defaultdict(list)
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            if os.path.isfile(path) and not os.path.islink(path):
                by_size[os.path.getsize(path)].append(path)

    saved = 0
    linked = 0

    # Для файлов одинакового размера — сравниваем хэши
    for size, paths in by_size.items():
        if len(paths) < 2 or size == 0:
            continue

        by_hash = defaultdict(list)
        for path in paths:
            by_hash[hash_file(path)].append(path)

        for file_hash, duplicates in by_hash.items():
            if len(duplicates) < 2:
                continue

            # Проверяем, не являются ли уже hard links
            original = duplicates[0]
            orig_stat = os.stat(original)

            for dup in duplicates[1:]:
                dup_stat = os.stat(dup)
                if orig_stat.st_ino == dup_stat.st_ino:
                    continue  # Уже hard link

                if dry_run:
                    print(f"  Would link: {dup} → {original}")
                else:
                    os.unlink(dup)
                    os.link(original, dup)
                    print(f"  Linked: {dup} → {original}")

                saved += size
                linked += 1

    print(f"\n{'Dry run: would save' if dry_run else 'Saved'}: "
          f"{saved / (1024**2):.1f} MiB ({linked} files)")

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    dry_run = "--apply" not in sys.argv
    if dry_run:
        print("Dry run mode (добавьте --apply для реального выполнения)\n")
    dedup_directory(path, dry_run=dry_run)
```

```bash
# Пробный запуск (ничего не меняет)
$ python3 dedup.py /data/photos/
Dry run mode (добавьте --apply для реального выполнения)

  Would link: /data/photos/2025/IMG_001.jpg → /data/photos/backup/IMG_001.jpg
  Would link: /data/photos/copies/report.pdf → /data/photos/work/report.pdf

Dry run: would save 847.3 MiB (156 files)

# Применить
$ python3 dedup.py /data/photos/ --apply
```

!!! info "Как это используют облачные хранилища"
    Публичные файловые хранилища (Dropbox, Google Drive) используют **серверную дедупликацию**:
    при загрузке файла сначала вычисляется хэш, и если файл с таким хэшем уже есть на сервере,
    сохраняется только ссылка. Поэтому загрузка популярного файла может быть «мгновенной» —
    данные не передаются по сети, а просто связываются с существующим блоком.

---

## Резюме

| Операция | Hard Link | Symbolic Link |
|----------|-----------|---------------|
| Создать | `ln target link` | `ln -s target link` |
| Прочитать цель | — | `readlink link` |
| Разрешить полный путь | — | `readlink -f link` |
| Проверить тип | `stat -c %h file` (nlink > 1) | `test -L link` |
| Удалить | `rm link` | `rm link` |

!!! tip "Когда использовать"
    - **Hard link**: бэкапы, атомарные обновления, экономия места для идентичных файлов
    - **Symbolic link**: версионирование, кросс-ФС ссылки, ссылки на директории, конфигурация

!!! warning "Помните"
    - Hard link не работает между файловыми системами
    - Symlink может быть битым (dangling)
    - Права symlink не используются — проверяются права целевого файла
    - При копировании/архивировании — проверяйте, как обрабатываются ссылки


??? question "Упражнения"
    **Задание 1.** Создайте файл `original.txt`, жёсткую ссылку `hard.txt` и символическую `soft.txt`. Удалите `original.txt`. Какая ссылка работает, какая стала «битой»? Почему?
    
    **Задание 2.** Выполните `find /usr -type l -xtype l 2>/dev/null | head` — что это за файлы? Что означает `-xtype l`?
    
    **Задание 3.** Попробуйте создать жёсткую ссылку на директорию (`ln dir1 dir2`). Что произойдёт и почему ОС запрещает это?

!!! tip "Следующая глава"
    Теперь мы понимаем, как файлы связываются между собой. Пора разобраться с **базовыми операциями** над файлами → [Файловые операции](05-file-operations.md)
