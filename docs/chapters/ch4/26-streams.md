# Глава 26. Потоки данных: stdin, stdout и философия UNIX

## Введение

В UNIX всё — файл. Но есть особый вид «файлов», который не хранит данные, а **передаёт** их: это **потоки** (streams). Понимание потоков — ключ к эффективной работе в командной строке и написанию программ, которые легко комбинируются друг с другом.

```
┌─────────────┐    stdin     ┌─────────────┐    stdout    ┌─────────────┐
│  Источник   │ ───────────→ │  Программа  │ ───────────→ │   Приёмник  │
│  (файл,     │              │             │              │   (файл,    │
│   клав-ра)  │              │             │ ───stderr──→ │    экран)   │
└─────────────┘              └─────────────┘              └─────────────┘
```

---

## 26.1 Три стандартных потока

Каждый процесс в UNIX рождается с тремя открытыми потоками:

| Поток | Файловый дескриптор | Назначение | По умолчанию |
|-------|---------------------|------------|--------------|
| **stdin** | 0 | Стандартный ввод | Клавиатура |
| **stdout** | 1 | Стандартный вывод | Экран (терминал) |
| **stderr** | 2 | Стандартный поток ошибок | Экран (терминал) |

```bash
# Программа читает из stdin, пишет в stdout
$ cat
Hello          # ← ввод с клавиатуры (stdin)
Hello          # ← вывод на экран (stdout)
^D             # ← Ctrl+D = конец ввода (EOF)

# Ошибки идут в stderr
$ ls /nonexistent
ls: /nonexistent: No such file or directory   # ← stderr
```

### Почему три потока?

```
┌─────────────────────────────────────────────────────────────┐
│  Разделение stdout и stderr позволяет:                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Перенаправлять данные, не теряя сообщения об ошибках    │
│  2. Логировать ошибки отдельно от результатов               │
│  3. Показывать прогресс, не засоряя вывод данных            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

```bash
# Данные в файл, ошибки на экран
$ find / -name "*.conf" > configs.txt 2>&1
#                       ^^^^^^^^^^^^^
#                       stdout → файл, stderr → туда же

# Данные в файл, ошибки в другой файл
$ find / -name "*.conf" > configs.txt 2> errors.txt

# Данные в файл, ошибки подавлены
$ find / -name "*.conf" > configs.txt 2>/dev/null
```

---

## 26.2 Перенаправление потоков

### Базовый синтаксис

```bash
# Вывод (stdout) в файл
command > file          # Перезаписать файл
command >> file         # Дописать в конец файла

# Ввод (stdin) из файла
command < file          # Читать из файла

# Ошибки (stderr) в файл
command 2> file         # stderr в файл
command 2>> file        # stderr дописать

# Комбинации
command > out.txt 2> err.txt    # stdout и stderr раздельно
command > all.txt 2>&1          # stderr туда же, куда stdout
command &> all.txt              # То же самое (bash 4+)
```

### Порядок имеет значение!

```bash
# ПРАВИЛЬНО: сначала stdout в файл, потом stderr туда же
$ command > file 2>&1

# НЕПРАВИЛЬНО: stderr идёт в старый stdout (экран), потом stdout в файл
$ command 2>&1 > file
```

Почему? Перенаправления выполняются слева направо:

```
command 2>&1 > file

1. 2>&1  — stderr (fd 2) → туда, куда сейчас указывает stdout (fd 1) = экран
2. > file — stdout (fd 1) → файл

Результат: stderr на экране, stdout в файле (не то, что хотели!)
```

### Here Documents и Here Strings

```bash
# Here Document: многострочный ввод
$ cat << EOF
Строка 1
Строка 2
Переменная: $HOME
EOF

# Here String: однострочный ввод
$ cat <<< "Одна строка с $HOME"

# Here Document без интерполяции (кавычки вокруг маркера)
$ cat << 'EOF'
Переменная $HOME не раскроется
EOF
```

---

## 26.3 Дополнительные файловые дескрипторы

Помимо 0, 1, 2 можно открывать дополнительные дескрипторы (3-9 и выше):

```bash
# Открыть fd 3 для чтения из файла
exec 3< input.txt

# Открыть fd 4 для записи в файл
exec 4> output.txt

# Открыть fd 5 для чтения и записи
exec 5<> file.txt

# Использование
read line <&3          # Читать из fd 3
echo "data" >&4        # Писать в fd 4

# Закрыть дескрипторы
exec 3<&-
exec 4>&-
```

### Практический пример: сохранение и восстановление stdout

```bash
#!/bin/bash
# Сохраняем оригинальный stdout в fd 3
exec 3>&1

# Перенаправляем stdout в файл
exec 1> log.txt

echo "Это идёт в log.txt"

# Восстанавливаем stdout
exec 1>&3

# Закрываем fd 3
exec 3>&-

echo "А это снова на экран"
```

### Пример: чтение из двух файлов одновременно

```bash
#!/bin/bash
# Сравнение двух файлов построчно

exec 3< file1.txt
exec 4< file2.txt

while IFS= read -r line1 <&3 && IFS= read -r line2 <&4; do
    if [[ "$line1" != "$line2" ]]; then
        echo "Различие: '$line1' vs '$line2'"
    fi
done

exec 3<&-
exec 4<&-
```

### Файловые дескрипторы в /proc

```bash
# Посмотреть открытые дескрипторы процесса
$ ls -la /proc/$$/fd
lrwx------ 1 user user 64 Feb  5 12:00 0 -> /dev/pts/0
lrwx------ 1 user user 64 Feb  5 12:00 1 -> /dev/pts/0
lrwx------ 1 user user 64 Feb  5 12:00 2 -> /dev/pts/0
lr-x------ 1 user user 64 Feb  5 12:00 3 -> /home/user/input.txt

# $$ — PID текущего shell
```

---

## 26.4 Pipes: конвейеры

Pipe (`|`) — главное изобретение UNIX. Он соединяет stdout одной программы со stdin другой:

```bash
# Классический конвейер
$ cat file.txt | grep "pattern" | sort | uniq -c | head -10
#     ^              ^              ^        ^          ^
#     читает файл    фильтрует      сортирует считает   первые 10
```

### Как работает pipe

```
┌─────────┐ stdout  ┌──────────────┐  stdin  ┌─────────┐
│  cmd1   │ ──────→ │ буфер (64KB) │ ──────→ │  cmd2   │
└─────────┘         └──────────────┘         └─────────┘
     ↓                                            ↓
   stderr                                      stderr
   (экран)                                     (экран)
```

```bash
# Pipe НЕ захватывает stderr!
$ ls /nonexistent | cat
ls: /nonexistent: No such file or directory  # ← на экране
                                             # ← пустой вывод от cat

# Чтобы передать и stderr:
$ ls /nonexistent 2>&1 | cat

# Или в bash 4+:
$ ls /nonexistent |& cat
```

### Буфер pipe и блокировка

```bash
# Размер буфера pipe (обычно 64KB)
$ cat /proc/sys/fs/pipe-max-size
1048576

# Если буфер полон — пишущий процесс блокируется
# Если буфер пуст — читающий процесс блокируется
```

### SIGPIPE: сигнал сломанной трубы

Когда читающий процесс завершается раньше пишущего:

```bash
$ yes | head -3
y
y
y
# yes получает SIGPIPE и завершается
```

```python
# Python: обработка SIGPIPE
import signal
import sys

# Стандартный обработчик — выход с кодом 141 (128 + 13)
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# Теперь можно безопасно использовать в конвейере:
# python script.py | head -10
```

### Создание именованных каналов (FIFO)

```bash
# Создание именованного канала
$ mkfifo /tmp/mypipe

# Терминал 1: запись
$ echo "Hello from pipe" > /tmp/mypipe

# Терминал 2: чтение (разблокирует терминал 1)
$ cat /tmp/mypipe
Hello from pipe

# Удаление
$ rm /tmp/mypipe
```

---

## 26.5 Строка как единица обработки

**Важнейшая концепция:** В потоковой обработке UNIX базовая единица — **строка** (line), ограниченная символом новой строки.

### Что такое «строка»?

```
┌─────────────────────────────────────────────────────────────┐
│  Строка = последовательность байтов до символа новой строки │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Unix (LF):          данные\n                               │
│  Windows (CRLF):     данные\r\n                             │
│  Старый Mac (CR):    данные\r                               │
│                                                             │
│  Последняя строка файла может НЕ иметь \n на конце!         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Проблема последней строки

```bash
# Файл без \n в конце
$ printf "line1\nline2" > test.txt
$ wc -l test.txt
1 test.txt       # wc считает только ПОЛНЫЕ строки!

$ cat test.txt | while read line; do echo "[$line]"; done
[line1]          # line2 потеряна!

# Решение: read возвращает данные даже без \n
$ cat test.txt | while IFS= read -r line || [[ -n "$line" ]]; do
    echo "[$line]"
done
[line1]
[line2]          # Теперь обе строки
```

### Нулевой разделитель (\0) для безопасности

Имена файлов могут содержать `\n`! Безопасная обработка:

```bash
# ОПАСНО: имена с \n сломают обработку
$ find . -name "*.txt" | while read f; do echo "$f"; done

# БЕЗОПАСНО: используем \0 как разделитель
$ find . -name "*.txt" -print0 | while IFS= read -r -d '' f; do
    echo "Файл: $f"
done

# Или с xargs
$ find . -name "*.txt" -print0 | xargs -0 ls -la
```

### Потоковая vs построчная обработка

```bash
# Построчная: буферизация до \n
$ tail -f log.txt | grep --line-buffered "ERROR"

# Побайтовая: без буферизации
$ tail -f log.txt | stdbuf -oL grep "ERROR"

# stdbuf управляет буферизацией:
#   -i = stdin, -o = stdout, -e = stderr
#   L = line-buffered, 0 = unbuffered
```

---

## 26.6 Процесс-подстановка (Process Substitution)

Bash позволяет использовать вывод команды как «файл»:

```bash
# <(command) — stdout команды как файл для чтения
$ diff <(sort file1.txt) <(sort file2.txt)

# >(command) — stdin команды как файл для записи  
$ tee >(gzip > archive.gz) >(wc -l > count.txt) < input.txt

# Что это на самом деле?
$ echo <(echo hello)
/dev/fd/63           # Это ссылка на файловый дескриптор!
```

### Практические примеры

```bash
# Сравнить отсортированные версии
$ diff <(sort a.txt) <(sort b.txt)

# Одновременно сжать и посчитать
$ cat huge.log | tee >(gzip > log.gz) | wc -l

# Обработать вывод двух команд
$ paste <(cut -f1 file.txt) <(cut -f2 file.txt | tr 'a-z' 'A-Z')

# Подставить результат в программу, ожидающую файл
$ wc -l <(find . -name "*.py")
```

---

## 26.7 Подстановка команд

```bash
# Старый синтаксис (обратные кавычки)
$ echo "Today is `date`"

# Современный синтаксис (рекомендуется)
$ echo "Today is $(date)"

# Вложенность
$ echo "Files: $(ls $(dirname $0))"

# В переменную
$ files=$(find . -name "*.txt")
```

### Разница с process substitution

```bash
# Command substitution: результат как СТРОКА
result=$(cat file.txt)
echo "$result"

# Process substitution: результат как ФАЙЛ
diff <(cat file1.txt) <(cat file2.txt)
```

---

## 26.8 Потоки в программировании

### C: stdio

```c
#include <stdio.h>

int main() {
    char buffer[1024];
    
    // stdin → stdout
    while (fgets(buffer, sizeof(buffer), stdin) != NULL) {
        fputs(buffer, stdout);
    }
    
    // stderr для ошибок
    fprintf(stderr, "Processed input\n");
    
    return 0;
}
```

### Python: sys.stdin/stdout

```python
import sys

# Построчное чтение stdin
for line in sys.stdin:
    # line включает \n
    processed = line.upper()
    sys.stdout.write(processed)
    
# Ошибки в stderr
print("Error occurred", file=sys.stderr)

# Бинарный режим
sys.stdin.buffer.read()    # bytes
sys.stdout.buffer.write(b'\x00\x01\x02')
```

### Буферизация в разных языках

!!! warning "Ловушка: Python в пайпах"
    По умолчанию Python использует **блочную буферизацию** для stdout когда он не подключён 
    к терминалу. Это означает, что в пайпах вывод появится только когда буфер заполнится 
    (обычно 4-8 КБ) или программа завершится.
    
    ```bash
    # Проблема: ничего не видно, пока script.py не завершится
    $ python script.py | tee log.txt
    
    # Решение 1: флаг -u (unbuffered)
    $ python -u script.py | tee log.txt
    
    # Решение 2: переменная окружения
    $ PYTHONUNBUFFERED=1 python script.py | tee log.txt
    ```

```python
# Python: управление буферизацией
import sys

# Способ 1: reconfigure для построчной буферизации
sys.stdout.reconfigure(line_buffering=True)

# Способ 2: flush=True в print()
print("Progress:", i, flush=True)

# Способ 3: явный flush
sys.stdout.write(f"Processing {i}\r")
sys.stdout.flush()

# Или через переменную окружения:
# PYTHONUNBUFFERED=1 python script.py
```

```bash
# Запуск с отключённой буферизацией
$ python -u script.py | grep pattern
$ stdbuf -oL python script.py | grep pattern

# stdbuf работает с любыми программами
$ stdbuf -oL long_running_command | tee output.log
```

!!! tip "Когда важна буферизация"
    - **Логирование в реальном времени**: `tail -f` + пайпы
    - **Прогресс-бары**: вывод `\r` без `flush` не виден
    - **Интерактивные пайплайны**: данные должны течь немедленно
    - **Отладка**: когда программа падает, буфер может не записаться

---

## 26.9 Специальные файлы-устройства

### /dev/null — чёрная дыра

```bash
# Подавить вывод
$ command > /dev/null

# Подавить всё
$ command > /dev/null 2>&1

# Читать — получишь пустоту (EOF сразу)
$ cat /dev/null
```

### /dev/zero — бесконечные нули

```bash
# Создать файл из нулей
$ dd if=/dev/zero of=zeros.bin bs=1M count=100

# Заполнить диск нулями (осторожно!)
$ dd if=/dev/zero of=/dev/sdX
```

### /dev/random и /dev/urandom

```bash
# Криптографически стойкие случайные байты
$ head -c 32 /dev/random | xxd

# Псевдослучайные байты (быстрее)
$ head -c 32 /dev/urandom | xxd

# Сгенерировать пароль
$ head -c 16 /dev/urandom | base64
```

### /dev/stdin, /dev/stdout, /dev/stderr

```bash
# Символические ссылки на потоки текущего процесса
$ ls -la /dev/stdin /dev/stdout /dev/stderr
lrwxrwxrwx 1 root root 15 Feb  5 00:00 /dev/stderr -> /proc/self/fd/2
lrwxrwxrwx 1 root root 15 Feb  5 00:00 /dev/stdin -> /proc/self/fd/0
lrwxrwxrwx 1 root root 15 Feb  5 00:00 /dev/stdout -> /proc/self/fd/1

# Использование: когда программа ожидает имя файла
$ cat /dev/stdin      # Эквивалент cat -
$ echo "test" | program /dev/stdin
```

### /dev/tty — управляющий терминал

```bash
# Вывод на терминал, даже если stdout перенаправлен
$ echo "Пароль:" > /dev/tty
$ read -s password < /dev/tty
```

---

## Резюме

### Стандартные потоки

| Дескриптор | Имя | Назначение |
|------------|-----|------------|
| 0 | stdin | Ввод данных |
| 1 | stdout | Вывод результатов |
| 2 | stderr | Вывод ошибок и диагностики |
| 3-9 | — | Пользовательские дескрипторы |

### Операторы перенаправления

| Оператор | Значение |
|----------|----------|
| `>` | stdout в файл (перезаписать) |
| `>>` | stdout в файл (дописать) |
| `<` | stdin из файла |
| `2>` | stderr в файл |
| `2>&1` | stderr туда же, куда stdout |
| `&>` | stdout и stderr в файл (bash) |
| `\|` | pipe: stdout → stdin |
| `\|&` | pipe: stdout+stderr → stdin (bash) |
| `<()` | process substitution (чтение) |
| `>()` | process substitution (запись) |

### Ключевые концепции

| Концепция | Описание |
|-----------|----------|
| **Строка** | Базовая единица обработки: байты до `\n` |
| **EOF** | End of File: конец потока (Ctrl+D в терминале) |
| **SIGPIPE** | Сигнал при записи в закрытый pipe |
| **Буферизация** | Line-buffered vs full-buffered vs unbuffered |


??? question "Упражнения"
    **Задание 1.** Перенаправьте stderr и stdout в разные файлы: `cmd >out.log 2>err.log`. Затем объедините оба в один: `cmd >all.log 2>&1`. Проверьте содержимое.
    
    **Задание 2.** Создайте pipeline из 5+ команд для реальной задачи: найдите 10 самых больших файлов `.py` в проекте, отсортированных по размеру.
    
    **Задание 3.** Используйте process substitution: `diff <(sort file1) <(sort file2)`. Объясните, как это работает без временных файлов.

!!! tip "Следующая глава"
    Познакомились с потоками. Теперь изучим **coreutils** — программы для обработки байтов и текста → [Coreutils: обработка данных](27-coreutils.md)
