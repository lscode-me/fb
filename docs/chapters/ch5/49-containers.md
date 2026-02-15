# Глава 49. Namespaces, контейнеры и OverlayFS: файловая изоляция

## Введение

Контейнеры (Docker, Podman, LXC) кажутся магией: изолированные «мини-ОС» без виртуализации. Но на самом деле контейнер — это просто **процесс с изменённым видом файловой системы**. В основе лежат механизмы ядра Linux, которые эволюционировали от простого `chroot` (1979) до полноценных namespaces и OverlayFS.

Эта глава — путь от `chroot` до `docker run`, через все слои абстракции.

---

## 49.1 chroot — первая изоляция (1979)

### Идея

`chroot` меняет **корневую директорию** процесса. После вызова процесс видит `/` в другом месте:

```bash
# Создаём минимальное дерево
$ mkdir -p /tmp/jail/{bin,lib,lib64,etc,proc}

# Копируем bash и его зависимости
$ cp /bin/bash /tmp/jail/bin/
$ ldd /bin/bash | grep -o '/lib[^ ]*' | xargs -I{} cp {} /tmp/jail{}

# Входим в «тюрьму»
$ sudo chroot /tmp/jail /bin/bash

bash-5.2# pwd
/
bash-5.2# ls /
bin  etc  lib  lib64  proc
# Хост-система «не существует»
```

### Как работает

```
До chroot:                     После chroot("/tmp/jail"):
                               
/                              / ← (на самом деле /tmp/jail)
├── bin/                       ├── bin/
├── etc/                       ├── etc/
├── home/                      ├── lib/
├── tmp/                       └── proc/
│   └── jail/      ───────►
│       ├── bin/               Процесс не может выйти
│       ├── etc/               «выше» нового корня
│       └── lib/               (в теории…)
└── usr/
```

### Ограничения chroot

| Проблема | Описание |
|----------|----------|
| **Побег** | root внутри chroot может выйти: `mkdir x; chroot x; cd ../../../` |
| **Только ФС** | Не изолирует PID, сеть, IPC, пользователей |
| **Общий /proc** | Процессы хоста видны через `/proc` |
| **Общая сеть** | Все порты общие с хостом |
| **Нет лимитов** | Может потребить все ресурсы CPU/RAM |

```c
/* Классический побег из chroot (только для root) */
#include <unistd.h>
#include <sys/stat.h>

int main() {
    mkdir("escape", 0755);
    chroot("escape");          // Новый chroot внутри старого
    for (int i = 0; i < 100; i++)
        chdir("..");           // Выходим за пределы
    chroot(".");               // Теперь корень = настоящий /
    execl("/bin/bash", "bash", NULL);
}
```

!!! warning "chroot ≠ безопасность"
    `chroot` никогда не проектировался как механизм безопасности. Это инструмент для **удобства**, не для изоляции. Для безопасности нужны namespaces + seccomp + capabilities.

---

## 49.2 Mount namespace — у каждого своя ФС

### Проблема

`chroot` меняет только «видимый корень», но все процессы по-прежнему разделяют одно дерево монтирования. Linux mount namespace (2002) решает это: каждый процесс может иметь **собственное дерево монтирования**.

### Создание mount namespace

```bash
# unshare создаёт новый namespace
$ sudo unshare --mount bash

# Теперь монтирования внутри этого shell
# НЕ ВИДНЫ снаружи
$ mount -t tmpfs tmpfs /tmp
$ mount | grep tmpfs
tmpfs on /tmp type tmpfs (rw,relatime)

# В другом терминале это монтирование НЕ видно
```

### Как устроено

```
Процесс A (host namespace)       Процесс B (новый mount namespace)
                                  
/                                 /  ← копия дерева на момент unshare
├── bin/                          ├── bin/
├── etc/                          ├── etc/
├── tmp/ (хост)                   ├── tmp/ (tmpfs!) ← видит другое
├── home/                         ├── home/
└── proc/                         └── proc/
```

```bash
# Посмотреть mount namespace процесса
$ ls -la /proc/self/ns/mnt
lrwxrwxrwx 1 root root 0 ... /proc/self/ns/mnt -> 'mnt:[4026531841]'

# Число в скобках — ID namespace
$ readlink /proc/1/ns/mnt          # Namespace init
mnt:[4026531841]

$ readlink /proc/$$/ns/mnt         # Наш namespace
mnt:[4026532200]                   # Другой ID!
```

### pivot_root — безопасная замена chroot

В контейнерах вместо `chroot` используют `pivot_root` — он **атомарно** меняет корень и помещает старый корень в указанную директорию:

```bash
# Подготовка
$ mkdir -p /tmp/newroot/oldroot
$ mount --bind /tmp/newroot /tmp/newroot  # Нужен mount point

# В новом mount namespace:
$ sudo unshare --mount bash
$ pivot_root /tmp/newroot /tmp/newroot/oldroot

# Теперь / = бывший /tmp/newroot
# Старый корень доступен в /oldroot
$ umount -l /oldroot   # Отмонтировать старый корень — полная изоляция
```

---

## 49.3 Все namespaces Linux

Mount namespace — лишь один из семи. Вместе они обеспечивают полную изоляцию:

| Namespace | Флаг | Что изолирует | Год |
|-----------|------|---------------|-----|
| **Mount** | `CLONE_NEWNS` | Точки монтирования, видимость ФС | 2002 |
| **UTS** | `CLONE_NEWUTS` | Hostname, domainname | 2006 |
| **IPC** | `CLONE_NEWIPC` | System V IPC, POSIX message queues | 2006 |
| **PID** | `CLONE_NEWPID` | Дерево процессов (PID 1 внутри) | 2008 |
| **Network** | `CLONE_NEWNET` | Сетевые интерфейсы, порты, маршруты | 2009 |
| **User** | `CLONE_NEWUSER` | UID/GID маппинг (root без root) | 2013 |
| **Cgroup** | `CLONE_NEWCGROUP` | Видимость cgroup-иерархии | 2016 |

```bash
# Посмотреть все namespaces процесса
$ ls -la /proc/self/ns/
lrwxrwxrwx 1 user user 0 ... cgroup -> 'cgroup:[4026531835]'
lrwxrwxrwx 1 user user 0 ... ipc -> 'ipc:[4026531839]'
lrwxrwxrwx 1 user user 0 ... mnt -> 'mnt:[4026531841]'
lrwxrwxrwx 1 user user 0 ... net -> 'net:[4026531840]'
lrwxrwxrwx 1 user user 0 ... pid -> 'pid:[4026531836]'
lrwxrwxrwx 1 user user 0 ... user -> 'user:[4026531837]'
lrwxrwxrwx 1 user user 0 ... uts -> 'uts:[4026531838]'

# Создать ВСЕ namespaces сразу
$ sudo unshare --mount --uts --ipc --pid --net --user --fork bash
```

### PID namespace

```bash
$ sudo unshare --pid --fork --mount-proc bash

root@host:/# ps aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0   ...   ...  pts/0    S    ...     0:00 bash
root         2  0.0  0.0   ...   ...  pts/0    R+   ...     0:00 ps aux
# Только 2 процесса! Наш bash = PID 1
```

### Network namespace

```bash
# Создать сетевой namespace
$ sudo ip netns add mynet

# Внутри — пустая сеть (только lo)
$ sudo ip netns exec mynet ip link
1: lo: <LOOPBACK> state DOWN ...

# Создать veth-пару (виртуальный «кабель»)
$ sudo ip link add veth0 type veth peer name veth1
$ sudo ip link set veth1 netns mynet

# Настроить IP
$ sudo ip addr add 10.0.0.1/24 dev veth0
$ sudo ip link set veth0 up
$ sudo ip netns exec mynet ip addr add 10.0.0.2/24 dev veth1
$ sudo ip netns exec mynet ip link set veth1 up
$ sudo ip netns exec mynet ip link set lo up

# Тест
$ ping 10.0.0.2  # Работает!
```

### User namespace — root без root

```bash
# Без sudo! Создаём user namespace
$ unshare --user --map-root-user bash

root@host:/# id
uid=0(root) gid=0(root) groups=0(root)
# Мы «root» внутри, но обычный юзер снаружи

root@host:/# cat /proc/self/uid_map
         0       1000          1
# UID 0 внутри = UID 1000 снаружи
```

---

## 49.4 Cgroups — лимиты ресурсов

Namespaces изолируют **видимость**, cgroups ограничивают **потребление**:

```bash
# Создать cgroup
$ sudo mkdir /sys/fs/cgroup/mycontainer

# Ограничить память до 100MB
$ echo 104857600 | sudo tee /sys/fs/cgroup/mycontainer/memory.max

# Ограничить CPU до 50%
$ echo "50000 100000" | sudo tee /sys/fs/cgroup/mycontainer/cpu.max

# Ограничить I/O (блочные устройства)
$ echo "8:0 wbps=10485760" | sudo tee /sys/fs/cgroup/mycontainer/io.max
#       ^^^                          10 MB/s запись на sda

# Добавить процесс в cgroup
$ echo $$ | sudo tee /sys/fs/cgroup/mycontainer/cgroup.procs
```

| Контроллер | Файл | Что ограничивает |
|------------|------|-----------------|
| `memory` | `memory.max` | RAM (в байтах) |
| `cpu` | `cpu.max` | CPU time (quota/period) |
| `io` | `io.max` | Дисковый I/O (rbps, wbps, riops, wiops) |
| `pids` | `pids.max` | Количество процессов |
| `cpuset` | `cpuset.cpus` | Привязка к ядрам CPU |

!!! note "cgroups v1 vs v2"
    В cgroups v1 каждый контроллер — отдельная иерархия (`/sys/fs/cgroup/memory/`, `/sys/fs/cgroup/cpu/`).
    В cgroups v2 (unified) — единая иерархия `/sys/fs/cgroup/`. Современные дистрибутивы (Ubuntu 22.04+, Fedora 38+) используют v2.

---

## 49.5 OverlayFS — слоёная файловая система

### Проблема

Контейнеру нужна **своя копия корневой ФС** (Ubuntu, Alpine, ...), но полное копирование — расточительно. Если 100 контейнеров используют один образ, зачем хранить 100 копий?

### Идея OverlayFS

OverlayFS **накладывает** слои друг на друга. Нижние слои — read-only (образ), верхний — read-write (изменения контейнера):

```
Вид контейнера (merged):     Что на диске:
                              
/                             upperdir/ (RW)     ← изменения контейнера
├── bin/bash (из lower)       ├── etc/
├── etc/hostname (из upper)   │   └── hostname    ← создан контейнером
├── etc/passwd (из lower)     │
├── tmp/myfile (из upper)     lowerdir/ (RO)     ← образ (неизменяемый)
└── usr/... (из lower)        ├── bin/bash
                              ├── etc/passwd
                              └── usr/...
```

### Монтирование

```bash
# Подготовка директорий
$ mkdir -p /tmp/overlay/{lower,upper,work,merged}

# Наполнить нижний слой (образ)
$ echo "original" > /tmp/overlay/lower/file.txt
$ echo "base config" > /tmp/overlay/lower/config.ini

# Смонтировать overlay
$ sudo mount -t overlay overlay \
    -o lowerdir=/tmp/overlay/lower,\
       upperdir=/tmp/overlay/upper,\
       workdir=/tmp/overlay/work \
    /tmp/overlay/merged

# Теперь в merged видны файлы из lower:
$ cat /tmp/overlay/merged/file.txt
original

# Изменяем — копируется в upper (Copy-on-Write):
$ echo "modified" > /tmp/overlay/merged/file.txt

# Оригинал не тронут!
$ cat /tmp/overlay/lower/file.txt
original

# Изменение в upper:
$ cat /tmp/overlay/upper/file.txt
modified
```

### Copy-on-Write (CoW)

При записи в файл из нижнего слоя OverlayFS **копирует** весь файл в верхний слой, затем модифицирует копию:

```
Чтение file.txt:                Запись в file.txt:
                                 
merged/file.txt                  merged/file.txt
    │                                │
    ▼                                ▼
upper/ (нет файла)               upper/file.txt (КОПИЯ + изменения)
    │                                
    ▼                            lower/file.txt (не тронут)
lower/file.txt (читаем)
```

### Удаление файлов — whiteout

Как «удалить» файл из read-only слоя? OverlayFS создаёт **whiteout** — специальный файл-маркер:

```bash
# Удаляем файл, который есть в lower
$ rm /tmp/overlay/merged/config.ini

# В lower файл остался:
$ ls /tmp/overlay/lower/config.ini
/tmp/overlay/lower/config.ini

# В upper появился whiteout (character device 0/0):
$ ls -la /tmp/overlay/upper/config.ini
c--------- 1 root root 0, 0 ... /tmp/overlay/upper/config.ini
```

Для директорий используется **opaque whiteout** — файл `.wh..wh..opq` внутри директории.

### Множественные нижние слои

OverlayFS поддерживает **стек** нижних слоёв (все read-only):

```bash
$ sudo mount -t overlay overlay \
    -o lowerdir=/layer3:/layer2:/layer1,\
       upperdir=/container,\
       workdir=/work \
    /merged

# Порядок: layer3 (верхний RO) → layer2 → layer1 (нижний RO)
# Файл ищется сверху вниз, первое совпадение побеждает
```

---

## 49.6 Docker: как всё собирается вместе

Docker-контейнер = namespaces + cgroups + OverlayFS:

```
docker run -it --memory=512m ubuntu bash

                    ┌─────────────────────────┐
                    │  Процесс bash (PID 1)    │
                    │                           │
  Namespaces:       │  mount: своя ФС          │
  ├── mount ns      │  pid:   свои процессы    │
  ├── pid ns        │  net:   свои интерфейсы  │
  ├── net ns        │  uts:   свой hostname    │
  ├── uts ns        │  user:  свой uid mapping  │
  ├── ipc ns        │  ipc:   свои очереди      │
  └── user ns       └─────────────┬─────────────┘
                                  │
  Cgroups:                        │ Ограничения:
  └── memory.max = 512MB          │ CPU, RAM, I/O, PIDs
                                  │
  OverlayFS:                      │ Файловая система:
  ├── lower: ubuntu image layers  │ /bin, /usr, /lib (RO)
  ├── upper: container layer      │ Изменения (RW)
  └── merged: /  (видимое)        │ Объединённый вид
```

### Слои Docker-образа

```bash
# Посмотреть слои образа
$ docker image inspect ubuntu --format '{{.RootFS.Layers}}'
[sha256:a1b2c3... sha256:d4e5f6... sha256:789abc...]

# Каждый слой — tar-архив с diff'ом
# Dockerfile:
# FROM ubuntu          ← базовый слой
# RUN apt-get update   ← слой 2 (только изменённые файлы)
# COPY app /app        ← слой 3 (только /app)

# Где хранятся слои на диске
$ ls /var/lib/docker/overlay2/
l/                              # Символические ссылки (короткие имена)
abc123.../                      # Слой 1
│   ├── diff/                   # Содержимое слоя
│   ├── link                    # Короткое имя
│   └── lower                   # Ссылка на предыдущий слой
def456.../                      # Слой 2
789abc.../                      # Container layer (upper)
│   ├── diff/                   # Изменения контейнера
│   ├── merged/                 # Объединённый вид (mount point)
│   ├── upper/                  # = diff/
│   └── work/                   # Рабочая директория OverlayFS
```

### Посмотреть overlay монтирование контейнера

```bash
$ docker run -d --name test ubuntu sleep 3600
$ docker inspect test --format '{{.GraphDriver.Data.MergedDir}}'
/var/lib/docker/overlay2/abc.../merged

$ mount | grep overlay
overlay on /var/lib/docker/overlay2/abc.../merged type overlay (
    lowerdir=/var/lib/docker/overlay2/l/LAYER3:
              /var/lib/docker/overlay2/l/LAYER2:
              /var/lib/docker/overlay2/l/LAYER1,
    upperdir=/var/lib/docker/overlay2/abc.../diff,
    workdir=/var/lib/docker/overlay2/abc.../work
)
```

### Общие слои между контейнерами

```
Container A          Container B          Container C
(upper: RW)          (upper: RW)          (upper: RW)
    │                    │                    │
    ▼                    ▼                    ▼
┌────────────────────────────────────────────────────┐
│           Ubuntu image layers (lower: RO)           │
│                                                      │
│  Один набор файлов на диске для всех контейнеров!   │
└────────────────────────────────────────────────────┘
```

100 контейнеров из одного образа = 1 копия образа + 100 тонких upper-слоёв.

---

## 49.7 Собираем контейнер вручную

Всё вместе — контейнер без Docker, только с помощью Linux-утилит:

```bash
#!/bin/bash
# mini-container.sh — контейнер за 30 строк

set -e
ROOTFS="/tmp/mycontainer"
UPPER="$ROOTFS/upper"
WORK="$ROOTFS/work"
MERGED="$ROOTFS/merged"
LOWER="/tmp/alpine-rootfs"  # Скачанный rootfs Alpine

# 1. Подготовка OverlayFS
mkdir -p "$UPPER" "$WORK" "$MERGED"
mount -t overlay overlay \
    -o "lowerdir=$LOWER,upperdir=$UPPER,workdir=$WORK" \
    "$MERGED"

# 2. Подготовка внутренних ФС
mount -t proc proc "$MERGED/proc"
mount -t sysfs sys "$MERGED/sys"
mount -t tmpfs tmpfs "$MERGED/tmp"

# 3. Создать cgroup с лимитами
CGROUP="/sys/fs/cgroup/mycontainer"
mkdir -p "$CGROUP"
echo "209715200" > "$CGROUP/memory.max"     # 200MB RAM
echo "50000 100000" > "$CGROUP/cpu.max"     # 50% CPU
echo "20" > "$CGROUP/pids.max"              # Макс 20 процессов

# 4. Запустить процесс во всех namespaces
unshare --mount --uts --ipc --pid --net --cgroup --fork \
    --root="$MERGED" \
    /bin/sh -c '
        hostname container
        echo $$ > /sys/fs/cgroup/mycontainer/cgroup.procs 2>/dev/null
        exec /bin/sh
    '

# 5. Очистка
umount -R "$MERGED"
rmdir "$CGROUP"
```

```bash
# Скачать rootfs Alpine для эксперимента
$ wget https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/\
  alpine-minirootfs-3.19.0-x86_64.tar.gz
$ mkdir /tmp/alpine-rootfs
$ tar xf alpine-minirootfs-*.tar.gz -C /tmp/alpine-rootfs

# Запустить
$ sudo bash mini-container.sh
/ # hostname
container
/ # ps aux
PID   USER     TIME  COMMAND
    1 root      0:00 /bin/sh
    2 root      0:00 ps aux
/ # cat /etc/os-release
NAME="Alpine Linux"
```

---

## 49.8 Альтернативы OverlayFS

| ФС / Драйвер | Механизм | Используется в |
|---------------|----------|---------------|
| **OverlayFS** | Слои + CoW на уровне файлов | Docker (по умолчанию), Podman |
| **Btrfs** | Subvolumes + snapshots + CoW на уровне блоков | Docker (btrfs driver) |
| **ZFS** | Clones + snapshots + CoW | Docker (zfs driver) |
| **Device Mapper** | Thin provisioning + CoW на уровне блоков | Docker (devicemapper) |
| **FUSE-overlayfs** | OverlayFS в userspace (без root) | Rootless Podman |
| **VFS** | Полное копирование (нет CoW) | Тестирование |

```bash
# Проверить storage driver Docker
$ docker info | grep "Storage Driver"
 Storage Driver: overlay2

# Btrfs снапшоты для контейнеров (альтернативный подход)
$ btrfs subvolume snapshot /images/ubuntu /containers/mycontainer
# Мгновенно, CoW на уровне блоков
```

---

## 49.9 Rootless-контейнеры и FUSE

### Проблема

OverlayFS требует **привилегии** (CAP_SYS_ADMIN или root). Как запускать контейнеры без root?

### Решение: User namespace + FUSE-overlayfs

```bash
# Podman — rootless из коробки
$ podman run --rm -it alpine sh
# Работает без sudo!

# Под капотом:
# 1. User namespace: uid 0 внутри = uid 1000 снаружи
# 2. fuse-overlayfs вместо overlayfs ядра
# 3. slirp4netns для сети (вместо veth)
```

```bash
# FUSE-overlayfs — OverlayFS в user space
$ fuse-overlayfs -o \
    lowerdir=/layer1:/layer2,\
    upperdir=/upper,\
    workdir=/work \
    /merged

# Работает без root через FUSE!
$ fusermount -u /merged   # Unmount
```

### Сравнение

| | Docker (root) | Podman (rootless) |
|---|---|---|
| Daemon | dockerd (root) | Нет демона |
| OverlayFS | Ядро (overlay2) | fuse-overlayfs |
| Сеть | veth + bridge | slirp4netns / pasta |
| User mapping | Не нужен | /etc/subuid, /etc/subgid |
| Безопасность | root на хосте | Обычный пользователь |
| Производительность | Выше | Чуть ниже (FUSE overhead) |

---

## 49.10 Эволюция изоляции: от chroot до контейнеров

```
1979  chroot        │ Только смена корня ФС
      │             │
1998  FreeBSD Jails │ chroot + изоляция процессов и сети
      │             │
2002  mount ns      │ Собственное дерево монтирования
      │             │
2006  uts + ipc ns  │ Свой hostname, свои IPC
      │             │
2007  cgroups       │ Лимиты ресурсов (CPU, RAM, I/O)
      │             │
2008  pid ns        │ Своё дерево процессов
      │             │ ──── LXC (2008): первые Linux-контейнеры ────
      │             │
2009  net ns        │ Своя сетевая подсистема
      │             │
2013  user ns       │ UID mapping (root без root)
      │             │ ──── Docker 1.0 (2014) ────
      │             │
2014  OverlayFS     │ В ядре Linux (3.18)
      │             │
2016  cgroup ns     │ Изоляция видимости cgroups
      │             │ ──── Rootless containers (Podman) ────
      │             │
2020+ Kata, gVisor  │ MicroVM / user-space kernel для доп. изоляции
```

!!! info "Plan 9 снова"
    Напомним, что **все** Linux namespaces вдохновлены Plan 9 (глава 48), где per-process namespace было фундаментальной концепцией с 1992 года.

---

## 49.11 Файловые аспекты контейнеров

### /proc, /sys, /dev внутри контейнера

```bash
# Docker монтирует внутрь контейнера:
/proc     ← proc fs (отфильтрованная через pid ns)
/sys      ← sysfs (частично read-only)
/dev      ← devtmpfs (минимальный набор устройств)
/dev/pts  ← pseudo-terminal
/etc/resolv.conf  ← DNS (bind mount с хоста)
/etc/hostname     ← Hostname контейнера

# Что Docker скрывает из /proc:
$ cat /proc/kcore         # Permission denied
$ cat /proc/sysrq-trigger # Permission denied
# Это достигается через masked paths (bind mount /dev/null)
```

### Volumes — прокидывание файлов

```bash
# Bind mount — прямой проброс директории
$ docker run -v /host/data:/data alpine ls /data

# Named volume — управляется Docker
$ docker volume create mydata
$ docker run -v mydata:/data alpine sh

# tmpfs — в памяти (ничего на диске)
$ docker run --tmpfs /tmp:rw,size=100m alpine sh

# Под капотом bind mount = mount --bind:
$ mount --bind /host/data /merged/data
```

### Immutable infrastructure

Слоёная ФС поощряет паттерн **неизменяемой инфраструктуры**:

- Образ (нижние слои) — **никогда не меняется**
- Контейнер (верхний слой) — **эфемерный**, удаляется при пересоздании  
- Данные — в **volumes**, переживают контейнеры

---

## 49.12 Упражнения

!!! example "Практика"
    **Задание 1.** Создайте chroot-окружение с bash и несколькими утилитами. Проверьте, что процессы хоста видны через `/proc`.

    **Задание 2.** Соберите «контейнер» вручную: `unshare` + `pivot_root` + `mount` (используйте скрипт из раздела 49.7). Проверьте изоляцию PID, hostname, файловой системы.

    **Задание 3.** Смонтируйте OverlayFS из трёх слоёв. Создайте, измените и удалите файлы в merged-директории. Исследуйте, что появляется в upper (copy-up, whiteout).

    **Задание 4.** Запустите два Docker-контейнера из одного образа. Найдите их overlay-монтирования (`mount | grep overlay`) и убедитесь, что нижние слои общие.

    **Задание 5.** Настройте cgroup для процесса: ограничьте RAM до 50MB и запустите программу, которая пытается аллоцировать 100MB. Что произойдёт?
    ```bash
    python3 -c "x = bytearray(100 * 1024 * 1024); print('OK')"
    ```

    **Задание 6.** Сравните rootless Podman и Docker: запустите одинаковый контейнер в обоих и сравните storage driver, mount table, uid mapping.

!!! quote "Solomon Hykes (создатель Docker)"
    *"Docker is really a toolbox for using Linux kernel features that already existed — namespaces, cgroups, overlay filesystems — and making them accessible."*

!!! tip "Следующая глава"
    Как текст превращается в числа для нейросетей — **токенизация, BPE, tiktoken** → [Токенизация](50-tokenization.md)
