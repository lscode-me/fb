# Глава 48. Plan 9: всё есть файл (по-настоящему)

## Введение

UNIX провозгласил принцип «всё есть файл», но на практике это не так: сетевые сокеты, процессы, графика, аутентификация — всё это работает через специализированные системные вызовы, а не через файловый API. **Plan 9 from Bell Labs** (1992) довёл эту идею до логического завершения: в Plan 9 буквально всё — файл.

Plan 9 разработали те же люди, что создали UNIX: Кен Томпсон, Роб Пайк, Деннис Ритчи, Дэйв Прессотто. Это не академический эксперимент — это попытка сделать UNIX правильно, с учётом опыта 20 лет.

---

## 48.1 Принцип «всё есть файл» — UNIX vs Plan 9

### Что UNIX назвал файлом, а что — нет

| Ресурс | UNIX | Plan 9 |
|--------|------|--------|
| Обычные файлы | `open/read/write` | `open/read/write` |
| Директории | `opendir/readdir` | `open/read` (обычный файл!) |
| Устройства | `/dev/*` | `/dev/*` |
| Процессы | `/proc` (Linux, не POSIX) | `/proc` (с первого дня) |
| **Сетевые соединения** | `socket/bind/listen/accept` | **`/net/tcp/clone`** |
| **Окна/GUI** | X11 протокол, Wayland | **`/dev/draw`, `/dev/mouse`** |
| **DNS** | `getaddrinfo()` (libc) | **`/net/dns`** |
| **Аутентификация** | PAM, Kerberos (библиотеки) | **`/mnt/factotum`** |
| **Консоль** | `ioctl()`, termios | **`/dev/cons`** (чтение/запись) |
| **Переменные окружения** | `getenv()` (библиотека) | **`/env/PATH`** (файл!) |

В UNIX для каждого нового ресурса изобретают новый API. В Plan 9 всё существующим `read`/`write`:

```
# Plan 9: установить TCP-соединение
% cat /net/tcp/clone
3                              # Получили номер соединения

% echo 'connect 93.184.216.34!80' > /net/tcp/3/ctl
% echo 'GET / HTTP/1.0\r\n\r\n' > /net/tcp/3/data
% cat /net/tcp/3/data
HTTP/1.0 200 OK
...
```

---

## 48.2 9P — файловый протокол

Ключевое изобретение Plan 9 — протокол **9P** (позже 9P2000). Это сетевой протокол для работы с файлами, через который работает **вся** система.

### Сообщения 9P

```
Tversion → Rversion    # Согласование версии
Tattach  → Rattach     # Подключение к серверу (аналог mount)
Twalk    → Rwalk       # Навигация по дереву (аналог path lookup)
Topen    → Ropen       # Открытие файла
Tread    → Rread       # Чтение
Twrite   → Rwrite      # Запись
Tclunk   → Rclunk      # Закрытие (release fid)
Tstat    → Rstat       # Метаданные файла
Tcreate  → Rcreate     # Создание файла
Tremove  → Rremove     # Удаление
```

Всего **~14 сообщений** — это весь API операционной системы. Для сравнения: Linux имеет 400+ системных вызовов.

### Почему это работает

Если каждый сервис представляет себя как дерево файлов, то для работы с ним нужен только файловый протокол:

```
# «Файловые серверы» в Plan 9
/net/tcp/      ← TCP-стек — файловый сервер
/net/dns/      ← DNS-резолвер — файловый сервер
/dev/draw/     ← Графическая система — файловый сервер
/mnt/factotum  ← Менеджер паролей — файловый сервер
/mnt/wiki/     ← Wiki — файловый сервер
```

---

## 48.3 Пространства имён (namespaces)

В UNIX пространство имён файловой системы **глобальное** — все процессы видят одно и то же дерево `/`. В Plan 9 каждый процесс может иметь **собственное пространство имён**.

```
# Каждый процесс может перестроить своё дерево
% bind -a /net.alt /net         # Добавить альтернативный сетевой стек
% bind '#c' /dev                # Смонтировать драйвер консоли
% mount /srv/wiki /mnt/wiki     # Подключить файловый сервер wiki
```

### Это не chroot

В отличие от `chroot` (ограничение видимости), Plan 9 namespaces — это **конструктивный** механизм: процесс собирает своё пространство из кусочков.

| Механизм | UNIX | Plan 9 |
|----------|------|--------|
| Изоляция ФС | `chroot`, `pivot_root` | namespace (per-process) |
| Объединение ФС | `mount --bind`, overlayfs | `bind` (встроено в ядро) |
| Сетевая изоляция | `network namespaces` (Linux) | namespace (единый механизм) |
| Контейнеры | Docker (cgroups + namespaces) | Не нужны — namespaces из коробки |

!!! note "Влияние на Linux"
    Linux namespaces (`mount`, `pid`, `net`, `user`) — прямое заимствование из Plan 9.
    Роб Пайк: *"Linux is the successor to Plan 9 that we didn't know we were building."*

---

## 48.4 /proc — процессы как файлы

В Plan 9 `/proc` существовал с самого начала (Linux добавил `/proc` позже, вдохновившись Plan 9).

```
/proc/
├── 1/
│   ├── ctl        # Управление процессом (запись: "kill", "stop", "start")
│   ├── status     # Статус (чтение: имя, pid, состояние)
│   ├── mem        # Память процесса (чтение/запись!)
│   ├── note       # Отправить «ноту» (аналог сигнала UNIX)
│   ├── notepg     # Нота для всей группы процессов
│   ├── text       # Исполняемый файл
│   └── fd         # Открытые дескрипторы
├── 2/
│   └── ...
```

```
# Убить процесс — записать в файл
% echo kill > /proc/42/ctl

# Прочитать статус
% cat /proc/42/status
rc              42  1  0:00.01  ...

# Отладка: прочитать память процесса
% dd -bs 1 -skip 0x400000 -count 256 < /proc/42/mem | xd
```

Обратите внимание: нет `kill()`, нет `ptrace()`, нет `waitpid()` — только `read` и `write` в `/proc`.

---

## 48.5 /net — сеть как файловая система

Вместо BSD sockets (socket/bind/listen/accept/connect) Plan 9 использует файлы:

```
/net/
├── tcp/
│   ├── clone       # Открыть → получить номер нового соединения
│   ├── stats       # Статистика TCP
│   ├── 0/          # Соединение #0
│   │   ├── ctl     # Управление ("connect host!port", "listen")
│   │   ├── data    # Данные (read/write)
│   │   ├── local   # Локальный адрес
│   │   ├── remote  # Удалённый адрес
│   │   └── status  # Состояние соединения
│   ├── 1/
│   └── ...
├── udp/
│   ├── clone
│   └── ...
├── dns             # DNS — тоже файл
└── cs              # Connection server (аналог getaddrinfo)
```

### TCP-клиент

```
# 1. Получить номер соединения
% echo -n '' > /net/tcp/clone
# Читаем номер: "3"

# 2. Подключиться
% echo 'connect 93.184.216.34!80' > /net/tcp/3/ctl

# 3. Отправить запрос
% echo -n 'GET / HTTP/1.0\r\nHost: example.com\r\n\r\n' > /net/tcp/3/data

# 4. Прочитать ответ
% cat /net/tcp/3/data
```

### TCP-сервер

```
% echo 'announce *!8080' > /net/tcp/5/ctl    # bind + listen
% echo 'accept' > /net/tcp/5/ctl             # accept
% cat /net/tcp/5/data                         # read from client
```

### Сравнение с BSD sockets

```c
/* UNIX: 7 разных системных вызовов */
int fd = socket(AF_INET, SOCK_STREAM, 0);
bind(fd, &addr, sizeof(addr));
listen(fd, 128);
int client = accept(fd, NULL, NULL);
read(client, buf, sizeof(buf));
write(client, response, len);
close(client);

/* Plan 9: те же open/read/write */
int ctl = open("/net/tcp/clone", ORDWR);
read(ctl, buf, sizeof(buf));  // получить номер
fprint(ctl, "announce *!8080");
fprint(ctl, "accept");
int data = open("/net/tcp/N/data", ORDWR);
read(data, buf, sizeof(buf));
write(data, response, len);
close(data);
```

---

## 48.6 Графика, ввод и окна

Window manager в Plan 9 (`rio`) — тоже файловый сервер:

```
/dev/
├── draw        # Графический буфер (запись команд рисования)
├── mouse       # Координаты мыши (чтение: "x y buttons")
├── cons        # Консоль (чтение/запись текста)
├── snarf       # Буфер обмена (clipboard)
└── winname     # Имя текущего окна
```

```
# Прочитать позицию мыши
% cat /dev/mouse
m 512 384 0

# Прочитать содержимое буфера обмена
% cat /dev/snarf
Hello, clipboard!

# Записать в буфер обмена
% echo "copied text" > /dev/snarf
```

Каждое окно в `rio` — это **отдельный namespace**. Программа внутри окна видит свои `/dev/cons`, `/dev/mouse`, `/dev/draw` — но это файлы, предоставленные оконным менеджером, а не ядром.

---

## 48.7 Factotum и Secstore — безопасность через файлы

**Factotum** — агент аутентификации, работающий как файловый сервер:

```
/mnt/factotum/
├── ctl         # Добавить ключи: "key proto=p9sk1 dom=example user=alice ..."
├── rpc         # RPC-интерфейс для аутентификации
└── confirm     # Подтверждение пользователем
```

Программам не нужно знать пароли — они просто просят factotum аутентифицироваться за них:

```
# Добавить ключ
% echo 'key proto=p9sk1 dom=bell-labs.com user=rob !password=secret' \
    > /mnt/factotum/ctl

# Программы (ssh, 9p mount, mail) обращаются к factotum автоматически
```

Это аналог SSH-agent, но **универсальный** — работает для любого протокола (9P, HTTP, IMAP...).

---

## 48.8 Наследие Plan 9

Plan 9 не стал массовой ОС, но его идеи проникли повсюду:

| Идея Plan 9 | Где используется |
|-------------|-----------------|
| `/proc` | Linux `/proc`, FreeBSD `/proc` |
| Namespaces | Linux mount/pid/net/user namespaces → Docker |
| UTF-8 | Изобретён Кеном Томпсоном для Plan 9 → стал стандартом |
| 9P протокол | WSL2 (Windows ↔ Linux), QEMU (virtio-9p), Chrome OS |
| Всё-есть-файл | FUSE (user space FS), `/sys`, `/dev`, systemd |
| Per-process namespace | `unshare`, `nsenter`, контейнеры |
| Factotum | SSH-agent, GNOME Keyring, macOS Keychain |

!!! info "9P сегодня"
    - **WSL2** использует 9P для доступа к Windows-файлам из Linux (`/mnt/c/`)
    - **QEMU/KVM** использует virtio-9p для shared folders между хостом и VM
    - **v9fs** — модуль ядра Linux для монтирования 9P-серверов
    - **Проект 9front** — активно развиваемый форк Plan 9

### Потомки Plan 9

- **Inferno OS** — следующая ОС от тех же авторов, портабельная VM (Dis) + Limbo язык
- **9front** — активный форк Plan 9 с современными драйверами
- **Harvey OS** — Plan 9, собираемый GCC
- **Akaros** — исследовательская ОС (UC Berkeley) с идеями Plan 9

---

## 48.9 Попробовать Plan 9

```bash
# Запустить Plan 9 в QEMU
$ wget https://9p.io/plan9/download/plan9.iso.bz2
$ bunzip2 plan9.iso.bz2
$ qemu-system-x86_64 -m 512 -cdrom plan9.iso -boot d

# Или 9front (более активный форк)
$ wget https://9front.org/iso/9front-10510.amd64.iso.gz
$ gunzip 9front-10510.amd64.iso.gz
$ qemu-system-x86_64 -m 1G -cdrom 9front-10510.amd64.iso -boot d
```

```bash
# Linux: примонтировать 9P-сервер
$ sudo modprobe 9p
$ sudo mount -t 9p -o trans=tcp,port=564 server:/path /mnt/plan9
```

---

## 48.10 Упражнения

!!! example "Практика"
    **Задание 1.** Запустите Plan 9 (или 9front) в QEMU. Исследуйте `/net/tcp/`, `/proc/`, `/env/`. Попробуйте установить TCP-соединение через файлы.

    **Задание 2.** Сравните `/proc` в Linux и Plan 9: какие файлы общие, чего не хватает в Linux?

    **Задание 3.** Смонтируйте 9P-сервер в Linux (`v9fs`). Чем этот протокол отличается от NFS и SMB?

    **Задание 4.** Реализуйте простой 9P-сервер на Python (библиотека `py9p`) или Go (`go9p`), который отдаёт содержимое словаря как файловое дерево.

    **Задание 5.** Используйте три разных namespace в Plan 9 (`rfork(RFNAMEG)`): в каждом смонтируйте разные файловые серверы и убедитесь, что процессы изолированы.

!!! quote "Rob Pike"
    *"If you think of the file server as a namespace server, then Plan 9 is just a collection of communicating namespace servers."*

!!! tip "Следующая глава"
    От Plan 9 namespaces к современным контейнерам — **chroot, namespaces, cgroups, OverlayFS, Docker** → [Контейнеры](49-containers.md)
