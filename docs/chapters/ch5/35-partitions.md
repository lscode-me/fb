# Глава 35. Разделы и таблицы разделов

## Введение

Прежде чем файловая система сможет хранить данные, диск должен быть **разбит на разделы** (partitions). Раздел — это логически обособленная часть диска, которая может содержать отдельную файловую систему.

---

## 35.1 Зачем нужны разделы

### Преимущества разбиения

- **Изоляция**: системный раздел отделён от данных пользователя
- **Мультизагрузка**: несколько ОС на одном диске
- **Резервное копирование**: проще делать бэкап отдельных разделов
- **Безопасность**: ограничение прав (noexec, nosuid)
- **Производительность**: оптимизация для разных типов нагрузки

### Типичная схема Linux

```
/dev/sda
├── /dev/sda1  →  /boot/efi  (EFI System Partition, 512MB)
├── /dev/sda2  →  /boot      (1GB, ext4)
├── /dev/sda3  →  /          (50GB, ext4)
├── /dev/sda4  →  /home      (остальное, ext4)
└── /dev/sda5  →  swap       (16GB)
```

---

## 35.2 MBR vs GPT

### MBR (Master Boot Record)

```
Байты 0-445:    Загрузчик (bootstrap code)
Байты 446-509:  Таблица разделов (4 записи по 16 байт)
Байты 510-511:  Сигнатура 0x55AA
```

**Ограничения MBR:**

- Максимум 4 первичных раздела (или 3 + расширенный)
- Максимальный размер раздела: 2 TB
- Только один загрузочный раздел

```bash
# Просмотр MBR таблицы
sudo fdisk -l /dev/sda
```

### GPT (GUID Partition Table)

```
┌─────────────────────────────────────┐
│  Protective MBR (LBA 0)             │
├─────────────────────────────────────┤
│  GPT Header (LBA 1)                 │
├─────────────────────────────────────┤
│  Partition Entry Array (LBA 2-33)   │
│  До 128 разделов                    │
├─────────────────────────────────────┤
│  Partitions...                      │
├─────────────────────────────────────┤
│  Backup Partition Array             │
├─────────────────────────────────────┤
│  Backup GPT Header                  │
└─────────────────────────────────────┘
```

**Преимущества GPT:**

- До 128 разделов (по умолчанию)
- Максимальный размер: 9.4 ZB (зеттабайт)
- Резервная копия таблицы в конце диска
- CRC32 контрольные суммы
- GUID для идентификации разделов

```bash
# Просмотр GPT таблицы
sudo gdisk -l /dev/sda
```

---

## 35.3 Инструменты разметки

### fdisk (MBR и GPT)

```bash
# Интерактивный режим
sudo fdisk /dev/sdb

# Команды внутри fdisk:
# p - показать разделы
# n - создать раздел
# d - удалить раздел
# t - изменить тип раздела
# w - записать изменения
# q - выйти без сохранения
```

### gdisk (только GPT)

```bash
sudo gdisk /dev/sdb

# Команды аналогичны fdisk
```

### parted (универсальный)

```bash
# Просмотр
sudo parted /dev/sdb print

# Создание GPT таблицы
sudo parted /dev/sdb mklabel gpt

# Создание раздела
sudo parted /dev/sdb mkpart primary ext4 0% 100%

# Неинтерактивный режим
sudo parted -s /dev/sdb mklabel gpt \
    mkpart primary fat32 1MiB 512MiB \
    mkpart primary ext4 512MiB 100%
```

---

## 35.4 Типы разделов

### GPT Type GUIDs

| GUID | Тип |
|------|-----|
| C12A7328-F81F-11D2-BA4B-00A0C93EC93B | EFI System |
| 0FC63DAF-8483-4772-8E79-3D69D8477DE4 | Linux filesystem |
| 0657FD6D-A4AB-43C4-84E5-0933C84B4F4F | Linux swap |
| E6D6D379-F507-44C2-A23C-238F2A3DF928 | Linux LVM |
| CA7D7CCB-63ED-4C53-861C-1742536059CC | Linux LUKS |

### MBR Type IDs

| ID | Тип |
|----|-----|
| 0x83 | Linux |
| 0x82 | Linux swap |
| 0x8e | Linux LVM |
| 0x07 | NTFS |
| 0x0c | FAT32 LBA |

---

## 35.5 Практические сценарии

### Создание разделов для сервера

```bash
# Создаём GPT таблицу
sudo parted /dev/sdb mklabel gpt

# EFI раздел
sudo parted /dev/sdb mkpart ESP fat32 1MiB 512MiB
sudo parted /dev/sdb set 1 esp on

# Boot раздел
sudo parted /dev/sdb mkpart boot ext4 512MiB 1536MiB

# Root раздел
sudo parted /dev/sdb mkpart root ext4 1536MiB 51712MiB

# Home раздел
sudo parted /dev/sdb mkpart home ext4 51712MiB 100%

# Форматирование
sudo mkfs.fat -F32 /dev/sdb1
sudo mkfs.ext4 /dev/sdb2
sudo mkfs.ext4 /dev/sdb3
sudo mkfs.ext4 /dev/sdb4
```

### Расширение раздела

```bash
# 1. Расширить раздел в parted
sudo parted /dev/sdb resizepart 3 100%

# 2. Расширить файловую систему
sudo resize2fs /dev/sdb3      # ext4
sudo xfs_growfs /mount/point  # XFS
```

---

## 35.6 Идентификация разделов

### По имени устройства

```bash
/dev/sda1       # SATA/SAS диск, раздел 1
/dev/nvme0n1p1  # NVMe диск, раздел 1
/dev/vda1       # Виртуальный диск (virtio)
```

### По UUID

```bash
# Просмотр UUID
sudo blkid

# В fstab
UUID=550e8400-e29b-41d4-a716-446655440000 /home ext4 defaults 0 2
```

### По метке

```bash
# Установка метки
sudo e2label /dev/sdb1 "DATA"

# В fstab
LABEL=DATA /data ext4 defaults 0 2
```

---

## Резюме

| Характеристика | MBR | GPT |
|----------------|-----|-----|
| Максимум разделов | 4 (+ логические) | 128 |
| Максимальный размер | 2 TB | 9.4 ZB |
| Резервная таблица | Нет | Да |
| Контрольные суммы | Нет | CRC32 |
| Совместимость | Старые BIOS | UEFI |

| Инструмент | MBR | GPT | Особенности |
|------------|-----|-----|-------------|
| fdisk | ✅ | ✅ | Интерактивный |
| gdisk | ❌ | ✅ | Только GPT |
| parted | ✅ | ✅ | Скриптуемый |

??? question "Упражнения"
    **Задание 1.** Определите тип таблицы разделов (MBR или GPT) на вашем диске: `sudo fdisk -l` (Linux) или `diskutil info disk0` (macOS).
    
    **Задание 2.** На тестовом loop-устройстве создайте GPT-разметку с 3 разделами через `gdisk` или `parted`. Проверьте результат через `lsblk -f`.
    
    **Задание 3.** Объясните, почему MBR ограничен 2 ТБ. Посчитайте: максимальный адрес LBA в 32 битах × размер сектора 512 байт.
