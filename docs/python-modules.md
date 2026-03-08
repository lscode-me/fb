# Индекс модулей Python

Алфавитный справочник модулей стандартной библиотеки и сторонних пакетов Python, упомянутых в книге.

---

## Стандартная библиотека

### A

ast
:   Разбор и анализ абстрактного синтаксического дерева (AST) Python-кода. Инспекция структуры кода без выполнения. → [Глава 31](chapters/ch4/31-python-deep.md)

asyncio
:   Фреймворк асинхронного ввода-вывода. Event loop, корутины, асинхронные потоки. → [Глава 46](chapters/ch5/46-http.md)

### C

codecs
:   Реестр кодеков: кодирование и декодирование текста, работа с потоками в нужной кодировке. → [Глава 15](chapters/ch2/15-python-encodings.md), [Глава 20](chapters/ch3/20-xml.md)

collections
:   Специализированные контейнеры: `namedtuple`, `defaultdict`, `deque`, `Counter`, `OrderedDict`. → [Глава 22](chapters/ch3/22-binary-structure.md), [Глава 50](chapters/ch5/50-tokenization.md)

configparser
:   Парсер конфигурационных файлов формата INI (секции, ключи, значения). → [Глава 18](chapters/ch3/18-toml-ini.md)

csv
:   Чтение и запись CSV-файлов. `csv.reader`, `csv.writer`, `csv.DictReader`, `csv.DictWriter`. Поддержка RFC 4180. → [Глава 19](chapters/ch3/19-csv-tsv.md), [Глава 25](chapters/ch3/25-media.md), [Глава 50](chapters/ch5/50-tokenization.md)

### D

datetime
:   Работа с датами, временем и временными промежутками. Форматирование через `strftime`/`strptime`. → [Глава 3](chapters/ch1/03-metadata-inode.md), [Глава 16](chapters/ch3/16-json.md), [Глава 21](chapters/ch3/21-binary-serialization.md)

decimal
:   Десятичная арифметика с фиксированной и плавающей точкой. Точные финансовые вычисления без ошибок float. → [Глава 16](chapters/ch3/16-json.md)

### E

encodings
:   Пакет встроенных текстовых кодеков Python: UTF-8, Latin-1, KOI8-R и др. → [Глава 15](chapters/ch2/15-python-encodings.md)

errno
:   Стандартные коды ошибок ОС: `ENOENT`, `EACCES`, `ENOSPC` и др. → [Глава 36](chapters/ch5/36-unix-fs.md)

### F

fcntl
:   Управление файловыми дескрипторами POSIX: блокировка файлов (`flock`, `lockf`), настройка размера pipe. → [Глава 5](chapters/ch1/05-file-operations.md), [Глава 7](chapters/ch1/07-descriptors.md)

### G

glob
:   Поиск файлов по Unix-шаблонам: `*`, `?`, `[abc]`, `**` (рекурсивно). → [Глава 23](chapters/ch3/23-bigdata-formats.md)

gzip
:   Сжатие и распаковка данных в формате GZIP. Работа с `.gz` файлами. → [Глава 24](chapters/ch3/24-archives.md)

### H

hashlib
:   Криптографические хеш-функции: SHA-256, SHA-1, MD5, BLAKE2. → [Глава 4](chapters/ch1/04-links.md), [Глава 22](chapters/ch3/22-binary-structure.md), [Глава 47](chapters/ch5/47-git-fs.md)

hmac
:   Аутентификация сообщений на основе хеш-кодов (HMAC). → [Глава 22](chapters/ch3/22-binary-structure.md)

### I

inspect
:   Интроспекция «живых» Python-объектов: исходный код, сигнатуры функций, стек вызовов. → [Глава 31](chapters/ch4/31-python-deep.md)

io
:   Базовые инструменты для потоков ввода-вывода: `TextIOWrapper`, `BytesIO`, `StringIO`, `BufferedReader`. → [Глава 22](chapters/ch3/22-binary-structure.md), [Глава 26](chapters/ch4/26-streams.md)

### J

json
:   Кодирование и декодирование JSON. `json.dumps`, `json.loads`, `json.load`, кастомные `JSONEncoder`/`JSONDecoder`. → [Глава 5](chapters/ch1/05-file-operations.md), [Глава 12](chapters/ch2/12-ascii.md), [Глава 16](chapters/ch3/16-json.md), [Глава 19](chapters/ch3/19-csv-tsv.md)

### L

locale
:   Поддержка интернационализации: форматирование чисел, дат; сортировка строк по правилам языка. → [Глава 15](chapters/ch2/15-python-encodings.md)

### M

mmap
:   Отображение файлов в память (memory-mapped files). Работа с файлом как с массивом байтов без явного чтения/записи. → [Глава 7](chapters/ch1/07-descriptors.md), [Глава 22](chapters/ch3/22-binary-structure.md), [Глава 31](chapters/ch4/31-python-deep.md)

msvcrt
:   Операции ввода-вывода консоли Windows. Нетранзитивное чтение символов, блокировка файлов на Windows. → [Глава 7](chapters/ch1/07-descriptors.md)

### O

os
:   Интерфейс к функциям ОС: файловые операции (`open`, `read`, `write`, `stat`, `chmod`, `link`), переменные окружения, процессы. → [Глава 2](chapters/ch1/02-file-types-content.md), [Глава 3](chapters/ch1/03-metadata-inode.md), [Глава 5](chapters/ch1/05-file-operations.md), [Глава 6](chapters/ch1/06-permissions.md), [Глава 7](chapters/ch1/07-descriptors.md), [Глава 9](chapters/ch1/09-extended-attrs.md), [Глава 14](chapters/ch2/14-unicode-utf8.md), [Глава 15](chapters/ch2/15-python-encodings.md), [Глава 24](chapters/ch3/24-archives.md), [Глава 33](chapters/ch4/33-duckdb.md)

### P

pathlib
:   Объектно-ориентированная работа с путями файловой системы. `Path`, `PurePath`, методы `exists()`, `read_text()`, `iterdir()`. → [Глава 14](chapters/ch2/14-unicode-utf8.md), [Глава 26](chapters/ch4/26-streams.md)

pickle
:   Сериализация Python-объектов в бинарный формат и обратно. Протоколы 0–5. **Внимание**: не использовать для недоверенных данных. → [Глава 21](chapters/ch3/21-binary-serialization.md)

pkgutil
:   Утилиты для пакетов Python: обнаружение ресурсов, обход пространств имён. → [Глава 15](chapters/ch2/15-python-encodings.md)

### R

re
:   Регулярные выражения. `re.search`, `re.findall`, `re.sub`, группы, lookahead. → [Глава 12](chapters/ch2/12-ascii.md), [Глава 15](chapters/ch2/15-python-encodings.md)

### S

select
:   Мультиплексирование ввода-вывода: `select`, `poll`, `epoll`, `kqueue`. Ожидание готовности файловых дескрипторов. → [Глава 7](chapters/ch1/07-descriptors.md)

signal
:   Обработка асинхронных сигналов ОС: `SIGPIPE`, `SIGINT`, `SIGTERM`. → [Глава 26](chapters/ch4/26-streams.md)

socket
:   Низкоуровневый сетевой интерфейс: создание сокетов TCP/UDP, подключение, передача данных. → [Глава 7](chapters/ch1/07-descriptors.md), [Глава 15](chapters/ch2/15-python-encodings.md)

sqlite3
:   Интерфейс к встроенной базе данных SQLite. SQL-запросы, транзакции. → [Глава 21](chapters/ch3/21-binary-serialization.md)

stat
:   Интерпретация результатов `os.stat()`: константы типов файлов (`S_ISREG`, `S_ISDIR`), маски прав (`S_IRUSR`). → [Глава 2](chapters/ch1/02-file-types-content.md)

struct
:   Упаковка и распаковка бинарных данных. Форматные строки: `>I` (big-endian uint32), `<H` (little-endian uint16) и др. → [Глава 5](chapters/ch1/05-file-operations.md), [Глава 7](chapters/ch1/07-descriptors.md), [Глава 22](chapters/ch3/22-binary-structure.md)

subprocess
:   Запуск внешних процессов: `subprocess.run`, пайплайны, перенаправление stdin/stdout/stderr. → [Глава 26](chapters/ch4/26-streams.md)

sys
:   Системные параметры Python: `sys.stdout`, `sys.stdin`, `sys.getdefaultencoding()`, `sys.maxunicode`. → [Глава 12](chapters/ch2/12-ascii.md), [Глава 15](chapters/ch2/15-python-encodings.md)

### T

tempfile
:   Создание временных файлов и директорий: `NamedTemporaryFile`, `TemporaryDirectory`, `mkstemp`. Автоудаление. → [Глава 5](chapters/ch1/05-file-operations.md), [Глава 7](chapters/ch1/07-descriptors.md)

time
:   Работа со временем: `time.time()`, `time.sleep()`, Unix timestamp. → [Глава 12](chapters/ch2/12-ascii.md)

tomllib
:   Чтение TOML-файлов (Python 3.11+). Только парсинг, без записи. → [Глава 18](chapters/ch3/18-toml-ini.md)

### U

unicodedata
:   База данных Unicode: имена символов, категории (`Lu`, `Nd`), нормализация (NFC/NFD). → [Глава 14](chapters/ch2/14-unicode-utf8.md)

urllib.parse
:   Разбор и конструирование URL. Percent-encoding/decoding (`%20`). → [Глава 12](chapters/ch2/12-ascii.md)

### Z

zipfile
:   Чтение и запись ZIP-архивов. Работа с отдельными элементами, сжатие, пароли. → [Глава 24](chapters/ch3/24-archives.md)

zlib
:   Сжатие данных (DEFLATE), совместимое с gzip. `compress`, `decompress`, `crc32`. → [Глава 22](chapters/ch3/22-binary-structure.md)

---

## Сторонние пакеты

### B

babel
:   Утилиты интернационализации: форматирование чисел и дат по локалям, клонирование CLDR-данных. → [Глава 15](chapters/ch2/15-python-encodings.md)

boto3
:   AWS SDK для Python. Работа с S3: загрузка, скачивание, presigned URL, multipart upload. → [Глава 45](chapters/ch5/45-s3.md)

bson
:   Сериализация в формат BSON (Binary JSON). Используется MongoDB (из пакета PyMongo). → [Глава 21](chapters/ch3/21-binary-serialization.md)

### C

chardet
:   Автоматическое определение кодировки текстовых файлов на основе статистического анализа. → [Глава 13](chapters/ch2/13-encodings-babel.md), [Глава 15](chapters/ch2/15-python-encodings.md)

### D

defusedxml
:   Безопасный парсинг XML: защита от XXE, billion laughs, external entities. Замена стандартных xml-парсеров. → [Глава 20](chapters/ch3/20-xml.md)

duckdb (Python)
:   Python-клиент DuckDB. SQL-запросы к CSV/Parquet/JSON, интеграция с pandas и PyArrow. → [Глава 32](chapters/ch4/32-modern-tools.md), [Глава 33](chapters/ch4/33-duckdb.md)

### G

grpc
:   Реализация протокола gRPC. Сервисы, сериализация через Protobuf, streaming. → [Глава 46](chapters/ch5/46-http.md)

### H

httpx
:   Асинхронный HTTP-клиент. Альтернатива `requests` с поддержкой HTTP/2, async/await. → [Глава 46](chapters/ch5/46-http.md)

### J

jsonschema
:   Валидация JSON-документов по JSON Schema. → [Глава 16](chapters/ch3/16-json.md)

### L

lxml
:   Быстрый парсинг XML и HTML. Поддержка XPath, XSLT, валидации. Обёртка над libxml2. → [Глава 20](chapters/ch3/20-xml.md)

### M

msgpack
:   Бинарная сериализация MessagePack: компактнее JSON, сохраняет ту же модель данных. → [Глава 16](chapters/ch3/16-json.md), [Глава 21](chapters/ch3/21-binary-serialization.md)

mutagen
:   Чтение и редактирование аудиометаданных: ID3-теги (MP3), Vorbis-комментарии (FLAC/OGG), MP4 atoms. → [Глава 25](chapters/ch3/25-media.md)

### P

pandas
:   Библиотека анализа и обработки данных. `DataFrame`, чтение CSV/JSON/Parquet, агрегации. → [Глава 19](chapters/ch3/19-csv-tsv.md), [Глава 32](chapters/ch4/32-modern-tools.md), [Глава 33](chapters/ch4/33-duckdb.md)

protobuf
:   Бинарная сериализация Protocol Buffers (Google). Схема в `.proto` файлах, компиляция в код. → [Глава 21](chapters/ch3/21-binary-serialization.md)

pyarrow
:   Python-обёртка Apache Arrow. Колоночные данные в памяти, чтение/запись Parquet, zero-copy. → [Глава 23](chapters/ch3/23-bigdata-formats.md), [Глава 33](chapters/ch4/33-duckdb.md)

pyuca
:   Реализация Unicode Collation Algorithm. Правильная сортировка строк по правилам Unicode. → [Глава 15](chapters/ch2/15-python-encodings.md)

pyyaml
:   Парсинг и генерация YAML. `yaml.safe_load` (безопасная загрузка), `yaml.dump`. → [Глава 17](chapters/ch3/17-yaml.md)

### R

regex
:   Расширенная библиотека регулярных выражений. Поддержка Unicode properties (`\p{Han}`), атомарных групп, possessive quantifiers. → [Глава 14](chapters/ch2/14-unicode-utf8.md), [Глава 15](chapters/ch2/15-python-encodings.md)

requests
:   HTTP-библиотека. `requests.get`, `requests.post`, сессии, загрузка файлов. → [Глава 45](chapters/ch5/45-s3.md), [Глава 46](chapters/ch5/46-http.md)

### S

sentencepiece
:   Токенизация текста: BPE, Unigram. Независимый от языка токенизатор для NLP и LLM. → [Глава 50](chapters/ch5/50-tokenization.md)

sseclient
:   Клиент Server-Sent Events (SSE). Чтение серверных событий через HTTP-streaming. → [Глава 46](chapters/ch5/46-http.md)

### T

tiktoken
:   Токенизатор OpenAI для моделей GPT. Кодирование текста в токены и обратно. → [Глава 50](chapters/ch5/50-tokenization.md)

tokenizers
:   Библиотека быстрой токенизации Hugging Face. Обучение BPE, WordPiece, тренировка на корпусе. → [Глава 50](chapters/ch5/50-tokenization.md)

tomli
:   Чтение TOML-файлов (для Python < 3.11). Обратно совместима с `tomllib`. → [Глава 18](chapters/ch3/18-toml-ini.md)

tomli_w
:   Запись TOML-файлов. Дополнение к `tomli`/`tomllib`, которые поддерживают только чтение. → [Глава 18](chapters/ch3/18-toml-ini.md)

tqdm
:   Прогресс-бар для циклов и загрузок. Обёртка над итератором с отображением прогресса. → [Глава 45](chapters/ch5/45-s3.md)

transformers
:   Библиотека Hugging Face для работы с LLM. `AutoTokenizer`, предобученные модели, пайплайны. → [Глава 50](chapters/ch5/50-tokenization.md)

### W

watchdog
:   Мониторинг событий файловой системы: создание, изменение, удаление файлов. Кроссплатформенный. → [Глава 5](chapters/ch1/05-file-operations.md)
