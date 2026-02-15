# Глава 42. mdadm — программный RAID в Linux

## Введение

**mdadm** (Multiple Disk Admin) — стандартный инструмент Linux для создания и управления программными RAID-массивами. Работает на уровне блочных устройств, ниже файловой системы.

---

## 42.1 Уровни RAID

### Основные уровни

```
RAID 0 (Stripe):
┌─────┬─────┬─────┬─────┐
│  A1 │  A2 │  A3 │  A4 │  Данные разбиваются на полосы
├─────┼─────┼─────┼─────┤
│ Disk1    │ Disk2     │
└──────────┴───────────┘
+ Максимальная скорость
+ Полная ёмкость (N дисков)
- Нет избыточности (потеря любого диска = потеря всего)

RAID 1 (Mirror):
┌─────────────┬─────────────┐
│     A1      │     A1      │  Полное дублирование
│     A2      │     A2      │
│     A3      │     A3      │
├─────────────┼─────────────┤
│   Disk 1    │   Disk 2    │
└─────────────┴─────────────┘
+ Высокая надёжность
+ Быстрое чтение
- 50% потеря ёмкости

RAID 5 (Striping with parity):
┌─────┬─────┬─────┐
│  A1 │  A2 │ Ap  │  Ap = A1 XOR A2 (parity)
│  B1 │ Bp  │  B2 │  Parity распределена
│ Cp  │  C1 │  C2 │
├─────┼─────┼─────┤
│ Disk1│Disk2│Disk3│
└─────┴─────┴─────┘
+ Баланс скорости и надёжности
+ Ёмкость: (N-1) дисков
- Долгая перестройка при замене диска

RAID 6 (Double parity):
┌─────┬─────┬─────┬─────┐
│  A1 │  A2 │ Ap  │ Aq  │  Два блока чётности
│  B1 │ Bp  │ Bq  │  B2 │
├─────┼─────┼─────┼─────┤
│Disk1│Disk2│Disk3│Disk4│
└─────┴─────┴─────┴─────┘
+ Переживает потерю 2 дисков
+ Ёмкость: (N-2) дисков
- Медленнее RAID5 на запись

RAID 10 (Stripe of mirrors):
┌─────────────────────────────────┐
│       RAID 0 (stripe)           │
│  ┌─────────┐    ┌─────────┐     │
│  │ RAID 1  │    │ RAID 1  │     │
│  │┌───┬───┐│    │┌───┬───┐│     │
│  ││ D1│ D2││    ││ D3│ D4││     │
│  │└───┴───┘│    │└───┴───┘│     │
│  └─────────┘    └─────────┘     │
└─────────────────────────────────┘
+ Высокая скорость + надёжность
- 50% потеря ёмкости
```

### Сравнение уровней

| Уровень | Min дисков | Избыточность | Ёмкость | Чтение | Запись |
|---------|------------|--------------|---------|--------|--------|
| RAID 0 | 2 | ❌ | N | ⬆⬆ | ⬆⬆ |
| RAID 1 | 2 | 1 диск | N/2 | ⬆⬆ | ➡ |
| RAID 5 | 3 | 1 диск | N-1 | ⬆ | ➡ |
| RAID 6 | 4 | 2 диска | N-2 | ⬆ | ⬇ |
| RAID 10 | 4 | 1 на пару | N/2 | ⬆⬆ | ⬆ |

---

## 42.2 Создание RAID массивов

### RAID 1 (зеркало)

```bash
# Создание RAID1
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc

# Проверка
cat /proc/mdstat
mdadm --detail /dev/md0

# Форматирование
mkfs.ext4 /dev/md0

# Монтирование
mount /dev/md0 /mnt
```

### RAID 5

```bash
# Создание RAID5 (минимум 3 диска)
mdadm --create /dev/md0 --level=5 --raid-devices=3 \
    /dev/sdb /dev/sdc /dev/sdd

# С горячим резервом
mdadm --create /dev/md0 --level=5 --raid-devices=3 \
    --spare-devices=1 \
    /dev/sdb /dev/sdc /dev/sdd /dev/sde
```

### RAID 6

```bash
# Создание RAID6 (минимум 4 диска)
mdadm --create /dev/md0 --level=6 --raid-devices=4 \
    /dev/sdb /dev/sdc /dev/sdd /dev/sde
```

### RAID 10

```bash
# Создание RAID10 (минимум 4 диска)
mdadm --create /dev/md0 --level=10 --raid-devices=4 \
    /dev/sdb /dev/sdc /dev/sdd /dev/sde

# Nested RAID10 (вручную)
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc
mdadm --create /dev/md1 --level=1 --raid-devices=2 /dev/sdd /dev/sde
mdadm --create /dev/md2 --level=0 --raid-devices=2 /dev/md0 /dev/md1
```

---

## 42.3 Сохранение конфигурации

```bash
# Сохранить конфигурацию
mdadm --detail --scan >> /etc/mdadm/mdadm.conf

# Обновить initramfs
update-initramfs -u

# Пример /etc/mdadm/mdadm.conf:
ARRAY /dev/md0 metadata=1.2 UUID=xxxxxxxx:xxxxxxxx:xxxxxxxx:xxxxxxxx
```

### /etc/fstab

```bash
# Монтирование по UUID (рекомендуется)
UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx /data ext4 defaults 0 2

# Или по имени устройства
/dev/md0 /data ext4 defaults 0 2
```

---

## 42.4 Мониторинг

### Статус массива

```bash
# Быстрый статус
cat /proc/mdstat

# Пример вывода:
Personalities : [raid1] [raid5]
md0 : active raid5 sdb[0] sdc[1] sdd[2]
      1953382400 blocks super 1.2 level 5, 512k chunk, algorithm 2 [3/3] [UUU]

# Подробности
mdadm --detail /dev/md0

# Информация о диске
mdadm --examine /dev/sdb
```

### Мониторинг в реальном времени

```bash
# Следить за синхронизацией
watch cat /proc/mdstat

# mdadm monitor daemon
mdadm --monitor --daemonise --mail=root@localhost /dev/md0
```

---

## 42.5 Замена дисков

### Симуляция отказа

```bash
# Отметить диск как неисправный
mdadm --manage /dev/md0 --fail /dev/sdb

# Удалить неисправный диск
mdadm --manage /dev/md0 --remove /dev/sdb
```

### Замена диска

```bash
# 1. Отметить неисправный
mdadm --manage /dev/md0 --fail /dev/sdb

# 2. Удалить
mdadm --manage /dev/md0 --remove /dev/sdb

# 3. Физически заменить диск

# 4. Добавить новый
mdadm --manage /dev/md0 --add /dev/sdf

# 5. Следить за перестройкой
watch cat /proc/mdstat
```

### Горячий резерв

```bash
# Добавить spare
mdadm --manage /dev/md0 --add-spare /dev/sdf

# При отказе диска spare автоматически заменит его
```

---

## 42.6 Расширение массива

### Добавление диска в RAID 5

```bash
# Добавить диск
mdadm --manage /dev/md0 --add /dev/sdf

# Увеличить количество устройств
mdadm --grow /dev/md0 --raid-devices=4

# Дождаться reshaping
watch cat /proc/mdstat

# Расширить файловую систему
resize2fs /dev/md0      # ext4
xfs_growfs /mountpoint  # XFS
```

---

## 42.7 Сборка и восстановление

### Сборка массива

```bash
# Автоматическая сборка
mdadm --assemble --scan

# Ручная сборка
mdadm --assemble /dev/md0 /dev/sdb /dev/sdc /dev/sdd

# Принудительная сборка (с degraded)
mdadm --assemble --force /dev/md0 /dev/sdb /dev/sdc
```

### Восстановление после сбоя

```bash
# Посмотреть superblock
mdadm --examine /dev/sdb

# Проверить UUID
mdadm --examine /dev/sdb | grep UUID

# Собрать по UUID
mdadm --assemble /dev/md0 --uuid=xxxxxxxx:xxxxxxxx:xxxxxxxx:xxxxxxxx
```

---

## 42.8 Производительность

### Настройка chunk size

```bash
# При создании (по умолчанию 512K)
mdadm --create /dev/md0 --level=5 --chunk=256 ...

# Оптимальный chunk зависит от нагрузки:
# - Большие файлы: 512K - 1M
# - Мелкие файлы/БД: 64K - 128K
```

### Stripe cache

```bash
# Увеличить кэш stripe (для RAID5/6)
echo 8192 > /sys/block/md0/md/stripe_cache_size

# В /etc/sysctl.conf
echo 'dev.raid.speed_limit_min = 50000' >> /etc/sysctl.conf
echo 'dev.raid.speed_limit_max = 200000' >> /etc/sysctl.conf
```

### Bitmap

```bash
# Включить bitmap для быстрой ресинхронизации
mdadm --grow /dev/md0 --bitmap=internal

# При частых перезагрузках значительно ускоряет resync
```

---

## 42.9 Практические сценарии

### Домашний NAS (RAID5)

```bash
# Создание
mdadm --create /dev/md0 --level=5 --raid-devices=4 \
    /dev/sd{b,c,d,e}

# Форматирование
mkfs.ext4 -E stride=128,stripe-width=384 /dev/md0

# stride = chunk_size / block_size = 512K / 4K = 128
# stripe-width = stride * (N-1) = 128 * 3 = 384

# Монтирование
mount -o noatime /dev/md0 /storage
```

### Сервер БД (RAID10)

```bash
# RAID10 для максимальной производительности
mdadm --create /dev/md0 --level=10 --raid-devices=4 \
    --chunk=64 /dev/sd{b,c,d,e}

mkfs.xfs /dev/md0
mount -o noatime,nodiratime /dev/md0 /var/lib/mysql
```

---

## 42.10 mdadm vs ZFS/Btrfs

| Аспект | mdadm | ZFS/Btrfs |
|--------|-------|-----------|
| Уровень | Блочные устройства | Интегрированная ФС |
| Checksums | ❌ | ✅ |
| Снапшоты | ❌ | ✅ |
| Сжатие | ❌ | ✅ |
| Write hole | ✅ (с bitmap) | ❌ (CoW) |
| Зрелость | Высокая | Средняя/Высокая |
| Простота | Средняя | Высокая |

---

## Резюме

```bash
# Создание
mdadm --create /dev/md0 --level=X --raid-devices=N /dev/sd...

# Мониторинг
cat /proc/mdstat
mdadm --detail /dev/md0

# Управление
mdadm --manage /dev/md0 --fail|--remove|--add /dev/sdX

# Сохранение
mdadm --detail --scan >> /etc/mdadm/mdadm.conf
update-initramfs -u
```

| Сценарий | Рекомендуемый уровень |
|----------|----------------------|
| Максимальная скорость | RAID 0 |
| Важные данные (2 диска) | RAID 1 |
| Сервер (3+ диска) | RAID 5 или RAID 6 |
| База данных | RAID 10 |

??? question "Упражнения"
    **Задание 1.** Создайте RAID 1 из двух loop-устройств: `mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/loop0 /dev/loop1`. Проверьте статус.
    
    **Задание 2.** Симулируйте отказ диска: `mdadm --fail /dev/md0 /dev/loop1`. Проверьте, что данные доступны. Замените диск и пересоберите.
    
    **Задание 3.** Рассчитайте: сколько дисков из 5×1 ТБ будет доступно для данных при RAID 0, 1, 5, 6, 10?
