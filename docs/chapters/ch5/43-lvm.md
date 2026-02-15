# Глава 43. LVM — Logical Volume Manager

## Введение

**LVM** (Logical Volume Manager) — подсистема Linux для гибкого управления дисковым пространством. LVM добавляет слой абстракции между физическими дисками и файловыми системами.

---

## 43.1 Зачем нужен LVM?

### Проблемы традиционного разбиения

```
Традиционные разделы:
┌─────────────────────────────────────────┐
│  /dev/sda                               │
├──────────────┬──────────────┬───────────┤
│  sda1 (/)    │  sda2 (/home)│  sda3     │
│  50 GB       │  100 GB      │  swap     │
│  ЗАПОЛНЕН!   │  свободно    │           │
└──────────────┴──────────────┴───────────┘

Проблема: / заполнен, а /home пустой
Решение без LVM: бэкап → переразбивка → восстановление
```

### Решение с LVM

```
LVM:
┌─────────────────────────────────────────────────────┐
│  Volume Group (VG)                                  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Логические тома (LV)                         │  │
│  │  ┌────────┐  ┌────────┐  ┌────────┐           │  │
│  │  │ root   │  │ home   │  │ swap   │           │  │
│  │  │ 50→80GB│  │ 100GB  │  │ 8GB    │           │  │
│  │  └────────┘  └────────┘  └────────┘           │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Physical Volumes (PV)                        │  │
│  │  /dev/sda1     /dev/sdb1     /dev/sdc1        │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

Решение: lvextend -L +30G /dev/vg/root
Online! Без перезагрузки!
```

---

## 43.2 Концепции LVM

### Иерархия

```
Physical Volume (PV)    →  Диск или раздел
         ↓
Volume Group (VG)       →  Пул из нескольких PV
         ↓
Logical Volume (LV)     →  Виртуальный "раздел"
         ↓
Файловая система        →  ext4, XFS, etc.
```

### Physical Extent (PE)

```
PV разбивается на PE (по умолчанию 4 MB):

┌────┬────┬────┬────┬────┬────┬────┬────┐
│ PE │ PE │ PE │ PE │ PE │ PE │ PE │ PE │  Physical Volume
└────┴────┴────┴────┴────┴────┴────┴────┘

LV состоит из LE (Logical Extent), которые маппятся на PE:

LV root:  [LE1]──▶PE5  [LE2]──▶PE7  [LE3]──▶PE10
LV home:  [LE1]──▶PE1  [LE2]──▶PE2  [LE3]──▶PE3
```

---

## 43.3 Базовые операции

### Создание LVM

```bash
# 1. Создать Physical Volume
pvcreate /dev/sdb
pvcreate /dev/sdc

# Проверка
pvs
pvdisplay /dev/sdb

# 2. Создать Volume Group
vgcreate mydata /dev/sdb /dev/sdc

# Проверка
vgs
vgdisplay mydata

# 3. Создать Logical Volume
lvcreate -n root -L 50G mydata
lvcreate -n home -L 100G mydata
lvcreate -n swap -L 8G mydata

# Использовать все оставшееся пространство
lvcreate -n data -l 100%FREE mydata

# Проверка
lvs
lvdisplay /dev/mydata/root

# 4. Форматирование
mkfs.ext4 /dev/mydata/root
mkfs.ext4 /dev/mydata/home
mkswap /dev/mydata/swap

# 5. Монтирование
mount /dev/mydata/root /mnt
```

### /etc/fstab

```bash
/dev/mydata/root  /      ext4  defaults  0  1
/dev/mydata/home  /home  ext4  defaults  0  2
/dev/mydata/swap  none   swap  sw        0  0
```

---

## 43.4 Изменение размера

### Увеличение LV (online!)

```bash
# Увеличить LV на 20GB
lvextend -L +20G /dev/mydata/root

# Или до конкретного размера
lvextend -L 100G /dev/mydata/root

# Использовать всё свободное место
lvextend -l +100%FREE /dev/mydata/root

# Расширить файловую систему
resize2fs /dev/mydata/root      # ext4
xfs_growfs /mount/point         # XFS (только увеличение)

# Или одной командой (автоматически расширяет ФС)
lvextend -L +20G --resizefs /dev/mydata/root
```

### Уменьшение LV

```bash
# ТОЛЬКО для ext2/3/4! XFS не уменьшается!
# ОСТОРОЖНО! Сначала уменьшаем ФС, потом LV!

# 1. Размонтировать
umount /mnt

# 2. Проверить ФС
e2fsck -f /dev/mydata/root

# 3. Уменьшить ФС
resize2fs /dev/mydata/root 30G

# 4. Уменьшить LV
lvreduce -L 30G /dev/mydata/root

# Или одной командой
lvreduce -L 30G --resizefs /dev/mydata/root
```

---

## 43.5 Добавление дисков

```bash
# 1. Создать PV на новом диске
pvcreate /dev/sdd

# 2. Добавить в существующий VG
vgextend mydata /dev/sdd

# 3. Теперь можно расширить LV
lvextend -L +50G /dev/mydata/home
resize2fs /dev/mydata/home
```

---

## 43.6 Удаление и миграция

### Удаление LV

```bash
# Размонтировать
umount /mountpoint

# Удалить LV
lvremove /dev/mydata/unused

# Удалить VG
vgremove mydata

# Удалить PV
pvremove /dev/sdb
```

### Миграция данных между дисками

```bash
# Переместить данные с одного PV на другой (online!)
pvmove /dev/sdb /dev/sdd

# Переместить конкретный LV
pvmove -n root /dev/sdb /dev/sdd

# После миграции можно удалить старый PV
vgreduce mydata /dev/sdb
pvremove /dev/sdb
```

---

## 43.7 Снапшоты LVM

### Создание снапшота

```bash
# Создать снапшот (CoW — Copy on Write)
lvcreate -s -n root-snap -L 10G /dev/mydata/root

# Размер снапшота = количество изменений
# Если изменений больше размера снапшота — он станет невалидным!
```

### Использование снапшота

```bash
# Монтирование снапшота
mount /dev/mydata/root-snap /mnt/snapshot

# Бэкап с консистентного снапшота
tar czf backup.tar.gz /mnt/snapshot

# Размонтирование и удаление
umount /mnt/snapshot
lvremove /dev/mydata/root-snap
```

### Откат к снапшоту

```bash
# Размонтировать
umount /mountpoint

# Объединить снапшот с оригиналом (откат)
lvconvert --merge /dev/mydata/root-snap

# Примонтировать обратно
mount /dev/mydata/root /mountpoint
```

---

## 43.8 Thin Provisioning

### Overcommit хранилища

```bash
# Thin pool — выделяем виртуальное пространство больше физического

# 1. Создать thin pool
lvcreate -T -L 100G mydata/thinpool

# 2. Создать thin volumes (виртуально по 50G, но реально занимают мало)
lvcreate -V 50G -T mydata/thinpool -n vm1
lvcreate -V 50G -T mydata/thinpool -n vm2
lvcreate -V 50G -T mydata/thinpool -n vm3

# Общий виртуальный размер: 150G
# Физически: данные занимают место по мере использования
```

### Мониторинг thin pool

```bash
# Использование thin pool
lvs -o+lv_layout,lv_role

# Расширение thin pool при заполнении
lvextend -L +50G mydata/thinpool
```

---

## 43.9 LVM + RAID

### LVM может создавать RAID volumes

```bash
# RAID1 (mirror)
lvcreate --type raid1 -m 1 -L 100G -n mirror_lv mydata

# RAID5
lvcreate --type raid5 -i 3 -L 100G -n raid5_lv mydata

# RAID10
lvcreate --type raid10 -i 2 -m 1 -L 100G -n raid10_lv mydata
```

---

## 43.10 LVM + шифрование (LUKS)

```bash
# Стек: LUKS → LVM

# 1. Шифрование раздела
cryptsetup luksFormat /dev/sdb

# 2. Открытие
cryptsetup luksOpen /dev/sdb crypted

# 3. LVM на шифрованном устройстве
pvcreate /dev/mapper/crypted
vgcreate secure /dev/mapper/crypted
lvcreate -n data -l 100%FREE secure

# 4. Файловая система
mkfs.ext4 /dev/secure/data
```

---

## 43.11 Типичные сценарии

### Сервер с LVM

```bash
# Разбиение диска
# sda1: /boot (без LVM, ext4, 1GB)
# sda2: LVM

# Создание LVM
pvcreate /dev/sda2
vgcreate system /dev/sda2
lvcreate -n root -L 50G system
lvcreate -n var -L 20G system
lvcreate -n home -L 50G system
lvcreate -n swap -L 8G system
```

### KVM/libvirt с LVM

```bash
# LV для виртуальных машин
lvcreate -n vm-ubuntu -L 50G vms
lvcreate -n vm-centos -L 30G vms

# В libvirt используем /dev/vms/vm-ubuntu как raw диск
```

---

## 43.12 Команды LVM

### Physical Volume

| Команда | Описание |
|---------|----------|
| pvcreate | Создать PV |
| pvs | Список PV (кратко) |
| pvdisplay | Подробная информация |
| pvremove | Удалить PV |
| pvmove | Переместить данные |

### Volume Group

| Команда | Описание |
|---------|----------|
| vgcreate | Создать VG |
| vgs | Список VG |
| vgdisplay | Подробная информация |
| vgextend | Добавить PV в VG |
| vgreduce | Удалить PV из VG |
| vgremove | Удалить VG |

### Logical Volume

| Команда | Описание |
|---------|----------|
| lvcreate | Создать LV |
| lvs | Список LV |
| lvdisplay | Подробная информация |
| lvextend | Увеличить LV |
| lvreduce | Уменьшить LV |
| lvremove | Удалить LV |
| lvrename | Переименовать LV |

---

## Резюме

```
LVM иерархия:
  Диски → PV → VG → LV → ФС

Ключевые преимущества:
  ✅ Онлайн расширение
  ✅ Снапшоты
  ✅ Миграция данных (pvmove)
  ✅ Thin provisioning
  ✅ RAID интеграция
```

| Задача | Команда |
|--------|---------|
| Расширить том | lvextend -L +10G --resizefs /dev/vg/lv |
| Добавить диск | pvcreate + vgextend |
| Снапшот | lvcreate -s -n snap -L 5G /dev/vg/lv |
| Миграция | pvmove /dev/old /dev/new |

??? question "Упражнения"
    **Задание 1.** Создайте цепочку: PV → VG → LV → mkfs → mount. Используйте loop-устройства как физические тома.
    
    **Задание 2.** Расширьте LV и файловую систему «на лету»: `lvextend -L +500M /dev/vg/lv && resize2fs /dev/vg/lv`. Работает без размонтирования!
    
    **Задание 3.** Создайте LVM-снапшот, сделайте бэкап с него, удалите снапшот. Объясните, почему снапшот должен быть временным.
