# Глава 2. Типы файлов и их содержимое

## Введение

В предыдущей главе мы узнали, **что такое файл** — именованная область данных с метаданными. Теперь разберёмся, **какие типы файлов** существуют и что находится внутри каждого из них.

В Unix существует 7 типов файлов, и только один из них — **regular file** — содержит произвольные пользовательские данные. Остальные типы имеют **специальное содержимое**, которое мы рассмотрим в этой главе.

!!! note "Напоминание: типы файлов"
    ```bash
    $ ls -l
    -rw-r--r--  file.txt       # - regular file
    drwxr-xr-x  directory/     # d directory
    lrwxrwxrwx  link -> file   # l symbolic link
    brw-rw----  /dev/sda       # b block device
    crw-rw-rw-  /dev/tty       # c character device
    prw-r--r--  mypipe         # p named pipe (FIFO)
    srwxrwxrwx  socket         # s socket
    ```

---

## 2.1 Директории: файлы со списком имён

### Что такое директория?

**Директория** (directory, каталог) — это специальный файл, содержащий **таблицу соответствия** (directory entries, dentry) между именами файлов и номерами inode.

```
┌─────────────────────────────────────────────────┐
│            Директория /home/user                │
│                  (inode #100)                 │
├─────────────────────────────────────────────────┤
│  Содержимое (directory entries):                │
│                                                 │
│    Имя          │  inode                        │
│   ─────────────────────────                     │
│    .            │  100     (сама директория)    │
│    ..           │  50      (родительская)       │
│    file.txt     │  131074                       │
│    document.pdf │  131075                       │
│    subdir       │  200                          │
│    README.md    │  131076                       │
└─────────────────────────────────────────────────┘
```

### Ключевая идея: имя отдельно от данных

В Unix **имя файла НЕ хранится в inode**. Оно хранится в директории!

Это позволяет:

1. **Один inode — много имён** (hard links)
2. **Переименование без копирования** данных
3. **Быстрое удаление** — просто убрать запись из директории

```bash
# Файл file.txt имеет inode 131074
$ ls -li file.txt
131074 -rw-r--r-- 1 user user 1234 Feb  4 10:00 file.txt

# Создаём hard link — добавляем ещё одно имя для того же inode
$ ln file.txt another_name.txt
$ ls -li
131074 -rw-r--r-- 2 user user 1234 Feb  4 10:00 another_name.txt
131074 -rw-r--r-- 2 user user 1234 Feb  4 10:00 file.txt
       ^         ^
       тот же    link count = 2
       inode
```

### Структура directory entry (dentry)

В классических Unix ФС (UFS, ext2) запись директории выглядит так:

```c
// Упрощённая структура ext2 directory entry
struct ext2_dir_entry {
    uint32_t inode;      // Номер inode (4 байта)
    uint16_t rec_len;    // Длина записи (2 байта)
    uint8_t  name_len;   // Длина имени (1 байт)
    uint8_t  file_type;  // Тип файла (1 байт)
    char     name[];     // Имя файла (переменная длина)
};
```

**Пример на диске:**

```
Offset  | inode | rec_len | name_len | type | name
--------|-------|---------|----------|------|--------
0x0000  | 100   | 12      | 1        | 2    | "."
0x000C  | 50    | 12      | 2        | 2    | ".."
0x0018  | 131074| 16      | 8        | 1    | "file.txt"
0x0028  | 131075| 20      | 12       | 1    | "document.pdf"
...
```

### Специальные записи: `.` и `..`

Каждая директория **обязательно** содержит две записи:

| Имя | Значение | Зачем нужно |
|-----|----------|-------------|
| `.` | inode самой директории | `cd .`, `./script.sh` |
| `..` | inode родительской директории | `cd ..`, `../file` |

```bash
$ pwd
/home/user/project

$ ls -lai
total 16
   200 drwxr-xr-x  3 user user 4096 Feb  4 10:00 .      # эта директория
    50 drwxr-xr-x 10 user user 4096 Feb  4 09:00 ..     # /home/user
131074 -rw-r--r--  1 user user 1234 Feb  4 10:00 file.txt
   201 drwxr-xr-x  2 user user 4096 Feb  4 10:00 subdir
```

!!! info "Корневая директория `/`"
    В корне файловой системы `.` и `..` указывают на **один и тот же inode**:
    ```bash
    $ ls -lai /
       2 drwxr-xr-x  20 root root 4096 Feb  1 00:00 .
       2 drwxr-xr-x  20 root root 4096 Feb  1 00:00 ..
    ```

### Почему директория не может быть пустой?

Минимальный размер директории — это `.` и `..`. Даже "пустая" директория содержит две записи:

```bash
$ mkdir empty_dir
$ ls -la empty_dir/
total 8
drwxr-xr-x 2 user user 4096 Feb  4 10:00 .
drwxr-xr-x 5 user user 4096 Feb  4 10:00 ..

# "Пустая" директория занимает 4 КБ на диске!
$ du -h empty_dir/
4.0K    empty_dir/
```

### Link count директории

**Link count директории** = 2 + количество поддиректорий.

Почему?

1. Сама директория ссылается на себя через `.`
2. Родительская директория содержит запись с именем этой директории
3. Каждая поддиректория ссылается на неё через `..`

```bash
$ mkdir -p parent/child1 parent/child2 parent/child3
$ ls -ld parent/
drwxr-xr-x 5 user user 4096 Feb  4 10:00 parent/
           ^
           5 = 2 (base) + 3 (subdirs)
```

### Чтение содержимого директории

=== "Linux"

    ```bash
    # Команда ls читает директорию
    $ ls /home/user
    
    # На низком уровне — системные вызовы (strace)
    $ strace ls /home/user 2>&1 | grep -E "openat|getdents"
    openat(AT_FDCWD, "/home/user", O_RDONLY|O_DIRECTORY) = 3
    getdents64(3, /* 15 entries */, 32768) = 488
    getdents64(3, /* 0 entries */, 32768) = 0
    ```

=== "FreeBSD / macOS"

    ```bash
    # Команда ls читает директорию
    $ ls /home/user
    
    # На низком уровне — системные вызовы (dtrace/truss)
    $ truss ls /home/user 2>&1 | grep -E "open|getdirentries"
    openat(AT_FDCWD,"/home/user",O_RDONLY|O_DIRECTORY,00) = 3
    getdirentries(3,"...",4096,0x...) = 488
    ```

**Python: чтение директории**

```python
import os

# Высокоуровневый API
entries = os.listdir('/home/user')
print(entries)  # ['file.txt', 'document.pdf', 'subdir']

# С метаданными
for entry in os.scandir('/home/user'):
    print(f"{entry.name:20} inode={entry.inode()} is_dir={entry.is_dir()}")

# Вывод:
# file.txt             inode=131074 is_dir=False
# document.pdf         inode=131075 is_dir=False
# subdir               inode=200 is_dir=True
```

### Различия между файловыми системами

| ФС | Структура директории | Особенности |
|----|---------------------|-------------|
| ext2/ext3 | Линейный список | Простая, медленная для больших директорий |
| ext4 | HTree (hash tree) | Быстрый поиск по имени |
| XFS | B+ дерево | Оптимизирована для больших директорий |
| Btrfs | B-дерево | Copy-on-write |
| NTFS | B+ дерево в MFT | Имя хранится в MFT, не в директории |

```bash
# ext4: включение HTree (обычно по умолчанию)
$ tune2fs -l /dev/sda1 | grep dir_index
Filesystem features: ... dir_index ...
```

---

## 2.2 Символические ссылки (Symbolic Links)

### Содержимое символической ссылки

**Символическая ссылка** (symbolic link, symlink, soft link) — это файл, содержащий **путь к другому файлу** (target path).

```bash
$ ln -s /home/user/original.txt /tmp/link.txt

$ ls -l /tmp/link.txt
lrwxrwxrwx 1 user user 23 Feb  4 10:00 /tmp/link.txt -> /home/user/original.txt
                       ^^
                       размер = длина пути (23 символа)

# Содержимое symlink — это просто текст пути
$ readlink /tmp/link.txt
/home/user/original.txt
```

### Хранение пути

В зависимости от длины пути, symlink может храниться:

**1. Inline (fast symlink)** — путь прямо в inode:

```
┌─────────────────────────────────────────────────┐
│              inode символической ссылки          │
├─────────────────────────────────────────────────┤
│  Тип: symbolic link (l)                         │
│  Размер: 23 байта                               │
│  ...                                            │
│  Данные: "/home/user/original.txt"  ← inline!   │
└─────────────────────────────────────────────────┘
```

**2. В блоке данных** — для длинных путей (> ~60 символов в ext4).

```bash
# Короткий symlink — 0 блоков
$ ln -s /tmp/x short_link
$ stat short_link
  Size: 6               Blocks: 0

# Длинный symlink — занимает блок
$ ln -s /very/long/path/that/exceeds/sixty/characters/limit/file.txt long_link
$ stat long_link
  Size: 65              Blocks: 8
```

### Symlink vs содержимое

```bash
# Читаем symlink (получаем путь)
$ readlink /tmp/link.txt
/home/user/original.txt

# Читаем файл через symlink (получаем содержимое original.txt)
$ cat /tmp/link.txt
Hello, this is the original file content.
```

---

## 2.3 Псевдофайлы: /proc и /sys

### Файлы, которых нет на диске

**Псевдофайловые системы** (pseudo filesystems) — это виртуальные ФС, где "файлы" генерируются ядром на лету.

!!! info "Различия между платформами"
    - **Linux**: `/proc` (procfs) + `/sys` (sysfs)
    - **FreeBSD**: `/proc` (опционально), информация через `sysctl`
    - **macOS**: нет `/proc`, используйте `sysctl` и утилиты
    - **OpenBSD**: `/proc` отключён по умолчанию

```bash
$ ls -l /proc/cpuinfo
-r--r--r-- 1 root root 0 Feb  4 10:00 /proc/cpuinfo
                       ^
                       размер = 0 (но данные есть!)

$ cat /proc/cpuinfo | head -5
processor       : 0
vendor_id       : GenuineIntel
cpu family      : 6
model           : 142
model name      : Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz
```

### procfs — информация о процессах

```
/proc/
├── 1/                    # Процесс PID=1 (init/systemd)
│   ├── cmdline           # Командная строка запуска
│   ├── cwd -> /          # Текущая директория (symlink)
│   ├── environ           # Переменные окружения
│   ├── exe -> /sbin/init # Исполняемый файл (symlink)
│   ├── fd/               # Открытые файловые дескрипторы
│   │   ├── 0 -> /dev/null
│   │   ├── 1 -> /dev/null
│   │   └── 2 -> /dev/null
│   ├── maps              # Карта памяти
│   └── status            # Статус процесса
├── self -> 1234          # Текущий процесс (symlink)
├── cpuinfo               # Информация о CPU
├── meminfo               # Информация о памяти
├── mounts                # Смонтированные ФС
└── sys/                  # Параметры ядра (sysctl)
    └── kernel/
        └── hostname      # Имя хоста
```

**Примеры использования:**

=== "Linux"

    ```bash
    # Узнать командную строку процесса
    $ cat /proc/1234/cmdline | tr '\0' ' '
    /usr/bin/python3 script.py --verbose
    
    # Посмотреть открытые файлы процесса
    $ ls -l /proc/1234/fd/
    lrwx------ 1 user user 64 Feb  4 10:00 0 -> /dev/pts/0
    lrwx------ 1 user user 64 Feb  4 10:00 1 -> /dev/pts/0
    lrwx------ 1 user user 64 Feb  4 10:00 3 -> /home/user/data.txt
    
    # Изменить параметр ядра
    $ echo "new-hostname" > /proc/sys/kernel/hostname
    ```

=== "FreeBSD / macOS"

    ```bash
    # Информация о процессе через ps
    $ ps -p 1234 -o command=
    /usr/bin/python3 script.py --verbose
    
    # Посмотреть открытые файлы процесса
    $ fstat -p 1234
    USER     CMD          PID   FD MOUNT      INUM MODE
    user     python3     1234    0 /dev         12 crw--w----
    user     python3     1234    1 /dev         12 crw--w----
    user     python3     1234    3 /home    131074 -rw-r--r--
    
    # Параметры ядра через sysctl
    $ sysctl kern.hostname
    kern.hostname: myhost
    $ sudo sysctl kern.hostname=new-hostname
    ```

### sysfs — информация об устройствах

```
/sys/
├── block/                # Блочные устройства
│   └── sda/
│       ├── size          # Размер в секторах
│       └── queue/        # Параметры очереди I/O
├── class/                # Классы устройств
│   ├── net/
│   │   └── eth0/
│   │       ├── address   # MAC-адрес
│   │       └── speed     # Скорость (Mbps)
│   └── power_supply/
│       └── BAT0/
│           ├── capacity  # Заряд батареи (%)
│           └── status    # Charging/Discharging
└── devices/              # Дерево устройств
```

**Примеры:**

```bash
# MAC-адрес сетевой карты
$ cat /sys/class/net/eth0/address
00:11:22:33:44:55

# Заряд батареи
$ cat /sys/class/power_supply/BAT0/capacity
87

# Яркость экрана (можно менять!)
$ echo 100 > /sys/class/backlight/intel_backlight/brightness
```

### Bash pseudo-files: сетевые сокеты через файлы

Bash предоставляет специальные псевдофайлы (это фича Bash, не ядра!):

```bash
# TCP-соединение через псевдофайл
$ exec 3<>/dev/tcp/example.com/80
$ echo -e "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n" >&3
$ cat <&3
HTTP/1.1 200 OK
...

# UDP-соединение
$ echo "test" > /dev/udp/localhost/514  # syslog

# Стандартные дескрипторы как файлы
$ cat /dev/fd/0       # То же, что cat /dev/stdin
$ echo "hello" > /dev/fd/1  # То же, что echo "hello"
```

| Псевдофайл | Описание |
|------------|----------|
| `/dev/fd/N` | Дескриптор N текущего процесса |
| `/dev/stdin` | Алиас для `/dev/fd/0` |
| `/dev/stdout` | Алиас для `/dev/fd/1` |
| `/dev/stderr` | Алиас для `/dev/fd/2` |
| `/dev/tcp/host/port` | TCP-сокет (Bash only) |
| `/dev/udp/host/port` | UDP-сокет (Bash only) |

!!! warning "Только Bash"
    `/dev/tcp` и `/dev/udp` — это фича Bash, не ядра. Они не работают в `sh`, `dash`, `zsh` без специальных настроек.

### Почему размер = 0?

Псевдофайлы не имеют фиксированного размера — содержимое генерируется при чтении:

```bash
$ stat /proc/cpuinfo
  Size: 0               Blocks: 0

$ wc -c /proc/cpuinfo
2847 /proc/cpuinfo    # Но данных — 2847 байт!
```

---

## 2.4 Файлы устройств: /dev

### Block devices vs Character devices

| Тип | Описание | Примеры |
|-----|----------|---------|
| **Block** (b) | Доступ блоками, буферизация, seek | `/dev/sda`, `/dev/nvme0n1` |
| **Character** (c) | Побайтовый/потоковый доступ | `/dev/tty`, `/dev/random` |

```bash
$ ls -l /dev/sda /dev/tty
brw-rw---- 1 root disk 8, 0 Feb  4 10:00 /dev/sda
crw-rw-rw- 1 root tty  5, 0 Feb  4 10:00 /dev/tty
^                     ^^^^
тип                   major, minor numbers
```

### Major и Minor numbers

Ядро идентифицирует устройства по паре чисел:

- **Major** — тип драйвера (8 = SCSI disk, 5 = TTY)
- **Minor** — конкретное устройство

```bash
$ ls -l /dev/sda*
brw-rw---- 1 root disk 8, 0 Feb  4 10:00 /dev/sda    # весь диск
brw-rw---- 1 root disk 8, 1 Feb  4 10:00 /dev/sda1   # раздел 1
brw-rw---- 1 root disk 8, 2 Feb  4 10:00 /dev/sda2   # раздел 2
                       ^  ^
                     major minor
```

### Специальные устройства

```bash
# /dev/null — чёрная дыра
$ echo "discarded" > /dev/null  # данные исчезают

# /dev/zero — бесконечный источник нулей
$ head -c 10 /dev/zero | xxd
00000000: 0000 0000 0000 0000 0000                 ..........

# /dev/random — криптографически случайные данные
$ head -c 16 /dev/random | xxd
00000000: 8a3f b21c 45d7 9e02 c1a8 7f3b 0e6d 2941  .?..E......;.m)A

# /dev/urandom — псевдослучайные данные (не блокирует)
$ head -c 16 /dev/urandom | xxd
00000000: 5c12 a9e7 3b8f 01d4 6c2a 9f7e 1d3b 4a82  \...;...l*.~.;J.
```

### Создание файла устройства

```bash
# Создать character device
$ mknod /tmp/my_null c 1 3

# Создать block device
$ mknod /tmp/my_loop b 7 0

# Проверить
$ ls -l /tmp/my_*
crw-r--r-- 1 root root 1, 3 Feb  4 10:00 /tmp/my_null
brw-r--r-- 1 root root 7, 0 Feb  4 10:00 /tmp/my_loop
```

---

## 2.5 Named pipes (FIFO) и Sockets

### Named pipe (FIFO)

**FIFO** — файл для межпроцессного взаимодействия. Данные читаются в том же порядке, в котором записаны.

```bash
# Создаём pipe
$ mkfifo /tmp/mypipe

$ ls -l /tmp/mypipe
prw-r--r-- 1 user user 0 Feb  4 10:00 /tmp/mypipe
^
p = pipe

# Терминал 1: писатель (заблокируется до появления читателя)
$ echo "Hello from writer" > /tmp/mypipe

# Терминал 2: читатель
$ cat /tmp/mypipe
Hello from writer
```

### Unix domain socket

**Socket** — файл для сетевого взаимодействия между процессами на одной машине.

```bash
$ ls -l /var/run/docker.sock
srwxrwxrwx 1 root docker 0 Feb  4 10:00 /var/run/docker.sock
^
s = socket

# Обращение к Docker через socket
$ curl --unix-socket /var/run/docker.sock http://localhost/version
```

---

## 2.7 Исполняемые файлы

Обычные файлы (regular files) могут содержать что угодно — текст, изображения, данные. Но есть особый подвид: **исполняемые файлы** — контейнеры для машинного кода.

Каждая ОС использует свой бинарный формат:

| Формат | ОС | Magic | Утилиты |
|--------|-----|-------|----------|
| **ELF** | Linux, BSD | `\x7fELF` | `readelf`, `objdump` |
| **Mach-O** | macOS, iOS | `\xcf\xfa\xed\xfe` | `otool`, `nm` |
| **PE** | Windows | `MZ` | `dumpbin` |

```bash
# Определить формат исполняемого файла
$ file /bin/ls
/bin/ls: ELF 64-bit LSB pie executable, x86-64, dynamically linked

# Посмотреть magic number
$ xxd /bin/ls | head -1
```

!!! tip "Подробнее"
    Детальная структура ELF, Mach-O и PE (секции, заголовки, magic numbers) — в [Главе 22. Бинарная структура файлов](../ch3/22-binary-structure.md).

---

## 2.8 Файловые операции по типам

Разные типы файлов поддерживают разные операции. Попытка выполнить неподдерживаемую операцию приводит к ошибке.

### Сводная таблица операций

| Операция | `-` regular | `d` dir | `l` symlink | `b` block | `c` char | `p` FIFO | `s` socket |
|----------|:-----------:|:-------:|:-----------:|:---------:|:--------:|:--------:|:----------:|
| `open()` | ✓ | ✓* | ✓** | ✓ | ✓ | ✓ | ✗*** |
| `read()` | ✓ | ✗ | — | ✓ | ✓ | ✓ | — |
| `write()` | ✓ | ✗ | — | ✓ | ✓ | ✓ | — |
| `seek()` | ✓ | ✗ | — | ✓ | ✗ | ✗ | — |
| `tell()` | ✓ | ✗ | — | ✓ | ✗**** | ✗ | — |
| `truncate()` | ✓ | ✗ | — | ✗ | ✗ | ✗ | — |
| `mmap()` | ✓ | ✗ | — | ✓ | ✗ | ✗ | — |

**Примечания:**

- `*` — директории открываются для `listdir()`, но не для `read()`/`write()`
- `**` — symlink автоматически разыменовывается, операции идут к target
- `***` — сокеты открываются через `socket.socket()`, не `open()`
- `****` — `tell()` возвращает 0, но это не имеет смысла

### Почему так?

| Тип | Модель данных | Следствия |
|-----|--------------|-----------|
| **Regular** | Массив байт фиксированного размера | Всё работает: произвольный доступ, изменение размера |
| **Directory** | Специальная структура ядра | Только через `readdir()`, прямой доступ запрещён |
| **Block device** | Массив блоков | Как regular, но размер фиксирован устройством |
| **Char device** | Поток байт | Нет позиции — данные "протекают" через устройство |
| **FIFO** | Односторонний буфер | Поток: что записали — то прочитали (один раз) |
| **Socket** | Двунаправленный канал | Отдельный API (`send`/`recv`), не файловые операции |

### Python: тестируем операции

```python
import os
import stat

def test_file_operations(path):
    """Тестирует файловые операции на разных типах файлов."""
    
    mode = os.stat(path).st_mode
    file_type = stat.filemode(mode)[0]  # Первый символ: -, d, l, b, c, p, s
    
    print(f"\n{'='*50}")
    print(f"Testing: {path}")
    print(f"Type: {file_type} ({get_type_name(file_type)})")
    print(f"{'='*50}")
    
    # Определяем режим открытия
    if file_type == 'd':
        print("Directory: using os.listdir() instead of open()")
        try:
            entries = os.listdir(path)
            print(f"  listdir(): ✓ ({len(entries)} entries)")
        except Exception as e:
            print(f"  listdir(): ✗ {e}")
        return
    
    if file_type == 's':
        print("Socket: requires socket module, not open()")
        return
    
    # Для остальных типов пробуем open()
    mode_flag = 'rb' if file_type in ('b', 'c', 'p') else 'rb'
    
    try:
        # Для FIFO нужен O_NONBLOCK, иначе заблокируется
        if file_type == 'p':
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
            f = os.fdopen(fd, 'rb')
        else:
            f = open(path, 'rb')
        
        print(f"  open(): ✓")
        
        # read()
        try:
            data = f.read(10)
            print(f"  read(10): ✓ got {len(data)} bytes")
        except Exception as e:
            print(f"  read(): ✗ {type(e).__name__}: {e}")
        
        # seek()
        try:
            f.seek(0)
            print(f"  seek(0): ✓")
        except Exception as e:
            print(f"  seek(): ✗ {type(e).__name__}")
        
        # tell()
        try:
            pos = f.tell()
            print(f"  tell(): ✓ position={pos}")
        except Exception as e:
            print(f"  tell(): ✗ {type(e).__name__}")
        
        # seekable()
        print(f"  seekable(): {f.seekable()}")
        
        f.close()
        
    except Exception as e:
        print(f"  open(): ✗ {type(e).__name__}: {e}")

def get_type_name(t):
    return {
        '-': 'regular file',
        'd': 'directory', 
        'l': 'symlink',
        'b': 'block device',
        'c': 'character device',
        'p': 'named pipe (FIFO)',
        's': 'socket'
    }.get(t, 'unknown')

# Примеры запуска:
# test_file_operations('/etc/passwd')         # regular
# test_file_operations('/tmp')                # directory
# test_file_operations('/dev/sda')            # block (нужен root)
# test_file_operations('/dev/null')           # character
# test_file_operations('/dev/tty')            # character
# test_file_operations('/tmp/mypipe')         # FIFO (создать: mkfifo /tmp/mypipe)
```

### Демонстрация различий

```python
# Regular file — всё работает
>>> f = open('/etc/passwd', 'rb')
>>> f.seekable()
True
>>> f.seek(100)
100
>>> f.tell()
100
>>> f.read(10)
b'news:x:9:9'

# Character device (/dev/null) — поток, нет позиции
>>> f = open('/dev/null', 'rb')
>>> f.seekable()
False
>>> f.seek(100)
OSError: [Errno 29] Illegal seek
>>> f.read(10)
b''  # /dev/null всегда возвращает EOF

# Character device (/dev/zero) — бесконечный поток нулей
>>> f = open('/dev/zero', 'rb')
>>> f.seekable()
False
>>> f.read(10)
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# Character device (/dev/urandom) — бесконечный поток случайных байт
>>> f = open('/dev/urandom', 'rb')
>>> f.seekable()
False
>>> f.read(10).hex()
'7a3f9c2d4e8b1a5f6c0d'

# Block device — как файл фиксированного размера (нужен root)
>>> f = open('/dev/sda', 'rb')  
>>> f.seekable()
True
>>> f.seek(512)  # Перейти к сектору 1
512
>>> f.read(16)   # Прочитать 16 байт
b'\x00\x00\x00\x00\x00\x00\x00\x00...'

# FIFO — блокирующий поток
>>> # mkfifo /tmp/testpipe
>>> f = open('/tmp/testpipe', 'rb')  # БЛОКИРУЕТСЯ пока кто-то не откроет на запись!
>>> f.seekable()  
False
>>> f.seek(0)
OSError: [Errno 29] Illegal seek

# Directory — нельзя читать как файл
>>> f = open('/tmp', 'rb')
IsADirectoryError: [Errno 21] Is a directory: '/tmp'
>>> os.listdir('/tmp')  # Используем специальный API
['file1.txt', 'file2.txt', ...]
```

### Атрибуты файловых объектов Python

```python
>>> f = open('/etc/passwd', 'rb')
>>> f.seekable()   # Можно ли seek()?
True
>>> f.readable()   # Можно ли read()?
True
>>> f.writable()   # Можно ли write()?
False              # Открыли в режиме 'rb'

>>> f = open('/dev/null', 'rb')
>>> f.seekable()
False
>>> f.readable()
True

>>> f = open('/dev/tty', 'rb')  # Терминал
>>> f.seekable()
False
>>> f.isatty()     # Это терминал?
True
```

---

!!! tip "Лимиты файловых систем"
    Макс. размер файла, тома и длина имён зависят от ФС (FAT32: 4 ГБ, ext4: 16 ТБ, ZFS: 16 ЭБ). Полная таблица лимитов — в [Главе 34. Архитектура хранения](../ch5/34-architecture.md).

---

## Резюме

| Тип файла | Содержимое | Пример |
|-----------|-----------|--------|
| **Regular** (-) | Произвольные данные | `file.txt` |
| **Directory** (d) | Таблица имя → inode | `/home/user/` |
| **Symlink** (l) | Путь к другому файлу | `link -> target` |
| **Block device** (b) | Интерфейс к устройству (блочный) | `/dev/sda` |
| **Char device** (c) | Интерфейс к устройству (потоковый) | `/dev/tty` |
| **FIFO** (p) | Буфер для IPC | `/tmp/mypipe` |
| **Socket** (s) | Endpoint для сетевого IPC | `/var/run/docker.sock` |

!!! tip "Ключевые идеи"
    - **Директория** — это файл с таблицей "имя → inode"
    - **Имя файла** хранится в директории, НЕ в inode
    - **Псевдофайлы** (`/proc`, `/sys`) генерируются ядром на лету
    - **Устройства** (`/dev`) — интерфейс к драйверам ядра


??? question "Упражнения"
    **Задание 1.** Создайте FIFO (`mkfifo my_pipe`), в одном терминале выполните `cat my_pipe`, в другом — `echo "Hello" > my_pipe`. Проверьте тип файла через `ls -l` и `file`.
    
    **Задание 2.** Напишите Python-скрипт, рекурсивно обходящий `/tmp` и подсчитывающий файлы каждого типа (обычные, директории, симлинки) через `os.scandir()`.
    
    **Задание 3.** Исследуйте `/proc/self/` (Linux): прочитайте `cmdline`, `status`, `maps`. Какие из этих «файлов» имеют нулевой размер по `stat`, но содержат данные? Почему?

!!! tip "Следующая глава"
    Теперь мы понимаем типы файлов и связь между именем файла и inode. Пора разобраться с **метаданными и структурой inode** → [Метаданные и inode](03-metadata-inode.md)
