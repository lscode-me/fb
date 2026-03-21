# Глоссарий

Ключевые термины книги. При первом упоминании в тексте термин даётся с определением; здесь — полный алфавитный справочник.

---

## 0–9

9P
:   Сетевой протокол Plan 9, представляющий все ресурсы ОС (файлы, сеть, устройства, процессы) как файлы, доступные через `read`/`write`. Основа философии «everything is a file» в чистом виде. → [Глава 48](chapters/ch5/48-plan9.md)

## A

ACL (Access Control List, список управления доступом)
:   Расширенная модель прав, позволяющая задавать разрешения для произвольных пользователей и групп, в отличие от базовой модели owner/group/other. → [Глава 9](chapters/ch1/09-extended-attrs.md)

Apache Arrow
:   Колоночный формат данных **в памяти** для эффективного обмена между системами и языками без сериализации. Zero-copy read, SIMD-оптимизации. → [Глава 23](chapters/ch3/23-bigdata-formats.md)

APFS (Apple File System)
:   Файловая система Apple (macOS 10.13+), заменившая HFS+. Copy-on-write, снапшоты, клонирование файлов, встроенное шифрование, space sharing между томами. → [Глава 38](chapters/ch5/38-bsd-fs.md)

ASCII (American Standard Code for Information Interchange)
:   7-битная кодировка символов, определяющая 128 символов (33 управляющих + 95 печатных). Основа всех современных кодировок. → [Глава 12](chapters/ch2/12-ascii.md)

Avro
:   Строковый формат сериализации данных Apache. Хранит схему вместе с данными, используется в Hadoop-экосистеме. → [Глава 23](chapters/ch3/23-bigdata-formats.md)

## B

B-tree / B+ tree (сбалансированное дерево)
:   Структура данных для индексирования с O(log n) поиском. B+ tree хранит данные только в листьях. Используется в XFS (allocation groups), Btrfs (вся ФС — одно B-tree), ext4 (dir_index). → [Глава 36](chapters/ch5/36-unix-fs.md), [Глава 40](chapters/ch5/40-zfs.md), [Глава 41](chapters/ch5/41-btrfs.md)

Base64
:   Схема кодирования бинарных данных в ASCII-символы. Используется для передачи бинарных данных через текстовые протоколы (email, JSON). → [Глава 11](chapters/ch2/11-bytes-encoding.md)

Big-endian / Little-endian (порядок байтов)
:   Порядок байтов (byte order, endianness). Big-endian — старший байт первый (сетевой порядок). Little-endian — младший байт первый (x86). → [Глава 10](chapters/ch2/10-binary-levels.md)

Block device (блочное устройство)
:   Устройство хранения, предоставляющее доступ к данным блоками фиксированного размера (обычно 512 байт или 4 КБ). Примеры: `/dev/sda`, `/dev/nvme0n1`. → [Глава 34](chapters/ch5/34-architecture.md)

Block group (группа блоков)
:   Единица организации ext2/ext3/ext4: раздел делится на группы, каждая содержит копию суперблока, inode table, bitmaps и блоки данных. Наследник cylinder group из FFS. → [Глава 36](chapters/ch5/36-unix-fs.md)

BOM (Byte Order Mark, метка порядка байтов)
:   Специальный символ Unicode U+FEFF в начале файла, указывающий порядок байтов для UTF-16/UTF-32. В UTF-8 не требуется, но иногда добавляется Windows-приложениями. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

Btrfs (B-tree File System)
:   Файловая система Linux с поддержкой copy-on-write, снапшотов, встроенного RAID, сжатия и дедупликации. → [Глава 41](chapters/ch5/41-btrfs.md)

## C

Checksum (контрольная сумма)
:   Хеш-значение, вычисленное по данным для обнаружения повреждений. ZFS и Btrfs хранят checksum для **каждого** блока; ext4 и XFS — только для метаданных. → [Глава 40](chapters/ch5/40-zfs.md), [Глава 41](chapters/ch5/41-btrfs.md)

CESU-8 (Compatibility Encoding Scheme for UTF-16: 8-Bit)
:   Нестандартный вариант UTF-8, кодирующий символы вне BMP через суррогатные пары (6 байтов вместо 4). MUTF-8 = CESU-8 + overlong NUL. Встречается в Oracle DB и некоторых XML-парсерах. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

Code point (кодовая позиция Unicode)
:   Уникальный числовой идентификатор символа в Unicode (U+0000 — U+10FFFF). Один code point может занимать 1–4 байта в UTF-8 или 2–4 байта в UTF-16. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

Codec (кодек)
:   Алгоритм сжатия/распаковки данных. В контексте медиа: H.264 (видео), AAC (аудио), Opus (аудио). Не путать с контейнером. → [Глава 25](chapters/ch3/25-media.md)

Container (контейнер, формат-контейнер)
:   Файловый формат, объединяющий несколько потоков данных (видео, аудио, субтитры). Примеры: MP4, MKV, WebM. Не путать с Docker-контейнерами. → [Глава 25](chapters/ch3/25-media.md)

Copy-on-Write (CoW, копирование при записи)
:   Стратегия записи: данные не перезаписываются на месте, а записываются в новое место. Используется в ZFS, Btrfs. Позволяет создавать мгновенные снапшоты. → [Глава 40](chapters/ch5/40-zfs.md), [Глава 41](chapters/ch5/41-btrfs.md)

Coreutils (базовые утилиты)
:   Набор базовых утилит GNU/POSIX: `cat`, `head`, `tail`, `sort`, `uniq`, `cut`, `tr`, `wc`, `tee`, `xargs` и др. → [Глава 27](chapters/ch4/27-coreutils.md)

cramfs (Compressed ROM File System)
:   Устаревшая read-only файловая система со сжатием для embedded Linux. Ограничения: максимум 16 МБ на файл. Заменена на SquashFS и EROFS. → [Глава 39](chapters/ch5/39-linux-fs.md)

CSV (Comma-Separated Values, значения через запятую)
:   Текстовый табличный формат. Каждая строка — запись, поля разделены запятыми. Стандарт: RFC 4180. → [Глава 19](chapters/ch3/19-csv-tsv.md)

Cylinder group (группа цилиндров)
:   Единица организации BSD FFS: диск делится на группы цилиндров, каждая с копией суперблока, inode table и данными. Минимизирует перемещение головки. Наследник — block group в ext2/ext3/ext4. → [Глава 36](chapters/ch5/36-unix-fs.md)

## D

dd (dataset definition / disk dump)
:   Утилита копирования и конвертации данных побайтно. Используется для создания образов дисков, запись ISO на USB, бинарный патчинг. Параметры: `if` (input), `of` (output), `bs` (block size), `seek`, `conv`. → [Глава 27](chapters/ch4/27-coreutils.md)

Deduplication (дедупликация)
:   Оптимизация хранения: одинаковые блоки данных хранятся в одном экземпляре, остальные ссылаются на него. Экономит место, но требует RAM. Поддерживается ZFS (inline), Btrfs (offline). → [Глава 40](chapters/ch5/40-zfs.md), [Глава 41](chapters/ch5/41-btrfs.md)

DEFLATE
:   Алгоритм сжатия без потерь, комбинация LZ77 (замена повторов ссылками) и Huffman coding (короткие коды для частых символов). Используется в gzip, PNG, ZIP. → [Глава 24](chapters/ch3/24-archives.md)

Dentry (directory entry, запись каталога)
:   Запись в директории, связывающая имя файла с номером inode. Директория — это файл, содержащий список dentry. → [Глава 2](chapters/ch1/02-file-types-content.md)

Docker / OCI
:   Docker — платформа контейнеризации на основе Linux namespaces и cgroups. OCI (Open Container Initiative) — стандарт образов и runtime контейнеров. Образы состоят из слоёв OverlayFS. → [Глава 49](chapters/ch5/49-containers.md)

DuckDB
:   Встраиваемая аналитическая СУБД (OLAP). Позволяет выполнять SQL-запросы напрямую к CSV, Parquet, JSON файлам без импорта. → [Глава 33](chapters/ch4/33-duckdb.md)

## E

ELF (Executable and Linkable Format)
:   Формат исполняемых файлов в Linux/Unix. Содержит заголовок, секции кода и данных, таблицу символов. Magic number: `\x7fELF`. → [Глава 22](chapters/ch3/22-binary-structure.md)

Endianness (порядок байтов)
:   См. Big-endian / Little-endian.

EROFS (Enhanced Read-Only File System)
:   Современная read-only файловая система для Linux (kernel 5.4+). Разработана Huawei для Android. Преимущества: высокая производительность на flash, LZ4/LZMA сжатие, shared page cache (Linux 7.0+) для дедупликации памяти между контейнерами. → [Глава 39](chapters/ch5/39-linux-fs.md), [Глава 49](chapters/ch5/49-containers.md)

EXIF (Exchangeable Image File Format)
:   Метаданные, встроенные в JPEG/TIFF: настройки камеры (ISO, диафрагма, выдержка), GPS-координаты, дата съёмки. Хранится в APP1-маркере JPEG. → [Глава 25](chapters/ch3/25-media.md)

Extent (экстент)
:   Непрерывный диапазон блоков (например, «блоки 1000–5000»), заменяющий косвенные указатели на отдельные блоки. Резко сокращает метаданные для больших файлов. Используется в ext4, XFS, Btrfs. → [Глава 36](chapters/ch5/36-unix-fs.md)

ext2 (Second Extended Filesystem)
:   ФС Linux (1993) с длинными именами файлов, настраиваемым размером блока и группами блоков. Не имеет журнала — `fsck` после сбоя проверяет весь диск. Превращается в ext3 командой `tune2fs -j`. → [Глава 36](chapters/ch5/36-unix-fs.md)

ext3 (Third Extended Filesystem)
:   ext2 + журналирование (2001). Три режима: journal (метаданные + данные), ordered (данные до метаданных), writeback (только метаданные). Восстановление после сбоя — секунды вместо минут. → [Глава 36](chapters/ch5/36-unix-fs.md)

ext4 (Fourth Extended Filesystem)
:   Основная файловая система Linux. Журналируемая, extents, delayed allocation, multiblock allocation. Файлы до 16 ТБ, разделы до 1 ЭБ. → [Глава 36](chapters/ch5/36-unix-fs.md), [Глава 39](chapters/ch5/39-linux-fs.md)

## F

FAT / FAT32 / exFAT (File Allocation Table)
:   Семейство простых ФС Microsoft. FAT32: максимум 4 ГБ на файл, 32 ГБ на раздел. exFAT: снимает ограничения, стандарт для флешек и SD-карт. Максимальная совместимость между ОС. → [Глава 37](chapters/ch5/37-windows-fs.md)

fd (file descriptor, файловый дескриптор)
:   Целочисленный идентификатор открытого файла в процессе. 0 = stdin, 1 = stdout, 2 = stderr. → [Глава 7](chapters/ch1/07-descriptors.md)

FFS (Fast File System, быстрая файловая система)
:   Революционная ФС Berkeley (4.2BSD, 1983). Ввела группы цилиндров, большие блоки (4–8 КБ) и ротационную оптимизацию, достигнув 50% пропускной способности диска. Основа для ext2/ext3/ext4. Не путать с UFS. → [Глава 36](chapters/ch5/36-unix-fs.md)

FIFO (named pipe, именованный канал)
:   Специальный файл для межпроцессного взаимодействия. Создаётся через `mkfifo`. Данные передаются в порядке FIFO. → [Глава 26](chapters/ch4/26-streams.md)

FLAC (Free Lossless Audio Codec)
:   Кодек сжатия аудио **без потерь**. Сжимает PCM-данные на ~40–60% с полным восстановлением оригинала. Открытый формат. → [Глава 25](chapters/ch3/25-media.md)

fsck (file system check, проверка файловой системы)
:   Утилита проверки и восстановления целостности ФС после сбоя. С журналированием (ext3/ext4) — секунды; без журнала (ext2) — минуты/часы на больших дисках. → [Глава 36](chapters/ch5/36-unix-fs.md)

FUSE (Filesystem in Userspace, файловая система в пользовательском пространстве)
:   Интерфейс для создания файловых систем в пользовательском пространстве без модификации ядра. Примеры: sshfs, s3fs. → [Глава 34](chapters/ch5/34-architecture.md)

## G

Git objects (объекты Git)
:   Content-addressable хранилище с четырьмя типами: blob (содержимое файла), tree (директория), commit (снапшот), tag (именованная ссылка). Идентифицируются SHA-1 хешами. → [Глава 47](chapters/ch5/47-git-fs.md)

GPT (GUID Partition Table, таблица разделов GUID)
:   Современная схема разметки дисков, замена MBR. Поддерживает до 128 разделов и диски > 2 ТБ. → [Глава 35](chapters/ch5/35-partitions.md)

GB18030
:   Китайский национальный стандарт кодирования символов. Единственная кодировка помимо UTF-*, покрывающая **все** code points Unicode. 1/2/4 байта переменной длины. Обязателен для всего ПО, продаваемого в Китае. Обратно совместим с GBK и GB2312. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

gzip (GNU zip)
:   Алгоритм сжатия на основе DEFLATE. Сжимает один файл (чаще всего tar-архив). `.tar.gz` / `.tgz` — самый распространённый формат архивов в Unix. → [Глава 24](chapters/ch3/24-archives.md)

## H

HAMMER / HAMMER2
:   Файловые системы DragonFly BSD. Copy-on-write, встроенные снапшоты, дедупликация. HAMMER2 добавляет сжатие и кластерную архитектуру. → [Глава 38](chapters/ch5/38-bsd-fs.md)

Hard link (жёсткая ссылка)
:   Дополнительное имя (dentry) для существующего inode. Все жёсткие ссылки равноправны. Файл удаляется когда счётчик ссылок достигает 0. → [Глава 4](chapters/ch1/04-links.md)

HFS+ (Hierarchical File System Plus)
:   Файловая система macOS до APFS. Журналирование, поддержка Unicode, case-insensitive по умолчанию. Заменена APFS в macOS 10.13+. → [Глава 38](chapters/ch5/38-bsd-fs.md)

Huffman coding (кодирование Хаффмана)
:   Алгоритм сжатия без потерь: частым символам назначаются короткие битовые коды, редким — длинные. Часть DEFLATE (используется в gzip, PNG, ZIP). → [Глава 24](chapters/ch3/24-archives.md)

## I

IDNA (Internationalized Domain Names in Applications)
:   Стандарт представления Unicode-доменов в ASCII через Punycode с префиксом `xn--`. Позволяет регистрировать домены вроде `münchen.de` или `пример.рф`. Уязвим к гомографическим атакам. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

Inode (index node, индексный узел)
:   Структура данных в файловой системе, хранящая метаданные файла: размер, владелец, права, временные метки, указатели на блоки данных. Не содержит имя файла. → [Глава 3](chapters/ch1/03-metadata-inode.md)

IOPS (Input/Output Operations Per Second, операции ввода-вывода в секунду)
:   Метрика производительности накопителя. HDD: ~100–200, SSD: ~10 000–100 000, NVMe: ~100 000–1 000 000. → [Глава 34](chapters/ch5/34-architecture.md)

iSCSI (Internet SCSI)
:   Протокол передачи SCSI-команд по TCP/IP. Позволяет использовать удалённое блочное хранилище как локальный диск. Более низкоуровневый, чем NFS/SMB. → [Глава 44](chapters/ch5/44-protocols.md)

ISO-8859-1 (Latin-1)
:   8-битная кодировка для западноевропейских языков. Совместима с ASCII (0x00–0x7F). Первые 256 code points Unicode совпадают с Latin-1. → [Глава 13](chapters/ch2/13-encodings-babel.md)

ISO9660
:   Стандарт файловой системы для CD/DVD (1988). Расширения: Rock Ridge (POSIX права, symlinks), Joliet (Unicode имена), El Torito (загрузка с CD). → [Глава 39](chapters/ch5/39-linux-fs.md)

## J

JSON (JavaScript Object Notation)
:   Текстовый формат обмена данными. Поддерживает: объекты, массивы, строки, числа, boolean, null. → [Глава 16](chapters/ch3/16-json.md)

JSON Lines (JSONL)
:   Формат, где каждая строка файла — отдельный JSON-объект. Удобен для потоковой обработки и логов. → [Глава 16](chapters/ch3/16-json.md)

Journaling (журналирование)
:   Техника обеспечения целостности ФС: операции сначала записываются в журнал, затем применяются. При сбое — повтор или откат из журнала. → [Глава 36](chapters/ch5/36-unix-fs.md), [Глава 39](chapters/ch5/39-linux-fs.md)

## K

KOI8-R
:   8-битная кодировка кириллицы. Особенность: при сбросе 8-го бита буквы дают читаемую транслитерацию. → [Глава 13](chapters/ch2/13-encodings-babel.md)

## L

LFS (Log-Structured File System)
:   ФС, записывающая все данные последовательно в кольцевой лог, как в журнал. Оптимальна для SSD (только последовательные записи). Реализация в NetBSD. Редко используется на практике. → [Глава 38](chapters/ch5/38-bsd-fs.md)

LVM (Logical Volume Manager, менеджер логических томов)
:   Абстракция между физическими дисками и файловыми системами в Linux. Позволяет расширять/уменьшать тома, создавать снапшоты. → [Глава 43](chapters/ch5/43-lvm.md)

## M

Mach-O (Mach Object)
:   Формат исполняемых файлов macOS/iOS. Аналог ELF для Apple-платформ. → [Глава 22](chapters/ch3/22-binary-structure.md)

Magic number (магическое число, сигнатура файла)
:   Последовательность байтов в начале файла, идентифицирующая формат. Примеры: `\x89PNG` (PNG), `%PDF` (PDF), `PK` (ZIP). → [Глава 22](chapters/ch3/22-binary-structure.md)

MBR (Master Boot Record, главная загрузочная запись)
:   Устаревшая схема разметки дисков. Ограничения: максимум 4 основных раздела, максимум 2 ТБ. → [Глава 35](chapters/ch5/35-partitions.md)

MessagePack (MsgPack)
:   Бинарный формат сериализации, совместимый по модели данных с JSON, но компактнее и быстрее. → [Глава 21](chapters/ch3/21-binary-serialization.md)

mmap (memory-mapped file, файл, отображённый в память)
:   Механизм отображения файла в память процесса. Позволяет работать с файлом как с массивом байтов. → [Глава 31](chapters/ch4/31-python-deep.md)

MUTF-8 (Modified UTF-8)
:   Нестандартный вариант UTF-8 для экосистемы Java. Два отличия: нулевой символ кодируется как `C0 80` (overlong encoding), символы вне BMP — через суррогатные пары (6 байтов). Используется в `.class` файлах, JNI, Android DEX. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

## N

NFS (Network File System, сетевая файловая система)
:   Протокол прозрачного доступа к удалённым файлам в Unix-мире. NFSv3 — stateless, NFSv4 — stateful с Kerberos-аутентификацией. Работает через RPC. → [Глава 44](chapters/ch5/44-protocols.md)

NFC / NFD (Unicode Normalization, нормализация Unicode)
:   Формы нормализации Unicode. NFC — composed (é = один code point). NFD — decomposed (é = e + combining accent). Важно при сравнении строк и именах файлов (macOS использует NFD). → [Глава 14](chapters/ch2/14-unicode-utf8.md)

NTFS (New Technology File System)
:   Файловая система Windows. Поддерживает журналирование, ACL, ADS (Alternate Data Streams), сжатие, шифрование. Центральная структура — MFT (Master File Table). → [Глава 37](chapters/ch5/37-windows-fs.md)

## O

Object storage (объектное хранилище)
:   Архитектура хранения данных без иерархии каталогов. Каждый объект = ключ + данные + метаданные. Пример: Amazon S3. → [Глава 45](chapters/ch5/45-s3.md)

ORC (Optimized Row Columnar)
:   Колоночный формат Apache Hive. Хранит данные в stripe’ах с лёгкой индексацией. Конкурент Parquet в экосистеме Hadoop. → [Глава 23](chapters/ch3/23-bigdata-formats.md)

OverlayFS
:   Слоёная файловая система Union FS типа. Объединяет несколько директорий в одну: read-only нижние слои (lower) + read-write верхний слой (upper) → объединённый вид (merged). Используется Docker и Podman для слоёв контейнерных образов. → [Глава 39](chapters/ch5/39-linux-fs.md), [Глава 49](chapters/ch5/49-containers.md)

## P

Page cache (страничный кеш)
:   Кеш дисковых страниц в оперативной памяти ядра. Повторное чтение файла не требует обращения к диску. В ZFS аналог — ARC (Adaptive Replacement Cache). → [Глава 34](chapters/ch5/34-architecture.md)

Parquet (колоночный формат)
:   Колоночный бинарный формат для аналитических данных. Эффективное сжатие, предикатный pushdown. Стандарт де-факто в Big Data. → [Глава 23](chapters/ch3/23-bigdata-formats.md)

PE (Portable Executable)
:   Формат исполняемых файлов Windows (`.exe`, `.dll`). → [Глава 22](chapters/ch3/22-binary-structure.md)

Pipe (канал, пайп)
:   Механизм соединения stdout одного процесса со stdin другого: `cmd1 | cmd2`. Основа философии UNIX. → [Глава 26](chapters/ch4/26-streams.md)

POSIX (Portable Operating System Interface)
:   Стандарт API для Unix-подобных ОС: `open`, `read`, `write`, `close`, `chmod`, `stat` и др. Обеспечивает переносимость программ между Linux, BSD, macOS. → используется во всех частях книги

procfs / sysfs (виртуальные файловые системы)
:   `/proc` — информация о процессах и системе (файлы генерируются ядром). `/sys` — устройства и подсистемы ядра в виде файлов. Не занимают места на диске. → [Глава 39](chapters/ch5/39-linux-fs.md)

Protocol Buffers (Protobuf)
:   Бинарный формат сериализации от Google. Требует определения схемы (`.proto` файл). Компактный и быстрый. → [Глава 21](chapters/ch3/21-binary-serialization.md)

Punycode
:   Алгоритм кодирования Unicode в ASCII-совместимую форму (`a-z`, `0-9`, `-`) для доменных имён. `münchen` → `xn--mnchen-3ya`. Используется в IDNA. В Python: `'münchen'.encode('punycode')`. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

## R

RAID (Redundant Array of Independent Disks, избыточный массив дисков)
:   Технология объединения дисков для повышения надёжности и/или производительности. Уровни: 0, 1, 5, 6, 10. → [Глава 42](chapters/ch5/42-mdadm.md)

ReFS (Resilient File System)
:   ФС Windows Server с контрольными суммами, автовосстановлением и поддержкой томов до 35 ПБ. Не поддерживает сжатие, шифрование и загрузку ОС. → [Глава 37](chapters/ch5/37-windows-fs.md)

## S

S3 (Simple Storage Service)
:   Объектное хранилище Amazon. API стал стандартом де-факто (MinIO, Ceph). Ключевые понятия: bucket, object, presigned URL. → [Глава 45](chapters/ch5/45-s3.md)

Scrub (скраб)
:   Операция проверки всех блоков данных по контрольным суммам. При наличии RAID автоматически восстанавливает повреждённые блоки из копии. Поддерживается ZFS и Btrfs. → [Глава 40](chapters/ch5/40-zfs.md), [Глава 41](chapters/ch5/41-btrfs.md)

SFTP (SSH File Transfer Protocol)
:   Протокол передачи файлов по шифрованному SSH-каналу. Поддерживает докачку, листинг, права. Не путать с FTP-over-SSL (FTPS). → [Глава 44](chapters/ch5/44-protocols.md)

Shift_JIS
:   Японская кодировка переменной длины (1–2 байта). Поддерживает кандзи, хирагану, катакану. Пример проблемы несовместимых региональных кодировок. → [Глава 13](chapters/ch2/13-encodings-babel.md)

Silent data corruption (тихое повреждение данных)
:   Диск возвращает испорченные данные **без сообщения об ошибке**. Причины: сбой прошивки, bit flip, ошибка на шине. ext4/XFS не обнаруживают; ZFS и Btrfs защищают через checksums. → [Глава 36](chapters/ch5/36-unix-fs.md), [Глава 40](chapters/ch5/40-zfs.md), [Глава 41](chapters/ch5/41-btrfs.md)

SMB / CIFS (Server Message Block)
:   Протокол сетевого доступа к файлам Windows. SMB3 добавляет шифрование и мультиканальность. Реализация для Unix — Samba. → [Глава 44](chapters/ch5/44-protocols.md)

Snapshot (снапшот)
:   Мгновенная копия состояния ФС через Copy-on-Write. Не дублирует данные — занимает место только по мере изменения блоков. Поддерживается ZFS, Btrfs, APFS, LVM. → [Глава 40](chapters/ch5/40-zfs.md), [Глава 41](chapters/ch5/41-btrfs.md)

Soft Updates
:   Механизм BSD FFS/UFS2 для crash consistency без журнала: ядро отслеживает зависимости между метаданными и упорядочивает записи так, чтобы сбой не приводил к несогласованности. → [Глава 38](chapters/ch5/38-bsd-fs.md)

Sparse file (разреженный файл)
:   Файл, в котором последовательности нулевых байтов не занимают место на диске. `ls -l` показывает логический размер, `du` — фактический. → [Глава 3](chapters/ch1/03-metadata-inode.md)

SquashFS
:   Read-only файловая система со сжатием (kernel 2.6.29+). Поддерживает gzip, xz, zstd, lzo. Используется в Ubuntu Live CD, Snap packages, embedded системах. Инструменты: `mksquashfs`, `unsquashfs`. → [Глава 39](chapters/ch5/39-linux-fs.md)

SSHFS
:   Файловая система на базе FUSE, монтирующая удалённые директории через SSH. Прозрачный доступ к удалённым файлам как к локальным. → [Глава 44](chapters/ch5/44-protocols.md)

Surrogate pair (суррогатная пара)
:   Механизм UTF-16 для кодирования символов вне BMP (U+10000+). Пара 16-битных значений: high surrogate (U+D800–U+DBFF) + low surrogate (U+DC00–U+DFFF). Даёт 1 024 × 1 024 = 1 048 576 комбинаций. Суррогатные code points не являются символами. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

Superblock (суперблок)
:   Главная метаданная структура ФС: magic number, размер блока, количество inode, общий размер. Копии распределяются по группам блоков для восстановления. → [Глава 34](chapters/ch5/34-architecture.md), [Глава 36](chapters/ch5/36-unix-fs.md)

Symbolic link (симлинк, символическая ссылка)
:   Специальный файл, содержащий путь к другому файлу. В отличие от жёсткой ссылки, может указывать на файлы в других ФС и на несуществующие файлы. → [Глава 4](chapters/ch1/04-links.md)

## T

tar (Tape Archive)
:   Формат архивирования (1979): последовательность 512-байтных заголовков и данных файлов. Без встроенного сжатия — комбинируется с gzip (`.tar.gz`), bzip2, xz, zstd. → [Глава 24](chapters/ch3/24-archives.md)

tmpfs (temporary filesystem)
:   Файловая система в оперативной памяти (и swap). Используется для `/tmp`, `/dev/shm`, `/run`. Содержимое исчезает при перезагрузке. → [Глава 39](chapters/ch5/39-linux-fs.md)

Tokenization (токенизация)
:   В контексте LLM: разбиение текста на подслова (subword tokens) через BPE или SentencePiece. Словарь ~32K–200K токенов. Определяет, как модель «видит» текст и файлы. → [Глава 50](chapters/ch5/50-tokenization.md)

TOML (Tom's Obvious Minimal Language)
:   Текстовый формат конфигураций. Явная типизация (даты, числа). Используется в `pyproject.toml`, `Cargo.toml`. → [Глава 18](chapters/ch3/18-toml-ini.md)

TRIM / Discard
:   Команда SSD (ATA TRIM / NVMe Deallocate) сообщающая, что блоки больше не используются. Позволяет SSD выполнять сборку мусора и поддерживать производительность. → [Глава 34](chapters/ch5/34-architecture.md)

TSV (Tab-Separated Values, значения через табуляцию)
:   Табличный формат с разделителем-табуляцией. Преимущество перед CSV: табуляция реже встречается в данных, меньше проблем с экранированием. → [Глава 19](chapters/ch3/19-csv-tsv.md)

## U

UFS / UFS2 (Unix File System)
:   Эволюция FFS для FreeBSD. UFS2 добавляет 64-битные указатели, наносекундные метки времени, расширенные атрибуты. Поддерживает Soft Updates и опциональное журналирование. → [Глава 36](chapters/ch5/36-unix-fs.md), [Глава 38](chapters/ch5/38-bsd-fs.md)

umask (маска прав)
:   Маска прав по умолчанию для новых файлов. Определяет, какие биты прав **не** устанавливаются. Типичное значение: 022 (файлы создаются с 644). → [Глава 6](chapters/ch1/06-permissions.md)

Unicode
:   Стандарт кодирования символов всех письменностей мира. Определяет ~150 000 символов в 17 плоскостях (planes). Code point записывается как U+XXXX. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

UTF-8
:   Кодировка Unicode с переменной длиной (1–4 байта на символ). ASCII-совместима. Стандарт де-факто для web и Unix. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

UTF-7
:   7-битная кодировка Unicode (RFC 2152). Не-ASCII символы кодируются через Modified Base64 в блоках `+...−`. Использовалась в email-шлюзах 1990-х. Стала вектором XSS-атак через автодетект кодировки. Единственное живое применение — Modified UTF-7 в IMAP. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

UTF-16
:   Кодировка Unicode: 2 байта для символов BMP (U+0000–U+FFFF), 4 байта (суррогатные пары) для остальных. Используется внутри Windows, Java, JavaScript. Требует BOM для указания порядка байтов. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

## V

vdev (Virtual Device)
:   Абстракция устройства хранения в ZFS: одиночный диск, mirror, raidz1/z2/z3. Пул (zpool) состоит из одного или нескольких vdev. → [Глава 40](chapters/ch5/40-zfs.md)

VFS (Virtual File System, виртуальная файловая система)
:   Абстракционный слой ядра, предоставляющий единый интерфейс для разных файловых систем. Программа вызывает `open()` — VFS направляет вызов в нужный драйвер ФС. → [Глава 34](chapters/ch5/34-architecture.md)

## W

WAPBL (Write-Ahead Physical Block Logging)
:   Реализация журналирования для NetBSD FFS. Записывает физические блоки в журнал перед изменением, обеспечивая crash consistency. → [Глава 38](chapters/ch5/38-bsd-fs.md)

WAV (Waveform Audio File Format)
:   Формат несжатого аудио (PCM) в контейнере RIFF. Настраиваемые параметры: частота дискретизации (44.1–48 кГц), разрядность (16–24 бит), каналы. → [Глава 25](chapters/ch3/25-media.md)

WebDAV (Web Distributed Authoring and Versioning)
:   Расширение HTTP (RFC 4918) для управления файлами: `PROPFIND`, `MKCOL`, `LOCK`. Работает через стандартные порты 80/443. → [Глава 46](chapters/ch5/46-http.md)

WebP
:   Формат изображений Google (2010). Поддерживает lossy, lossless, анимацию, прозрачность. На ~30% компактнее JPEG при сопоставимом качестве. → [Глава 25](chapters/ch3/25-media.md)

Windows-1251
:   8-битная кодировка кириллицы для Windows. Буквы А–Я расположены последовательно. Несовместима с KOI8-R и ISO-8859-5. → [Глава 13](chapters/ch2/13-encodings-babel.md)

Write barrier (барьер записи)
:   Команда диску: «запиши всё предыдущее, прежде чем записывать это». Предотвращает переупорядочивание записей дисковым кешем. Критично для корректности журналирования (ext3/ext4). → [Глава 36](chapters/ch5/36-unix-fs.md)

WTF-8 (Wobbly Transformation Format — 8-bit)
:   Расширение UTF-8, допускающее непарные суррогаты. Нужен для представления «грязных» UTF-16 данных (например, имён файлов Windows с невалидными суррогатами). Используется в Rust (`OsString`) и Firefox. → [Глава 14](chapters/ch2/14-unicode-utf8.md)

## X

xattr (extended attributes, расширенные атрибуты)
:   Пары ключ-значение, хранимые в inode. Используются для SELinux-меток, capabilities, пользовательских данных (`user.*`). → [Глава 9](chapters/ch1/09-extended-attrs.md)

XFS
:   64-битная журналируемая ФС от SGI (IRIX, 1993, портирована в Linux). Allocation groups для параллельного I/O, B+ trees для метаданных, delayed allocation. Оптимальна для больших файлов. По умолчанию в RHEL/CentOS. → [Глава 36](chapters/ch5/36-unix-fs.md), [Глава 39](chapters/ch5/39-linux-fs.md)

xfs_healer
:   Утилита автоматического обнаружения и восстановления повреждений XFS (Linux 7.0+). Работает в online-режиме без размонтирования ФС. User-space демон получает события через `XFS_IOC_HEALTH_MONITOR` ioctl и принимает решения о восстановлении. Требует форматирования с `rmapbt=1`, `parent=1` и kernel 6.12+. Экспериментальная функция. → [Глава 36](chapters/ch5/36-unix-fs.md)

XML (Extensible Markup Language, расширяемый язык разметки)
:   Текстовый формат для структурированных данных с тегами. Поддерживает пространства имён, схемы (DTD, XSD), запросы (XPath). → [Глава 20](chapters/ch3/20-xml.md)

## Y

YAML (YAML Ain't Markup Language)
:   Текстовый формат конфигураций, использующий отступы для вложенности. Надмножество JSON. Широко используется в Kubernetes, Ansible, CI/CD. → [Глава 17](chapters/ch3/17-yaml.md)

## Z

ZFS (Zettabyte File System)
:   Файловая система и менеджер томов. Объединяет ФС, RAID (RAID-Z), LVM в единую архитектуру. Поддерживает CoW, снапшоты, дедупликацию, сжатие, self-healing. → [Глава 40](chapters/ch5/40-zfs.md)

zpool
:   Пул хранения ZFS. Объединяет vdev'ы (диски, зеркала, raidz) в единое пространство. На пуле создаются datasets (файловые системы) и zvols (блочные устройства). → [Глава 40](chapters/ch5/40-zfs.md)

zstd (Zstandard)
:   Алгоритм сжатия от Facebook. Компромисс между скоростью (как LZ4) и степенью сжатия (как zlib). Настраиваемый уровень 1–22. → [Глава 24](chapters/ch3/24-archives.md)
