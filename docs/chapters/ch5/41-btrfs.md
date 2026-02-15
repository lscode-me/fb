# Глава 41. Btrfs — CoW файловая система Linux

## Введение

**Btrfs** (B-tree File System) — современная copy-on-write файловая система для Linux. Это "родной" ответ Linux на ZFS, интегрированный в ядро с 2009 года.

---

## 41.1 Зачем Btrfs?

### Проблемы традиционных ФС

```
ext4 / XFS:
❌ Нет встроенных снапшотов
❌ Нет проверки целостности данных
❌ Нет встроенного RAID
❌ Нет сжатия
❌ Сложное управление (LVM + mdadm + ФС)
```

### Решения Btrfs

```
Btrfs:
✅ Мгновенные снапшоты (Copy-on-Write)
✅ Checksum всех данных и метаданных
✅ Встроенный RAID (0, 1, 10, 5, 6)
✅ Прозрачное сжатие (zstd, lzo, zlib)
✅ Subvolumes (логические разделы)
✅ Send/receive (репликация)
✅ Online resize, defrag, scrub
```

---

## 41.2 Базовые концепции

### Copy-on-Write (CoW)

```
Традиционная ФС:                  Btrfs (CoW):
┌─────────────┐                   ┌─────────────┐
│ Блок A      │                   │ Блок A      │
│ "Старые     │  ──перезапись──▶  │ "Новые      │
│  данные"    │                   │  данные"    │
└─────────────┘                   └─────────────┘

                                  ┌─────────────┐
                                  │ Блок A      │
                                  │ "Старые     │  ← остаётся
                                  │  данные"    │
                                  └─────────────┘
                                  ┌─────────────┐
                                  │ Блок B      │  ← новый блок
                                  │ "Новые      │
                                  │  данные"    │
                                  └─────────────┘
                                  Указатель: A → B

Преимущества CoW:
- Атомарные обновления
- Снапшоты бесплатны
- Нет потери данных при сбое
```

### Subvolumes

```
Btrfs Volume:
├── @ (root subvolume)           → /
├── @home                        → /home
├── @var                         → /var
├── @snapshots                   → /.snapshots
│   ├── @-2024-01-15
│   └── @home-2024-01-15
└── @swap                        → /swap (nodatacow)
```

---

## 41.3 Создание и монтирование

### Создание Btrfs

```bash
# Простое создание
mkfs.btrfs /dev/sdb

# С меткой
mkfs.btrfs -L "DATA" /dev/sdb

# На нескольких дисках (RAID0 для данных, RAID1 для метаданных)
mkfs.btrfs -d raid0 -m raid1 /dev/sdb /dev/sdc

# RAID1 (зеркало)
mkfs.btrfs -d raid1 -m raid1 /dev/sdb /dev/sdc

# Mixed mode (для малых дисков < 16GB)
mkfs.btrfs --mixed /dev/sdb
```

### Монтирование

```bash
# Базовое монтирование
mount /dev/sdb /mnt

# Со сжатием
mount -o compress=zstd /dev/sdb /mnt

# Рекомендуемые опции
mount -o noatime,compress=zstd:3,space_cache=v2 /dev/sdb /mnt

# Монтирование subvolume
mount -o subvol=@home /dev/sdb /home
mount -o subvolid=258 /dev/sdb /var
```

### /etc/fstab

```bash
# Btrfs с subvolumes
UUID=xxxxx  /         btrfs  noatime,compress=zstd,subvol=@        0  0
UUID=xxxxx  /home     btrfs  noatime,compress=zstd,subvol=@home    0  0
UUID=xxxxx  /var      btrfs  noatime,compress=zstd,subvol=@var     0  0
UUID=xxxxx  /.snapshots btrfs noatime,compress=zstd,subvol=@snapshots 0 0
```

---

## 41.4 Subvolumes

### Управление subvolumes

```bash
# Создание
btrfs subvolume create /mnt/@
btrfs subvolume create /mnt/@home
btrfs subvolume create /mnt/@var

# Список
btrfs subvolume list /mnt
btrfs subvolume list -a /mnt

# Удаление
btrfs subvolume delete /mnt/@old

# Установка по умолчанию
btrfs subvolume set-default 256 /mnt
```

### Типичная структура для Linux

```bash
# Создание структуры
mount /dev/sdb /mnt

btrfs subvolume create /mnt/@
btrfs subvolume create /mnt/@home
btrfs subvolume create /mnt/@var
btrfs subvolume create /mnt/@snapshots

# В /etc/fstab монтируем каждый subvolume отдельно
```

---

## 41.5 Снапшоты

### Создание снапшотов

```bash
# Обычный снапшот (r/w)
btrfs subvolume snapshot /mnt/@ /mnt/@snapshots/@-$(date +%Y%m%d)

# Read-only снапшот
btrfs subvolume snapshot -r /mnt/@ /mnt/@snapshots/@-$(date +%Y%m%d)

# Рекурсивный снапшот (все вложенные subvolumes)
# Btrfs не поддерживает напрямую — используйте скрипт
```

### Восстановление из снапшота

```bash
# Вариант 1: Откат (замена текущего на снапшот)
mv /mnt/@ /mnt/@.old
btrfs subvolume snapshot /mnt/@snapshots/@-20240115 /mnt/@
# Перезагрузка

# Вариант 2: Восстановление конкретных файлов
cp /mnt/@snapshots/@-20240115/path/to/file /mnt/@/path/to/file
```

### Автоматические снапшоты (Snapper)

```bash
# Установка
apt install snapper  # или yum install snapper

# Конфигурация для root
snapper -c root create-config /

# Настройка
snapper -c root set-config "TIMELINE_CREATE=yes"
snapper -c root set-config "TIMELINE_CLEANUP=yes"

# Список снапшотов
snapper -c root list

# Сравнение
snapper -c root diff 10..11

# Восстановление
snapper -c root undochange 10..11
```

---

## 41.6 RAID в Btrfs

### Типы RAID

| Тип | Описание | Min дисков | Потеря ёмкости |
|-----|----------|------------|----------------|
| single | Без избыточности | 1 | 0% |
| dup | Дублирование на одном диске | 1 | 50% |
| raid0 | Stripe (скорость) | 2+ | 0% |
| raid1 | Mirror (надёжность) | 2+ | 50% |
| raid10 | Stripe of mirrors | 4+ | 50% |
| raid5 | Parity (осторожно!) | 3+ | 1 диск |
| raid6 | Double parity (осторожно!) | 4+ | 2 диска |

### Создание RAID

```bash
# RAID1
mkfs.btrfs -d raid1 -m raid1 /dev/sdb /dev/sdc

# RAID10
mkfs.btrfs -d raid10 -m raid10 /dev/sd{b,c,d,e}

# RAID5 (ОСТОРОЖНО - была проблема write hole)
mkfs.btrfs -d raid5 -m raid1 /dev/sd{b,c,d}
```

### Добавление и удаление дисков

```bash
# Добавить диск
btrfs device add /dev/sdd /mnt

# Перебалансировать на новый диск
btrfs balance start -dconvert=raid1 -mconvert=raid1 /mnt

# Удалить диск
btrfs device remove /dev/sdb /mnt

# Замена неисправного диска
btrfs replace start /dev/sdb /dev/sde /mnt
btrfs replace status /mnt
```

---

## 41.7 Сжатие

### Типы сжатия

| Алгоритм | Скорость | Степень сжатия | Когда использовать |
|----------|----------|----------------|-------------------|
| lzo | Очень быстро | Низкая | CPU-bound нагрузки |
| zlib | Медленно | Высокая | Архивы |
| zstd | Быстро | Высокая | Универсальное (рекомендуется) |

### Настройка сжатия

```bash
# При монтировании
mount -o compress=zstd /dev/sdb /mnt

# Уровень zstd (1-15)
mount -o compress=zstd:3 /dev/sdb /mnt  # баланс
mount -o compress=zstd:15 /dev/sdb /mnt # максимум

# Принудительное сжатие всего
mount -o compress-force=zstd /dev/sdb /mnt

# Сжатие существующих файлов
btrfs filesystem defragment -r -v -czstd /mnt
```

### Проверка эффективности

```bash
# Общая статистика
btrfs filesystem df /mnt

# Подробно
compsize /mnt  # требует compsize утилиту
```

---

## 41.8 Проверка и обслуживание

### Scrub

```bash
# Проверка целостности (online)
btrfs scrub start /mnt
btrfs scrub status /mnt

# В cron (еженедельно)
0 2 * * 0 /sbin/btrfs scrub start /
```

### Balance

```bash
# Перераспределение данных
btrfs balance start /mnt

# Только данные
btrfs balance start -dusage=50 /mnt

# Статус
btrfs balance status /mnt

# Отмена
btrfs balance cancel /mnt
```

### Defrag

```bash
# Дефрагментация файла
btrfs filesystem defragment /mnt/file

# Рекурсивная дефрагментация
btrfs filesystem defragment -r /mnt

# С сжатием
btrfs filesystem defragment -r -czstd /mnt
```

### Check

```bash
# Проверка (только unmounted!)
btrfs check /dev/sdb

# Repair (осторожно!)
btrfs check --repair /dev/sdb
```

---

## 41.9 Send/Receive

### Репликация снапшотов

```bash
# Локальная репликация
btrfs send /mnt/@snapshots/@-20240115 | btrfs receive /backup/

# Инкрементальная репликация
btrfs send -p /mnt/@snapshots/@-20240114 /mnt/@snapshots/@-20240115 \
    | btrfs receive /backup/

# По SSH
btrfs send /mnt/@snapshots/@-20240115 | ssh backup_server btrfs receive /backup/

# Со сжатием
btrfs send /mnt/@snapshots/@-20240115 | zstd | \
    ssh server "zstd -d | btrfs receive /backup/"
```

---

## 41.10 Дедупликация

```bash
# Btrfs не имеет встроенной дедупликации в реальном времени
# Используйте offline дедупликаторы:

# duperemove
duperemove -dr /mnt

# bees (background deduplication)
# Более сложная настройка, работает как сервис
```

---

## 41.11 Btrfs vs ZFS

| Аспект | Btrfs | ZFS |
|--------|-------|-----|
| В ядре Linux | Да | Нет (DKMS/kmod) |
| Лицензия | GPL | CDDL |
| RAID5/6 | Проблемы | Стабильно |
| RAM требования | Низкие | Высокие |
| Деdup in-line | Нет | Да |
| ARC кэш | Нет | Да |
| Зрелость | Средняя | Высокая |
| Send/receive | Да | Да |
| Шифрование | Планируется | Да |

---

## Резюме

```
Btrfs = CoW + Snapshots + RAID + Compression + Subvolumes
      = "Родная" продвинутая ФС Linux
```

**Рекомендации:**

| Сценарий | Рекомендация |
|----------|--------------|
| Desktop | ✅ Рекомендуется |
| Сервер (данные) | ⚠️ С осторожностью |
| NAS | ✅ Хороший выбор |
| RAID5/6 | ❌ Не рекомендуется |
| Снапшоты | ✅ Отлично |

```bash
# Минимальная проверка здоровья
btrfs device stats /mnt
```

??? question "Упражнения"
    **Задание 1.** Создайте Btrfs на loop-устройстве. Создайте subvolume и снапшот. Измените файл в оригинале — изменится ли снапшот?
    
    **Задание 2.** Включите сжатие (`mount -o compress=zstd`). Скопируйте данные и сравните `compsize` — какой коэффициент сжатия?
    
    **Задание 3.** Отправьте снапшот на другой диск через `btrfs send | btrfs receive`. Это основа инкрементальных бэкапов — объясните механизм.
