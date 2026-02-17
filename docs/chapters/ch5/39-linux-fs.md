# Глава 39. Файловые системы Linux

## Введение

Linux поддерживает огромное количество файловых систем — от классических ext4 и XFS до современных Btrfs, F2FS и Bcachefs. В этой главе рассмотрим ФС, специфичные для Linux, не затронутые в предыдущих главах.

---

## 39.1 Обзор файловых систем Linux

```
                    Linux Filesystem Timeline
─────────────────────────────────────────────────────────
1991  ext       Первая ФС Linux (Rémy Card)
1993  ext2      Стабильная ФС без журнала
1994  FAT/VFAT  Совместимость с DOS/Windows
1997  ReiserFS  Первая журналируемая ФС Linux
2001  ext3      Журнал для ext2
2001  XFS       Портирована из IRIX
2004  Reiser4   Улучшенная ReiserFS (не вошла в mainline)
2008  ext4      Современный стандарт
2009  Btrfs     Copy-on-write ФС
2012  F2FS      Flash-Friendly FS (Samsung)
2015  OverlayFS Слоёная ФС для контейнеров
2023  Bcachefs  Новая CoW ФС (mainline 6.7)
─────────────────────────────────────────────────────────
```

---

## 39.2 Btrfs (B-tree File System)

### Особенности Btrfs

- **Copy-on-Write** (данные не перезаписываются)
- **Встроенные снапшоты** (мгновенные, бесплатные)
- **Checksum** всех данных и метаданных
- **Сжатие** (zlib, lzo, zstd)
- **Дедупликация**
- **RAID** (0, 1, 10, 5, 6 — экспериментально)
- **Subvolumes** (логические разделы)

### Базовые операции

```bash
# Создание Btrfs
mkfs.btrfs /dev/sdb1

# С меткой и сжатием
mkfs.btrfs -L "BTRFS_DATA" /dev/sdb1

# Монтирование со сжатием
mount -o compress=zstd /dev/sdb1 /mnt

# Информация
btrfs filesystem show
btrfs filesystem df /mnt
```

### Subvolumes

```bash
# Создание subvolume
btrfs subvolume create /mnt/home
btrfs subvolume create /mnt/var

# Список subvolumes
btrfs subvolume list /mnt

# Монтирование конкретного subvolume
mount -o subvol=home /dev/sdb1 /home

# Удаление
btrfs subvolume delete /mnt/old
```

### Снапшоты

```bash
# Создание снапшота (мгновенно!)
btrfs subvolume snapshot /mnt/home /mnt/snapshots/home-$(date +%Y%m%d)

# Read-only снапшот
btrfs subvolume snapshot -r /mnt/home /mnt/snapshots/home-backup

# Восстановление из снапшота
btrfs subvolume delete /mnt/home
btrfs subvolume snapshot /mnt/snapshots/home-20240115 /mnt/home
```

### RAID в Btrfs

```bash
# Создание RAID1 (зеркало)
mkfs.btrfs -d raid1 -m raid1 /dev/sdb /dev/sdc

# Добавление диска
btrfs device add /dev/sdd /mnt

# Конвертация в RAID1
btrfs balance start -dconvert=raid1 -mconvert=raid1 /mnt

# Удаление диска
btrfs device remove /dev/sdb /mnt

# Замена неисправного диска
btrfs replace start /dev/sdb /dev/sde /mnt
```

### Сжатие и дедупликация

```bash
# Монтирование со сжатием
mount -o compress=zstd:3 /dev/sdb1 /mnt

# Уровни zstd: 1-15 (3 — баланс скорость/сжатие)

# Сжатие существующих файлов
btrfs filesystem defragment -r -v -czstd /mnt

# Дедупликация (нужен duperemove)
duperemove -dr /mnt
```

### Проверка и восстановление

```bash
# Scrub (проверка целостности online)
btrfs scrub start /mnt
btrfs scrub status /mnt

# Проверка (offline)
btrfs check /dev/sdb1

# Восстановление (осторожно!)
btrfs check --repair /dev/sdb1
```

---

## 39.3 F2FS (Flash-Friendly File System)

### Особенности F2FS

Оптимизирована для NAND flash (SSD, SD-карты, eMMC):

- **Log-structured** дизайн
- **Multi-head logging**
- **Adaptive logging**
- **Roll-back recovery**
- **Online resize/defrag**

```bash
# Создание F2FS
mkfs.f2fs /dev/sdb1

# С параметрами
mkfs.f2fs -l "SSD_DATA" -O encrypt,extra_attr /dev/sdb1

# Монтирование
mount -t f2fs /dev/sdb1 /mnt

# С параметрами
mount -t f2fs -o discard,noatime /dev/sdb1 /mnt
```

### Рекомендации F2FS

```bash
# Идеально для:
# - Android устройства (многие используют F2FS)
# - SD-карты
# - USB-флешки
# - Дешёвые SSD

# В /etc/fstab:
/dev/sdb1 /data f2fs noatime,discard,inline_xattr 0 0
```

---

## 39.4 Bcachefs

### Новейшая ФС Linux (mainline с 6.7)

```
Особенности:
- Copy-on-Write
- Checksum всех данных
- Сжатие (lz4, gzip, zstd)
- Шифрование (ChaCha20/Poly1305)
- RAID 1/5/6
- Снапшоты
- Кэширование (bcache наследие)
```

```bash
# Создание
bcachefs format /dev/sdb1

# С шифрованием
bcachefs format --encrypted /dev/sdb1

# Монтирование
bcachefs mount /dev/sdb1 /mnt

# RAID1
bcachefs format --replicas=2 /dev/sdb /dev/sdc
```

---

## 39.5 OverlayFS

### Слоёная файловая система

OverlayFS объединяет несколько директорий в одну:

```
┌─────────────────────────────────────┐
│  merged (результат)                 │  ← /mnt/merged
├─────────────────────────────────────┤
│  upper (изменения, r/w)             │  ← /var/overlay/upper
├─────────────────────────────────────┤
│  lower (база, r/o)                  │  ← /var/overlay/lower
└─────────────────────────────────────┘
```

```bash
# Монтирование OverlayFS
mount -t overlay overlay \
    -o lowerdir=/var/overlay/lower,\
       upperdir=/var/overlay/upper,\
       workdir=/var/overlay/work \
    /mnt/merged

# Изменения в merged записываются в upper
# Lower остаётся неизменным
```

### Docker и OverlayFS

```bash
# Docker использует overlay2 по умолчанию
docker info | grep Storage

# Слои образа — это lower directories
# Контейнер записывает в upper
```

---

## 39.6 Специальные файловые системы

### tmpfs (RAM диск)

```bash
# Временные файлы в памяти
mount -t tmpfs -o size=2G tmpfs /mnt/ramdisk

# В fstab
tmpfs /tmp tmpfs defaults,noatime,mode=1777 0 0

# Проверка использования
df -h /tmp
```

### ramfs

```bash
# Без ограничения размера (осторожно!)
mount -t ramfs ramfs /mnt/ramdisk
```

### devtmpfs, sysfs, procfs

```bash
# Виртуальные ФС ядра
mount | grep -E 'devtmpfs|sysfs|proc'

devtmpfs on /dev type devtmpfs
sysfs on /sys type sysfs
proc on /proc type proc
```

---

## 39.7 Сетевые файловые системы

### NFS (Network File System)

```bash
# Сервер (exports)
echo "/data 192.168.1.0/24(rw,sync,no_subtree_check)" >> /etc/exports
exportfs -a
systemctl restart nfs-server

# Клиент
mount -t nfs server:/data /mnt
```

### CIFS/SMB

```bash
# Монтирование Windows share
mount -t cifs //server/share /mnt -o username=user,password=pass

# В fstab (с credentials файлом)
//server/share /mnt cifs credentials=/root/.smbcreds 0 0
```

### SSHFS

```bash
# Монтирование через SSH
sshfs user@server:/path /mnt

# Размонтирование
fusermount -u /mnt
```

---

## 39.8 Сравнение Linux ФС

| ФС | COW | Снапшоты | Сжатие | RAID | Для чего |
|----|-----|----------|--------|------|----------|
| ext4 | ❌ | ❌ | ❌ | ❌ | Универсальная |
| XFS | ❌ | ❌ | ❌ | ❌ | Большие файлы |
| Btrfs | ✅ | ✅ | ✅ | ✅ | Десктоп, NAS |
| F2FS | ❌ | ❌ | ✅ | ❌ | Flash/SSD |
| Bcachefs | ✅ | ✅ | ✅ | ✅ | Новое, экспериментальное |
| ZFS | ✅ | ✅ | ✅ | ✅ | Серверы, NAS |

### Рекомендации

| Сценарий | Рекомендация |
|----------|--------------|
| Сервер (стабильность) | ext4 или XFS |
| Desktop (снапшоты) | Btrfs |
| NAS (защита данных) | ZFS или Btrfs |
| SSD/Flash | F2FS или ext4 |
| Embedded | SquashFS + OverlayFS |
| Контейнеры | OverlayFS |

---

## 39.8 tmpfs и ramfs — файловые системы в RAM

Иногда файлы нужно хранить **только в оперативной памяти** — для скорости, безопасности или временных данных.

### tmpfs vs ramfs

| Характеристика | tmpfs | ramfs |
|---------------|-------|-------|
| Ограничение размера | ✅ Да (по умолчанию 50% RAM) | ❌ Нет (растёт бесконечно!) |
| Swap | ✅ Может свопиться на диск | ❌ Только RAM |
| Безопасность | Лучше (ограничен) | ⚠️ Может съесть всю память |
| Рекомендация | ✅ Используйте это | ❌ Только если точно знаете зачем |

### Типичные точки монтирования

| Путь | Тип | Назначение |
|------|-----|-----------|
| `/tmp` | Часто tmpfs | Временные файлы (очищается при перезагрузке) |
| `/dev/shm` | tmpfs | POSIX shared memory (IPC между процессами) |
| `/run` | tmpfs | PID-файлы, сокеты, runtime-данные |
| `/sys` | sysfs | Интерфейс к ядру (не RAM-диск, но виртуальная ФС) |
| `/proc` | procfs | Информация о процессах |

```bash
# Создать tmpfs вручную
sudo mount -t tmpfs -o size=2G tmpfs /mnt/ramdisk

# Проверить
df -h /mnt/ramdisk
# tmpfs     2.0G     0  2.0G   0% /mnt/ramdisk

# Запись — мгновенная
dd if=/dev/zero of=/mnt/ramdisk/test bs=1M count=500
# 524288000 bytes copied, 0.15 s, 3.4 GB/s  ← скорость RAM!
```

### Применение

**Ускорение сборок:**
```bash
# Компиляция в tmpfs — в разы быстрее
mkdir -p /mnt/ramdisk/build
cmake -B /mnt/ramdisk/build -S ./project
make -C /mnt/ramdisk/build -j$(nproc)
```

**Хранение секретов без записи на диск:**
```bash
# Секреты в tmpfs — не попадут на SSD/HDD
mount -t tmpfs -o size=10M,mode=0700 tmpfs /run/secrets
echo "API_KEY=sk-12345" > /run/secrets/env
source /run/secrets/env
# При перезагрузке — всё исчезает
```

**macOS: RAM-диск через diskutil:**
```bash
# Создать RAM-диск на 2 ГБ (2097152 блоков по 512 байт)
DISK=$(hdiutil attach -nomount ram://4194304)
diskutil erasevolume APFS "RAMDisk" $DISK

# Использовать
ls /Volumes/RAMDisk/

# Удалить
hdiutil detach $DISK
```

---

## 39.9 Сравнительная таблица файловых систем

| | ext4 | XFS | Btrfs | ZFS | APFS | NTFS |
|---|---|---|---|---|---|---|
| **ОС** | Linux | Linux | Linux | Linux/BSD | macOS | Windows |
| **Copy-on-Write** | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Снапшоты** | ❌ | ❌ | ✅ | ✅ | ✅ | VSS (ограниченно) |
| **Журналирование** | ✅ | ✅ | CoW | CoW | CoW | ✅ |
| **Компрессия** | ❌ | ❌ | ✅ (zstd, lzo) | ✅ (lz4, zstd) | ✅ (lzfse) | ✅ |
| **Дедупликация** | ❌ | ❌ | ⚠️ (offline) | ✅ (online) | ✅ (клоны) | ❌ |
| **RAID** | Внешний | Внешний | ✅ Встроенный | ✅ Встроенный | ❌ | Внешний |
| **Max файл** | 16 ТБ | 8 ЭБ | 16 ЭБ | 16 ЭБ | 8 ЭБ | 16 ТБ |
| **Max ФС** | 1 ЭБ | 8 ЭБ | 16 ЭБ | 256 ZB | 8 ЭБ | 256 ТБ |
| **Шифрование** | fscrypt | ❌ | ❌ | ✅ | ✅ | ✅ (EFS, BitLocker) |
| **Стабильность** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Сложность** | Простая | Простая | Средняя | Высокая | — (Apple) | — (Windows) |

!!! tip "Краткая рекомендация"
    - **Linux-сервер, проверенное решение** → ext4 или XFS
    - **Нужны снапшоты и сжатие** → Btrfs (если Linux) или ZFS
    - **Критичные данные, NAS** → ZFS
    - **macOS** → APFS (выбора нет, и это хорошо)
    - **Windows** → NTFS (или ReFS для серверов)

---

## Резюме

```
ext4     →  Стандарт Linux, стабильность
XFS      →  Большие файлы, параллельный I/O
Btrfs    →  Снапшоты, сжатие, современные возможности
F2FS     →  Оптимизация для flash
Bcachefs →  Новейшая CoW ФС, experimenting
tmpfs    →  Файлы в RAM (быстро, но потеря при перезагрузке)
overlay  →  Слоёная ФС для контейнеров
```

??? question "Упражнения"
    **Задание 1.** Смонтируйте tmpfs: `mount -t tmpfs -o size=100m tmpfs /mnt/ramdisk`. Запишите файлы, замерьте скорость. Что произойдёт при перезагрузке?
    
    **Задание 2.** Создайте overlayfs из двух директорий (lower + upper). Измените файл — где сохранятся изменения? Как Docker использует этот механизм?
    
    **Задание 3.** Если доступен Bcachefs или F2FS: создайте ФС на loop-устройстве, сравните скорость с ext4 для мелких файлов.
