# Глава 23. Форматы для больших данных

## Введение

При обработке больших объёмов данных (десятки/сотни гигабайт) важны:
- **Эффективность сжатия**
- **Скорость чтения** (особенно выборочного)
- **Schema evolution** (изменение структуры данных)

**Ключевое различие:** строковые vs колоночные форматы.

---

## 23.1 Строковые vs Колоночные форматы

### Строковый формат (Row-based)

```
Row 1: {id: 1, name: "Иван", age: 30, salary: 50000}
Row 2: {id: 2, name: "Мария", age: 25, salary: 45000}
Row 3: {id: 3, name: "Пётр", age: 35, salary: 60000}

На диске:
[1, "Иван", 30, 50000] [2, "Мария", 25, 45000] [3, "Пётр", 35, 60000]
```

**Преимущества:**
- Быстрая вставка строки
- Быстрое чтение всей строки

**Недостатки:**
- Медленная аналитика (нужны только отдельные колонки)

### Колоночный формат (Column-based)

```
На диске:
id:     [1, 2, 3]
name:   ["Иван", "Мария", "Пётр"]
age:    [30, 25, 35]
salary: [50000, 45000, 60000]
```

**Преимущества:**
- Быстрая аналитика (читаем только нужные колонки)
- Лучшее сжатие (однотипные данные в колонке)

**Недостатки:**
- Медленная вставка/обновление отдельных строк

---

## 23.2 Parquet: колоночный стандарт

**Apache Parquet** (2013) — колоночный формат для Hadoop экосистемы.

### Структура

```
Parquet файл
├── Magic Number: PAR1
├── Row Group 1 (chunk данных)
│   ├── Column Chunk: id
│   │   └── [1, 2, 3, ..., 1000]
│   ├── Column Chunk: name
│   │   └── ["Иван", "Мария", ..., "Пётр"]
│   └── Column Chunk: salary
│       └── [50000, 45000, ..., 60000]
├── Row Group 2
│   └── ...
└── Footer (метаданные, схема, статистика)
```

### Python: чтение и запись

```python
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Создание DataFrame
df = pd.DataFrame({
    'id': range(1, 1000001),
    'name': ['User' + str(i) for i in range(1, 1000001)],
    'age': [20 + i % 50 for i in range(1000000)],
    'salary': [30000 + i * 10 for i in range(1000000)]
})

# Запись в Parquet
df.to_parquet('data.parquet', compression='snappy', index=False)

# Чтение всего файла
df_loaded = pd.read_parquet('data.parquet')

# Чтение только отдельных колонок (эффективно!)
df_subset = pd.read_parquet('data.parquet', columns=['name', 'salary'])

# Фильтрация на уровне Parquet
df_filtered = pd.read_parquet(
    'data.parquet',
    filters=[('age', '>', 30), ('salary', '<', 60000)]
)
```

### Сравнение с CSV

```bash
$ ls -lh
-rw-r--r-- 1 user user  45M Feb  4 10:00 data.csv
-rw-r--r-- 1 user user  12M Feb  4 10:00 data.parquet (snappy)
-rw-r--r-- 1 user user 8.5M Feb  4 10:00 data.parquet (gzip)

# Чтение времени
$ time python -c "import pandas as pd; pd.read_csv('data.csv')"
real    0m8.234s

$ time python -c "import pandas as pd; pd.read_parquet('data.parquet')"
real    0m1.456s    # ~5.6x быстрее
```

### Сжатие

```python
# Разные алгоритмы сжатия
df.to_parquet('data_snappy.parquet', compression='snappy')  # Быстро
df.to_parquet('data_gzip.parquet', compression='gzip')      # Лучше сжимает
df.to_parquet('data_zstd.parquet', compression='zstd')      # Баланс
df.to_parquet('data_none.parquet', compression='none')      # Без сжатия
```

| Сжатие | Размер | Скорость записи | Скорость чтения |
|--------|--------|----------------|-----------------|
| **none** | 38 МБ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **snappy** | 12 МБ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **gzip** | 8.5 МБ | ⭐⭐ | ⭐⭐⭐ |
| **zstd** | 9 МБ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

### Parquet Internals: почему чтение 1 колонки из 100 — мгновенное

**Row Group** — это горизонтальный «срез» данных (обычно 128 МБ). Каждый Row Group содержит **Column Chunk** для каждой колонки. Footer файла хранит **метаданные**: где начинается каждый chunk, его размер, и **статистику** (min/max значений).

```text
Запрос: SELECT salary FROM employees WHERE age > 30

Шаг 1: Прочитать Footer (последние байты файла)
        → Узнать позиции Column Chunks

Шаг 2: Predicate Pushdown — проверить статистику
        Row Group 1: age min=20, max=25 → ПРОПУСТИТЬ (все < 30)
        Row Group 2: age min=22, max=45 → ЧИТАТЬ
        Row Group 3: age min=31, max=60 → ЧИТАТЬ

Шаг 3: Прочитать только Column Chunk "salary" из Row Groups 2, 3
        → Остальные 99 колонок НЕ читаются!
```

**Predicate Pushdown** — фильтрация «опускается» на уровень формата. Движок **не загружает** Row Groups, чья статистика (min/max) гарантирует отсутствие подходящих строк.

**Column Pruning** — если нужны 2 колонки из 100, читаются только 2 Column Chunk'а. При строковом хранении (CSV) пришлось бы прочитать все 100.

```python
# Исследование метаданных Parquet
import pyarrow.parquet as pq

meta = pq.read_metadata("data.parquet")
print(f"Row Groups: {meta.num_row_groups}")
print(f"Колонок: {meta.num_columns}")
print(f"Строк: {meta.num_rows}")

# Статистика Row Group 0
rg = meta.row_group(0)
for i in range(rg.num_columns):
    col = rg.column(i)
    print(f"  {col.path_in_schema}: min={col.statistics.min}, max={col.statistics.max}")
```

---

## 23.3 ORC: Optimized Row Columnar

**Apache ORC** (2013) — альтернатива Parquet для Hive.

### Особенности

- **Stripe-based:** данные разбиты на stripes (по умолчанию 64 МБ)
- **Встроенная статистика:** min/max/sum/count для каждой колонки
- **ACID поддержка:** в Hive с ORC можно делать UPDATE/DELETE

```python
import pandas as pd
import pyarrow as pa
import pyarrow.orc as orc

# Запись
df.to_orc('data.orc')

# Чтение
df_loaded = pd.read_orc('data.orc')

# Чтение с фильтрацией
df_filtered = pd.read_orc('data.orc', columns=['name', 'salary'])
```

### Parquet vs ORC

| Критерий | Parquet | ORC |
|----------|---------|-----|
| **Экосистема** | Spark, широкое применение | Hive, Presto |
| **Сжатие** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (немного лучше) |
| **Скорость чтения** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **ACID** | ❌ | ✅ (в Hive) |
| **Совместимость** | Больше инструментов | Меньше |

!!! tip "Когда использовать"
    - **Parquet:** универсальный выбор, Spark, Python, широкая поддержка
    - **ORC:** если работаете преимущественно в Hive/Presto экосистеме

---

## 23.4 Avro: строковый формат со схемой

**Apache Avro** (2009) — строковый формат с сильной типизацией.

### Схема

```json
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "id", "type": "int"},
    {"name": "name", "type": "string"},
    {"name": "age", "type": "int"},
    {"name": "email", "type": ["null", "string"], "default": null}
  ]
}
```

### Python

```python
from avro.datafile import DataFileWriter, DataFileReader
from avro.io import DatumWriter, DatumReader
import avro.schema

# Схема
schema = avro.schema.parse(open("user.avsc").read())

# Запись
writer = DataFileWriter(open("users.avro", "wb"), DatumWriter(), schema)
writer.append({"id": 1, "name": "Иван", "age": 30, "email": "ivan@example.com"})
writer.append({"id": 2, "name": "Мария", "age": 25, "email": None})
writer.close()

# Чтение
reader = DataFileReader(open("users.avro", "rb"), DatumReader())
for user in reader:
    print(user)
# {'id': 1, 'name': 'Иван', 'age': 30, 'email': 'ivan@example.com'}
# {'id': 2, 'name': 'Мария', 'age': 25, 'email': None}
reader.close()
```

### Schema Evolution

```json
// Версия 1
{"name": "age", "type": "int"}

// Версия 2 (добавили поле с default)
{"name": "age", "type": "int"}
{"name": "city", "type": "string", "default": "Unknown"}

// Старые файлы читаются новой схемой (city = "Unknown")
// Новые файлы читаются старой схемой (city игнорируется)
```

### Применение

- **Kafka:** сериализация сообщений
- **Hadoop:** обмен данными между системами
- **RPC:** схема для удалённых вызовов

!!! warning "Avro и Protobuf требуют схему для чтения"
    В отличие от JSON (self-describing), Avro и Protobuf **не содержат имён полей** в бинарных данных. Для декодирования нужна схема:
    
    ```python
    # JSON — self-describing, можно прочитать без схемы
    {"name": "Иван", "age": 30}
    
    # Avro — бинарные данные, без схемы нельзя понять структуру
    0x08 0xD0 0x98 0xD0 0xB2 0xD0 0xB0 0xD0 0xBD 0x3C
    # Это "Иван" (UTF-8) и 30 (zigzag encoded)
    ```
    
    **Следствия:**
    
    - `.avro` файлы содержат схему внутри (можно прочитать)
    - Kafka + Avro требует **Schema Registry** для хранения схем
    - Protobuf файлы без `.proto` схемы практически нечитаемы
    
    В отличие от них, **Parquet** хранит схему в footer файла — поэтому его можно "просто открыть".

### Schema Registry — управление схемами вне файла

В стриминговых системах (Apache Kafka) сообщения Avro не могут содержать схему в каждом сообщении — это слишком накладно. Решение — **Schema Registry**:

```text
┌──────────┐     ┌──────────────────┐     ┌──────────┐
│ Producer │────→│  Schema Registry │←────│ Consumer │
│          │     │  ┌─────────────┐ │     │          │
│ schema + │     │  │ v1: {name}  │ │     │ Получает │
│ data     │     │  │ v2: +email  │ │     │ schema   │
│          │     │  │ v3: +phone  │ │     │ по ID    │
└──────────┘     │  └─────────────┘ │     └──────────┘
                 └──────────────────┘
```

**Как работает:**

1. Producer регистрирует схему → получает **schema_id**
2. Сообщение в Kafka: `[magic_byte | schema_id (4 bytes) | avro_data]`
3. Consumer извлекает `schema_id` → запрашивает схему из Registry → декодирует

**Правила совместимости:**

| Режим | Правило | Пример |
|-------|---------|--------|
| **BACKWARD** | Новая схема читает старые данные | Добавить поле с default |
| **FORWARD** | Старая схема читает новые данные | Удалить поле с default |
| **FULL** | Оба направления | Только добавление/удаление полей с default |
| **NONE** | Без проверок | Опасно |

!!! info "Confluent Schema Registry"
    Самая популярная реализация — **Confluent Schema Registry** (REST API). Поддерживает Avro, Protobuf и JSON Schema. Альтернативы: AWS Glue Schema Registry, Apicurio Registry.

---

## 23.5 Сравнение форматов

### Таблица

| Формат | Тип | Размер | Сжатие | Schema | Применение |
|--------|-----|--------|--------|--------|------------|
| **CSV** | Строковый | 100% | ❌ | ❌ | Простой обмен |
| **JSON Lines** | Строковый | 110% | ❌ | ⚠️ | Логи, стриминг |
| **Avro** | Строковый | 40% | ✅ | ✅✅ | Kafka, обмен данными |
| **Parquet** | Колоночный | 25% | ✅✅ | ✅ | Аналитика (Spark) |
| **ORC** | Колоночный | 22% | ✅✅ | ✅ | Hive, ACID |

### Benchmark (1M строк, 4 колонки)

```bash
# Размер файлов
-rw-r--r-- 1 user user  45M Feb  4 10:00 data.csv
-rw-r--r-- 1 user user  18M Feb  4 10:00 data.avro
-rw-r--r-- 1 user user  12M Feb  4 10:00 data.parquet
-rw-r--r-- 1 user user  10M Feb  4 10:00 data.orc

# Время чтения всех данных (pandas)
CSV:      8.2s
Avro:     3.1s
Parquet:  1.4s
ORC:      1.6s

# Время чтения 1 колонки
CSV:      8.2s  (читает весь файл!)
Avro:     3.1s  (читает весь файл!)
Parquet:  0.3s  (читает только нужную колонку!)
ORC:      0.4s  (читает только нужную колонку!)
```

---

## 23.6 Практические примеры

### Преобразование CSV → Parquet

```python
import pandas as pd
import glob

# Batch processing больших CSV
for csv_file in glob.glob('data/*.csv'):
    parquet_file = csv_file.replace('.csv', '.parquet')
    
    # Читаем chunks (не загружаем всё в память)
    chunks = pd.read_csv(csv_file, chunksize=100000)
    
    for i, chunk in enumerate(chunks):
        if i == 0:
            # Первый chunk — создаём файл
            chunk.to_parquet(parquet_file, compression='snappy', index=False)
        else:
            # Остальные chunks — добавляем
            chunk.to_parquet(parquet_file, compression='snappy', index=False, append=True)
```

### Партиционирование данных

```python
# Разбивка по году и месяцу
df['date'] = pd.to_datetime(df['timestamp'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

# Сохранение с партиционированием
df.to_parquet(
    'data/',
    partition_cols=['year', 'month'],
    compression='snappy'
)

# Структура директорий:
# data/
#   year=2023/
#     month=1/
#       part-0.parquet
#     month=2/
#       part-0.parquet
#   year=2024/
#     month=1/
#       part-0.parquet

# Чтение только данных за январь 2024
df_jan = pd.read_parquet('data/', filters=[('year', '=', 2024), ('month', '=', 1)])
```

### Использование в Spark

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("ParquetExample").getOrCreate()

# Чтение
df = spark.read.parquet("data.parquet")

# SQL запросы
df.createOrReplaceTempView("users")
result = spark.sql("SELECT name, AVG(salary) FROM users WHERE age > 30 GROUP BY name")

# Запись
result.write.parquet("output.parquet", mode="overwrite", compression="snappy")
```

---

## Резюме

### Выбор формата

| Задача | Формат |
|--------|--------|
| **Аналитика (Spark, Pandas)** | Parquet |
| **Hive/Presto с ACID** | ORC |
| **Kafka, обмен данными** | Avro |
| **Логи, стриминг** | JSON Lines |
| **Простой обмен** | CSV |

### Ключевые преимущества колоночных форматов

1. **Выборочное чтение:** читаем только нужные колонки
2. **Лучшее сжатие:** однотипные данные сжимаются эффективнее
3. **Статистика:** min/max/count в метаданных → пропуск блоков
4. **Скорость:** 5-10x быстрее для аналитических запросов


??? question "Упражнения"
    **Задание 1.** Конвертируйте CSV в Parquet через Python (`pandas` или `pyarrow`). Сравните размер файлов и скорость чтения с фильтрацией.
    
    **Задание 2.** Прочитайте метаданные Parquet-файла (через `pyarrow.parquet.read_metadata`): количество row groups, схему, статистику столбцов.
    
    **Задание 3.** Выполните агрегирующий запрос к Parquet-файлу через DuckDB. Сравните скорость с тем же запросом к CSV-оригиналу.

!!! tip "Следующая глава"
    Разобрались с форматами больших данных. Теперь перейдём к **архивам и контейнерам** → [Архивы и контейнеры](24-archives.md)
