# Глава 30. Языки программирования: итераторы и потоковая обработка

## Введение

Shell-утилиты (`grep`, `sed`, `awk`) хороши для простых задач, но сложная логика требует полноценного языка программирования. В этой главе рассмотрим, как языки работают с потоками данных, и особенно — **итераторы** и **генераторы** для обработки данных по частям без загрузки в память.

---

## 30.1 Потоковая обработка: ключевые концепции

### Проблема памяти

```python
# ПЛОХО: загрузить весь файл в память
data = open("huge.log").read()        # 10GB в RAM!
lines = data.split("\n")
for line in lines:
    process(line)

# ХОРОШО: обрабатывать построчно
for line in open("huge.log"):         # Одна строка за раз
    process(line)
```

### Итератор vs Список

```
┌─────────────────────────────────────────────────────────────┐
│  СПИСОК (list)                                              │
│  • Все элементы в памяти                                    │
│  • Можно обращаться по индексу                              │
│  • Можно итерировать многократно                            │
│                                                             │
│  ИТЕРАТОР (iterator)                                        │
│  • Генерирует элементы по запросу (lazy)                    │
│  • Минимальное использование памяти                         │
│  • Можно итерировать только ОДИН раз                        │
│                                                             │
│  ГЕНЕРАТОР (generator)                                      │
│  • Функция, которая yield'ит значения                       │
│  • Создаёт итератор                                         │
│  • Сохраняет состояние между вызовами                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 30.2 Python: генераторы и итераторы

### Базовая потоковая обработка

```python
import sys

# Построчное чтение stdin
for line in sys.stdin:
    # line включает '\n'
    processed = line.strip().upper()
    print(processed)

# Использование: cat file.txt | python script.py
```

### Генераторы с yield

```python
def read_in_chunks(file_path, chunk_size=8192):
    """Читает файл по частям (чанкам)."""
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

# Использование
for chunk in read_in_chunks("huge.bin"):
    process(chunk)
    # Только один chunk в памяти!
```

### Generator expressions

```python
# List comprehension — создаёт список в памяти
squares = [x**2 for x in range(1000000)]  # 1M элементов в RAM

# Generator expression — создаёт итератор
squares = (x**2 for x in range(1000000))  # Почти 0 RAM
for s in squares:
    print(s)

# Передача в функции
sum(x**2 for x in range(1000000))  # Эффективно
max(len(line) for line in open('file.txt'))  # Один проход
```

### Цепочки генераторов

```python
def read_lines(filename):
    """Генератор строк из файла."""
    with open(filename) as f:
        for line in f:
            yield line.rstrip('\n')

def filter_pattern(lines, pattern):
    """Фильтрует строки по паттерну."""
    import re
    regex = re.compile(pattern)
    for line in lines:
        if regex.search(line):
            yield line

def extract_field(lines, index, delimiter='\t'):
    """Извлекает поле по индексу."""
    for line in lines:
        parts = line.split(delimiter)
        if len(parts) > index:
            yield parts[index]

# Цепочка — как pipe в shell!
lines = read_lines('access.log')
errors = filter_pattern(lines, r'ERROR')
timestamps = extract_field(errors, 0)

for ts in timestamps:
    print(ts)
# Файл читается по одной строке, все операции ленивые
```

### itertools — инструменты для итераторов

```python
import itertools

# Бесконечные итераторы
itertools.count(10)         # 10, 11, 12, ...
itertools.cycle([1, 2, 3])  # 1, 2, 3, 1, 2, 3, ...
itertools.repeat('x', 5)    # 'x', 'x', 'x', 'x', 'x'

# Комбинаторика
itertools.chain(iter1, iter2)     # Последовательно
itertools.islice(iter, 10)        # Первые 10 элементов
itertools.takewhile(pred, iter)   # Пока pred() True
itertools.dropwhile(pred, iter)   # Пропустить пока pred() True
itertools.filterfalse(pred, iter) # Противоположность filter

# Группировка
for key, group in itertools.groupby(sorted_data, key=lambda x: x[0]):
    print(key, list(group))

# Batch processing
def batched(iterable, n):
    """Группирует элементы по n штук."""
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, n))
        if not batch:
            break
        yield batch

for batch in batched(range(25), 10):
    print(batch)  # [0-9], [10-19], [20-24]
```

### Обработка нескольких файлов

```python
import itertools
import glob

def process_many_files(pattern):
    """Обрабатывает множество файлов как один поток."""
    for filepath in glob.glob(pattern):
        with open(filepath) as f:
            for line in f:
                yield filepath, line

# Или через itertools.chain
def lines_from_files(filenames):
    """Объединяет содержимое файлов."""
    return itertools.chain.from_iterable(
        open(f) for f in filenames
    )

for line in lines_from_files(['a.txt', 'b.txt', 'c.txt']):
    print(line.strip())
```

### Контекст: contextlib

```python
from contextlib import contextmanager

@contextmanager
def open_with_encoding_detection(filename):
    """Открывает файл с автодетектом кодировки."""
    import chardet
    
    # Определяем кодировку
    with open(filename, 'rb') as f:
        raw = f.read(10000)
    encoding = chardet.detect(raw)['encoding']
    
    # Открываем с нужной кодировкой
    f = open(filename, encoding=encoding)
    try:
        yield f
    finally:
        f.close()

with open_with_encoding_detection('legacy.txt') as f:
    for line in f:
        print(line)
```

---

## 30.3 Bash: обработка потоков

### while read — построчное чтение

```bash
# Базовый паттерн
while IFS= read -r line; do
    echo "Processing: $line"
done < input.txt

# IFS=     — не обрезать пробелы
# -r       — не интерпретировать backslash
```

### Обработка последней строки без \n

```bash
# Проблема: read возвращает false при EOF без \n
$ printf "line1\nline2" | while read line; do echo "$line"; done
line1
# line2 потеряна!

# Решение
while IFS= read -r line || [[ -n "$line" ]]; do
    echo "$line"
done < file.txt
```

### Параллельная обработка

```bash
# xargs для параллельной обработки
$ find . -name "*.txt" | xargs -P 4 -I {} wc -l {}
#                             ^^^^
#                             4 параллельных процесса

# GNU Parallel (более мощный)
$ cat urls.txt | parallel -j 4 curl -O {}
```

---

## 30.4 Perl: однострочники и потоки

Perl — мощный язык для обработки текста, часто используемый в one-liners.

### Режимы работы

```bash
# -n : while (<>) { ... }
$ perl -ne 'print if /pattern/' file.txt

# -p : while (<>) { ... } continue { print }
$ perl -pe 's/old/new/g' file.txt

# -a : автоматический split (@F)
$ perl -ane 'print $F[0]' file.txt    # Первое поле

# -F : разделитель для -a
$ perl -F: -ane 'print $F[0]' /etc/passwd
```

### Практические примеры

```bash
# Замена (мощнее sed)
$ perl -pe 's/(\d+)/sprintf("%05d", $1)/ge' file.txt

# Сумма столбца
$ perl -ane '$sum += $F[0]; END { print $sum }' numbers.txt

# Уникальные строки (без сортировки!)
$ perl -ne 'print unless $seen{$_}++' file.txt

# Между маркерами
$ perl -ne 'print if /START/.../END/' file.txt

# In-place редактирование с бэкапом
$ perl -i.bak -pe 's/old/new/g' file.txt
```

---

## 30.5 Ruby: элегантная обработка

```ruby
# Построчная обработка
ARGF.each_line do |line|
  puts line.upcase
end

# Чтение чанками
File.open('huge.bin', 'rb') do |f|
  while chunk = f.read(8192)
    process(chunk)
  end
end

# Enumerator — ленивые итераторы
File.open('huge.txt')
    .each_line
    .lazy
    .map(&:strip)
    .select { |line| line.include?('ERROR') }
    .first(10)
    .each { |line| puts line }
```

### One-liners

```bash
# Ruby как замена awk
$ ruby -ane 'puts $F[0]' file.txt
$ ruby -ne 'print if /pattern/' file.txt
$ ruby -pe 'gsub(/old/, "new")' file.txt
```

---

## 30.6 JavaScript/Node.js: потоки

```javascript
const fs = require('fs');
const readline = require('readline');

// Построчное чтение
const rl = readline.createInterface({
    input: fs.createReadStream('huge.log'),
    crlfDelay: Infinity
});

rl.on('line', (line) => {
    if (line.includes('ERROR')) {
        console.log(line);
    }
});
```

### Async iterators (ES2018+)

```javascript
async function* readLines(filename) {
    const rl = readline.createInterface({
        input: fs.createReadStream(filename),
        crlfDelay: Infinity
    });
    
    for await (const line of rl) {
        yield line;
    }
}

// Использование
for await (const line of readLines('huge.log')) {
    if (line.includes('ERROR')) {
        console.log(line);
    }
}
```

---

## 30.7 Go: эффективная потоковая обработка

```go
package main

import (
    "bufio"
    "fmt"
    "os"
    "strings"
)

func main() {
    // Построчное чтение из stdin
    scanner := bufio.NewScanner(os.Stdin)
    for scanner.Scan() {
        line := scanner.Text()
        fmt.Println(strings.ToUpper(line))
    }
    
    if err := scanner.Err(); err != nil {
        fmt.Fprintln(os.Stderr, "error:", err)
    }
}
```

---

## 30.8 Сравнение подходов

| Язык | Скорость | Память | Use case |
|------|----------|--------|----------|
| **awk** | Очень быстро | Мало | Простые преобразования |
| **Perl** | Быстро | Умеренно | Сложные regex |
| **Python** | Умеренно | Умеренно | Читаемость, библиотеки |
| **Go** | Очень быстро | Мало | Производительность |
| **Ruby** | Умеренно | Умеренно | Выразительность |

---

## 30.9 Best practices

### Не загружать всё в память

```python
# ПЛОХО
lines = open('huge.log').readlines()

# ХОРОШО  
for line in open('huge.log'):
    ...
```

### Использовать генераторы

```python
# ПЛОХО
def get_errors(filename):
    result = []
    for line in open(filename):
        if 'ERROR' in line:
            result.append(line)
    return result

# ХОРОШО
def get_errors(filename):
    for line in open(filename):
        if 'ERROR' in line:
            yield line
```

### Обрабатывать SIGPIPE

```python
import signal
import sys

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

for line in sys.stdin:
    print(line.upper(), end='')
```

### Указывать кодировку явно

```python
with open('file.txt', encoding='utf-8') as f:
    for line in f:
        ...
```

---

## Резюме

### Ключевые концепции

| Концепция | Описание |
|-----------|----------|
| **Iterator** | Объект, генерирующий элементы по запросу |
| **Generator** | Функция с `yield`, создающая итератор |
| **Lazy evaluation** | Вычисление только при необходимости |
| **Chunked reading** | Чтение файла частями |


??? question "Упражнения"
    **Задание 1.** Напишите Python-генератор, который построчно читает файл 1 ГБ и считает строки, содержащие слово "error". Замерьте потребление памяти через `tracemalloc`.
    
    **Задание 2.** Реализуйте `head -n 10` на Python тремя способами: через `readlines()`, через `islice(file, 10)`, через `enumerate + break`. Какой способ эффективнее для больших файлов?
    
    **Задание 3.** Реализуйте pipeline `cat file | grep pattern | wc -l` как цепочку Python-генераторов (без subprocess).

!!! tip "Следующая глава"
    Изучили итераторы и генераторы в разных языках. Теперь глубоко погрузимся в **Python** — самый популярный язык для обработки данных → [Python: глубокое погружение](31-python-deep.md)
