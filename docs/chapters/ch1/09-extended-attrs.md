# Глава 9. Расширенные атрибуты и механизмы безопасности

## Введение

Стандартные права доступа Unix (rwx для owner/group/others) — это лишь базовый уровень контроля. Современные системы предоставляют **расширенные механизмы**:

- **Extended Attributes (xattr)** — произвольные метаданные файлов
- **Access Control Lists (ACL)** — гранулярные права доступа
- **SELinux / AppArmor** — мандатный контроль доступа (MAC, Mandatory Access Control)
- **File capabilities** — привилегии без SUID
- **NTFS Alternate Data Streams** — скрытые потоки данных

---

## 9.1 Extended Attributes (xattr)

### Что такое xattr?

**Extended Attributes** — это пары ключ-значение, привязанные к файлу. Они позволяют хранить **произвольные метаданные**, не меняя содержимое файла.

!!! warning "Важно: xattr ≠ содержимое"
    Расширенные атрибуты **не имеют никакого отношения к содержимому файла**. Они хранятся в inode или
    в отдельном блоке файловой системы. Можно удалить все xattr — и файл останется точно
    таким же. Можно изменить содержимое файла — атрибуты не изменятся. Это
    принципиально отличает xattr от метаданных, встроенных в формат файла (EXIF в JPEG,
    ID3 в MP3 — см. главу 25).

```bash
# Установить атрибут
$ setfattr -n user.comment -v "Important file" myfile.txt

# Прочитать атрибуты
$ getfattr -d myfile.txt
# file: myfile.txt
user.comment="Important file"

# Удалить атрибут
$ setfattr -x user.comment myfile.txt
```

### Пространства имён (namespaces)

| Namespace | Описание | Доступ |
|-----------|----------|--------|
| `user` | Пользовательские атрибуты | Любой пользователь (с правами на файл) |
| `trusted` | Доверенные атрибуты | Только root |
| `system` | Системные (ACL, capabilities) | Через специальные API |
| `security` | SELinux, AppArmor, IMA | Подсистема безопасности |

```bash
# Просмотр всех атрибутов (включая system)
$ getfattr -d -m - myfile.txt
# file: myfile.txt
security.selinux="unconfined_u:object_r:user_home_t:s0"
user.comment="Important file"
```

### FreeBSD и OpenBSD

В BSD системах xattr работает через другие утилиты:

```bash
# FreeBSD
$ setextattr user comment "Important file" myfile.txt
$ getextattr user comment myfile.txt
myfile.txt  Important file
$ lsextattr user myfile.txt
myfile.txt  comment

# Все namespaces в FreeBSD
$ lsextattr -q system myfile.txt
```

### macOS: xattr и карантин

macOS активно использует xattr для системных целей:

```bash
# Файлы из интернета получают карантинный атрибут
$ xattr -l downloaded_file.dmg
com.apple.quarantine: 0083;5f3a1b2c;Safari;...

# Gatekeeper проверяет этот атрибут перед запуском
$ xattr -d com.apple.quarantine downloaded_file.dmg

# Другие системные атрибуты macOS
com.apple.FinderInfo          # Информация Finder (цвет метки, иконка)
com.apple.ResourceFork        # Resource fork (legacy)
com.apple.metadata:kMDItemWhereFroms  # Откуда скачан файл
```

!!! info "Браузеры и расширенные атрибуты"
    Браузеры (Safari, Chrome, Firefox) **автоматически ставят** расширенные атрибуты
    на скачанные файлы. На macOS это `com.apple.quarantine` (защита Gatekeeper) и
    `com.apple.metadata:kMDItemWhereFroms` (URL источника). На Linux с соответствующей настройкой — `user.xdg.origin.url`.
    
    ```bash
    # Проверить, откуда скачан файл (macOS)
    $ xattr -p com.apple.metadata:kMDItemWhereFroms ~/Downloads/file.zip
    https://example.com/file.zip
    
    # Chrome на Linux
    $ getfattr -d ~/Downloads/file.zip
    user.xdg.origin.url="https://example.com/file.zip"
    user.xdg.referrer.url="https://example.com/download"
    ```
    
    Эти атрибуты помогают ОС предупреждать пользователя при запуске непроверенных файлов.

### Python: работа с xattr

```python
import os

# Linux
os.setxattr('myfile.txt', 'user.comment', b'Important file')
value = os.getxattr('myfile.txt', 'user.comment')
print(value)  # b'Important file'

# Список всех атрибутов
attrs = os.listxattr('myfile.txt')
print(attrs)  # ['user.comment', 'security.selinux']

# Удалить атрибут
os.removexattr('myfile.txt', 'user.comment')
```

### Ограничения xattr

| ФС | Поддержка | Макс. размер значения |
|----|-----------|----------------------|
| ext4 | ✅ | 4 КБ (в inode) или больше (в блоке) |
| XFS | ✅ | 64 КБ |
| Btrfs | ✅ | 64 КБ |
| ZFS | ✅ | 64 КБ |
| NTFS | ✅ (через ADS) | 64 КБ |
| FAT32 | ❌ | — |
| exFAT | ❌ | — |

!!! warning "xattr и копирование"
    Не все утилиты сохраняют xattr при копировании:
    ```bash
    # cp по умолчанию НЕ копирует xattr
    $ cp file.txt copy.txt
    
    # Нужен флаг --preserve
    $ cp --preserve=xattr file.txt copy.txt
    
    # rsync нужен флаг -X
    $ rsync -avX source/ dest/
    ```

---

## 9.2 Access Control Lists (ACL)

### Зачем нужны ACL?

Стандартные права Unix ограничены: owner, group, others. Что если нужно дать права **конкретному пользователю**?

```bash
# Проблема: как дать alice чтение, bob — запись, остальным — ничего?
# Стандартными правами — никак!

# Решение: ACL
$ setfacl -m u:alice:r-- myfile.txt
$ setfacl -m u:bob:rw- myfile.txt
$ setfacl -m o::--- myfile.txt
```

### Просмотр и установка ACL

```bash
# Установить ACL
$ setfacl -m u:alice:rwx myfile.txt     # пользователю alice
$ setfacl -m g:developers:rx myfile.txt  # группе developers
$ setfacl -m o::r myfile.txt             # остальным

# Просмотр ACL
$ getfacl myfile.txt
# file: myfile.txt
# owner: user
# group: user
user::rw-
user:alice:rwx
group::r--
group:developers:r-x
mask::rwx
other::r--

# Файл с ACL помечается "+" в ls
$ ls -l myfile.txt
-rw-rwxr--+ 1 user user 1234 Feb  4 10:00 myfile.txt
          ^
          ACL присутствует
```

### Default ACL для директорий

```bash
# Все новые файлы в директории унаследуют ACL
$ setfacl -d -m u:alice:rwx project/
$ setfacl -d -m g:developers:rx project/

# Проверка
$ getfacl project/
# file: project/
# owner: user
# group: user
user::rwx
group::r-x
other::r-x
default:user::rwx
default:user:alice:rwx
default:group::r-x
default:group:developers:r-x
default:mask::rwx
default:other::r-x
```

### ACL в FreeBSD и OpenBSD

```bash
# FreeBSD: NFSv4 ACL (более мощные)
$ setfacl -m u:alice:rwxp:fd:allow myfile.txt
$ getfacl myfile.txt

# OpenBSD: минимальная поддержка ACL
# Только через nfs4_setfacl на NFSv4
```

---

## 9.3 SELinux

### Что такое SELinux?

**SELinux** (Security-Enhanced Linux) — система мандатного контроля доступа (MAC). В отличие от стандартных прав (DAC), SELinux контролирует доступ на основе **политик**, а не владельца.

```bash
# Проверить статус SELinux
$ getenforce
Enforcing

# Контекст безопасности файла
$ ls -Z myfile.txt
unconfined_u:object_r:user_home_t:s0 myfile.txt
```

### Контекст SELinux

Формат: `user:role:type:level`

```
unconfined_u:object_r:httpd_sys_content_t:s0
     │          │              │           │
     │          │              │           └── MLS level (Multi-Level Security)
     │          │              └── Тип (самое важное!)
     │          └── Роль
     └── Пользователь SELinux
```

### Типичные проблемы и решения

```bash
# Проблема: веб-сервер не может прочитать файл
$ ls -Z /var/www/html/index.html
unconfined_u:object_r:user_home_t:s0 /var/www/html/index.html
#                     ^^^^^^^^^^^
#                     Неправильный тип!

# Решение: установить правильный контекст
$ chcon -t httpd_sys_content_t /var/www/html/index.html

# Или восстановить из политики
$ restorecon -v /var/www/html/index.html
```

### Логи SELinux

```bash
# Denied-сообщения в audit log
$ ausearch -m avc -ts recent
type=AVC msg=audit(1234567890.123:456): avc:  denied  { read } for
  pid=1234 comm="httpd" name="index.html" dev="sda1" ino=131074
  scontext=system_u:system_r:httpd_t:s0
  tcontext=unconfined_u:object_r:user_home_t:s0 tclass=file

# Генерация правила для разрешения
$ audit2allow -a -M mypolicy
$ semodule -i mypolicy.pp
```

---

## 9.4 AppArmor

### Альтернатива SELinux

**AppArmor** — более простая система MAC, используемая в Ubuntu, SUSE, Debian.

```bash
# Статус AppArmor
$ aa-status
apparmor module is loaded.
15 profiles are loaded.
15 profiles are in enforce mode.
   /usr/bin/firefox
   /usr/sbin/mysqld
   ...
```

### Профили AppArmor

```bash
# Профиль Firefox
$ cat /etc/apparmor.d/usr.bin.firefox
#include <tunables/global>

/usr/bin/firefox {
  #include <abstractions/base>
  #include <abstractions/fonts>
  #include <abstractions/X>
  
  # Доступ к домашней директории
  owner @{HOME}/** rw,
  
  # Запрет доступа к SSH ключам
  deny @{HOME}/.ssh/** rw,
  
  # Сеть
  network inet stream,
  network inet6 stream,
}
```

### Управление профилями

```bash
# Перевести в режим обучения (complain)
$ aa-complain /usr/bin/firefox

# Перевести в режим enforce
$ aa-enforce /usr/bin/firefox

# Генерация профиля из логов
$ aa-genprof /usr/bin/myapp
```

---

## 9.5 NTFS Alternate Data Streams (ADS)

### Скрытые потоки данных в Windows

NTFS позволяет хранить **несколько потоков данных** в одном файле:

```powershell
# Основной поток (обычное содержимое)
PS> Set-Content -Path file.txt -Value "Visible content"

# Альтернативный поток (скрытый)
PS> Set-Content -Path file.txt:hidden -Value "Secret data"

# Основной файл показывает только видимое содержимое
PS> Get-Content file.txt
Visible content

# Скрытый поток
PS> Get-Content file.txt:hidden
Secret data
```

### Просмотр всех потоков

```powershell
# Список потоков
PS> Get-Item file.txt -Stream *
   FileName: C:\Users\user\file.txt

Stream           Length
------           ------
:$DATA               15    # основной поток
hidden               11    # скрытый поток

# dir /r показывает ADS
PS> cmd /c "dir /r file.txt"
     15 file.txt
     11 file.txt:hidden:$DATA
```

### Использование ADS

**Легитимное использование:**
- Зона происхождения файла (`Zone.Identifier`)
- Метаданные Windows Search
- Иконки и превью

```powershell
# Зона происхождения (как карантин в macOS)
PS> Get-Content file.exe:Zone.Identifier
[ZoneTransfer]
ZoneId=3
ReferrerUrl=https://example.com/file.exe
HostUrl=https://cdn.example.com/file.exe
```

!!! warning "Безопасность"
    ADS может использоваться malware для скрытия данных. Многие антивирусы сканируют ADS.

---

## 9.6 File Capabilities (Linux)

### Привилегии без SUID

Вместо SUID root можно дать программе **только нужные привилегии**:

```bash
# Старый способ: SUID root (опасно!)
$ chmod u+s /usr/bin/ping
$ ls -l /usr/bin/ping
-rwsr-xr-x 1 root root 64424 Feb  4 10:00 /usr/bin/ping

# Новый способ: только CAP_NET_RAW
$ setcap cap_net_raw+ep /usr/bin/ping
$ getcap /usr/bin/ping
/usr/bin/ping = cap_net_raw+ep
```

### Основные capabilities

| Capability | Описание |
|------------|----------|
| `CAP_NET_RAW` | Создание raw sockets (ping, tcpdump) |
| `CAP_NET_BIND_SERVICE` | Привязка к портам < 1024 |
| `CAP_SYS_ADMIN` | Множество админских операций |
| `CAP_DAC_OVERRIDE` | Обход проверки прав доступа |
| `CAP_CHOWN` | Изменение владельца файлов |

```bash
# Веб-сервер на порту 80 без root
$ setcap cap_net_bind_service+ep /usr/bin/node
$ node server.js  # может слушать порт 80
```

---

## 9.7 Immutable и Append-only атрибуты

### chattr / lsattr (Linux ext4)

```bash
# Сделать файл неизменяемым (даже root не сможет изменить!)
$ chattr +i important.conf
$ lsattr important.conf
----i------------ important.conf

$ rm important.conf
rm: cannot remove 'important.conf': Operation not permitted

# Снять атрибут
$ chattr -i important.conf

# Append-only (только добавление)
$ chattr +a logfile.log
# Можно: echo "new line" >> logfile.log
# Нельзя: echo "overwrite" > logfile.log
```

### chflags (FreeBSD, macOS)

```bash
# FreeBSD / macOS: system immutable (даже root в single-user)
$ chflags schg important.conf

# User immutable (только root может снять)
$ chflags uchg important.conf

# Просмотр флагов
$ ls -lo important.conf
-rw-r--r--  1 root  wheel  schg 1234 Feb  4 10:00 important.conf

# Снять флаг
$ chflags noschg important.conf
```

---

## Резюме

| Механизм | Назначение | ОС |
|----------|-----------|-----|
| **xattr** | Произвольные метаданные | Linux, FreeBSD, macOS |
| **ACL** | Гранулярные права доступа | Linux, FreeBSD, macOS, Windows |
| **SELinux** | Мандатный контроль (MAC) | RHEL, Fedora, CentOS |
| **AppArmor** | Мандатный контроль (проще) | Ubuntu, SUSE, Debian |
| **NTFS ADS** | Множественные потоки данных | Windows |
| **Capabilities** | Привилегии без SUID | Linux |
| **chattr/chflags** | Immutable, append-only | Linux, FreeBSD, macOS |

!!! tip "Практические команды"
    ```bash
    # xattr
    getfattr -d file        # Linux
    xattr -l file           # macOS
    
    # ACL
    getfacl file
    setfacl -m u:user:rwx file
    
    # SELinux
    ls -Z file
    chcon -t type file
    
    # Capabilities
    getcap file
    setcap cap_net_raw+ep file
    
    # Immutable
    chattr +i file          # Linux
    chflags schg file       # BSD/macOS
    ```

??? question "Упражнения"
    **Задание 1.** Установите расширенный атрибут на файл: `setfattr -n user.description -v "test data" file` (Linux) или `xattr -w user.description "test data" file` (macOS). Прочитайте его обратно.
    
    **Задание 2.** Проверьте ACL на файле: `getfacl file` (Linux). Добавьте разрешение на чтение для конкретного пользователя через `setfacl`.
    
    **Задание 3.** На Linux: проверьте SELinux-контекст файла (`ls -Z`). Какие ещё атрибуты безопасности привязаны к файлам в вашей системе?

---

## Troubleshooting: типичные проблемы Части I

!!! bug "Permission denied, хотя я владелец"
    Проверьте:
    
    - **Монтирование**: `mount | grep /dev/sdX` — файловая система может быть смонтирована с `noexec` или `ro`.
    - **ACL**: `getfacl file` — ACL может переопределять POSIX-права.
    - **Immutable-флаг**: `lsattr file` (Linux) — файл может быть защищён от изменений.
    - **SELinux/AppArmor**: `ls -Z file` — контекст безопасности может запрещать доступ.

!!! bug "Disk full, но `df` показывает свободное место"
    Два возможных виновника:
    
    - **Кончились inode**: `df -i` — каждый файл требует inode. Миллионы мелких файлов могут исчерпать inode при свободных блоках.
    - **Удалённые, но открытые файлы**: `lsof +L1` — процесс держит удалённый файл, место не освобождается до закрытия дескриптора.

!!! bug "Символическая ссылка 'сломалась'"
    ```bash
    # Найти все битые симлинки в директории
    find /path -xtype l
    
    # Проверить, куда ведёт ссылка
    readlink -f broken_link
    ```
    Симлинк хранит только путь — если цель перемещена или удалена, ссылка становится «висячей» (dangling). Это не ошибка ФС, а ожидаемое поведение.

!!! bug "Имя файла с пробелами / спецсимволами ломает скрипты"
    ```bash
    # Неправильно:
    for f in $(ls *.txt); do cat $f; done
    
    # Правильно:
    for f in *.txt; do cat "$f"; done
    ```
    Всегда оборачивайте переменные в кавычки. Используйте `find ... -print0 | xargs -0` для безопасной обработки.


!!! success "Глава 1 завершена!"
    Мы изучили всё о **структуре файлов**: от блоков на диске до расширенных атрибутов безопасности.
    
    В следующей главе разберёмся с **содержимым файлов** — форматами данных, кодировками, архивами → [Глава 2: Форматы и содержимое](../ch2/00-intro.md)
