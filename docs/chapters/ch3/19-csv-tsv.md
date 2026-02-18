---
title: CSV и TSV — работа с табличными данными
description: CSV и TSV форматы: синтаксис, подводные камни, обработка в Python (csv, pandas). Кодировки, экранирование, RFC 4180.
---

# Глава 19. CSV и TSV: табличные данные

## Введение

**CSV** (Comma-Separated Values) и **TSV** (Tab-Separated Values) — простейшие текстовые форматы для хранения табличных данных. Несмотря на кажущуюся простоту, работа с CSV полна подводных камней.

---

## 19.1 Структура CSV

### Базовый формат

```csv
name,age,city
Alice,30,Moscow
Bob,25,London
Charlie,35,Paris
```

### Правила RFC 4180

Стандарт RFC 4180 определяет:

1. Каждая запись на отдельной строке
2. Поля разделены запятыми
3. Первая строка может содержать заголовки
4. Поля могут быть в двойных кавычках
5. Двойная кавычка внутри поля экранируется удвоением

```csv
name,description,price
"Widget","A simple widget",9.99
"Gadget","A ""fancy"" gadget",19.99
"Thing","Multi-line
description",29.99
```

---

## 19.2 Экранирование и кавычки

### Когда нужны кавычки

```csv
# Запятая в значении
name,address
Alice,"123 Main St, Apt 4"

# Кавычки в значении
name,quote
Bob,"He said ""Hello"""

# Перенос строки в значении
name,bio
Charlie,"Line 1
Line 2"

# Пробелы в начале/конце
name,value
Dave," padded "
```

### Проблемы без кавычек

```csv
# ПЛОХО: неоднозначно
name,address
Alice,123 Main St, Apt 4

# Парсер может увидеть:
# name: Alice
# address: 123 Main St
# ???: Apt 4
```

---

## 19.3 TSV — Tab-Separated Values

TSV использует табуляцию как разделитель:

```tsv
name	age	city
Alice	30	Moscow
Bob	25	London
```

### Преимущества TSV

- Табуляция реже встречается в данных
- Меньше нужды в кавычках
- Проще визуальное выравнивание

### Недостатки TSV

- Табуляция может быть заменена пробелами редакторами
- Менее распространён чем CSV

---

## 19.4 CSV в Python

### Модуль csv

```python
import csv

# Чтение как список
with open('data.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # Первая строка — заголовки
    for row in reader:
        print(row)  # ['Alice', '30', 'Moscow']

# Чтение как словарь
with open('data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row['name'], row['age'])

# Запись списков
with open('output.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'age', 'city'])
    writer.writerow(['Alice', 30, 'Moscow'])
    writer.writerows([
        ['Bob', 25, 'London'],
        ['Charlie', 35, 'Paris']
    ])

# Запись словарей
with open('output.csv', 'w', encoding='utf-8', newline='') as f:
    fieldnames = ['name', 'age', 'city']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'name': 'Alice', 'age': 30, 'city': 'Moscow'})
```

!!! warning "newline='' на Windows"
    Без `newline=''` на Windows будут лишние пустые строки.

### Диалекты CSV

```python
import csv

# Excel-совместимый (по умолчанию)
reader = csv.reader(f, dialect='excel')

# TSV
reader = csv.reader(f, delimiter='\t')

# Кастомный диалект
csv.register_dialect('pipes', delimiter='|', quoting=csv.QUOTE_MINIMAL)
reader = csv.reader(f, dialect='pipes')

# Параметры напрямую
reader = csv.reader(f, 
    delimiter=';',           # Разделитель полей
    quotechar='"',           # Символ кавычек
    escapechar='\\',         # Символ экранирования
    doublequote=True,        # Удваивать кавычки при экранировании
    skipinitialspace=True,   # Пропускать пробелы после разделителя
    quoting=csv.QUOTE_MINIMAL  # Когда использовать кавычки
)
```

### Режимы кавычек

| Константа | Описание |
|-----------|----------|
| `QUOTE_MINIMAL` | Только когда необходимо |
| `QUOTE_ALL` | Все поля |
| `QUOTE_NONNUMERIC` | Все нечисловые поля |
| `QUOTE_NONE` | Никогда (использовать escapechar) |

---

## 19.5 CSV и pandas

```python
import pandas as pd

# Чтение
df = pd.read_csv('data.csv')
df = pd.read_csv('data.csv', encoding='cp1251')
df = pd.read_csv('data.csv', sep=';', decimal=',')  # Европейский формат

# Продвинутые параметры
df = pd.read_csv('data.csv',
    header=0,              # Строка заголовков (None если нет)
    names=['a', 'b', 'c'], # Указать имена колонок
    usecols=['name', 'age'],  # Читать только эти колонки
    dtype={'age': int},    # Типы колонок
    parse_dates=['date'],  # Парсить как даты
    na_values=['N/A', ''], # Значения для NaN
    nrows=1000,            # Читать только N строк
    skiprows=5,            # Пропустить первые N строк
    chunksize=10000        # Читать порциями
)

# Запись
df.to_csv('output.csv', index=False)
df.to_csv('output.csv', 
    index=False,
    encoding='utf-8-sig',  # С BOM для Excel
    sep=';',
    decimal=','
)
```

---

## 19.6 Проблемы CSV

### Excel и UTF-8

Excel ожидает BOM для UTF-8:

```python
# Для совместимости с Excel
with open('for_excel.csv', 'w', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['Имя', 'Возраст'])
    writer.writerow(['Иван', 30])
```

### Региональные настройки

В некоторых странах Excel использует `;` как разделитель:

```csv
name;age;city
Alice;30;Moscow
```

### Числа с ведущими нулями

```csv
id,phone
1,007123456
```

Excel преобразует `007` в `7`. Решение — кавычки или формат `="007"`.

### Инъекции формул

```csv
name,value
Alice,=1+1
Bob,=HYPERLINK("http://evil.com")
```

!!! danger "Безопасность"
    Никогда не открывайте CSV из недоверенных источников в Excel без проверки.

---

## 19.7 Инструменты командной строки

### csvkit

```bash
# Просмотр статистики
csvstat data.csv

# SQL-запросы к CSV
csvsql --query "SELECT name, age FROM data WHERE age > 25" data.csv

# Конвертация в JSON
csvjson data.csv

# Извлечение колонок
csvcut -c name,age data.csv
```

### miller (mlr)

```bash
# Фильтрация
mlr --csv filter '$age > 25' data.csv

# Преобразование
mlr --csv put '$full_name = $first . " " . $last' data.csv

# Агрегация
mlr --csv stats1 -a mean,sum -f age data.csv

# Конвертация форматов
mlr --icsv --ojson cat data.csv
```

### cut, awk

```bash
# Извлечь колонку 2
cut -d',' -f2 data.csv

# Обработка с awk
awk -F',' '{print $1, $3}' data.csv
```

---

## Резюме

| Характеристика | CSV | TSV |
|----------------|-----|-----|
| Расширение | `.csv` | `.tsv`, `.tab` |
| MIME-тип | `text/csv` | `text/tab-separated-values` |
| Разделитель | `,` | `\t` |
| Стандарт | RFC 4180 | Нет |
| Excel-совместимость | Да (с BOM) | Ограничена |
| Применение | Обмен данными, экспорт | Научные данные |


??? question "Упражнения"
    **Задание 1.** Создайте CSV-файл с полями, содержащими запятые, кавычки и переводы строк. Прочитайте его через `csv.reader()` и убедитесь в корректности.
    
    **Задание 2.** Сравните производительность: прочитайте CSV 100 МБ через `csv.reader()`, `pandas.read_csv()` и `DuckDB`. Замерьте время через `time`.
    
    **Задание 3.** Создайте CSV с BOM (UTF-8-sig) для совместимости с Excel. Откройте в Excel и убедитесь, что кириллица отображается корректно.

!!! tip "Следующая глава"
    Разобрались с CSV. Теперь — самый «тяжёлый» текстовый формат — **XML** → [XML](20-xml.md)
