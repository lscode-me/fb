# Глава 27. GNU Coreutils: инструменты для работы с байтами и текстом

## Введение

**Coreutils** — набор базовых утилит GNU, присутствующий практически в каждой Linux-системе. Это «швейцарский нож» для работы с файлами и потоками данных.

!!! warning "Важное понимание"
    Программы coreutils работают с **последовательностями байтов**, а не с «текстом» или «символами». 
    Отображение на экране — это **интерпретация** байтов терминалом согласно текущей локали.
    
    ```
    Файл (байты):     48 65 6C 6C 6F 0A
                      ↓
    Программа cat:    читает байты, пишет байты
                      ↓  
    Терминал:         интерпретирует как "Hello\n"
    ```

---

## 27.1 Философия UNIX-утилит

```
┌─────────────────────────────────────────────────────────────┐
│  Каждая программа делает ОДНУ вещь и делает её ХОРОШО       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • cat   — конкатенация файлов                              │
│  • head  — начало файла                                     │
│  • tail  — конец файла                                      │
│  • sort  — сортировка строк                                 │
│  • uniq  — уникальные строки                                │
│  • cut   — извлечение полей                                 │
│  • tr    — замена символов                                  │
│                                                             │
│  Комбинируй через pipes для сложных задач                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 27.2 Вывод содержимого файлов

### cat — конкатенация и вывод

```bash
# Базовое использование
$ cat file.txt              # Вывести файл
$ cat file1.txt file2.txt   # Конкатенация нескольких файлов
$ cat                       # Читать из stdin до EOF (Ctrl+D)

# Полезные опции
$ cat -n file.txt           # Нумерация всех строк
$ cat -b file.txt           # Нумерация непустых строк
$ cat -s file.txt           # Сжать множественные пустые строки
$ cat -A file.txt           # Показать непечатаемые символы
                            # $ = конец строки, ^I = tab, ^M = CR

# Пример -A для диагностики
$ printf "Hello\tWorld\r\n" | cat -A
Hello^IWorld^M$
#     ^^^     ^^
#     TAB     CRLF
```

!!! note "cat — это про байты"
    `cat` не знает о кодировках. Он просто копирует байты из входа на выход.
    Если файл в CP1251, а терминал в UTF-8 — вы увидите «кракозябры», 
    но `cat` работает корректно.

### head и tail — начало и конец

```bash
# head: первые N строк (по умолчанию 10)
$ head file.txt             # Первые 10 строк
$ head -n 5 file.txt        # Первые 5 строк
$ head -n -5 file.txt       # Всё, КРОМЕ последних 5 строк
$ head -c 100 file.txt      # Первые 100 байт

# tail: последние N строк
$ tail file.txt             # Последние 10 строк
$ tail -n 5 file.txt        # Последние 5 строк
$ tail -n +5 file.txt       # Начиная с 5-й строки
$ tail -c 100 file.txt      # Последние 100 байт

# Следить за файлом (логи)
$ tail -f /var/log/syslog          # Следить за новыми строками
$ tail -F /var/log/syslog          # + переоткрывать при ротации
$ tail -f -n 0 /var/log/syslog     # Только новые (без истории)
```

### Извлечение диапазона строк

```bash
# Строки с 10 по 20
$ sed -n '10,20p' file.txt

# Или через head/tail
$ head -n 20 file.txt | tail -n 11

# Или через awk
$ awk 'NR>=10 && NR<=20' file.txt
```

### tac — cat наоборот

```bash
# Вывести файл в обратном порядке строк
$ tac file.txt

# Полезно для логов (новые записи сверху)
$ tac /var/log/syslog | head -20
```

### rev — развернуть каждую строку

```bash
$ echo "Hello" | rev
olleH

# Извлечь расширение файла
$ echo "document.tar.gz" | rev | cut -d. -f1 | rev
gz
```

---

## 27.3 Фильтрация и преобразование

### grep — поиск по шаблону

```bash
# Базовый поиск
$ grep "pattern" file.txt        # Строки с pattern
$ grep -v "pattern" file.txt     # Строки БЕЗ pattern
$ grep -i "pattern" file.txt     # Регистронезависимо
$ grep -n "pattern" file.txt     # С номерами строк

# Регулярные выражения
$ grep -E "pattern1|pattern2" file.txt   # Extended regex (ERE)
$ grep -P "\d{3}-\d{4}" file.txt         # Perl regex (PCRE)

# Контекст
$ grep -B 2 "error" log.txt      # 2 строки ДО совпадения
$ grep -A 2 "error" log.txt      # 2 строки ПОСЛЕ
$ grep -C 2 "error" log.txt      # 2 строки вокруг

# Рекурсивный поиск
$ grep -r "TODO" ./src/          # Рекурсивно в директории
$ grep -rn "TODO" ./src/         # + номера строк
$ grep -rl "TODO" ./src/         # Только имена файлов

# Подсчёт
$ grep -c "error" log.txt        # Количество совпадений
$ grep -o "error" log.txt | wc -l  # Количество вхождений
```

### sort — сортировка строк

```bash
# Базовая сортировка (лексикографическая)
$ sort file.txt

# Числовая сортировка
$ sort -n numbers.txt            # 1, 2, 10 (не 1, 10, 2)
$ sort -h sizes.txt              # Human-readable (1K, 2M, 3G)

# Обратный порядок
$ sort -r file.txt

# По полю
$ sort -t: -k3 -n /etc/passwd    # По 3-му полю (UID), числовое
$ sort -t, -k2 data.csv          # CSV: по 2-му полю

# Уникальные строки при сортировке
$ sort -u file.txt               # Эквивалент sort | uniq

# Стабильная сортировка
$ sort -s file.txt               # Сохранить порядок равных

# Проверка отсортированности
$ sort -c file.txt               # Ошибка, если не отсортировано
```

!!! warning "Сортировка и локаль"
    Порядок сортировки зависит от переменной `LC_COLLATE`:
    ```bash
    $ echo -e "a\nA\nb\nB" | sort           # Зависит от локали
    $ echo -e "a\nA\nb\nB" | LC_ALL=C sort  # Строго по ASCII: A B a b
    ```

### uniq — уникальные строки

```bash
# Убрать СМЕЖНЫЕ дубликаты (требует предварительной сортировки!)
$ sort file.txt | uniq

# Подсчитать повторения
$ sort file.txt | uniq -c

# Только дубликаты
$ sort file.txt | uniq -d

# Только уникальные (встречаются 1 раз)
$ sort file.txt | uniq -u

# Игнорировать регистр
$ sort file.txt | uniq -i

# Игнорировать первые N полей
$ sort file.txt | uniq -f 1
```

### tr — замена/удаление символов

`tr` работает с **отдельными символами** (байтами), не со строками!

```bash
# Замена символов
$ echo "hello" | tr 'a-z' 'A-Z'      # HELLO
$ echo "hello" | tr 'aeiou' '12345'  # h2ll4

# Удаление символов
$ echo "hello 123" | tr -d '0-9'     # hello 
$ echo "hello" | tr -d 'aeiou'       # hll

# Сжатие повторяющихся символов
$ echo "heeello" | tr -s 'e'         # hello
$ echo "a    b    c" | tr -s ' '     # a b c

# Дополнение множества (complement)
$ echo "hello123" | tr -cd '0-9'     # 123 (удалить всё, кроме цифр)

# Специальные классы
$ tr '[:lower:]' '[:upper:]'         # Регистр
$ tr '[:space:]' '\n'                # Пробелы в переводы строк
```

### cut — извлечение полей

```bash
# По разделителю (delimiter)
$ cut -d: -f1 /etc/passwd            # Первое поле (имя пользователя)
$ cut -d: -f1,3 /etc/passwd          # Поля 1 и 3
$ cut -d: -f1-3 /etc/passwd          # Поля 1-3

# По позиции символов
$ cut -c1-10 file.txt                # Символы 1-10
$ cut -c5- file.txt                  # С 5-го до конца

# По позиции байтов
$ cut -b1-10 file.txt                # Байты 1-10 (важно для UTF-8!)

# Изменить разделитель на выходе
$ cut -d: -f1,3 --output-delimiter=',' /etc/passwd
```

!!! warning "cut и Unicode"
    `cut -c` работает с **символами** согласно локали, 
    `cut -b` — с **байтами**. Для UTF-8 это разные вещи!
    ```bash
    $ echo "Привет" | cut -c1-3    # При (3 символа)
    $ echo "Привет" | cut -b1-3    # П (3 байта = 1.5 символа UTF-8)
    ```

### paste — объединение файлов по столбцам

```bash
# Объединить файлы параллельно
$ paste file1.txt file2.txt

# С разделителем
$ paste -d, file1.txt file2.txt

# Объединить строки одного файла
$ paste -s file.txt                  # Все строки в одну
$ paste -d, -s file.txt              # Через запятую
```

---

## 27.4 Подсчёт и статистика

### wc — подсчёт слов/строк/байтов

```bash
$ wc file.txt
  100   500  3000 file.txt
# ^^^   ^^^  ^^^^
# строки слова байты

$ wc -l file.txt    # Только строки
$ wc -w file.txt    # Только слова
$ wc -c file.txt    # Только байты
$ wc -m file.txt    # Только символы (с учётом кодировки)
$ wc -L file.txt    # Длина самой длинной строки

# Подсчёт файлов
$ find . -name "*.py" | wc -l
```

!!! note "wc -l считает `\n`"
    `wc -l` считает символы новой строки. Если последняя строка 
    не заканчивается `\n`, она НЕ будет посчитана!
    
    ```bash
    $ printf "line1\nline2" | wc -l   # 1 (не 2!)
    $ printf "line1\nline2\n" | wc -l # 2
    ```

---

## 27.5 Трансформация данных

### sed — потоковый редактор

```bash
# Замена (первое вхождение в строке)
$ sed 's/old/new/' file.txt

# Замена (все вхождения)
$ sed 's/old/new/g' file.txt

# Замена на месте
$ sed -i 's/old/new/g' file.txt       # Linux
$ sed -i '' 's/old/new/g' file.txt    # macOS

# Удаление строк
$ sed '/pattern/d' file.txt           # Удалить строки с pattern
$ sed '1d' file.txt                   # Удалить первую строку
$ sed '1,5d' file.txt                 # Удалить строки 1-5

# Печать конкретных строк
$ sed -n '10,20p' file.txt            # Только строки 10-20
$ sed -n '/start/,/end/p' file.txt    # Между pattern'ами

# Вставка
$ sed '1i\Заголовок' file.txt         # Вставить перед строкой 1
$ sed '$a\Подвал' file.txt            # Добавить после последней
```

### awk — язык обработки текста

```bash
# Печать полей
$ awk '{print $1}' file.txt           # Первое поле
$ awk '{print $1, $3}' file.txt       # Поля 1 и 3
$ awk '{print $NF}' file.txt          # Последнее поле

# Разделитель полей
$ awk -F: '{print $1}' /etc/passwd
$ awk -F',' '{print $2}' data.csv

# Условия
$ awk '$3 > 100' file.txt             # Где 3-е поле > 100
$ awk '/pattern/' file.txt            # Строки с pattern
$ awk 'NR > 1' file.txt               # Пропустить заголовок

# Вычисления
$ awk '{sum += $1} END {print sum}' numbers.txt
$ awk '{sum += $1; count++} END {print sum/count}' numbers.txt

# Форматирование
$ awk '{printf "%-20s %10d\n", $1, $2}' file.txt
```

---

## 27.6 Сравнение файлов

### diff — различия между файлами

```bash
# Обычный формат
$ diff file1.txt file2.txt

# Unified формат (как в git)
$ diff -u file1.txt file2.txt

# Краткий отчёт
$ diff -q file1.txt file2.txt   # Только "различаются" или ничего

# Игнорировать пробелы
$ diff -w file1.txt file2.txt   # Игнорировать все пробелы
$ diff -b file1.txt file2.txt   # Игнорировать trailing spaces

# Рекурсивное сравнение директорий
$ diff -r dir1/ dir2/
```

### comm — сравнение отсортированных файлов

```bash
# Вывод в 3 колонки: только в 1-м | только во 2-м | в обоих
$ comm file1.txt file2.txt

# Подавить колонки
$ comm -12 file1.txt file2.txt  # Только общие строки
$ comm -23 file1.txt file2.txt  # Только в file1
$ comm -13 file1.txt file2.txt  # Только в file2
```

### cmp — байтовое сравнение

```bash
# Сравнить побайтово
$ cmp file1 file2
file1 file2 differ: byte 10, line 1

# Тихий режим (только код возврата)
$ cmp -s file1 file2 && echo "Identical" || echo "Different"
```

---

## 27.7 Работа с бинарными данными

### od — octal dump

```bash
# Восьмеричный дамп
$ od file.bin

# Шестнадцатеричный
$ od -A x -t x1z file.bin
#   ^       ^^^
#   hex     hex bytes + ASCII

# Разные форматы
$ od -t c file.bin    # Символы
$ od -t d1 file.bin   # Знаковые байты
$ od -t u1 file.bin   # Беззнаковые байты
```

### xxd — hex dump (vim)

```bash
# Hex dump
$ xxd file.bin

# Обратное преобразование (hex → binary)
$ xxd -r hexdump.txt > file.bin

# Только hex без ASCII
$ xxd -p file.bin

# Определённое количество байт
$ xxd -l 64 file.bin
```

### hexdump — гибкий hex dump

```bash
# Канонический формат
$ hexdump -C file.bin

# Пользовательский формат
$ hexdump -e '16/1 "%02x " "\n"' file.bin
```

### dd — копирование и конвертация

```bash
# Создать файл заданного размера
$ dd if=/dev/zero of=file.bin bs=1M count=100

# Конвертация регистра
$ dd if=file.txt of=upper.txt conv=ucase

# Извлечь фрагмент (skip=смещение, count=размер)
$ dd if=image.iso of=mbr.bin bs=512 count=1

# Прогресс
$ dd if=/dev/sda of=disk.img bs=4M status=progress
```

---

## 27.8 Утилиты для специальных задач

### split — разбить файл

```bash
# По размеру
$ split -b 100M huge.file part_     # part_aa, part_ab, ...

# По количеству строк
$ split -l 1000 data.txt chunk_     # По 1000 строк

# Объединить обратно
$ cat part_* > restored.file
```

### csplit — разбить по шаблону

```bash
# Разбить по regex
$ csplit file.txt '/^Chapter/' '{*}'
```

### nl — нумерация строк

```bash
$ nl file.txt              # Нумерация непустых
$ nl -ba file.txt          # Нумерация всех строк
$ nl -s ': ' file.txt      # С разделителем
```

### expand/unexpand — табы и пробелы

```bash
$ expand file.txt          # TAB → пробелы (8 по умолчанию)
$ expand -t 4 file.txt     # TAB → 4 пробела
$ unexpand -a file.txt     # Пробелы → TAB
```

### fold — перенос длинных строк

```bash
$ fold -w 80 file.txt      # Перенос на 80 символов
$ fold -w 80 -s file.txt   # Перенос по словам
```

### fmt — форматирование абзацев

```bash
$ fmt -w 72 file.txt       # Ширина 72
$ fmt -u file.txt          # Uniform spacing
```

### pr — подготовка к печати

```bash
$ pr file.txt              # Разбить на страницы с заголовками
$ pr -2 file.txt           # В 2 колонки
$ pr -h "Title" file.txt   # С заголовком
```

---

## 27.9 Параллельная обработка

### xargs -P — параллельный xargs

```bash
# Последовательная обработка (по умолчанию)
$ find . -name "*.jpg" | xargs -n1 convert_image

# Параллельная обработка (4 процесса)
$ find . -name "*.jpg" | xargs -n1 -P4 convert_image

# Максимальный параллелизм (все CPU)
$ find . -name "*.jpg" | xargs -n1 -P0 convert_image

# С null-разделителем для сложных имён
$ find . -name "*.jpg" -print0 | xargs -0 -n1 -P4 convert_image
```

### Практические примеры xargs -P

```bash
# Сжатие всех файлов параллельно
$ find . -name "*.log" -print0 | xargs -0 -P8 -n1 gzip

# Скачивание списка URL
$ cat urls.txt | xargs -P10 -n1 curl -O

# Конвертация изображений
$ ls *.png | xargs -P4 -I{} convert {} -resize 50% resized_{}

# Запуск тестов параллельно
$ find tests/ -name "test_*.py" | xargs -P4 -n1 python
```

### GNU Parallel — мощный инструмент

```bash
# Установка
$ brew install parallel          # macOS
$ apt install parallel           # Debian/Ubuntu

# Базовое использование (как xargs -P, но умнее)
$ parallel convert {} {.}.jpg ::: *.png

# Из файла
$ cat files.txt | parallel process_file {}

# Количество задач
$ parallel -j4 command ::: arg1 arg2 arg3 arg4 arg5

# Распределение по серверам (SSH)
$ parallel -S server1,server2 --sshlogin hostname process ::: files*
```

### Parallel vs xargs -P

```
┌─────────────────────────────────────────────────────────────┐
│  xargs -P                    │  GNU Parallel                │
├──────────────────────────────┼──────────────────────────────┤
│  Встроен в систему           │  Требует установки           │
│  Простой синтаксис           │  Богатый функционал          │
│  Только локально             │  SSH на удалённые машины     │
│  Вывод перемешан             │  Группировка вывода          │
│  Нет progress bar            │  Есть прогресс (--progress)  │
└──────────────────────────────┴──────────────────────────────┘
```

```bash
# Parallel сохраняет порядок и группирует вывод
$ parallel --keep-order 'echo "Start {}"; sleep 1; echo "End {}"' ::: A B C

# Прогресс-бар
$ parallel --progress command ::: files*

# Сохранение результатов в отдельные файлы
$ parallel --results output_dir/ command ::: inputs*
```

!!! tip "Когда использовать параллельную обработку"
    - **I/O-bound задачи**: скачивание файлов, обработка изображений
    - **CPU-bound задачи**: компрессия, рендеринг, компиляция
    - **Независимые задачи**: файлы не зависят друг от друга
    - **Большой объём**: сотни/тысячи файлов, где последовательная обработка займёт часы

---

## 27.10 Кодировка и coreutils

### Локаль и обработка

```bash
# Текущая локаль
$ locale
LANG=en_US.UTF-8
LC_ALL=

# Локаль влияет на:
# - sort: порядок сортировки
# - tr: определение классов символов
# - wc -m: подсчёт символов
# - cut -c: позиции символов

# Для предсказуемого поведения:
$ LC_ALL=C sort file.txt           # Байтовая сортировка
$ LC_ALL=C tr '[:lower:]' '[:upper:]'  # ASCII only
```

### iconv — конвертация кодировок

```bash
# Конвертировать из CP1251 в UTF-8
$ iconv -f CP1251 -t UTF-8 file.txt > file_utf8.txt

# Список кодировок
$ iconv -l

# С заменой неконвертируемых символов
$ iconv -f CP1251 -t UTF-8//TRANSLIT file.txt
$ iconv -f CP1251 -t UTF-8//IGNORE file.txt
```

### file — определение типа файла

```bash
$ file document.txt
document.txt: UTF-8 Unicode text

$ file image.png
image.png: PNG image data, 800 x 600, 8-bit/color RGBA

$ file binary
binary: ELF 64-bit LSB executable, x86-64
```

---

## Справочная таблица

### Утилиты вывода

| Команда | Назначение |
|---------|-----------|
| `cat` | Конкатенация файлов |
| `tac` | Вывод в обратном порядке |
| `head` | Начало файла |
| `tail` | Конец файла (-f для слежения) |
| `less` | Постраничный просмотр |

### Утилиты фильтрации

| Команда | Назначение |
|---------|-----------|
| `grep` | Поиск по шаблону |
| `sort` | Сортировка строк |
| `uniq` | Уникальные строки |
| `tr` | Замена символов |
| `cut` | Извлечение полей |
| `paste` | Объединение по столбцам |

### Утилиты анализа

| Команда | Назначение |
|---------|-----------|
| `wc` | Подсчёт строк/слов/байтов |
| `diff` | Сравнение файлов |
| `comm` | Сравнение отсортированных |
| `cmp` | Побайтовое сравнение |

### Утилиты преобразования

| Команда | Назначение |
|---------|-----------|
| `sed` | Потоковое редактирование |
| `awk` | Обработка полей |
| `iconv` | Конвертация кодировок |
| `dd` | Копирование/конвертация |


??? question "Упражнения"
    **Задание 1.** Одной командой (pipeline) подсчитайте, сколько раз каждое слово встречается в текстовом файле. Подсказка: `tr`, `sort`, `uniq -c`.
    
    **Задание 2.** Используя `find` + `xargs`, найдите все файлы больше 10 МБ, модифицированные за последние 7 дней, и выведите их размер в human-readable формате.
    
    **Задание 3.** Напишите pipeline, эмулирующий `tail -f`: с помощью `while true; do ...; done` непрерывно отслеживайте новые строки в лог-файле.

!!! tip "Следующая глава"
    Изучили базовые утилиты. Теперь углубимся в **grep, sed и awk** — мощные инструменты потоковой обработки → [Потоковая обработка: grep, sed, awk](28-text-processing.md)
