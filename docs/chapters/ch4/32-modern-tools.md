# Глава 32. Современные инструменты для работы с данными

## Введение

Классические утилиты (`grep`, `awk`, `sed`) создавались для текстовых файлов. Но современные данные часто хранятся в структурированных форматах: JSON, CSV, Parquet. Для их обработки появились специализированные инструменты, которые понимают структуру данных и работают эффективнее.

---

## 32.1 jq — процессор JSON

### Основы

```bash
# Красивый вывод
$ cat data.json | jq .

# Извлечение поля
$ echo '{"name": "Alice", "age": 30}' | jq '.name'
"Alice"

# Без кавычек
$ echo '{"name": "Alice"}' | jq -r '.name'
Alice
```

### Навигация

```bash
# Вложенные объекты
$ jq '.user.address.city' data.json

# Массивы
$ jq '.[0]' array.json        # Первый элемент
$ jq '.[-1]' array.json       # Последний элемент
$ jq '.[2:5]' array.json      # Slice

# Все элементы массива
$ jq '.users[].name' data.json
```

### Фильтрация и трансформация

```bash
# select — фильтрация
$ jq '.[] | select(.age > 25)' users.json

# map — трансформация массива
$ jq 'map(.name)' users.json
$ jq 'map({user: .name, years: .age})' users.json

# Условия
$ jq 'if .status == "active" then .name else empty end' data.json
```

### Агрегация

```bash
# Подсчёт
$ jq 'length' array.json
$ jq '[.[] | select(.active)] | length' users.json

# Сумма, мин, макс
$ jq '[.[].price] | add' orders.json
$ jq '[.[].price] | min' orders.json
$ jq '[.[].price] | max' orders.json

# Группировка
$ jq 'group_by(.category) | map({category: .[0].category, count: length})' items.json
```

### Практические примеры

```bash
# Парсинг API-ответа
$ curl -s api.example.com/users | jq '.data[] | {id, email}'

# Преобразование в CSV
$ jq -r '.[] | [.name, .email] | @csv' users.json

# Слияние файлов
$ jq -s 'add' file1.json file2.json

# Изменение на месте (с sponge)
$ jq '.version = "2.0"' config.json | sponge config.json
```

---

## 32.2 yq — jq для YAML

```bash
# Чтение YAML
$ yq '.spec.containers[0].image' deployment.yaml

# Изменение
$ yq -i '.metadata.name = "new-name"' deployment.yaml

# Конвертация YAML → JSON
$ yq -o json config.yaml

# JSON → YAML
$ yq -P config.json
```

---

## 32.3 Miller (mlr) — швейцарский нож для табличных данных

### Что такое Miller

Miller — как awk, но понимает CSV, JSON, и другие форматы. Сохраняет заголовки и типы данных.

### Основные команды

```bash
# Вывод как таблица
$ mlr --csv --opprint cat data.csv

# Выбор столбцов
$ mlr --csv cut -f name,email data.csv

# Фильтрация
$ mlr --csv filter '$age > 25' data.csv

# Сортировка
$ mlr --csv sort -f name data.csv
$ mlr --csv sort -nr age data.csv  # Числовая, обратная

# Уникальные значения
$ mlr --csv uniq -g category data.csv
```

### Трансформации

```bash
# Добавить столбец
$ mlr --csv put '$full_name = $first . " " . $last' data.csv

# Переименовать
$ mlr --csv rename old_name,new_name data.csv

# Вычисления
$ mlr --csv put '$total = $price * $quantity' orders.csv
```

### Агрегация

```bash
# Статистика
$ mlr --csv stats1 -a sum,mean,count -f amount data.csv

# Группировка
$ mlr --csv stats1 -a sum -f amount -g category data.csv

# Топ N
$ mlr --csv top -f sales -n 10 data.csv
```

### Конвертация форматов

```bash
# CSV → JSON
$ mlr --icsv --ojson cat data.csv

# JSON → CSV
$ mlr --ijson --ocsv cat data.json

# Все форматы: csv, json, dkvp, pprint, markdown
$ mlr --icsv --omd cat data.csv  # Markdown таблица
```

---

## 32.4 csvkit — инструменты для CSV

### Набор утилит

```bash
# Информация о файле
$ csvstat data.csv              # Статистика по столбцам
$ csvlook data.csv              # Красивый вывод

# Выбор столбцов
$ csvcut -c name,email data.csv
$ csvcut -c 1,3,5 data.csv      # По номерам

# Фильтрация
$ csvgrep -c status -m "active" data.csv
$ csvgrep -c age -r "^[3-4][0-9]$" data.csv  # Regex

# Сортировка
$ csvsort -c date data.csv

# Объединение
$ csvjoin -c id left.csv right.csv
$ csvstack file1.csv file2.csv file3.csv
```

### SQL по CSV

```bash
# csvsql — SQL-запросы к CSV
$ csvsql --query "SELECT name, SUM(amount) FROM data GROUP BY name" data.csv

# Создать таблицу в SQLite
$ csvsql --db sqlite:///data.db --insert data.csv

# Выгрузить из базы в CSV
$ sql2csv --db sqlite:///data.db --query "SELECT * FROM users"
```

---

## 32.5 xsv — быстрый инструмент для CSV

Написан на Rust, работает очень быстро с большими файлами.

```bash
# Информация
$ xsv stats data.csv --everything

# Выбор столбцов
$ xsv select name,email data.csv
$ xsv select '!password' data.csv  # Все кроме

# Поиск
$ xsv search -s name "Alice" data.csv

# Slice
$ xsv slice -s 0 -e 100 data.csv   # Первые 100 строк

# Частота значений
$ xsv frequency -s category data.csv

# Join
$ xsv join id left.csv id right.csv

# Сэмплирование
$ xsv sample 1000 huge.csv > sample.csv
```

---

## 32.6 DuckDB — SQL для файлов

!!! info "Подробно о DuckDB"
    DuckDB — мощный инструмент, заслуживающий отдельной главы. Здесь — краткий обзор, полное руководство в [Главе 33](33-duckdb.md).

DuckDB — встраиваемая аналитическая база данных. Может работать напрямую с файлами без импорта.

```bash
# Запрос к CSV
$ duckdb -c "SELECT count(*) FROM 'data.csv'"

# Запрос к Parquet
$ duckdb -c "SELECT * FROM 'events.parquet' LIMIT 10"

# Конвертация CSV → Parquet
$ duckdb -c "COPY (SELECT * FROM 'data.csv') TO 'data.parquet' (FORMAT PARQUET)"
```

```python
import duckdb

# Прямой запрос к файлу
result = duckdb.query("SELECT * FROM 'data.csv' WHERE amount > 100").df()

# Работа с pandas DataFrame
import pandas as pd
df = pd.read_csv("data.csv")
result = duckdb.query("SELECT * FROM df WHERE category = 'A'").df()
```

→ Подробнее: агрегации, window functions, Python-интеграция — [Глава 33. DuckDB](33-duckdb.md)

---

## 32.7 VisiData — интерактивный просмотр

```bash
# Открыть CSV
$ vd data.csv

# Открыть JSON
$ vd data.json

# Горячие клавиши в vd:
# q     — выйти
# /     — поиск
# [, ]  — сортировка
# F     — frequency table
# +     — агрегация
# ^     — переименовать столбец
```

---

## 32.8 Сравнение инструментов

| Инструмент | Формат | Скорость | Сложные запросы | Интерактивность |
|------------|--------|----------|-----------------|-----------------|
| **jq** | JSON | Быстро | Средне | - |
| **yq** | YAML | Быстро | Средне | - |
| **mlr** | CSV/JSON | Быстро | Средне | - |
| **csvkit** | CSV | Средне | SQL | - |
| **xsv** | CSV | Очень быстро | Простые | - |
| **DuckDB** | Любой | Очень быстро | SQL (полный) | - |
| **VisiData** | Любой | Средне | Базовые | ✅ |

---

## 32.9 Инструменты нового поколения

### ripgrep (rg) — быстрый grep

ripgrep (rg) — замена grep, написанная на Rust. Быстрее grep, умнее с .gitignore.

```bash
# Установка
$ brew install ripgrep     # macOS
$ apt install ripgrep      # Debian/Ubuntu

# Базовое использование
$ rg "pattern" ./src/
$ rg "TODO" --type py              # Только .py файлы
$ rg "import" -g "*.{py,js}"       # Glob patterns

# Умные умолчания
$ rg "secret"                      # Автоматически игнорирует .gitignore
$ rg "secret" --no-ignore          # Включая игнорируемые файлы
$ rg "secret" --hidden             # Включая скрытые файлы

# Вывод контекста
$ rg -B3 -A3 "error"               # 3 строки до и после
$ rg --context 5 "error"           # То же самое

# JSON вывод (для парсинга)
$ rg --json "pattern" | jq '.data.lines.text'

# Замена (предпросмотр)
$ rg "old" --replace "new"

# Статистика
$ rg "TODO" --stats
```

### bat — cat с подсветкой

```bash
# Установка
$ brew install bat         # macOS
$ apt install bat          # Debian/Ubuntu (может быть batcat)

# Использование
$ bat file.py              # Подсветка синтаксиса + номера строк
$ bat -A file.txt          # Показать непечатаемые символы
$ bat --style=plain file   # Без декораций (как cat)

# Интеграция с другими инструментами
$ rg "error" -l | xargs bat   # Показать файлы с подсветкой
$ git diff | bat              # Diff с подсветкой
```

### fzf — fuzzy finder

fzf — интерактивный фильтр для любых списков.

```bash
# Установка
$ brew install fzf         # macOS
$ apt install fzf          # Debian/Ubuntu

# Базовое использование
$ fzf                      # Интерактивный поиск файлов
$ cat file.txt | fzf       # Фильтрация любого списка

# Интеграция с командами
$ vim $(fzf)               # Открыть выбранный файл в vim
$ cd $(find . -type d | fzf)  # Перейти в выбранную директорию

# С предпросмотром
$ fzf --preview 'bat --color=always {}'
$ fzf --preview 'head -100 {}'

# Множественный выбор
$ fzf -m                   # Tab для выбора, Enter для подтверждения
$ cat $(fzf -m)            # Показать несколько файлов
```

### fzf + ripgrep: мощная комбинация

```bash
# Интерактивный grep
$ rg --line-number "" | fzf

# Поиск с предпросмотром содержимого
$ rg -l "pattern" | fzf --preview 'rg --color=always "pattern" {}'

# Функция для .bashrc/.zshrc
rgi() {
    rg --line-number --no-heading "" | 
    fzf --delimiter : --preview 'bat --color=always {1} --highlight-line {2}' |
    cut -d: -f1,2
}
```

### fd — быстрый find

```bash
# Установка
$ brew install fd          # macOS
$ apt install fd-find      # Debian/Ubuntu (fd-find)

# Простой синтаксис
$ fd "pattern"             # Найти файлы по шаблону
$ fd -e py                 # Только .py файлы
$ fd -t d                  # Только директории

# Умные умолчания
$ fd                       # Игнорирует .gitignore
$ fd --hidden              # Включая скрытые
$ fd -x command {}         # Выполнить команду для каждого
```

### Сравнение современных альтернатив

| Классика | Современный | Преимущества |
|----------|-------------|--------------|
| `grep` | `ripgrep` | 10-100x быстрее, .gitignore, цвета |
| `cat` | `bat` | Подсветка синтаксиса, номера строк |
| `find` | `fd` | Простой синтаксис, .gitignore, быстрее |
| `ls` | `exa`/`eza` | Цвета, git-статус, иконки |

---

## 32.10 Когда что использовать

```
┌─────────────────────────────────────────────────────────────┐
│  ВЫБОР ИНСТРУМЕНТА                                          │
├─────────────────────────────────────────────────────────────┤
│  JSON + простые запросы      → jq                           │
│  YAML                        → yq                           │
│  CSV + простые операции      → xsv (скорость) / csvkit      │
│  CSV + трансформации         → mlr                          │
│  CSV/Parquet + SQL           → DuckDB                       │
│  Интерактивный анализ        → VisiData                     │
│  Сложная логика              → Python + pandas              │
└─────────────────────────────────────────────────────────────┘
```

---

## 32.11 Установка

```bash
# macOS (Homebrew)
brew install jq yq miller csvkit xsv duckdb visidata

# Ubuntu/Debian
apt install jq miller
pip install csvkit yq visidata

# Python
pip install duckdb
```

---

## 32.7 Дополнительные полезные инструменты

| Инструмент | Назначение | Замена для | Установка |
|-----------|-----------|-----------|-----------|
| **[uv](https://github.com/astral-sh/uv)** | Менеджер пакетов Python (10-100× быстрее pip) | pip, pip-tools, venv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **[dust](https://github.com/bootandy/dust)** | Визуализация использования диска | `du` | `brew install dust` / `cargo install du-dust` |
| **[tokei](https://github.com/XAMPPRocky/tokei)** | Статистика строк кода по языкам | `cloc`, `sloccount` | `brew install tokei` / `cargo install tokei` |
| **[hexyl](https://github.com/sharkdp/hexyl)** | Hex-просмотрщик с подсветкой | `xxd`, `hexdump` | `brew install hexyl` / `cargo install hexyl` |
| **[delta](https://github.com/dandavison/delta)** | Красивый diff (для git) | `diff`, `colordiff` | `brew install git-delta` |
| **[zoxide](https://github.com/ajeetdsouza/zoxide)** | Умная навигация по директориям | `cd`, `autojump` | `brew install zoxide` |

```bash
# uv — молниеносная установка пакетов
uv pip install pandas numpy  # В 10-100 раз быстрее pip!
uv venv .venv                # Создание venv за миллисекунды

# dust — где место на диске?
dust -n 10 /home             # Топ-10 директорий по размеру

# tokei — сколько кода в проекте?
tokei ./src
# ───────────────────────────────────
#  Language   Files  Lines  Code  Comments  Blanks
#  Python     42     12345  9876  1234      1235
#  YAML       8      456    400   20        36

# hexyl — красивый hex-дамп
hexyl --length 128 photo.jpg
```

---

## Резюме

| Инструмент | Сильные стороны |
|------------|----------------|
| **jq** | Стандарт для JSON, мощный язык запросов |
| **mlr** | Универсален, сохраняет структуру |
| **xsv** | Скорость на больших CSV |
| **DuckDB** | SQL для файлов, аналитика |
| **VisiData** | Интерактивное исследование |

!!! success "Заключение главы"
    Теперь в вашем арсенале полный набор инструментов: от базовых `cat`/`grep` до мощных `DuckDB` и `jq`. Выбирайте инструмент под задачу — и обрабатывайте данные эффективно!


??? question "Упражнения"
    **Задание 1.** Извлеките из JSON API ответа все значения определённого ключа с помощью `jq`. Пример: `curl -s api.github.com/users/octocat/repos | jq '.[].name'`.
    
    **Задание 2.** Обработайте CSV-файл с помощью `mlr`: переименуйте столбцы, отфильтруйте строки, добавьте вычисляемый столбец. Всё — одной командой.
    
    **Задание 3.** Постройте pipeline: `rg "pattern" -l | fzf --preview 'bat {}'` для интерактивного поиска. Добавьте эту функцию в `.bashrc`.

!!! tip "Следующая глава"
    Познакомились с инструментами. Теперь — подробнее про **DuckDB** и SQL для локальных файлов → [DuckDB](33-duckdb.md)
