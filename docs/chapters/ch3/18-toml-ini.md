# Глава 18. TOML и INI: конфигурационные форматы

## Введение

**TOML** (Tom's Obvious Minimal Language) и **INI** — форматы, специально разработанные для конфигурационных файлов. Они проще YAML и безопаснее при парсинге.

---

# Часть 1: TOML

## 18.1 Синтаксис TOML

### Базовые типы

```toml
# Комментарий

# Строки
name = "Alice"
path = 'C:\Users\name'           # Литеральная строка (без экранирования)
multiline = """
Первая строка
Вторая строка
"""

# Числа
integer = 42
negative = -17
hex = 0xDEADBEEF
octal = 0o755
binary = 0b11010110
float = 3.14159
scientific = 5.0e+22
infinity = inf
not_a_number = nan

# Булевы
enabled = true
disabled = false

# Дата и время
date = 2024-01-15
time = 14:30:00
datetime = 2024-01-15T14:30:00Z
datetime_local = 2024-01-15T14:30:00
```

### Таблицы (секции)

```toml
# Простая таблица
[server]
host = "localhost"
port = 8080

# Вложенная таблица
[database.primary]
host = "db1.example.com"
port = 5432

[database.replica]
host = "db2.example.com"
port = 5432

# Inline таблица
point = { x = 10, y = 20 }
```

### Массивы

```toml
# Простой массив
ports = [8080, 8081, 8082]

# Массив разных типов (запрещено!)
# mixed = [1, "two", 3]  # ОШИБКА

# Массив таблиц
[[servers]]
name = "alpha"
ip = "10.0.0.1"

[[servers]]
name = "beta"
ip = "10.0.0.2"

# Результат:
# servers = [
#   { name = "alpha", ip = "10.0.0.1" },
#   { name = "beta", ip = "10.0.0.2" }
# ]
```

---

## 18.2 TOML в Python

### Стандартная библиотека (Python 3.11+)

```python
import tomllib  # Только чтение

with open('config.toml', 'rb') as f:
    config = tomllib.load(f)

# Или из строки
toml_string = """
[server]
host = "localhost"
port = 8080
"""
config = tomllib.loads(toml_string)
```

### Библиотека toml/tomli

```python
# tomli (чтение, для Python < 3.11)
import tomli

with open('config.toml', 'rb') as f:
    config = tomli.load(f)

# tomli-w (запись)
import tomli_w

data = {
    'server': {
        'host': 'localhost',
        'port': 8080
    }
}

with open('config.toml', 'wb') as f:
    tomli_w.dump(data, f)
```

---

## 18.3 Применение TOML

TOML используется в:

- **Python**: `pyproject.toml` (PEP 518)
- **Rust**: `Cargo.toml`
- **Hugo**: конфигурация сайта
- **GitHub Actions**: `dependabot.yml` (частично)

### Пример pyproject.toml

```toml
[project]
name = "my-package"
version = "1.0.0"
description = "My awesome package"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.28.0",
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
```

---

# Часть 2: INI

## 18.4 Синтаксис INI

INI — простейший формат конфигурации:

```ini
; Комментарий (точка с запятой)
# Комментарий (решётка)

[section]
key = value
another_key = another value

[database]
host = localhost
port = 5432
name = mydb

[logging]
level = DEBUG
file = /var/log/app.log
```

### Ограничения INI

- Нет стандартной спецификации
- Нет вложенных секций
- Нет типов данных (всё — строки)
- Нет массивов
- Разные реализации по-разному обрабатывают кавычки, пробелы, escape-последовательности

---

## 18.5 INI в Python

### Модуль configparser

```python
import configparser

# Чтение
config = configparser.ConfigParser()
config.read('config.ini')

# Доступ к значениям
host = config['database']['host']          # 'localhost'
port = config.getint('database', 'port')   # 5432
debug = config.getboolean('app', 'debug')  # True/False

# Значение по умолчанию
timeout = config.getint('database', 'timeout', fallback=30)

# Проверка существования
if 'logging' in config:
    log_level = config['logging']['level']

# Запись
config['new_section'] = {
    'key1': 'value1',
    'key2': 'value2'
}

with open('config.ini', 'w') as f:
    config.write(f)
```

### Интерполяция

```ini
[paths]
base = /opt/app
logs = %(base)s/logs
data = %(base)s/data
```

```python
config = configparser.ConfigParser()
config.read('config.ini')

print(config['paths']['logs'])  # /opt/app/logs
```

---

## 18.6 TOML vs INI vs YAML vs JSON

| Характеристика | TOML | INI | YAML | JSON |
|----------------|------|-----|------|------|
| Типы данных | Да | Нет (строки) | Да | Да |
| Вложенность | Да | Нет | Да | Да |
| Массивы | Да | Нет | Да | Да |
| Комментарии | Да | Да | Да | Нет |
| Спецификация | Строгая | Нет | Строгая | Строгая |
| Безопасность | Высокая | Высокая | Средняя | Высокая |
| Читаемость | Высокая | Высокая | Высокая | Средняя |

---

## 18.7 Подводные камни и edge cases

### TOML: вложенные таблицы

```toml
# ❗ Порядок секций важен!
[servers]
[servers.alpha]
ip = "10.0.0.1"

[servers.beta]
ip = "10.0.0.2"

# ❗ Нельзя вернуться к [servers] после подсекций!
```

### INI: отсутствие типизации

```python
import configparser

config = configparser.ConfigParser()
config.read('app.ini')

# ❗ Все значения — строки!
port = config['server']['port']  # "8080" (str, не int!)
port = config.getint('server', 'port')  # 8080 (✅)

# ❗ Boolean тоже нужно конвертировать
debug = config.getboolean('server', 'debug')  # True/False
```

### Миграция INI → TOML

!!! tip "Когда мигрировать"
    Если вам нужны: вложенность > 1, типизация, списки — переходите на TOML. INI подходит только для плоских key-value конфигураций.

---

## Резюме

### TOML

| Характеристика | Значение |
|----------------|----------|
| Расширение | `.toml` |
| MIME-тип | `application/toml` |
| Комментарии | Да (`#`) |
| Типизация | Строгая |
| Применение | Конфигурации проектов (Python, Rust) |

### INI

| Характеристика | Значение |
|----------------|----------|
| Расширение | `.ini`, `.cfg`, `.conf` |
| Комментарии | Да (`;`, `#`) |
| Типизация | Нет (только строки) |
| Применение | Простые конфигурации, Windows |


??? question "Упражнения"
    **Задание 1.** Создайте `pyproject.toml` для Python-проекта с зависимостями, метаданными автора и настройками pytest. Прочитайте его через `tomllib` (Python 3.11+).
    
    **Задание 2.** Напишите конфигурацию в INI-формате и прочитайте через `configparser`. Какие типы данных поддерживает INI? Что происходит с числами и boolean?
    
    **Задание 3.** Сравните один и тот же набор данных в TOML, YAML и JSON: размер файла, читаемость, возможность комментариев.

!!! tip "Следующая глава"
    Познакомились с конфигурационными форматами. Перейдём к **табличным данным** — CSV и TSV → [CSV и TSV](19-csv-tsv.md)
