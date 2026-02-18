---
description: "Потоковая обработка текста в Linux. Поиск с grep, замена с sed, анализ с awk. Регулярные выражения, практические примеры."
---

# Глава 28. Потоковая обработка: grep, sed, awk

## Введение

Три инструмента — `grep`, `sed` и `awk` — составляют основу потоковой обработки текста в UNIX. Каждый решает свою задачу:

```
┌─────────────────────────────────────────────────────────────┐
│  grep  →  ПОИСК: найти строки, соответствующие шаблону      │
│  sed   →  ЗАМЕНА: найти и заменить, удалить, вставить       │
│  awk   →  АНАЛИЗ: извлечь поля, вычислить, трансформировать │
└─────────────────────────────────────────────────────────────┘
```

Все три работают **построчно**: читают строку, обрабатывают, выводят (или нет), переходят к следующей.

---

## 28.1 grep: поиск шаблонов

### Базовое использование

```bash
# Найти строки, содержащие pattern
$ grep "error" /var/log/syslog

# Инвертировать (строки БЕЗ pattern)
$ grep -v "debug" app.log

# Регистронезависимый поиск
$ grep -i "warning" app.log

# С номерами строк
$ grep -n "TODO" *.py
```

### Регулярные выражения

```bash
# Basic Regular Expressions (BRE) — по умолчанию
$ grep "^#" file.txt           # Начинается с #
$ grep "\.py$" file.txt        # Заканчивается на .py
$ grep "[0-9]\{3\}" file.txt   # Три цифры подряд

# Extended Regular Expressions (ERE)
$ grep -E "error|warning" log.txt     # Альтернатива
$ grep -E "[0-9]{3}-[0-9]{4}" file    # {n} без экранирования
$ grep -E "(ab)+" file.txt            # Группировка

# Perl-Compatible Regular Expressions (PCRE)
$ grep -P "\d{3}-\d{4}" file.txt      # \d вместо [0-9]
$ grep -P "(?<=@)\w+" emails.txt      # Lookbehind
$ grep -P "foo(?=bar)" file.txt       # Lookahead
```

### Контекст совпадений

```bash
# Строки вокруг совпадения
$ grep -B 3 "error" log.txt    # 3 строки ДО (Before)
$ grep -A 3 "error" log.txt    # 3 строки ПОСЛЕ (After)
$ grep -C 3 "error" log.txt    # 3 строки вокруг (Context)

# Вывод с разделителями групп
$ grep -C 2 --group-separator="---" "error" log.txt
```

### Рекурсивный поиск

```bash
# В директории
$ grep -r "TODO" ./src/

# С указанием типов файлов
$ grep -r --include="*.py" "import" ./

# Исключить директории
$ grep -r --exclude-dir=".git" --exclude-dir="node_modules" "pattern" ./

# Только имена файлов
$ grep -rl "pattern" ./src/   # Файлы с совпадениями
$ grep -rL "pattern" ./src/   # Файлы БЕЗ совпадений
```

### Подсчёт и извлечение

```bash
# Количество строк с совпадениями
$ grep -c "error" log.txt

# Только совпадающие части (не вся строка)
$ grep -o "[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+" access.log

# С выводом имени файла (всегда)
$ grep -H "pattern" file.txt

# Без имени файла (никогда)
$ grep -h "pattern" *.txt
```

### Бинарные файлы

```bash
# Обрабатывать бинарные как текст
$ grep -a "string" binary_file

# Игнорировать бинарные
$ grep -I "pattern" *
```

### Практические примеры

```bash
# Найти IP-адреса
$ grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" access.log

# Найти email-адреса
$ grep -oE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" file.txt

# Найти URL
$ grep -oP "https?://[^\s\"'>]+" file.html

# Строки между маркерами
$ grep -Pzo "(?s)START.*?END" file.txt
```

---

## 28.2 sed: потоковый редактор

### Синтаксис sed

```
sed [options] 'command' file
sed [options] -e 'cmd1' -e 'cmd2' file
sed [options] -f script.sed file
```

### Команда замены (s)

```bash
# Замена первого вхождения в строке
$ sed 's/old/new/' file.txt

# Замена всех вхождений (global)
$ sed 's/old/new/g' file.txt

# Замена N-го вхождения
$ sed 's/old/new/2' file.txt      # Второе вхождение

# Замена с флагами
$ sed 's/old/new/gi' file.txt     # Регистронезависимо

# Другой разделитель (полезно для путей)
$ sed 's|/usr/local|/opt|g' file.txt
$ sed 's#old#new#g' file.txt
```

### Адресация строк

```bash
# Конкретная строка
$ sed '5s/old/new/' file.txt      # Только в строке 5

# Диапазон строк
$ sed '10,20s/old/new/g' file.txt # Строки 10-20

# От строки до конца
$ sed '10,$s/old/new/g' file.txt  # С 10-й до конца

# По шаблону
$ sed '/pattern/s/old/new/g' file.txt

# Между шаблонами
$ sed '/START/,/END/s/old/new/g' file.txt

# Кроме указанных строк
$ sed '1,5!s/old/new/g' file.txt  # Кроме строк 1-5
```

### Другие команды

```bash
# Удаление строк (d)
$ sed '/pattern/d' file.txt       # Удалить строки с pattern
$ sed '1d' file.txt               # Удалить первую строку
$ sed '/^$/d' file.txt            # Удалить пустые строки
$ sed '/^#/d' file.txt            # Удалить комментарии

# Печать (p) — требует -n
$ sed -n '10,20p' file.txt        # Напечатать строки 10-20
$ sed -n '/pattern/p' file.txt    # Напечатать совпадения

# Вставка (i — перед, a — после)
$ sed '1i\Заголовок' file.txt     # Вставить перед строкой 1
$ sed '$a\Конец файла' file.txt   # Добавить после последней

# Замена строки целиком (c)
$ sed '/pattern/c\Новая строка' file.txt
```

### Редактирование на месте

```bash
# Linux
$ sed -i 's/old/new/g' file.txt

# macOS (требует пустой суффикс)
$ sed -i '' 's/old/new/g' file.txt

# С бэкапом
$ sed -i.bak 's/old/new/g' file.txt  # Создаст file.txt.bak
```

### Обратные ссылки

```bash
# Захват групп \( \) и использование \1, \2, ...
$ echo "hello world" | sed 's/\(hello\) \(world\)/\2 \1/'
world hello

# Вся совпавшая строка: &
$ echo "hello" | sed 's/.*/[&]/'
[hello]

# Перестановка полей
$ echo "John Smith" | sed 's/\([^ ]*\) \([^ ]*\)/\2, \1/'
Smith, John

# Дублирование
$ echo "test" | sed 's/.*/& &/'
test test
```

### Extended regex в sed

```bash
# GNU sed: -E или -r
$ sed -E 's/[0-9]{3}-[0-9]{4}/XXX-XXXX/g' file.txt

# + и ? без экранирования
$ sed -E 's/colou?r/COLOR/g' file.txt
```

### Многострочная обработка

```bash
# N — добавить следующую строку в буфер
$ sed 'N;s/\n/ /' file.txt        # Объединить каждые 2 строки

# D — удалить первую строку буфера
# P — напечатать первую строку буфера

# Объединить строки, продолженные \ 
$ sed ':a;/\\$/N;s/\\\n//;ta' file.txt
```

### Практические примеры

```bash
# Удалить trailing whitespace
$ sed 's/[[:space:]]*$//' file.txt

# Удалить leading whitespace
$ sed 's/^[[:space:]]*//' file.txt

# Удалить HTML-теги
$ sed 's/<[^>]*>//g' file.html

# Удалить пустые строки и комментарии
$ sed '/^$/d;/^#/d' config.txt

# Добавить строку после совпадения
$ sed '/pattern/a\Новая строка' file.txt

# Заменить между маркерами
$ sed '/START/,/END/{s/old/new/g}' file.txt
```

---

## 28.3 awk: язык обработки данных

### Структура программы awk

```
awk 'pattern { action }' file
awk 'BEGIN { init } pattern { action } END { finish }' file
```

### Встроенные переменные

| Переменная | Значение |
|------------|----------|
| `$0` | Вся текущая строка |
| `$1`, `$2`, ... | Поля 1, 2, ... |
| `$NF` | Последнее поле |
| `NF` | Количество полей |
| `NR` | Номер текущей записи (строки) |
| `FNR` | Номер записи в текущем файле |
| `FS` | Field Separator (по умолчанию пробел/таб) |
| `OFS` | Output Field Separator |
| `RS` | Record Separator (по умолчанию \n) |
| `ORS` | Output Record Separator |
| `FILENAME` | Имя текущего файла |

### Базовые операции

```bash
# Печать полей
$ awk '{print $1}' file.txt              # Первое поле
$ awk '{print $1, $3}' file.txt          # Поля 1 и 3
$ awk '{print $NF}' file.txt             # Последнее поле
$ awk '{print $(NF-1)}' file.txt         # Предпоследнее

# Разделитель полей
$ awk -F: '{print $1}' /etc/passwd       # Разделитель :
$ awk -F',' '{print $2}' data.csv        # Разделитель ,
$ awk -F'\t' '{print $1}' file.tsv       # Разделитель TAB

# Выходной разделитель
$ awk -F: 'BEGIN{OFS=","} {print $1,$3}' /etc/passwd
```

### Шаблоны (patterns)

```bash
# Regex
$ awk '/pattern/' file.txt               # Строки с pattern
$ awk '!/pattern/' file.txt              # Строки БЕЗ pattern

# Сравнение
$ awk '$3 > 100' file.txt                # Поле 3 > 100
$ awk '$1 == "admin"' file.txt           # Поле 1 равно "admin"
$ awk 'length($0) > 80' file.txt         # Строки длиннее 80

# Диапазон
$ awk '/START/,/END/' file.txt           # Между маркерами
$ awk 'NR==10,NR==20' file.txt           # Строки 10-20

# Логические операции
$ awk '$1 == "error" && $2 > 100' file
$ awk '$1 == "A" || $1 == "B"' file
```

### BEGIN и END

```bash
# Инициализация и финализация
$ awk 'BEGIN {print "Start"} {print} END {print "End"}' file.txt

# Подсчёт и статистика
$ awk '{sum += $1} END {print "Sum:", sum}' numbers.txt
$ awk '{sum += $1; count++} END {print "Avg:", sum/count}' numbers.txt

# Заголовок и подвал для CSV
$ awk 'BEGIN {print "name,value"} {print $1","$2} END {print "# EOF"}' data.txt
```

### Переменные и массивы

```bash
# Переменные
$ awk '{total += $1} END {print total}' file.txt

# Передача переменных извне
$ awk -v threshold=100 '$1 > threshold' file.txt
$ awk -v name="$USER" 'BEGIN {print "User:", name}'

# Ассоциативные массивы
$ awk '{count[$1]++} END {for (word in count) print word, count[word]}' file.txt

# Подсчёт уникальных значений
$ awk '{seen[$1] = 1} END {for (k in seen) n++; print n}' file.txt
```

### Функции

```bash
# Встроенные функции
$ awk '{print length($0)}' file.txt           # Длина строки
$ awk '{print toupper($0)}' file.txt          # Верхний регистр
$ awk '{print tolower($0)}' file.txt          # Нижний регистр
$ awk '{print substr($1, 1, 3)}' file.txt     # Подстрока

# Математические
$ awk '{print sqrt($1)}' numbers.txt
$ awk '{print int($1)}' numbers.txt
$ awk 'BEGIN {print sin(3.14159/2)}'

# Строковые функции
$ awk '{gsub(/old/, "new"); print}' file.txt  # Замена
$ awk '{split($0, a, ":"); print a[1]}' file  # Разбиение
$ awk '{if (match($0, /[0-9]+/)) print substr($0, RSTART, RLENGTH)}' file

# Пользовательские функции
$ awk 'function double(x) {return x*2} {print double($1)}' file.txt
```

### Форматированный вывод

```bash
# printf (как в C)
$ awk '{printf "%-20s %10.2f\n", $1, $2}' file.txt
#       ^^^^^^^^^^^^^ ^^^^^^^^
#       строка 20 сим  число 10.2

# Флаги форматирования
# -  : выравнивание влево
# +  : показывать знак +
# 0  : дополнять нулями
# .N : точность для чисел / max длина для строк
```

### Практические примеры

```bash
# Сумма столбца
$ awk '{sum += $2} END {print sum}' data.txt

# Максимальное значение
$ awk 'NR==1 || $2 > max {max=$2} END {print max}' data.txt

# Частота слов
$ awk '{for(i=1;i<=NF;i++) count[$i]++} END {for(w in count) print count[w], w}' file.txt | sort -rn | head

# CSV → JSON (простой)
$ awk -F, 'NR>1 {printf "{\"name\":\"%s\",\"value\":%s}\n", $1, $2}' data.csv

# Группировка и суммирование
$ awk -F, '{sum[$1] += $2} END {for (k in sum) print k, sum[k]}' data.csv

# Транспонирование таблицы
$ awk '{for(i=1;i<=NF;i++) a[NR,i]=$i} END {for(i=1;i<=NF;i++) {for(j=1;j<=NR;j++) printf "%s ", a[j,i]; print ""}}' file.txt

# Фильтр по нескольким условиям
$ awk -F: '$3 >= 1000 && $7 !~ /nologin/' /etc/passwd

# Вывод с условным форматированием
$ awk '{if ($2 > 100) color="HIGH"; else color="low"; printf "%s: %s\n", $1, color}' file.txt
```

### AWK как мост: генерация SQL и JSON

AWK отлично подходит для **генерации** кода и запросов из данных:

```bash
# Генерация SQL INSERT из CSV
$ awk -F, 'NR>1 {
    printf "INSERT INTO users (name, email, age) VALUES ('\''%s'\'', '\''%s'\'', %s);\n", 
           $1, $2, $3
}' users.csv

# Результат:
# INSERT INTO users (name, email, age) VALUES ('Alice', 'alice@mail.com', 30);
# INSERT INTO users (name, email, age) VALUES ('Bob', 'bob@mail.com', 25);
```

```bash
# Генерация SQL UPDATE
$ awk -F, 'NR>1 {
    printf "UPDATE products SET price = %s WHERE sku = '\''%s'\'';\n", $3, $1
}' prices.csv

# Генерация DELETE с условием
$ awk '$2 < "2020-01-01" {
    printf "DELETE FROM logs WHERE id = %s;\n", $1
}' old_records.txt
```

```bash
# Генерация JSON массива из текстовых данных
$ awk 'BEGIN {print "["} 
       NR>1 {if(NR>2) print ","; printf "  {\"id\": %d, \"name\": \"%s\"}", NR-1, $0} 
       END {print "\n]"}' names.txt

# Более сложный JSON с escape
$ awk -F'\t' 'NR>1 {
    gsub(/"/, "\\\"", $2)  # Escape кавычек в данных
    printf "{\"code\": \"%s\", \"description\": \"%s\"},\n", $1, $2
}' data.tsv
```

!!! tip "Когда использовать AWK для генерации"
    - **Миграции данных**: быстрая конвертация CSV → SQL для одноразового импорта
    - **Ad-hoc запросы**: не хочется писать скрипт на Python для простой задачи
    - **Пайплайны**: `generate_sql.awk | psql -d mydb`
    - **Шаблонизация**: любой формат, включая YAML, XML, конфиги

---

## 28.4 Комбинирование инструментов

### grep + sed + awk вместе

```bash
# Найти, извлечь, обработать
$ grep "ERROR" log.txt | sed 's/.*\[//' | sed 's/\].*//' | sort | uniq -c | sort -rn

# Упростить через awk
$ awk '/ERROR/ {gsub(/.*\[|\].*/, ""); print}' log.txt | sort | uniq -c | sort -rn

# Или полностью в awk
$ awk '/ERROR/ {
    gsub(/.*\[|\].*/, "")
    count[$0]++
} END {
    for (err in count) print count[err], err
}' log.txt | sort -rn
```

### Когда что использовать

| Задача | Инструмент | Пример |
|--------|-----------|--------|
| Найти строки | grep | `grep "error" log.txt` |
| Простая замена | sed | `sed 's/old/new/g' file.txt` |
| Извлечь поля | awk/cut | `awk -F: '{print $1}' /etc/passwd` |
| Подсчёт/статистика | awk | `awk '{sum+=$1} END {print sum}'` |
| Сложная логика | awk | Ассоциативные массивы, функции |

---

## 28.5 Альтернативы: ripgrep, sd, miller

### ripgrep (rg) — быстрый grep

```bash
# Установка
$ brew install ripgrep  # macOS
$ apt install ripgrep   # Debian/Ubuntu

# Использование (быстрее grep, умнее с .gitignore)
$ rg "pattern" ./src/
$ rg -t py "import"            # Только .py файлы
$ rg -g "*.py" "pattern"       # Glob pattern
$ rg --json "pattern"          # JSON output
```

### sd — современный sed

```bash
# Установка
$ cargo install sd

# Использование (без regex escaping!)
$ sd "old" "new" file.txt
$ sd "func\(" "function(" *.js  # Проще, чем sed
```

### miller (mlr) — awk для структурированных данных

```bash
# Установка
$ brew install miller

# CSV с заголовками
$ mlr --csv filter '$age > 30' data.csv
$ mlr --csv sort -f name data.csv
$ mlr --csv stats1 -a sum,mean -f salary data.csv
$ mlr --c2j cat data.csv  # CSV → JSON
```

---

## Резюме

### Выбор инструмента

```
┌─────────────────────────────────────────────────────────────┐
│  Задача                          │  Инструмент              │
├──────────────────────────────────┼──────────────────────────┤
│  Найти строки по шаблону         │  grep                    │
│  Замена текста                   │  sed                     │
│  Извлечение полей                │  awk, cut                │
│  Сложные вычисления              │  awk                     │
│  Структурированные данные        │  miller, jq, xsv         │
│  Максимальная скорость           │  ripgrep                 │
└──────────────────────────────────┴──────────────────────────┘
```

### Шпаргалка

```bash
# grep: поиск
grep "pattern" file          # Найти
grep -v "pattern" file       # Инвертировать
grep -i "pattern" file       # Без учёта регистра
grep -rn "pattern" ./        # Рекурсивно с номерами

# sed: замена
sed 's/old/new/' file        # Первое вхождение
sed 's/old/new/g' file       # Все вхождения
sed -i 's/old/new/g' file    # На месте
sed '/pattern/d' file        # Удалить строки

# awk: обработка
awk '{print $1}' file        # Первое поле
awk -F: '{print $1}' file    # С разделителем
awk '$3 > 100' file          # Условие
awk '{sum+=$1} END {print sum}' file  # Сумма
```


??? question "Упражнения"
    **Задание 1.** Напишите `grep`-выражение для поиска всех email-адресов в текстовом файле. Используйте extended regex (`grep -E`).
    
    **Задание 2.** С помощью `sed` замените все даты в формате `DD/MM/YYYY` на `YYYY-MM-DD` в файле. Используйте группы захвата.
    
    **Задание 3.** Напишите `awk`-скрипт, который читает CSV и генерирует SQL INSERT-выражения для каждой строки.

!!! tip "Следующая глава"
    Освоили потоковую обработку. Теперь рассмотрим **редакторы и просмотрщики** — инструменты для интерактивной работы с файлами → [Редакторы и просмотрщики](29-editors.md)
