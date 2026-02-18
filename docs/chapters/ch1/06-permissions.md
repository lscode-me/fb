---
title: Права доступа в Linux — chmod, chown, umask, ACL
description: Полное руководство по правам доступа в Linux. Чтение/запись/выполнение (rwx), числовой и символьный режим, SUID/SGID, sticky bit, ACL.
---

# Глава 6. Права доступа и владение

## Введение

Теперь, когда мы понимаем связь между именами файлов и inode, давайте разберёмся с одним из важнейших аспектов — **правами доступа** (permissions).

Кто может читать файл? Кто может его изменять? Кто может выполнять? Эти вопросы критичны для безопасности системы.

!!! note "Права хранятся в inode"
    Права доступа — это часть метаданных файла, хранящихся в inode. При обращении к файлу ядро проверяет права **целевого файла**, а не symlink.

---

## 6.1 Модель прав Unix: rwx

### Три категории пользователей

Unix разделяет всех пользователей на три категории:

| Категория | Описание | Обозначение | chmod |
|-----------|----------|-------------|-------|
| **Owner** (владелец) | Пользователь, владеющий файлом | user | u |
| **Group** (группа) | Члены группы файла | group | g |
| **Others** (остальные) | Все остальные пользователи | others | o |

### Три типа прав

Для каждой категории определены три права:

| Право | Буква | Бит | Для файла | Для директории |
|-------|-------|-----|-----------|----------------|
| **Read** | r | 4 | Читать содержимое | Читать список файлов |
| **Write** | w | 2 | Изменять содержимое | Создавать/удалять файлы |
| **Execute** | x | 1 | Выполнять как программу | Входить в директорию |

### Просмотр прав

```bash
$ ls -l myfile.txt
-rw-r--r-- 1 alice developers 1234 Feb  4 10:00 myfile.txt
│├──┼──┼──┤   │     │
││  │  │  │   │     └── группа файла
││  │  │  │   └── владелец файла
││  │  │  └── others: r-- (только чтение)
││  │  └── group: r-- (только чтение)
││  └── owner: rw- (чтение и запись)
│└── тип файла: - (regular file)
```

### Числовое представление (octal)

Каждое право — это бит. Три бита образуют число от 0 до 7:

```
rwx = 4 + 2 + 1 = 7
rw- = 4 + 2 + 0 = 6
r-x = 4 + 0 + 1 = 5
r-- = 4 + 0 + 0 = 4
--- = 0 + 0 + 0 = 0
```

**Типичные комбинации:**

| Octal | Символьный | Значение |
|-------|------------|----------|
| 755 | rwxr-xr-x | Исполняемый файл, скрипт |
| 644 | rw-r--r-- | Обычный файл |
| 600 | rw------- | Приватный файл |
| 700 | rwx------ | Приватная директория |
| 777 | rwxrwxrwx | Полный доступ (опасно!) |

---

## 6.2 Изменение прав: chmod

### Символьный синтаксис

```bash
# Добавить право выполнения владельцу
$ chmod u+x script.sh

# Убрать право записи у группы и others
$ chmod go-w file.txt

# Установить конкретные права
$ chmod u=rwx,g=rx,o=r file.txt

# Права для всех категорий сразу
$ chmod a+r file.txt      # a = all (u+g+o)
$ chmod +x script.sh      # То же, что a+x
```

### Числовой синтаксис

```bash
$ chmod 755 script.sh     # rwxr-xr-x
$ chmod 644 config.txt    # rw-r--r--
$ chmod 600 secret.key    # rw-------
```

### Рекурсивное изменение

```bash
# Рекурсивно для директории и всего содержимого
$ chmod -R 755 project/

# Часто нужно разные права для файлов и директорий
$ find project/ -type f -exec chmod 644 {} \;
$ find project/ -type d -exec chmod 755 {} \;
```

---

## 6.3 Права для директорий

Права для директорий работают **иначе**, чем для файлов:

| Право | Для директории |
|-------|----------------|
| **r** (read) | Читать список файлов (`ls`) |
| **w** (write) | Создавать, удалять, переименовывать файлы |
| **x** (execute) | Входить в директорию (`cd`), обращаться к файлам внутри |

### Примеры

```bash
# Директория без x — нельзя войти
$ chmod 640 mydir/    # rw-r-----
$ cd mydir/
bash: cd: mydir/: Permission denied

# Директория без r — нельзя листинг, но можно обратиться к файлу
$ chmod 711 mydir/    # rwx--x--x
$ ls mydir/
ls: cannot open directory 'mydir/': Permission denied
$ cat mydir/known_file.txt   # Работает, если знаешь имя!

# Директория без w — нельзя создавать/удалять файлы
$ chmod 555 mydir/    # r-xr-xr-x
$ touch mydir/newfile
touch: cannot touch 'mydir/newfile': Permission denied
$ rm mydir/existing_file
rm: cannot remove 'mydir/existing_file': Permission denied
```

!!! warning "Удаление файла — право на директорию!"
    Чтобы удалить файл, нужно право **w на директорию**, а не на сам файл:
    ```bash
    $ ls -l
    drwxrwxrwx 2 user user 4096 Feb  4 10:00 dir/
    -r--r--r-- 1 user user  100 Feb  4 10:00 dir/readonly.txt
    
    $ rm dir/readonly.txt   # Успешно! (w на dir/)
    ```

---

## 6.4 Владение: chown и chgrp

### Изменение владельца

```bash
# Только root может менять владельца
$ sudo chown alice file.txt
$ sudo chown alice:developers file.txt  # Владелец и группа
$ sudo chown :developers file.txt       # Только группа
```

### Изменение группы

```bash
# Пользователь может менять группу на свою
$ chgrp developers file.txt

# Рекурсивно
$ chown -R alice:developers project/
```

### FreeBSD / OpenBSD

```bash
# Синтаксис идентичен Linux
$ chown alice:wheel file.txt

# В BSD традиционно используется группа wheel для sudo
$ chgrp wheel /usr/local/bin/script.sh
```

---

## 6.5 Специальные биты

Помимо rwx, существуют три специальных бита:

### SUID (Set User ID) — бит 4000

При выполнении файла процесс получает права **владельца файла**, а не запустившего пользователя.

```bash
$ ls -l /usr/bin/passwd
-rwsr-xr-x 1 root root 68208 Feb  4 10:00 /usr/bin/passwd
   ^
   s вместо x = SUID установлен

# Любой пользователь может изменить свой пароль,
# хотя /etc/shadow доступен только root
```

```bash
# Установить SUID
$ chmod u+s program
$ chmod 4755 program
```

### SGID (Set Group ID) — бит 2000

**Для файлов:** процесс получает права группы файла.

**Для директорий:** новые файлы наследуют группу директории.

```bash
# SGID на директории — полезно для совместной работы
$ chmod g+s shared_project/
$ ls -ld shared_project/
drwxrwsr-x 2 alice developers 4096 Feb  4 10:00 shared_project/
      ^
      s = SGID

# Теперь все файлы в shared_project/ будут группы developers
$ touch shared_project/newfile.txt
$ ls -l shared_project/newfile.txt
-rw-r--r-- 1 bob developers 0 Feb  4 10:00 newfile.txt
                ^^^^^^^^^^
                Группа унаследована от директории
```

### Sticky bit — бит 1000

**Для директорий:** файлы может удалять только их владелец (или root).

!!! note "Историческая справка: sticky bit для файлов"
    Изначально sticky bit предназначался для **обычных файлов**: он просил ядро удерживать
    текст (код) программы в swap после завершения, чтобы ускорить повторный запуск.
    Отсюда и название — «sticky» (прилипчивый). В современных системах эта семантика
    для файлов **устарела и не используется** — её заменили более эффективные механизмы
    кеширования (page cache). Сегодня sticky bit имеет смысл только для директорий.

```bash
$ ls -ld /tmp
drwxrwxrwt 10 root root 4096 Feb  4 10:00 /tmp
         ^
         t = sticky bit

# Все могут создавать файлы в /tmp
# Но удалить можно только свои
$ touch /tmp/myfile
$ sudo -u otheruser rm /tmp/myfile
rm: cannot remove '/tmp/myfile': Operation not permitted
```

```bash
# Установить sticky bit
$ chmod +t directory/
$ chmod 1777 directory/
```

### Сводная таблица

| Бит | Числовое | Для файла | Для директории |
|-----|----------|-----------|----------------|
| SUID | 4000 | Выполнять от имени владельца | — |
| SGID | 2000 | Выполнять от имени группы | Наследование группы |
| Sticky | 1000 | — | Удалять только свои файлы |

```bash
# Комбинация: 4755 = SUID + rwxr-xr-x
$ chmod 4755 program

# Комбинация: 2775 = SGID + rwxrwxr-x
$ chmod 2775 shared_dir/

# Комбинация: 1777 = Sticky + rwxrwxrwx
$ chmod 1777 /tmp
```

---

## 6.6 umask: права по умолчанию

### Что такое umask?

**umask** — маска, которая **убирает** биты из прав по умолчанию.

По умолчанию:
- Файлы создаются с правами 666 (rw-rw-rw-)
- Директории создаются с правами 777 (rwxrwxrwx)

umask **вычитается** из этих значений.

```bash
$ umask
0022

# Новый файл: 666 - 022 = 644 (rw-r--r--)
$ touch newfile
$ ls -l newfile
-rw-r--r-- 1 user user 0 Feb  4 10:00 newfile

# Новая директория: 777 - 022 = 755 (rwxr-xr-x)
$ mkdir newdir
$ ls -ld newdir
drwxr-xr-x 2 user user 4096 Feb  4 10:00 newdir
```

### Типичные значения umask

| umask | Файлы | Директории | Использование |
|-------|-------|------------|---------------|
| 022 | 644 | 755 | Стандартный |
| 027 | 640 | 750 | Более приватный |
| 077 | 600 | 700 | Максимально приватный |
| 002 | 664 | 775 | Для групповой работы |

```bash
# Установить umask
$ umask 027

# Символьный синтаксис (показывает что РАЗРЕШЕНО)
$ umask -S
u=rwx,g=rx,o=
```

---

## 6.7 Права в Windows

### Базовая модель

Windows использует **ACL (Access Control Lists)**, но также имеет упрощённые атрибуты:

```powershell
# Просмотр атрибутов
PS> Get-ItemProperty file.txt | Select-Object Attributes
Attributes
----------
   Archive

# Атрибуты: Archive, ReadOnly, Hidden, System
PS> Set-ItemProperty file.txt -Name IsReadOnly -Value $true
```

### icacls — управление правами

```powershell
# Просмотр ACL
PS> icacls file.txt
file.txt BUILTIN\Administrators:(F)
         NT AUTHORITY\SYSTEM:(F)
         BUILTIN\Users:(RX)
         user:(M)

# F = Full, M = Modify, RX = Read & Execute, R = Read, W = Write

# Добавить права
PS> icacls file.txt /grant "Users:(R)"

# Убрать права
PS> icacls file.txt /remove "Users"

# Рекурсивно
PS> icacls folder /grant "Users:(OI)(CI)(M)" /T
# OI = Object Inherit, CI = Container Inherit
```

### Сравнение Unix и Windows

| Unix | Windows | Описание |
|------|---------|----------|
| r | R (Read) | Чтение |
| w | W (Write) | Запись |
| x | X (Execute) | Выполнение |
| — | M (Modify) | r + w + x + delete |
| — | F (Full) | Полный контроль |

---

## 6.8 Проверка прав

### Команда test / [

```bash
# Проверка в shell
if [ -r file.txt ]; then echo "Readable"; fi
if [ -w file.txt ]; then echo "Writable"; fi
if [ -x file.txt ]; then echo "Executable"; fi

# Комбинации
[ -r file.txt ] && [ -w file.txt ] && echo "R/W"
```

### Python: os.access()

```python
import os

# Проверка прав текущего пользователя
os.access('file.txt', os.R_OK)  # Readable?
os.access('file.txt', os.W_OK)  # Writable?
os.access('file.txt', os.X_OK)  # Executable?

# Комбинация
os.access('file.txt', os.R_OK | os.W_OK)

# Получить права как число
stat_info = os.stat('file.txt')
mode = stat_info.st_mode & 0o777  # Маскируем только права
print(oct(mode))  # '0o644'

# Изменить права
os.chmod('file.txt', 0o755)
```

### Системный вызов access()

```c
#include <unistd.h>

// Проверка прав
if (access("file.txt", R_OK) == 0) {
    printf("Readable\n");
}

// R_OK, W_OK, X_OK, F_OK (существование)
```

!!! warning "TOCTOU race condition"
    Между `access()` и фактическим открытием файла права могут измениться. Безопаснее просто пытаться открыть файл и обрабатывать ошибки.

---

## 6.9 Частые ошибки и подводные камни

### 1. chmod 777 — плохая идея

```bash
# ❌ Плохо: даёт всем полный доступ
$ chmod 777 config.php

# ✅ Хорошо: минимально необходимые права
$ chmod 640 config.php
$ chown www-data:www-data config.php
```

### 2. Права на родительские директории

```bash
# Файл доступен, но директория — нет
$ chmod 644 /secret/file.txt
$ chmod 700 /secret/

# Другой пользователь не может прочитать file.txt,
# даже если права на файл разрешают!
$ sudo -u otheruser cat /secret/file.txt
cat: /secret/file.txt: Permission denied
```

### 3. root игнорирует права на чтение/запись

```bash
$ chmod 000 secret.txt
$ cat secret.txt
cat: secret.txt: Permission denied

$ sudo cat secret.txt
This is secret content.  # root может всё!
```

### 4. Execute bit для скриптов

```bash
# Скрипт без x не запускается напрямую
$ ./script.sh
bash: ./script.sh: Permission denied

# Но можно запустить через интерпретатор
$ bash script.sh
Hello!

# Правильный способ
$ chmod +x script.sh
$ ./script.sh
Hello!
```

### Shebang: как текст становится исполняемым

Когда вы запускаете `./script.sh`, ядро смотрит на первые байты файла:

```bash
# Magic bytes разных файлов:
7F 45 4C 46  →  ELF binary (нативный исполняемый файл)
23 21        →  #! (shebang) → запустить интерпретатор
```

**Shebang** (`#!`) в первой строке указывает интерпретатор:

```bash
#!/bin/bash
echo "Hello from bash"

#!/usr/bin/env python3
print("Hello from Python")

#!/usr/bin/perl
print "Hello from Perl\n";
```

**Как это работает:**

```
$ ./script.py
    ↓
Ядро: читает первые байты → "#!/usr/bin/env python3"
    ↓
Exec: /usr/bin/env python3 ./script.py
    ↓
env находит python3 в PATH
    ↓
Python интерпретирует файл
```

!!! tip "Почему `/usr/bin/env`?"
    `#!/usr/bin/env python3` лучше `#!/usr/bin/python3`:
    
    - `python3` может быть в `/usr/local/bin`, `/opt/bin`, или virtualenv
    - `env` ищет в `PATH`, находит правильный интерпретатор

---

## 6.8 Шифрование: защита данных на диске (Data at Rest)

Права доступа защищают файлы **внутри работающей ОС**. Но если злоумышленник получит физический доступ к диску (украденный ноутбук, изъятый сервер), права бесполезны — он просто смонтирует диск в другой системе.

**Шифрование** решает эту проблему: данные на диске нечитаемы без ключа.

### Уровни шифрования

| Уровень | Технология | Что защищает |
|---------|-----------|-------------|
| **Полнодисковое** (FDE) | LUKS, BitLocker, FileVault | Весь диск / раздел |
| **На уровне ФС** | fscrypt (ext4), APFS encryption | Отдельные директории |
| **Контейнер** | VeraCrypt, LUKS-файл | Отдельный зашифрованный том |
| **Файл** | GPG, `age`, openssl | Один конкретный файл |

### Основные инструменты

=== "Linux (LUKS)"
    ```bash
    # Создание зашифрованного раздела
    sudo cryptsetup luksFormat /dev/sdX2
    sudo cryptsetup open /dev/sdX2 encrypted
    sudo mkfs.ext4 /dev/mapper/encrypted
    sudo mount /dev/mapper/encrypted /mnt/secret
    
    # Закрытие
    sudo umount /mnt/secret
    sudo cryptsetup close encrypted
    ```

=== "macOS (FileVault)"
    ```bash
    # Включение FileVault (шифрование всего диска)
    sudo fdesetup enable
    
    # Статус
    fdesetup status
    # FileVault is On.
    # Encryption type: APFS
    ```

=== "Windows (BitLocker)"
    ```powershell
    # Включение BitLocker (PowerShell от администратора)
    Enable-BitLocker -MountPoint "C:" -EncryptionMethod XtsAes256
    
    # Статус
    manage-bde -status C:
    ```

=== "Кросс-платформенное (VeraCrypt)"
    ```bash
    # Создание контейнера
    veracrypt --text --create container.vc \
      --size=1G --encryption=AES --hash=SHA-512 \
      --filesystem=ext4 --volume-type=normal
    
    # Монтирование
    veracrypt container.vc /mnt/vc
    ```

!!! warning "Шифрование ≠ безопасное удаление"
    Шифрование защищает **живые данные**. Для безопасного удаления с SSD нужен Secure Erase (→ Глава 34), так как `shred` бесполезен из-за wear leveling.

!!! info "Подробнее"
    Детальный разбор блочного шифрования (LUKS + LVM, loop devices) → [Глава 34: Архитектура накопителей](../ch5/34-architecture.md) и [Глава 43: LVM](../ch5/43-lvm.md).

---

## Резюме

| Команда | Описание |
|---------|----------|
| `ls -l` | Показать права |
| `chmod 755 file` | Установить права (числовой) |
| `chmod u+x file` | Добавить право (символьный) |
| `chown user:group file` | Изменить владельца |
| `chgrp group file` | Изменить группу |
| `umask 022` | Установить маску по умолчанию |

| Специальный бит | Числовое | Эффект |
|-----------------|----------|--------|
| SUID | 4000 | Выполнение от имени владельца |
| SGID | 2000 | Выполнение от имени группы / наследование группы |
| Sticky | 1000 | Удалять только свои файлы |

!!! tip "Принцип минимальных привилегий"
    Всегда давайте **минимально необходимые** права. Лучше добавить права позже, чем страдать от взлома.


??? question "Упражнения"
    **Задание 1.** Установите SUID-бит на скрипт (`chmod u+s script.sh`). Выполните от другого пользователя. Работает ли SUID для скриптов? Почему?
    
    **Задание 2.** Установите `umask 077` и создайте файл и директорию. Какие права они получили? Повторите с `umask 022`. Объясните разницу.
    
    **Задание 3.** Создайте директорию со sticky bit (`chmod +t dir`). Попробуйте удалить чужой файл в ней. Где в системе уже используется sticky bit?

!!! tip "Следующая глава"
    Права установлены, но как **процессы** работают с файлами? → [Дескрипторы и потоки](07-descriptors.md)
