# Глава 38. Файловые системы BSD

## Введение

Семейство BSD (FreeBSD, OpenBSD, NetBSD, DragonFly BSD) имеет богатую историю развития файловых систем. От классической UFS до современной HAMMER2 — BSD-системы предлагают надёжные и инновационные решения.

---

## 38.1 UFS2 (Unix File System 2)

### Особенности UFS2

UFS2 — основная файловая система FreeBSD, эволюция Berkeley FFS:

- **64-битные указатели** (поддержка больших дисков)
- **Наносекундные timestamps**
- **Extended attributes**
- **Soft Updates** (альтернатива журналированию)
- **Journaled Soft Updates (SU+J)** — комбинация

### Структура UFS2

```
┌────────────────────────────────────────┐
│  Boot Block                            │
├────────────────────────────────────────┤
│  Superblock                            │
├────────────────────────────────────────┤
│  Cylinder Group 0                      │
│  ├── CG Header                         │
│  ├── Inode Bitmap                      │
│  ├── Block Bitmap                      │
│  ├── Inode Table                       │
│  └── Data Blocks                       │
├────────────────────────────────────────┤
│  Cylinder Group 1...N                  │
└────────────────────────────────────────┘
```

### Soft Updates

Soft Updates обеспечивают целостность без традиционного журнала:

```
                Metadata Update Sequence
                ─────────────────────────
Создание файла:
1. Выделить inode                ──▶ записать inode
2. Добавить запись в каталог     ──▶ записать directory
3. Выделить блоки данных         ──▶ записать данные

Soft Updates гарантирует порядок: 1 → 2 → 3
При сбое: возможны "потерянные" inode, но нет повреждений
```

### Работа с UFS2

```bash
# Создание UFS2
newfs -U /dev/da0p1           # с Soft Updates
newfs -j /dev/da0p1           # с журналом (SU+J)

# Параметры
newfs -b 32768 -f 4096 /dev/da0p1  # размер блока/фрагмента

# Монтирование
mount /dev/da0p1 /mnt

# Включение/выключение Soft Updates
tunefs -n enable /dev/da0p1   # включить SU
tunefs -j enable /dev/da0p1   # включить журнал

# Проверка
fsck_ufs /dev/da0p1
fsck_ufs -y /dev/da0p1        # автоисправление

# Информация
dumpfs /dev/da0p1 | head -50
```

### Снапшоты UFS2

```bash
# Создание снапшота
mount -u -o snapshot /mnt/.snap/backup /mnt

# Или через mksnap_ffs
mksnap_ffs /mnt /mnt/.snap/backup

# Монтирование снапшота (только чтение)
mdconfig -a -t vnode -f /mnt/.snap/backup -u 0
mount -r /dev/md0 /mnt/snapshot

# Удаление
rm /mnt/.snap/backup
```

---

## 38.2 ZFS в FreeBSD

FreeBSD имеет первоклассную поддержку ZFS (см. главу 40 для подробностей):

```bash
# Создание пула
zpool create tank /dev/da1

# Создание датасета
zfs create tank/data

# Снапшот
zfs snapshot tank/data@backup

# Boot environments
bectl create upgrade
bectl activate upgrade
```

---

## 38.3 OpenBSD: FFS и softdep

### Особенности OpenBSD FFS

OpenBSD использует собственную версию FFS с фокусом на безопасность:

- **KARL** (Kernel Address Randomized Link)
- **W^X** (Write XOR Execute)
- **Pledge/Unveil** ограничения

```bash
# Создание FFS
newfs /dev/sd0a

# С soft dependencies
newfs -O 2 /dev/sd0a
mount -o softdep /dev/sd0a /mnt

# disklabel для разметки
disklabel -E sd0
```

### fstab в OpenBSD

```bash
# /etc/fstab
/dev/sd0a  /     ffs  rw,softdep  1  1
/dev/sd0b  none  swap sw          0  0
/dev/sd0d  /home ffs  rw,softdep,nodev,nosuid  1  2
```

---

## 38.4 NetBSD: FFS и LFS

### LFS (Log-structured File System)

NetBSD поддерживает экспериментальную LFS:

```
Традиционная ФС:          LFS:
┌─────────────────┐       ┌─────────────────┐
│ Superblock      │       │ Superblock      │
│ Inode Table     │       │ Checkpoint      │
│ Data Block 1    │       │ Segment 1       │
│ Data Block 2    │       │   (inode+data)  │
│ ...             │       │ Segment 2       │
│ Data Block N    │       │   (inode+data)  │
└─────────────────┘       └─────────────────┘

Все записи последовательные → отлично для SSD
```

```bash
# Создание LFS
newfs_lfs /dev/wd0a

# Монтирование (требуется lfs_cleanerd)
mount -t lfs /dev/wd0a /mnt
```

### WAPBL (Write Ahead Physical Block Logging)

NetBSD FFS с журналированием:

```bash
# Создание FFS с журналом
newfs -O 2 /dev/wd0a
tunefs -l enable /dev/wd0a

# Монтирование
mount -o log /dev/wd0a /mnt
```

---

## 38.5 DragonFly BSD: HAMMER и HAMMER2

### HAMMER

```
Особенности:
- Copy-on-write
- Встроенные снапшоты
- Кластеризация
- Дедупликация
- Checksum данных
```

```bash
# Создание HAMMER
newfs_hammer -L DATA /dev/da0s1

# Монтирование
mount -t hammer /dev/da0s1 /mnt

# Снапшоты (автоматические каждые 60 секунд)
ls /mnt/@@-1h    # час назад
ls /mnt/@@-1d    # день назад
```

### HAMMER2

Современная ФС DragonFly BSD:

```
Улучшения над HAMMER:
- Лучшая производительность
- Встроенное сжатие (LZ4, ZLIB)
- Дедупликация на лету
- Кластеризация
- Checksum (xxhash64)
```

```bash
# Создание HAMMER2
newfs_hammer2 -L SYSTEM /dev/da0s1

# Монтирование
mount -t hammer2 /dev/da0s1 /mnt

# Снапшоты
hammer2 -s /mnt pfs-snapshot mysnap
```

---

## 38.6 Сравнение BSD файловых систем

| ФС | BSD | Журнал | Снапшоты | CoW | Max Size |
|----|-----|--------|----------|-----|----------|
| UFS2 | FreeBSD | SU+J | ✅ | ❌ | 32 PB |
| FFS | OpenBSD | Soft dep | ❌ | ❌ | 16 TB |
| FFS/WAPBL | NetBSD | ✅ | ❌ | ❌ | 8 EB |
| LFS | NetBSD | Log-based | ❌ | ❌ | Exp. |
| HAMMER | DragonFly | ✅ | ✅ | ✅ | 1 EB |
| HAMMER2 | DragonFly | ✅ | ✅ | ✅ | 1 EB |
| ZFS | FreeBSD | ✅ | ✅ | ✅ | 256 ZB |

### Рекомендации

| Сценарий | Рекомендация |
|----------|--------------|
| FreeBSD сервер | ZFS |
| FreeBSD desktop | UFS2 с SU+J или ZFS |
| OpenBSD (безопасность) | FFS с softdep |
| NetBSD (совместимость) | FFS с WAPBL |
| DragonFly (производительность) | HAMMER2 |

---

## 38.7 APFS — Apple File System

APFS (2017) заменила HFS+ на всех устройствах Apple (macOS, iOS, watchOS, tvOS). Хотя macOS имеет BSD-корни, APFS — полностью оригинальная разработка Apple.

### Архитектура: контейнеры и тома

В отличие от традиционных ФС, где один раздел = одна ФС, APFS использует **контейнеры**:

```text
┌─────────────────────────────────────────────┐
│ APFS Container (весь SSD или раздел)        │
│ Общий пул свободного пространства           │
│                                             │
│ ┌───────────┐ ┌───────────┐ ┌─────────────┐ │
│ │ Volume 1  │ │ Volume 2  │ │ Volume 3    │ │
│ │ "Macintosh│ │ "Data"    │ │ "Preboot"   │ │
│ │  HD"      │ │           │ │             │ │
│ │ 50 ГБ     │ │ 200 ГБ    │ │ 1 ГБ        │ │
│ └───────────┘ └───────────┘ └─────────────┘ │
│           ↕ Место делится динамически ↕     │
└─────────────────────────────────────────────┘
```

Тома **не имеют фиксированного размера** — пространство распределяется из общего пула контейнера.

### Клоны файлов (Clones)

Копирование файла в APFS — **мгновенная операция** (O(1), независимо от размера):

```bash
# Клонирование (мгновенно, даже для файла в 10 ГБ)
cp -c large_file.iso clone.iso   # macOS: -c = clone

# Проверка: оба файла занимают место ОДНОГО
diskutil apfs list  # Показывает "Cloned" usage
```

При клонировании копируются только **метаданные**. Данные копируются позже — только при **изменении** (Copy-on-Write).

### Снапшоты

```bash
# Создать снапшот
tmutil localsnapshot

# Список снапшотов
tmutil listlocalsnapshots /

# Удалить
tmutil deletelocalsnapshots 2024-01-15-120000
```

Time Machine использует APFS-снапшоты для мгновенных локальных бэкапов.

### Сравнение с HFS+

| Характеристика | HFS+ | APFS |
|---------------|------|------|
| Copy-on-Write | ❌ | ✅ |
| Клоны файлов | ❌ | ✅ (мгновенно) |
| Снапшоты | ❌ | ✅ |
| Шифрование | FileVault (поверх) | **Встроенное** (per-volume/per-file) |
| Timestamps | 1 секунда | **Наносекунды** |
| Crash protection | Журнал | **CoW** (не нужен журнал) |
| SSD-оптимизация | Нет | TRIM, space sharing |
| Max файл | 8 ЭБ | 8 ЭБ |

!!! info "Почему нет APFS для Linux?"
    APFS — закрытый формат Apple. Существует read-only драйвер `apfs-fuse` (FUSE), но полная поддержка записи отсутствует. Для обмена данными между macOS и Linux используйте exFAT.

---

## Резюме

```
UFS2      →  Классическая BSD ФС, Soft Updates
OpenBSD   →  Безопасность превыше всего
NetBSD    →  Переносимость, экспериментальная LFS
HAMMER2   →  Современная CoW ФС для DragonFly
ZFS       →  Лучший выбор для FreeBSD серверов
```

??? question "Упражнения"
    **Задание 1.** Если доступна FreeBSD (или VM): создайте ZFS pool из одного диска. Создайте dataset и снапшот.
    
    **Задание 2.** Сравните UFS2 (FreeBSD) и ext4 (Linux) по возможностям: журналирование, максимальный размер файла, soft updates vs journal.
    
    **Задание 3.** Объясните концепцию soft updates в FFS/UFS2. Чем она отличается от традиционного журналирования?
