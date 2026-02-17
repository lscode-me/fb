# Глава 33. DuckDB: SQL для локальных файлов

## Введение

**DuckDB** — аналитическая база данных, работающая локально и позволяющая выполнять SQL-запросы напрямую к CSV, Parquet, JSON и другим файлам без предварительной загрузки. Идеальный инструмент для data engineering и ad-hoc анализа.

---

## 33.1 Установка и запуск

### Установка

```bash
# Python
pip install duckdb

# CLI
brew install duckdb      # macOS
# или скачать с https://duckdb.org
```

### Интерактивный режим

```bash
$ duckdb
D SELECT 'Hello, DuckDB!' as greeting;
┌─────────────────┐
│    greeting     │
│     varchar     │
├─────────────────┤
│ Hello, DuckDB!  │
└─────────────────┘
```

---

## 33.2 Запросы к файлам

### CSV

```sql
-- Чтение CSV
SELECT * FROM 'data.csv';

-- С явными параметрами
SELECT * FROM read_csv('data.csv',
    header = true,
    delim = ',',
    quote = '"',
    columns = {'name': 'VARCHAR', 'age': 'INTEGER'}
);

-- Чтение нескольких файлов
SELECT * FROM 'data/*.csv';
SELECT * FROM read_csv(['file1.csv', 'file2.csv']);

-- Запись в CSV
COPY (SELECT * FROM my_table) TO 'output.csv' (HEADER, DELIMITER ',');
```

### Parquet

```sql
-- Чтение Parquet
SELECT * FROM 'data.parquet';

-- Чтение папки с partition
SELECT * FROM 'data/year=*/month=*/*.parquet';

-- Метаданные
SELECT * FROM parquet_metadata('data.parquet');
SELECT * FROM parquet_schema('data.parquet');

-- Запись в Parquet
COPY (SELECT * FROM my_table) TO 'output.parquet' (FORMAT PARQUET);
```

### JSON

```sql
-- JSON Lines (каждая строка — объект)
SELECT * FROM 'data.jsonl';

-- JSON массив
SELECT * FROM read_json('data.json', format = 'array');

-- Извлечение вложенных полей
SELECT 
    json->>'name' as name,
    json->'address'->>'city' as city
FROM read_json('data.json');
```

---

## 33.3 Python интеграция

### Базовое использование

```python
import duckdb

# Создание соединения (in-memory)
con = duckdb.connect()

# Выполнение запроса
result = con.execute("SELECT 42 as answer").fetchall()
# [(42,)]

# Получение DataFrame
df = con.execute("SELECT * FROM 'data.csv'").df()

# Запрос к DataFrame
import pandas as pd
my_df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
result = con.execute("SELECT * FROM my_df WHERE a > 1").df()
```

### Без явного соединения

```python
import duckdb

# Прямой запрос
df = duckdb.query("SELECT * FROM 'data.parquet' LIMIT 10").df()

# SQL к pandas DataFrame
import pandas as pd
df = pd.read_csv('data.csv')
result = duckdb.query("SELECT name, AVG(age) FROM df GROUP BY name").df()
```

### Контекстный менеджер

```python
import duckdb

with duckdb.connect('my_database.db') as con:
    con.execute("CREATE TABLE users AS SELECT * FROM 'users.csv'")
    con.execute("INSERT INTO users VALUES ('Alice', 30)")
    result = con.execute("SELECT * FROM users").df()
```

---

## 33.4 Аналитические функции

### Оконные функции

```sql
SELECT 
    name,
    department,
    salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as rank
FROM 'employees.csv';
```

### Агрегация

```sql
-- Группировка
SELECT 
    category,
    COUNT(*) as count,
    SUM(amount) as total,
    AVG(amount) as average,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) as median
FROM 'sales.csv'
GROUP BY category;

-- ROLLUP
SELECT 
    COALESCE(region, 'Total') as region,
    COALESCE(category, 'All') as category,
    SUM(sales) as total_sales
FROM 'sales.csv'
GROUP BY ROLLUP(region, category);
```

### Pivot / Unpivot

```sql
-- Pivot
PIVOT 'sales.csv' 
ON category 
USING SUM(amount) 
GROUP BY region;

-- Unpivot
UNPIVOT 'wide_data.csv' 
ON col1, col2, col3 
INTO NAME variable VALUE value;
```

---

## 33.5 Работа с большими данными

### Ленивая загрузка

```python
# DuckDB читает только нужные столбцы и строки
result = duckdb.query("""
    SELECT name, age 
    FROM 'huge_file.parquet' 
    WHERE age > 30 
    LIMIT 100
""").df()
# Не загружает весь файл в память!
```

### Параллельное выполнение

```sql
-- DuckDB автоматически использует все ядра
SELECT COUNT(*) FROM 'big_data/*.parquet';
```

### Streaming результатов

```python
# Итерация по результатам без загрузки в память
con = duckdb.connect()
result = con.execute("SELECT * FROM 'huge.csv'")

while batch := result.fetchmany(10000):
    process_batch(batch)
```

---

## 33.6 Экспорт данных

```sql
-- В CSV
COPY (SELECT * FROM my_query) TO 'output.csv' (HEADER);

-- В Parquet
COPY (SELECT * FROM my_query) TO 'output.parquet' (FORMAT PARQUET);

-- В JSON
COPY (SELECT * FROM my_query) TO 'output.json' (FORMAT JSON);

-- Partitioned вывод
COPY (SELECT * FROM sales) 
TO 'output' 
(FORMAT PARQUET, PARTITION_BY (year, month));
```

---

## 33.7 Практические примеры

### Анализ логов

```sql
-- Парсинг Apache логов
SELECT 
    regexp_extract(line, '^(\S+)', 1) as ip,
    regexp_extract(line, '"(\w+) ', 1) as method,
    regexp_extract(line, '" (\d+) ', 1)::int as status,
    COUNT(*) as requests
FROM read_csv('access.log', columns = {'line': 'VARCHAR'}, header = false)
GROUP BY ip, method, status
ORDER BY requests DESC
LIMIT 20;
```

### ETL пайплайн

```python
import duckdb

# Читаем из разных источников
con = duckdb.connect()

con.execute("""
    CREATE TABLE merged AS
    SELECT a.*, b.category 
    FROM 'transactions/*.csv' a
    JOIN 'categories.parquet' b ON a.category_id = b.id
    WHERE a.date >= '2024-01-01'
""")

# Агрегируем и сохраняем
con.execute("""
    COPY (
        SELECT 
            category,
            DATE_TRUNC('month', date) as month,
            SUM(amount) as total
        FROM merged
        GROUP BY category, month
    ) TO 'monthly_summary.parquet' (FORMAT PARQUET)
""")
```

### Сравнение файлов

```sql
-- Найти различия между двумя CSV
SELECT * FROM 'old.csv'
EXCEPT
SELECT * FROM 'new.csv';

-- Новые записи
SELECT * FROM 'new.csv'
EXCEPT  
SELECT * FROM 'old.csv';
```

---

## 33.8 DuckDB vs другие инструменты

| Задача | DuckDB | pandas | SQLite | Spark |
|--------|--------|--------|--------|-------|
| Читать Parquet | ✅ Native | ✅ pyarrow | ❌ | ✅ |
| Читать огромный CSV | ✅ Streaming | ⚠️ Память | ❌ Import | ✅ |
| SQL | ✅ Полный | ⚠️ pandasql | ✅ | ✅ |
| Скорость | 🚀 Быстро | 🐢 Медленно | 🐢 Медленно | 🚀 Распределённо |
| Зависимости | Минимум | Много | Минимум | Много |
| Развёртывание | Локально | Локально | Локально | Кластер |

---

## Резюме

| Характеристика | Значение |
|----------------|----------|
| Тип | Встраиваемая OLAP база |
| Расширение БД | `.duckdb`, `.db` |
| Поддержка форматов | CSV, Parquet, JSON, Excel |
| Python API | `pip install duckdb` |
| CLI | `duckdb` |
| Лицензия | MIT |

**Когда использовать DuckDB:**

- Анализ локальных файлов (CSV, Parquet)
- ETL на одной машине
- Замена pandas для SQL-запросов
- Прототипирование перед переходом на Spark


??? question "Упражнения"
    **Задание 1.** Загрузите CSV-файл в DuckDB и выполните GROUP BY с агрегацией. Сравните скорость с `pandas.groupby()`.
    
    **Задание 2.** Выполните запрос к нескольким Parquet-файлам через glob: `SELECT * FROM 'data/2024/*/*.parquet'`. Работает ли predicate pushdown?
    
    **Задание 3.** Конвертируйте CSV в Parquet одной SQL-командой DuckDB: `COPY (SELECT * FROM 'input.csv') TO 'output.parquet' (FORMAT PARQUET)`. Сравните размер.

---

## Troubleshooting: типичные проблемы Части IV

!!! bug "Pipeline зависает (deadlock)"
    ```bash
    # Зависает, если fifo никто не читает:
    echo "data" > my_fifo &
    # ( и наоборот — cat my_fifo зависнет, если никто не пишет )
    ```
    Пайпы имеют ограниченный буфер (~64 KB в Linux). Если читатель не потребляет данные, писатель блокируется. Решение: проверяйте обе стороны пайплайна, используйте `timeout`.

!!! bug "Out of Memory при обработке большого файла"
    ```python
    # Неправильно — весь файл в памяти:
    data = open('10gb.csv').read()
    
    # Правильно — построчная обработка:
    with open('10gb.csv') as f:
        for line in f:  # итератор, не загружает всё сразу
            process(line)
    
    # Ещё лучше — DuckDB / Polars (ленивые вычисления):
    import duckdb
    duckdb.sql("SELECT count(*) FROM '10gb.csv'")
    ```

!!! bug "grep/sed ведут себя странно с бинарными файлами"
    ```bash
    # grep может сказать "Binary file matches":
    grep -a "pattern" binary_file  # -a = treat as text
    
    # Или работайте с hex:
    xxd binary_file | grep "pattern"
    ```
    Coreutils инструменты рассчитаны на текстовые потоки. Для бинарных данных используйте `hexdump`, `xxd`, `binwalk`.

!!! bug "Кодировка в pipe отличается от интерактивного режима"
    ```bash
    # В терминале работает, а в pipe — кракозябры:
    python script.py | less  # PYTHONIOENCODING может быть ASCII в pipe!
    
    # Решение:
    export PYTHONIOENCODING=utf-8
    # или:
    python -u script.py | less  # -u = unbuffered
    ```
    В pipe Python может выбрать ASCII вместо UTF-8. Задайте `PYTHONIOENCODING=utf-8`.

!!! tip "Следующая глава"
    Завершили практическую часть. Теперь перейдём к **инфраструктуре хранения** — от физических дисков до файловых систем → [Архитектура накопителей](../ch5/34-architecture.md)
