# Глава 44. Сетевые протоколы доступа к файлам

## Введение

Файлы могут находиться не только на локальных дисках, но и на удалённых серверах. Сетевые протоколы позволяют работать с удалёнными файлами так же, как с локальными.

---

## 44.1 Обзор протоколов

```
┌─────────────────────────────────────────────────────────────┐
│                    Уровень приложений                       │
├─────────────────┬─────────────────────┬─────────────────────┤
│      NFS        │       SMB/CIFS      │      WebDAV         │
│   (UNIX/Linux)  │   (Windows/Samba)   │   (HTTP-based)      │
├─────────────────┼─────────────────────┼─────────────────────┤
│      FTP        │       SFTP/SCP      │      rsync          │
│   (legacy)      │   (SSH-based)       │   (delta sync)      │
└─────────────────┴─────────────────────┴─────────────────────┘
```

---

## 44.2 NFS (Network File System)

### Особенности NFS

- **Прозрачный доступ** к удалённым файлам
- **Нативен для UNIX/Linux**
- **NFSv4** — современная версия с улучшенной безопасностью

### Сервер NFS

```bash
# Установка (Debian/Ubuntu)
apt install nfs-kernel-server

# Конфигурация /etc/exports
/data/share  192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash)
/data/public *(ro,sync)

# Параметры:
# rw/ro           — чтение-запись / только чтение
# sync/async     — синхронная / асинхронная запись
# no_root_squash — root клиента = root сервера
# root_squash    — root клиента = nobody (безопаснее)

# Применить изменения
exportfs -ra

# Статус
exportfs -v
```

### Клиент NFS

```bash
# Установка
apt install nfs-common

# Монтирование
mount -t nfs server:/data/share /mnt

# С опциями
mount -t nfs -o vers=4,noatime server:/data /mnt

# В /etc/fstab
server:/data  /remote  nfs  defaults,noatime,nofail  0  0

# Autofs (автомонтирование)
apt install autofs
echo "/mnt  /etc/auto.nfs" >> /etc/auto.master
echo "data  -fstype=nfs  server:/data" > /etc/auto.nfs
systemctl restart autofs
# Доступ: ls /mnt/data (монтируется автоматически)
```

### Проверка

```bash
# Какие шары экспортирует сервер
showmount -e server

# Статистика NFS
nfsstat

# Монитор RPC
rpcinfo -p server
```

---

## 44.3 SMB/CIFS (Samba)

### Особенности SMB

- **Нативен для Windows**
- **Samba** — реализация для Unix
- **Современный SMB3** — шифрование, подписи

### Samba сервер

```bash
# Установка
apt install samba

# /etc/samba/smb.conf
[global]
   workgroup = WORKGROUP
   security = user
   map to guest = Bad User

[share]
   path = /data/share
   browseable = yes
   read only = no
   guest ok = no
   valid users = @samba_users

# Добавить пользователя Samba
smbpasswd -a username

# Перезапуск
systemctl restart smbd

# Проверка
testparm
```

### SMB клиент (Linux)

```bash
# Просмотр шар
smbclient -L //server -U username

# Интерактивный доступ
smbclient //server/share -U username

# Монтирование
mount -t cifs //server/share /mnt -o username=user,password=pass

# С файлом credentials
mount -t cifs //server/share /mnt -o credentials=/root/.smbcred

# /root/.smbcred:
# username=user
# password=pass
# domain=WORKGROUP

# В /etc/fstab
//server/share /mnt cifs credentials=/root/.smbcred,uid=1000 0 0
```

---

## 44.4 SFTP и SCP (SSH)

### SFTP

```bash
# Интерактивный режим
sftp user@server

# Команды внутри sftp:
# ls, cd, pwd          — навигация на сервере
# lls, lcd, lpwd       — навигация локально
# get file             — скачать
# put file             — загрузить
# mget *.txt           — скачать несколько
# bye, quit            — выход

# Скачать файл
sftp user@server:remote/file local/

# Загрузить
sftp user@server <<< "put localfile remotepath"
```

### SCP

```bash
# Копирование на сервер
scp file.txt user@server:/path/

# Копирование с сервера
scp user@server:/path/file.txt ./

# Рекурсивно
scp -r dir/ user@server:/path/

# С нестандартным портом
scp -P 2222 file.txt user@server:/path/
```

### SSHFS (монтирование через SSH)

```bash
# Установка
apt install sshfs

# Монтирование
sshfs user@server:/path /mnt

# С опциями
sshfs -o allow_other,default_permissions user@server:/data /mnt

# Размонтирование
fusermount -u /mnt

# В /etc/fstab
user@server:/data  /mnt  fuse.sshfs  defaults,_netdev  0  0
```

---

## 44.5 FTP

### Классический FTP (не рекомендуется)

```bash
# FTP клиент
ftp server

# Команды:
# USER username
# PASS password
# ls, cd, pwd
# get file
# put file
# binary        — бинарный режим
# ascii         — текстовый режим
# bye

# Проблемы FTP:
# - Пароли передаются открытым текстом
# - Активный/пассивный режим и файрволы
# - Два соединения (команды + данные)
```

### FTPS vs SFTP

```
FTPS (FTP over SSL):
├── FTP с шифрованием TLS
├── Порты 21 (control) + data ports
└── Сложнее для файрволов

SFTP (SSH File Transfer Protocol):
├── Совершенно другой протокол!
├── Через SSH (порт 22)
└── Проще, безопаснее
```

---

## 44.6 rsync

### Эффективная синхронизация

```bash
# Локальная синхронизация
rsync -av /source/ /destination/

# Удалённая синхронизация (через SSH)
rsync -avz -e ssh /local/ user@server:/remote/

# Параметры:
# -a    archive mode (рекурсия, права, времена)
# -v    verbose
# -z    сжатие при передаче
# -P    progress + partial (возобновление)
# --delete   удалять лишние файлы в destination

# Полная синхронизация
rsync -avz --delete /source/ user@server:/backup/

# Dry run (предпросмотр)
rsync -avzn --delete /source/ /destination/
```

### rsync daemon

```bash
# /etc/rsyncd.conf
[backup]
path = /data/backup
comment = Backup area
read only = false
auth users = backupuser
secrets file = /etc/rsyncd.secrets

# /etc/rsyncd.secrets
backupuser:password

# Клиент
rsync -avz rsync://backupuser@server/backup/ /local/
```

---

## 44.7 WebDAV

### HTTP как файловая система

```bash
# Установка модуля Apache
apt install apache2
a2enmod dav dav_fs

# Конфигурация
<VirtualHost *:80>
    DocumentRoot /var/www/webdav
    <Directory /var/www/webdav>
        DAV On
        AuthType Basic
        AuthName "WebDAV"
        AuthUserFile /etc/apache2/.htpasswd
        Require valid-user
    </Directory>
</VirtualHost>

# Создание пользователя
htpasswd -c /etc/apache2/.htpasswd username
```

### WebDAV клиент

```bash
# Установка
apt install davfs2

# Монтирование
mount -t davfs https://server/webdav /mnt

# В /etc/fstab
https://server/webdav /mnt davfs user,noauto 0 0

# Credentials
# /etc/davfs2/secrets
https://server/webdav username password
```

---

## 44.8 Сравнение протоколов

| Протокол | Шифрование | Поддержка | Скорость | Использование |
|----------|------------|-----------|----------|---------------|
| NFS | NFSv4+Kerberos | UNIX | Высокая | Серверы, кластеры |
| SMB/CIFS | SMB3 | Все | Средняя | Windows среда |
| SFTP | Да (SSH) | Все | Средняя | Безопасная передача |
| SCP | Да (SSH) | Все | Высокая | Быстрые копии |
| SSHFS | Да (SSH) | UNIX | Средняя | Разработка |
| FTP | Нет (FTPS) | Все | Высокая | Легаси |
| rsync | SSH | UNIX | Высокая | Бэкапы, синхронизация |
| WebDAV | HTTPS | Все | Низкая | Облачное хранение |

---

## 44.9 Рекомендации

### Linux ↔ Linux

```bash
# Внутри доверенной сети: NFS
# Через интернет: rsync через SSH или SFTP
```

### Linux ↔ Windows

```bash
# Samba (SMB/CIFS)
# Или: WinSCP, FileZilla (SFTP)
```

### Бэкапы

```bash
# rsync — идеален для инкрементального бэкапа
rsync -avz --delete --backup --backup-dir=/backup/old \
    /data/ user@backup-server:/backup/current/
```

---

## Резюме

| Задача | Рекомендуемый протокол |
|--------|------------------------|
| Linux кластер | NFS v4 |
| Windows сеть | SMB3 (Samba) |
| Безопасная передача | SFTP/SCP |
| Удалённая разработка | SSHFS |
| Бэкапы | rsync |
| Облачный доступ | WebDAV |

??? question "Упражнения"
    **Задание 1.** Передайте файл по сети тремя способами: `scp`, `rsync`, `sftp`. Замерьте скорость. Какой способ эффективнее для повторной синхронизации?
    
    **Задание 2.** Настройте `rsync` с инкрементальным бэкапом: `rsync -avz --backup --backup-dir=backup_$(date +%F) src/ dst/`.
    
    **Задание 3.** Смонтируйте удалённую директорию через SSHFS: `sshfs user@host:/path /mnt/remote`. Работает ли это прозрачно для приложений?
