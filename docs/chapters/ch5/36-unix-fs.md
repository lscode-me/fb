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

**Важные опции:**

| Опция | Значение |
|-------|----------|
| defaults | rw,suid,dev,exec,auto,nouser,async |
| noatime | Не обновлять время доступа |
| nodiratime | Не обновлять время доступа к каталогам |
| nofail | Не останавливать загрузку при ошибке |
| noexec | Запретить выполнение файлов |
| nosuid | Игнорировать SUID/SGID биты |

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
