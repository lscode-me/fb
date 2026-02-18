---
title: ZFS — руководство по файловой системе
description: ZFS файловая система: pools, datasets, snapshots, репликация. Установка ZFS на Linux, настройка RAID-Z, практические примеры.hide:
  - title---

# Глава 40. ZFS — файловая система будущего

## Введение

**ZFS** (Zettabyte File System) — это революционная файловая система, объединяющая функции ФС и менеджера томов. Разработана Sun Microsystems в 2005 году, сейчас развивается как OpenZFS.

---

## 40.1 Философия ZFS

### Проблемы традиционных ФС

```
Традиционный стек:
┌─────────────────────┐
│  Файловая система   │  ext4, XFS
├─────────────────────┤
│  Менеджер томов     │  LVM
├─────────────────────┤
│  RAID               │  mdadm
├─────────────────────┤
│  Диски              │  /dev/sda, /dev/sdb
└─────────────────────┘

Проблемы:
- Раздельное управление
- Нет сквозной проверки целостности
- Silent data corruption
```

### Подход ZFS

```
ZFS стек:
┌─────────────────────────────────────┐
│  ZFS (всё в одном)                  │
│  ├── Файловая система               │
│  ├── Менеджер томов                 │
│  ├── RAID (RAIDZ1, Z2, Z3)          │
│  ├── Checksums (все данные)         │
│  ├── Сжатие (lz4, zstd)             │
│  ├── Шифрование (AES-256-GCM)       │
│  └── Снапшоты (мгновенные)          │
├─────────────────────────────────────┤
│  Диски (vdevs)                      │
└─────────────────────────────────────┘
```

---

## 40.2 Концепции ZFS

### Pool (Пул)

```
Pool = коллекция vdevs
     = единое пространство хранения

         ┌─────────────────────────────┐
         │         POOL "tank"         │
         ├─────────────────────────────┤
         │  vdev (mirror)   vdev (raidz1)
         │  ┌─────────┐     ┌──────────┐
         │  │ sda sdb │     │sdc sdd sde│
         │  └─────────┘     └──────────┘
         └─────────────────────────────┘
```

### vdev (Virtual Device)

Типы vdevs:

| Тип | Описание | Пример |
|-----|----------|--------|
| disk | Один диск | /dev/sda |
| mirror | Зеркало (RAID1) | mirror sda sdb |
| raidz1 | RAID5 аналог | raidz1 sda sdb sdc |
| raidz2 | RAID6 аналог | raidz2 sda sdb sdc sdd |
| raidz3 | Тройная чётность | raidz3 sda sdb sdc sdd sde |
| spare | Горячий резерв | spare sdf |
| log | ZIL (write log) | log nvme0n1 |
| cache | L2ARC (read cache) | cache nvme0n2 |

### Dataset

```
Датасеты в пуле:
tank
├── tank/home          (filesystem)
├── tank/vm            (filesystem)
│   └── tank/vm/win10  (zvol для VM)
├── tank/backup        (filesystem)
└── tank/docker        (filesystem)
```

---

## 40.3 Создание и управление пулами

### Создание пула

```bash
# Простой пул (один диск)
zpool create tank /dev/sdb

# Зеркало (RAID1)
zpool create tank mirror /dev/sdb /dev/sdc

# RAIDZ1 (RAID5 аналог)
zpool create tank raidz1 /dev/sdb /dev/sdc /dev/sdd

# RAIDZ2 (RAID6 аналог)
zpool create tank raidz2 /dev/sdb /dev/sdc /dev/sdd /dev/sde

# Stripe зеркал (RAID10)
zpool create tank \
    mirror /dev/sdb /dev/sdc \
    mirror /dev/sdd /dev/sde
```

### Управление пулом

```bash
# Статус пула
zpool status
zpool status tank

# Список пулов
zpool list

# Добавление vdev
zpool add tank mirror /dev/sdf /dev/sdg

# Удаление vdev (ZFS 0.8+)
zpool remove tank /dev/sdf

# Замена диска
zpool replace tank /dev/sdb /dev/sdh

# Импорт/экспорт
zpool export tank
zpool import tank
zpool import -d /dev/disk/by-id tank
```

### Scrub (проверка целостности)

```bash
# Запуск scrub
zpool scrub tank

# Статус
zpool status tank

# Рекомендуется: еженедельный scrub через cron
0 2 * * 0 /sbin/zpool scrub tank
```

---

## 40.4 Датасеты и свойства

### Создание датасетов

```bash
# Создание файловой системы
zfs create tank/data
zfs create tank/home
zfs create tank/home/user1

# Создание zvol (блочное устройство)
zfs create -V 100G tank/vm/disk1
```

### Свойства

```bash
# Просмотр свойств
zfs get all tank/data
zfs get compression tank/data

# Установка свойств
zfs set compression=lz4 tank/data
zfs set quota=100G tank/home/user1
zfs set reservation=50G tank/important
zfs set atime=off tank

# Наследование
zfs inherit compression tank/data/subdir
```

### Важные свойства

| Свойство | Значения | Описание |
|----------|----------|----------|
| compression | off, lz4, zstd, gzip | Сжатие |
| quota | size | Лимит места |
| reservation | size | Гарантированное место |
| recordsize | 4K-1M | Размер блока |
| atime | on/off | Время доступа |
| dedup | on/off | Дедупликация |
| encryption | off/aes-256-gcm | Шифрование |

---

## 40.5 Снапшоты и клоны

### Снапшоты

```bash
# Создание снапшота
zfs snapshot tank/data@backup-2024-01-15

# Рекурсивный снапшот
zfs snapshot -r tank@daily

# Список снапшотов
zfs list -t snapshot

# Откат к снапшоту
zfs rollback tank/data@backup-2024-01-15

# Удаление
zfs destroy tank/data@old-snapshot

# Доступ к файлам снапшота
ls /tank/data/.zfs/snapshot/backup-2024-01-15/
```

### Клоны

```bash
# Создание клона из снапшота
zfs clone tank/data@template tank/data-copy

# Клон занимает место только для изменений
# Полезно для: VM шаблоны, тестирование, разработка
```

### Send/Receive (репликация)

```bash
# Отправка снапшота
zfs send tank/data@backup | zfs receive backup/data

# Инкрементальная отправка
zfs send -i tank/data@snap1 tank/data@snap2 | zfs receive backup/data

# По SSH
zfs send tank/data@backup | ssh server zfs receive backup/data

# Сжатая передача
zfs send tank/data@backup | pv | lz4 | ssh server "lz4 -d | zfs receive backup/data"
```

---

## 40.6 Сжатие и дедупликация

### Сжатие

```bash
# Включить lz4 (рекомендуется)
zfs set compression=lz4 tank

# zstd (лучшее сжатие)
zfs set compression=zstd tank/archive

# Проверка эффективности
zfs get compressratio tank
zfs get used,logicalused tank
```

### Дедупликация

```bash
# ВНИМАНИЕ: требует много RAM!
# ~5GB RAM на 1TB данных

# Включение (осторожно!)
zfs set dedup=on tank/backup

# Проверка
zpool list -o name,size,dedupratio

# Симуляция дедупликации
zdb -S tank
```

---

## 40.7 Шифрование

```bash
# Создание шифрованного датасета
zfs create -o encryption=aes-256-gcm -o keyformat=passphrase tank/secret

# С файлом ключа
dd if=/dev/urandom of=/root/zfs.key bs=32 count=1
zfs create -o encryption=aes-256-gcm -o keyformat=raw -o keylocation=file:///root/zfs.key tank/encrypted

# Загрузка ключа
zfs load-key tank/secret

# Выгрузка ключа
zfs unload-key tank/secret

# Автозагрузка при монтировании
zfs set keylocation=file:///root/zfs.key tank/secret
```

---

## 40.8 Производительность

### ARC (Adaptive Replacement Cache)

```bash
# Статистика ARC
arc_summary

# Ограничение ARC
echo "options zfs zfs_arc_max=8589934592" > /etc/modprobe.d/zfs.conf

# В /etc/default/zfs:
ZFS_ARC_MAX=8589934592  # 8GB
```

### L2ARC (Level 2 ARC)

```bash
# Добавить SSD как кэш чтения
zpool add tank cache /dev/nvme0n1
```

### SLOG (Separate Log)

```bash
# Добавить быстрый диск для ZIL
zpool add tank log mirror /dev/nvme0n1 /dev/nvme1n1
```

---

## 40.9 ZFS и Boot

### FreeBSD с ZFS

```bash
# FreeBSD: Boot Environments
bectl list
bectl create upgrade-13.2
bectl activate upgrade-13.2
bectl jail upgrade-13.2
```

### Linux с ZFS root

```bash
# Убунту с ZFS root:
# Установщик поддерживает ZFS

# Ручная настройка:
zpool create -O mountpoint=none rpool mirror /dev/sda2 /dev/sdb2
zfs create -O mountpoint=/ rpool/ROOT/ubuntu
```

---

## 40.10 Практические советы

### Мониторинг

```bash
# Здоровье пула
zpool status -v

# События
zpool events -v

# Iostat
zpool iostat 1

# Автоматические уведомления
# ZED (ZFS Event Daemon) отправляет email при проблемах
```

### Best Practices

1. **Регулярный scrub** (еженедельно)
2. **Не используйте dedup** без достаточной RAM
3. **Используйте lz4 или zstd** сжатие
4. **Минимум 8GB RAM** для ZFS
5. **ECC память** рекомендуется
6. **Снапшоты перед обновлениями**

---

## Резюме

| Возможность | ZFS |
|-------------|-----|
| Copy-on-Write | ✅ |
| Checksums | Все данные и метаданные |
| Снапшоты | Мгновенные, бесплатные |
| RAID | RAIDZ1/Z2/Z3, mirror |
| Сжатие | lz4, zstd, gzip |
| Шифрование | AES-256-GCM |
| Дедупликация | ✅ (требует RAM) |
| Max размер | 256 ZB |

```
ZFS = ФС + Volume Manager + RAID + Checksums + Snapshots
    = "Last word in filesystems"
```

??? question "Упражнения"
    **Задание 1.** Создайте ZFS pool из файлов-образов: `zpool create testpool mirror /tmp/disk1.img /tmp/disk2.img`. Создайте dataset с включённым сжатием.
    
    **Задание 2.** Сделайте снапшот dataset-а, измените данные, откатитесь через `zfs rollback`. Проверьте, что данные восстановились.
    
    **Задание 3.** Выполните `zpool scrub` и проверьте целостность данных. Симулируйте повреждение одного диска и проверьте self-healing.
