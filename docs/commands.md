# Индекс команд

Алфавитный справочник команд bash/shell, утилит и программ, упомянутых в книге.

---

## A

awk
:   Язык обработки текстовых данных по полям. Разбивает строку на поля по разделителю, позволяет фильтровать, трансформировать и агрегировать данные. → [Глава 19](chapters/ch3/19-csv-tsv.md), [Глава 28](chapters/ch4/28-text-processing.md)

## B

base32
:   Кодирование и декодирование данных в формате Base32. → [Глава 12](chapters/ch2/12-ascii.md)

base64
:   Кодирование и декодирование бинарных данных в текстовый формат Base64. → [Глава 12](chapters/ch2/12-ascii.md), [Глава 26](chapters/ch4/26-streams.md)

bat
:   Современная замена `cat` с подсветкой синтаксиса, номерами строк и интеграцией с Git. → [Глава 32](chapters/ch4/32-modern-tools.md)

bc
:   Калькулятор произвольной точности для командной строки. → [Глава 12](chapters/ch2/12-ascii.md)

blkid
:   Отображение идентификаторов блочных устройств (UUID, тип ФС, метка). → [Глава 34](chapters/ch5/34-architecture.md)

## C

cabextract
:   Распаковка архивов формата Windows CAB. → [Глава 24](chapters/ch3/24-archives.md)

cat
:   Вывод содержимого файлов в stdout. Конкатенация нескольких файлов. → [Глава 27](chapters/ch4/27-coreutils.md)

chgrp
:   Смена группы-владельца файла. → [Глава 6](chapters/ch1/06-permissions.md)

chmod
:   Изменение прав доступа к файлу (чтение, запись, исполнение). Поддерживает числовой (`755`) и символьный (`u+x`) форматы. → [Глава 6](chapters/ch1/06-permissions.md), [Глава 9](chapters/ch1/09-extended-attrs.md)

chown
:   Смена владельца и/или группы файла. → [Глава 3](chapters/ch1/03-metadata-inode.md), [Глава 6](chapters/ch1/06-permissions.md)

chroot
:   Смена корневой директории для процесса — изоляция файловой системы. → [Глава 1](chapters/ch1/01-file-definition.md)

comm
:   Построчное сравнение двух отсортированных файлов: уникальные для первого, для второго и общие строки. → [Глава 28](chapters/ch4/28-text-processing.md)

cp
:   Копирование файлов и директорий. Поддерживает `--reflink` для Copy-on-Write на Btrfs/XFS. → [Глава 5](chapters/ch1/05-file-operations.md)

cryptsetup
:   Утилита настройки шифрования дисков (LUKS). Создание, открытие и управление зашифрованными томами. → [Глава 6](chapters/ch1/06-permissions.md)

curl
:   Передача данных по URL — HTTP, HTTPS, FTP и другие протоколы. → [Глава 15](chapters/ch2/15-python-encodings.md), [Глава 46](chapters/ch5/46-http.md)

cut
:   Извлечение полей или столбцов из строк по разделителю или позиции символов. → [Глава 19](chapters/ch3/19-csv-tsv.md), [Глава 28](chapters/ch4/28-text-processing.md)

## D

date
:   Отображение и установка системной даты/времени. Форматирование через `+%FORMAT`. → [Глава 3](chapters/ch1/03-metadata-inode.md), [Глава 12](chapters/ch2/12-ascii.md)

dd
:   Побайтовое копирование и конвертация данных. Параметры: `if` (вход), `of` (выход), `bs` (размер блока), `seek`, `conv`. → [Глава 3](chapters/ch1/03-metadata-inode.md), [Глава 27](chapters/ch4/27-coreutils.md), [Глава 34](chapters/ch5/34-architecture.md)

debugfs
:   Интерактивный отладчик файловых систем ext2/ext3/ext4. Доступ к inode, блокам, журналу. → [Глава 36](chapters/ch5/36-unix-fs.md)

diff
:   Построчное сравнение двух файлов. Форматы вывода: unified (`-u`), context, ed. → [Глава 26](chapters/ch4/26-streams.md), [Глава 28](chapters/ch4/28-text-processing.md)

dirname
:   Извлечение директории из полного пути (`/a/b/c` → `/a/b`). → [Глава 8](chapters/ch1/08-paths-names.md)

diskutil
:   Утилита управления дисками в macOS. Форматирование, разметка, монтирование. → [Глава 34](chapters/ch5/34-architecture.md)

dos2unix
:   Конвертация окончаний строк из DOS/Windows (CRLF) в Unix (LF). → [Глава 12](chapters/ch2/12-ascii.md)

duckdb
:   Встраиваемая аналитическая СУБД. SQL-запросы напрямую к CSV, Parquet, JSON без импорта данных. → [Глава 33](chapters/ch4/33-duckdb.md)

dumpe2fs
:   Вывод информации о файловой системе ext2/ext3/ext4: суперблок, группы блоков, параметры. → [Глава 34](chapters/ch5/34-architecture.md), [Глава 36](chapters/ch5/36-unix-fs.md)

## E

echo
:   Вывод текста в stdout. С флагом `-e` поддерживает escape-последовательности (`\n`, `\t`, `\x41`). → [Глава 8](chapters/ch1/08-paths-names.md), [Глава 12](chapters/ch2/12-ascii.md)

emacs
:   Расширяемый текстовый редактор на базе Lisp. Набор режимов для разных языков и задач. → [Глава 29](chapters/ch4/29-editors.md)

enca
:   Определение и конвертация кодировок файлов. Автодетект на основе статистического анализа. → [Глава 13](chapters/ch2/13-encodings-babel.md)

expand
:   Замена символов табуляции на пробелы. → [Глава 28](chapters/ch4/28-text-processing.md)

exiftool
:   Чтение и редактирование метаданных медиафайлов: EXIF, IPTC, XMP в JPEG, TIFF, MP4, PDF и др. → [Глава 25](chapters/ch3/25-media.md)

## F

fd
:   Современная альтернатива `find`: быстрый поиск файлов с человекопонятным синтаксисом и подсветкой. → [Глава 32](chapters/ch4/32-modern-tools.md)

fdisk
:   Редактор разделов (MBR). Интерактивное создание, удаление и изменение таблицы разделов. → [Глава 34](chapters/ch5/34-architecture.md), [Глава 35](chapters/ch5/35-partitions.md)

ffmpeg
:   Утилита кодирования, декодирования и транскодирования аудио/видео. Поддерживает сотни форматов и кодеков. → [Глава 25](chapters/ch3/25-media.md)

ffprobe
:   Анализ свойств медиафайлов: кодеки, битрейт, разрешение, длительность. → [Глава 24](chapters/ch3/24-archives.md), [Глава 25](chapters/ch3/25-media.md)

file
:   Определение типа файла по magic bytes (сигнатуре), а не по расширению. → [Глава 10](chapters/ch2/10-binary-levels.md), [Глава 22](chapters/ch3/22-binary-structure.md)

find
:   Рекурсивный поиск файлов по имени, типу, размеру, времени, правам и другим критериям. → [Глава 5](chapters/ch1/05-file-operations.md), [Глава 13](chapters/ch2/13-encodings-babel.md)

fmt
:   Переформатирование текстовых абзацев: установка ширины строки, выравнивание. → [Глава 28](chapters/ch4/28-text-processing.md)

fsck
:   Проверка и восстановление целостности файловой системы. С журналированием — секунды, без — минуты/часы. → [Глава 36](chapters/ch5/36-unix-fs.md), [Глава 43](chapters/ch5/43-lvm.md)

fzf
:   Интерактивный нечёткий поиск (fuzzy finder). Фильтрация списков, файлов и истории команд. → [Глава 32](chapters/ch4/32-modern-tools.md)

## G

gdisk
:   Редактор разделов GPT. Аналог `fdisk` для таблицы разделов GUID. → [Глава 35](chapters/ch5/35-partitions.md)

getfacl
:   Чтение записей POSIX ACL (расширенных прав доступа) файла. → [Глава 6](chapters/ch1/06-permissions.md)

getfattr
:   Чтение расширенных атрибутов (xattr) файла. → [Глава 9](chapters/ch1/09-extended-attrs.md), [Глава 37](chapters/ch5/37-windows-fs.md)

git
:   Распределённая система контроля версий. Хранит объекты как content-addressable storage: blob, tree, commit, tag. → [Глава 30](chapters/ch4/30-languages.md), [Глава 47](chapters/ch5/47-git-fs.md)

grep
:   Поиск строк по регулярному выражению или фиксированной строке. Флаги: `-r` (рекурсивно), `-i` (без учёта регистра), `-c` (счёт), `-l` (имена файлов). → [Глава 28](chapters/ch4/28-text-processing.md)

## H

hdparm
:   Получение и настройка параметров жёстких дисков: режим DMA, кеширование, бенчмарк чтения. → [Глава 34](chapters/ch5/34-architecture.md)

head
:   Вывод первых N строк файла (по умолчанию 10). С параметром `-c` — первых N байтов. → [Глава 27](chapters/ch4/27-coreutils.md)

hexdump
:   Отображение содержимого файла в шестнадцатеричном формате. → [Глава 12](chapters/ch2/12-ascii.md), [Глава 29](chapters/ch4/29-editors.md)

## I

iconv
:   Конвертация текста между кодировками. Синтаксис: `iconv -f FROM -t TO`. → [Глава 13](chapters/ch2/13-encodings-babel.md), [Глава 14](chapters/ch2/14-unicode-utf8.md)

## J

jq
:   Процессор JSON: парсинг, фильтрация, трансформация JSON-данных из командной строки. → [Глава 16](chapters/ch3/16-json.md), [Глава 32](chapters/ch4/32-modern-tools.md)

## K

kpartx
:   Создание device-map для разделов внутри образа диска. Используется для работы с образами без записи на физический диск. → [Глава 34](chapters/ch5/34-architecture.md)

## L

ldd
:   Вывод списка динамических библиотек, от которых зависит исполняемый файл (ELF). → [Глава 22](chapters/ch3/22-binary-structure.md)

less
:   Постраничный просмотр файлов с навигацией, поиском и подсветкой. → [Глава 28](chapters/ch4/28-text-processing.md)

link
:   Создание жёсткой ссылки (низкоуровневый вызов). → [Глава 4](chapters/ch1/04-links.md)

ln
:   Создание ссылок: жёстких (`ln`) и символических (`ln -s`). → [Глава 4](chapters/ch1/04-links.md), [Глава 5](chapters/ch1/05-file-operations.md)

losetup
:   Создание и управление loop-устройствами: подключение файла-образа как блочного устройства. → [Глава 34](chapters/ch5/34-architecture.md)

lsblk
:   Отображение блочных устройств в виде дерева: диски, разделы, размеры, точки монтирования. → [Глава 34](chapters/ch5/34-architecture.md), [Глава 35](chapters/ch5/35-partitions.md)

lsof
:   Список открытых файлов и процессов, которые их используют. → [Глава 0](chapters/ch0/00-intro.md)

lvs
:   Вывод информации о логических томах LVM. → [Глава 43](chapters/ch5/43-lvm.md)

## M

mdadm
:   Управление программными RAID-массивами Linux: создание, мониторинг, расширение, восстановление. → [Глава 42](chapters/ch5/42-mdadm.md)

mkdir
:   Создание директорий. С флагом `-p` — рекурсивное создание вместе с родительскими. → [Глава 5](chapters/ch1/05-file-operations.md)

mkfifo
:   Создание именованного канала (FIFO) для межпроцессного взаимодействия. → [Глава 26](chapters/ch4/26-streams.md)

mkfs
:   Создание файловой системы на устройстве. Обёртка для `mkfs.ext4`, `mkfs.xfs` и др. → [Глава 34](chapters/ch5/34-architecture.md), [Глава 35](chapters/ch5/35-partitions.md)

mkfs.ext4
:   Создание файловой системы ext4 с настройкой размера блока, inode, журнала. → [Глава 36](chapters/ch5/36-unix-fs.md), [Глава 43](chapters/ch5/43-lvm.md)

mkfs.xfs
:   Создание файловой системы XFS. → [Глава 36](chapters/ch5/36-unix-fs.md)

mksquashfs
:   Создание read-only файловой системы SquashFS со сжатием. → [Глава 39](chapters/ch5/39-linux-fs.md)

mlr (Miller)
:   Обработка структурированных данных (CSV, JSON, TSV) из командной строки: фильтрация, сортировка, агрегация. → [Глава 19](chapters/ch3/19-csv-tsv.md), [Глава 32](chapters/ch4/32-modern-tools.md)

mount
:   Монтирование файловой системы в указанную директорию. Параметры: `-t` (тип ФС), `-o` (опции). → [Глава 34](chapters/ch5/34-architecture.md), [Глава 49](chapters/ch5/49-containers.md)

mv
:   Перемещение или переименование файлов и директорий. На одном разделе — атомарная операция (rename). → [Глава 5](chapters/ch1/05-file-operations.md)

## N

nano
:   Простой текстовый редактор с интуитивным интерфейсом. Подсказки горячих клавиш внизу экрана. → [Глава 29](chapters/ch4/29-editors.md)

nc (netcat)
:   Чтение и запись данных через сетевые соединения TCP/UDP. Универсальный «сетевой швейцарский нож». → [Глава 15](chapters/ch2/15-python-encodings.md)

nl
:   Нумерация строк в тексте с гибкими настройками формата. → [Глава 28](chapters/ch4/28-text-processing.md)

nm
:   Вывод таблицы символов (имена функций, переменных) из бинарных файлов (ELF). → [Глава 22](chapters/ch3/22-binary-structure.md)

## O

objdump
:   Дизассемблирование и анализ объектных файлов ELF: секции, заголовки, код. → [Глава 2](chapters/ch1/02-file-types-content.md), [Глава 22](chapters/ch3/22-binary-structure.md)

od
:   Дамп содержимого файла в восьмеричном, шестнадцатеричном или символьном формате. → [Глава 12](chapters/ch2/12-ascii.md), [Глава 26](chapters/ch4/26-streams.md)

otool
:   Анализ бинарных файлов Mach-O (macOS): заголовки, секции, библиотеки. Аналог `objdump`/`readelf` для Apple. → [Глава 22](chapters/ch3/22-binary-structure.md)

## P

parted
:   Универсальный редактор разделов (MBR и GPT). Поддерживает изменение размера разделов. → [Глава 35](chapters/ch5/35-partitions.md)

paste
:   Объединение строк из нескольких файлов бок о бок (через разделитель). → [Глава 28](chapters/ch4/28-text-processing.md)

perl
:   Язык программирования. В контексте обработки текста — мощные однострочники с regex. → [Глава 30](chapters/ch4/30-languages.md)

printf
:   Форматированный вывод в стиле C. Поддерживает `%s`, `%d`, `%x`, octal-последовательности (`\101` = A). → [Глава 12](chapters/ch2/12-ascii.md), [Глава 28](chapters/ch4/28-text-processing.md)

pvcreate
:   Инициализация физического тома для LVM. → [Глава 43](chapters/ch5/43-lvm.md)

pvs
:   Вывод информации о физических томах LVM. → [Глава 43](chapters/ch5/43-lvm.md)

## R

readelf
:   Отображение структуры ELF-файлов: заголовки, секции, таблица символов, dynamic linking. → [Глава 22](chapters/ch3/22-binary-structure.md)

readlink
:   Вывод цели символической ссылки. → [Глава 4](chapters/ch1/04-links.md), [Глава 8](chapters/ch1/08-paths-names.md)

realpath
:   Разрешение пути в абсолютный канонический (без симлинков и `..`). → [Глава 4](chapters/ch1/04-links.md), [Глава 8](chapters/ch1/08-paths-names.md)

resize2fs
:   Изменение размера файловой системы ext2/ext3/ext4 (расширение или уменьшение). → [Глава 42](chapters/ch5/42-mdadm.md), [Глава 43](chapters/ch5/43-lvm.md)

rev
:   Переворот каждой строки файла задом наперёд. → [Глава 28](chapters/ch4/28-text-processing.md)

rg (ripgrep)
:   Быстрый поиск по regex в файлах. Уважает `.gitignore`, поддерживает Unicode. Современная замена `grep -r`. → [Глава 32](chapters/ch4/32-modern-tools.md)

rm
:   Удаление файлов. С флагом `-r` — рекурсивное удаление директорий. → [Глава 5](chapters/ch1/05-file-operations.md)

rmdir
:   Удаление пустых директорий. → [Глава 5](chapters/ch1/05-file-operations.md)

ruby
:   Язык программирования. В контексте книги — пример файлового I/O в различных языках. → [Глава 30](chapters/ch4/30-languages.md)

## S

sed
:   Потоковый редактор: подстановка (`s/old/new/`), удаление, вставка строк. Обработка без загрузки всего файла в память. → [Глава 14](chapters/ch2/14-unicode-utf8.md), [Глава 28](chapters/ch4/28-text-processing.md)

setfacl
:   Установка записей POSIX ACL (расширенных прав доступа) на файлы. → [Глава 6](chapters/ch1/06-permissions.md)

setfattr
:   Установка расширенных атрибутов (xattr) файла. → [Глава 9](chapters/ch1/09-extended-attrs.md)

smartctl
:   Мониторинг здоровья дисков через S.M.A.R.T.: температура, переназначенные секторы, часы работы. → [Глава 34](chapters/ch5/34-architecture.md)

sort
:   Сортировка строк. Ключевые флаги: `-n` (числовая), `-k` (по полю), `-t` (разделитель), `-u` (уникальные). → [Глава 26](chapters/ch4/26-streams.md), [Глава 28](chapters/ch4/28-text-processing.md)

sqlite3
:   Клиент командной строки для SQLite. Также используется как аналитический инструмент для структурированных данных. → [Глава 32](chapters/ch4/32-modern-tools.md)

stat
:   Вывод метаданных файла: inode, размер, права, владелец, временные метки (atime, mtime, ctime). → [Глава 3](chapters/ch1/03-metadata-inode.md), [Глава 36](chapters/ch5/36-unix-fs.md)

stdbuf
:   Изменение режима буферизации потоков (unbuffered, line-buffered, fully buffered) для запущенной программы. → [Глава 26](chapters/ch4/26-streams.md)

strace
:   Трассировка системных вызовов процесса: `open`, `read`, `write`, `close`, `mmap` и др. Инструмент отладки. → [Глава 1](chapters/ch1/00-intro.md), [Глава 7](chapters/ch1/07-descriptors.md), [Глава 28](chapters/ch4/28-text-processing.md)

strings
:   Извлечение текстовых строк из бинарных файлов. Полезно для поиска читаемых данных в исполняемых файлах и дампах. → [Глава 22](chapters/ch3/22-binary-structure.md), [Глава 29](chapters/ch4/29-editors.md)

## T

tail
:   Вывод последних N строк файла. С флагом `-f` — непрерывное отслеживание новых строк (слежение за логами). → [Глава 26](chapters/ch4/26-streams.md), [Глава 27](chapters/ch4/27-coreutils.md)

tar
:   Создание и распаковка архивов (Tape Archive). Формат — последовательность 512-байтных блоков. Сжатие через внешние алгоритмы: `-z` (gzip), `-j` (bzip2), `-J` (xz), `--zstd`. → [Глава 24](chapters/ch3/24-archives.md), [Глава 42](chapters/ch5/42-mdadm.md)

tee
:   Дублирование потока: вывод одновременно в файл и в stdout. → [Глава 26](chapters/ch4/26-streams.md), [Глава 27](chapters/ch4/27-coreutils.md)

touch
:   Создание пустого файла или обновление временных меток существующего. → [Глава 5](chapters/ch1/05-file-operations.md)

tr
:   Замена, удаление или сжатие символов. Работает посимвольно (не по строкам). → [Глава 12](chapters/ch2/12-ascii.md), [Глава 26](chapters/ch4/26-streams.md), [Глава 27](chapters/ch4/27-coreutils.md)

tune2fs
:   Настройка параметров ext2/ext3/ext4: добавление журнала (`-j`), изменение mount count, зарезервированное пространство. → [Глава 3](chapters/ch1/03-metadata-inode.md), [Глава 36](chapters/ch5/36-unix-fs.md)

## U

umount
:   Размонтирование файловой системы. → [Глава 34](chapters/ch5/34-architecture.md)

uniq
:   Удаление или подсчёт повторяющихся **смежных** строк. Обычно используется после `sort`. → [Глава 26](chapters/ch4/26-streams.md), [Глава 28](chapters/ch4/28-text-processing.md)

unix2dos
:   Конвертация окончаний строк из Unix (LF) в DOS/Windows (CRLF). → [Глава 12](chapters/ch2/12-ascii.md)

unlink
:   Удаление файла (низкоуровневый системный вызов). Удаляет запись dentry, уменьшает счётчик ссылок inode. → [Глава 5](chapters/ch1/05-file-operations.md)

unshare
:   Запуск процесса в отдельных Linux namespaces (mount, PID, network). Основа контейнерной изоляции. → [Глава 1](chapters/ch1/01-file-definition.md), [Глава 49](chapters/ch5/49-containers.md)

unzip
:   Распаковка ZIP-архивов. → [Глава 24](chapters/ch3/24-archives.md)

## V

vgcreate
:   Создание группы томов LVM из физических томов. → [Глава 43](chapters/ch5/43-lvm.md)

vgs
:   Вывод информации о группах томов LVM. → [Глава 43](chapters/ch5/43-lvm.md)

vim
:   Текстовый редактор с модальным интерфейсом. Мощное редактирование через комбинации команд. Hex-режим через `%!xxd`. → [Глава 29](chapters/ch4/29-editors.md)

## W

wc
:   Подсчёт строк (`-l`), слов (`-w`) и байтов (`-c`) в файлах. → [Глава 26](chapters/ch4/26-streams.md), [Глава 27](chapters/ch4/27-coreutils.md), [Глава 28](chapters/ch4/28-text-processing.md)

wget
:   Загрузка файлов по HTTP/HTTPS. Поддерживает рекурсивную загрузку и докачку (`-c`). → [Глава 15](chapters/ch2/15-python-encodings.md)

## X

xargs
:   Построение и выполнение команд из stdin. Часто используется с `find`: `find . -name '*.txt' | xargs grep pattern`. → [Глава 27](chapters/ch4/27-coreutils.md)

xxd
:   Шестнадцатеричный редактор/просмотрщик. Двустороннее преобразование: бинарный ↔ hex-дамп. Reverse-режим: `xxd -r`. → [Глава 10](chapters/ch2/10-binary-levels.md), [Глава 12](chapters/ch2/12-ascii.md)

## Y

yes
:   Бесконечный вывод строки (по умолчанию `y`). Используется для автоматизации интерактивных команд. → [Глава 26](chapters/ch4/26-streams.md)

yq
:   Процессор YAML из командной строки. Аналог `jq` для YAML. → [Глава 17](chapters/ch3/17-yaml.md), [Глава 32](chapters/ch4/32-modern-tools.md)

## Z

zip
:   Создание ZIP-архивов. Каждый файл сжимается независимо (в отличие от tar+gzip). → [Глава 24](chapters/ch3/24-archives.md)
