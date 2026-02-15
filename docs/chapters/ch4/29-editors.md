# Глава 29. Редакторы и просмотрщики файлов

## Введение

До сих пор мы работали с файлами через потоки и конвейеры. Но часто нужен интерактивный доступ: просмотреть длинный файл, отредактировать конфигурацию, изучить бинарник. В этой главе — инструменты для такой работы.

---

## 29.1 Просмотрщики: less, more, view

### less — универсальный просмотрщик

`less` — стандарт для просмотра файлов в терминале. Название — игра слов: "less is more".

```bash
$ less file.txt
$ command | less           # Просмотр вывода команды
$ less -N file.txt         # С номерами строк
$ less -S file.txt         # Не переносить длинные строки
$ less +G file.txt         # Начать с конца файла
$ less +/pattern file.txt  # Начать с первого совпадения
```

**Навигация в less:**

| Клавиша | Действие |
|---------|----------|
| `Space`, `f` | Страница вперёд |
| `b` | Страница назад |
| `g` | В начало файла |
| `G` | В конец файла |
| `j`, `↓` | Строка вниз |
| `k`, `↑` | Строка вверх |
| `/pattern` | Поиск вперёд |
| `?pattern` | Поиск назад |
| `n` | Следующее совпадение |
| `N` | Предыдущее совпадение |
| `q` | Выход |
| `h` | Справка |

**Расширенные возможности:**

```bash
# Следить за файлом (как tail -f)
$ less +F /var/log/syslog
# Ctrl+C — приостановить следование
# Shift+F — возобновить

# Открыть редактор на текущей позиции
# v — открывает $EDITOR

# Множественные файлы
$ less file1.txt file2.txt
# :n — следующий файл
# :p — предыдущий файл
```

### more — предшественник less

```bash
$ more file.txt
# Только вперёд, меньше возможностей
# Space — страница вперёд
# Enter — строка вперёд
# q — выход
```

### bat — modern cat с подсветкой

```bash
# Установка
$ brew install bat      # macOS
$ apt install bat       # Debian (может быть batcat)

# Использование
$ bat file.py           # С подсветкой синтаксиса
$ bat -n file.txt       # С номерами строк
$ bat -A file.txt       # Показать непечатаемые
$ bat --diff file.txt   # Подсветить git diff

# Как pager для man и git
$ export MANPAGER="sh -c 'col -bx | bat -l man -p'"
$ git config --global core.pager "bat"
```

---

## 29.2 Консольные текстовые редакторы

### nano — простой редактор

Идеален для начинающих и быстрых правок:

```bash
$ nano file.txt
$ nano +10 file.txt     # Открыть на строке 10
$ nano -B file.txt      # Создавать backup при сохранении
```

**Основные команды (Ctrl+):**

| Комбинация | Действие |
|------------|----------|
| `Ctrl+O` | Сохранить |
| `Ctrl+X` | Выйти |
| `Ctrl+K` | Вырезать строку |
| `Ctrl+U` | Вставить |
| `Ctrl+W` | Поиск |
| `Ctrl+\` | Поиск и замена |
| `Ctrl+G` | Справка |

### vim — мощный редактор

Vim (Vi IMproved) — выбор профессионалов. Крутая кривая обучения, но высокая эффективность.

!!! tip "vimtutor — лучшее начало"
    Запустите `vimtutor` в терминале — это встроенный интерактивный учебник (~30 минут).
    Он проведёт вас через основы навигации, редактирования и команд прямо в Vim.

```bash
$ vim file.txt
$ vim +10 file.txt      # Открыть на строке 10
$ vim +/pattern file.txt  # Открыть на первом совпадении
$ vim -R file.txt       # Только чтение (view)
$ vimdiff file1 file2   # Сравнение файлов
```

**Режимы vim:**

```
┌─────────────────────────────────────────────────────────────┐
│  NORMAL   ←──── ESC ←──── INSERT                            │
│     │                        ↑                              │
│     │                        │ i, a, o                      │
│     └───────────────────────→┘                              │
│                                                             │
│  NORMAL   ←──── ESC ←──── VISUAL (v, V, Ctrl+v)             │
│                                                             │
│  NORMAL   ←──── Enter ←── COMMAND (:)                       │
└─────────────────────────────────────────────────────────────┘
```

**Минимум для выживания:**

| Клавиша | Режим | Действие |
|---------|-------|----------|
| `i` | Normal→Insert | Режим вставки |
| `Esc` | →Normal | Выход в нормальный режим |
| `:w` | Command | Сохранить |
| `:q` | Command | Выйти |
| `:wq` | Command | Сохранить и выйти |
| `:q!` | Command | Выйти без сохранения |
| `dd` | Normal | Удалить строку |
| `yy` | Normal | Копировать строку |
| `p` | Normal | Вставить |
| `u` | Normal | Отменить |
| `/pattern` | Normal | Поиск |

**Продвинутые возможности:**

```vim
# Навигация
gg      " В начало файла
G       " В конец файла
:10     " На строку 10
w       " Слово вперёд
b       " Слово назад
0       " В начало строки
$       " В конец строки

# Редактирование
ciw     " Change Inner Word — заменить слово
di"     " Delete Inner " — удалить содержимое кавычек
ya{     " Yank (copy) around { — скопировать блок

# Поиск и замена
:%s/old/new/g     " Заменить везде
:%s/old/new/gc    " С подтверждением
:10,20s/old/new/g " В строках 10-20

# Множественные файлы
:e file2.txt      " Открыть файл
:bn               " Следующий буфер
:bp               " Предыдущий буфер
:split            " Горизонтальный сплит
:vsplit           " Вертикальный сплит
Ctrl+w w          " Переключение между окнами
```

### neovim — современный vim

```bash
$ brew install neovim
$ nvim file.txt

# Совместим с vim, но:
# + Lua scripting
# + Встроенный LSP
# + Асинхронные плагины
# + Лучшая производительность
```

### micro — современный nano

```bash
$ brew install micro
$ micro file.txt

# Привычные сочетания (Ctrl+S, Ctrl+C, Ctrl+V)
# Мышь работает из коробки
# Подсветка синтаксиса
```

---

## 29.3 Hex-редакторы

Для работы с бинарными файлами нужны специальные инструменты.

### xxd + vim

```bash
# Открыть файл как hex в vim
$ vim file.bin
:% !xxd          # Преобразовать в hex
# ... редактируем ...
:% !xxd -r       # Преобразовать обратно
:w               # Сохранить
```

### hexedit

```bash
$ brew install hexedit
$ hexedit file.bin

# Tab — переключение hex/ASCII
# Ctrl+X — сохранить и выйти
# Ctrl+C — выйти без сохранения
```

### hexyl — hex viewer с подсветкой

```bash
$ brew install hexyl
$ hexyl file.bin
$ hexyl -n 256 file.bin   # Первые 256 байт
$ hexyl --skip 1024 file  # Пропустить 1KB
```

### ImHex — GUI hex editor

Современный кроссплатформенный hex-редактор с:
- Шаблоны для разбора форматов
- Визуализация структур
- Сравнение файлов
- Pattern matching

---

## 29.4 Специализированные просмотрщики

### jq — JSON viewer/processor

```bash
$ brew install jq

# Красивый вывод
$ cat data.json | jq '.'

# Извлечение полей
$ cat data.json | jq '.name'
$ cat data.json | jq '.users[0].email'

# Фильтрация
$ cat data.json | jq '.users[] | select(.age > 30)'

# Преобразование
$ cat data.json | jq '[.users[] | {name, email}]'
```

### yq — YAML processor

```bash
$ brew install yq

$ cat config.yaml | yq '.services'
$ yq -i '.version = "2.0"' config.yaml  # Редактирование на месте
```

### xsv — CSV toolkit

```bash
$ brew install xsv

$ xsv headers data.csv          # Показать заголовки
$ xsv select name,age data.csv  # Выбрать столбцы
$ xsv search "pattern" data.csv # Поиск
$ xsv stats data.csv            # Статистика
$ xsv sort -s age data.csv      # Сортировка
```

### visidata — TUI для табличных данных

```bash
$ brew install visidata
$ vd data.csv
$ vd data.json
$ vd data.sqlite

# Интерактивный анализ, сортировка, фильтрация
# Frequency tables, pivot, join
```

---

## 29.5 Редакторы в IDE и GUI

### VS Code из командной строки

```bash
# Установить code в PATH: Cmd+Shift+P → "Shell Command"
$ code file.txt
$ code .                    # Открыть папку
$ code --diff file1 file2   # Сравнение
$ code -r file.txt          # В существующем окне
```

### Sublime Text

```bash
$ brew install --cask sublime-text
$ subl file.txt
$ subl .
```

### Другие редакторы

```bash
# Открыть в системном редакторе по умолчанию
$ open file.txt           # macOS
$ xdg-open file.txt       # Linux

# EDITOR и VISUAL
$ export EDITOR=vim
$ export VISUAL=code
$ git commit              # Использует $EDITOR
```

---

## 29.6 Просмотр специальных файлов

### PDF

```bash
# macOS
$ open file.pdf

# Linux
$ evince file.pdf
$ xdg-open file.pdf

# В терминале (текст)
$ pdftotext file.pdf -
$ pdftotext file.pdf - | less
```

### Изображения

```bash
# macOS Quick Look
$ qlmanage -p image.png

# В терминале (ASCII art)
$ brew install chafa
$ chafa image.png

# Или catimg
$ brew install catimg
$ catimg image.png
```

### Архивы

```bash
# Просмотр содержимого без распаковки
$ tar -tvf archive.tar.gz
$ unzip -l archive.zip
$ 7z l archive.7z

# Чтение файла из архива
$ tar -xOf archive.tar.gz path/to/file.txt | less
$ unzip -p archive.zip file.txt | less
```

### SQLite

```bash
$ sqlite3 database.db
sqlite> .tables
sqlite> .schema users
sqlite> SELECT * FROM users LIMIT 10;
sqlite> .quit

# Или через datasette (web UI)
$ pip install datasette
$ datasette database.db
```

---

## Резюме

### Выбор инструмента

| Задача | Инструмент |
|--------|-----------|
| Просмотр текста | `less`, `bat` |
| Быстрая правка | `nano`, `micro` |
| Мощное редактирование | `vim`, `neovim` |
| Бинарные файлы | `hexedit`, `xxd`, `ImHex` |
| JSON | `jq`, VS Code |
| CSV | `xsv`, `visidata`, `mlr` |
| YAML | `yq` |

### Настройка окружения

```bash
# ~/.bashrc или ~/.zshrc

# Редактор по умолчанию
export EDITOR=vim
export VISUAL=code

# Pager
export PAGER=less
export LESS='-R -S -M +Gg'   # Цвета, без переноса, статусная строка

# Алиасы
alias v='vim'
alias n='nano'
alias l='less'
alias cat='bat --paging=never'  # Заменить cat на bat
```


??? question "Упражнения"
    **Задание 1.** В `vim` выполните поиск и замену по всему файлу: `:%s/old/new/g`. Научитесь отменять (`u`) и повторять (`.`) действия.
    
    **Задание 2.** Исследуйте бинарный файл через `xxd file | less`. Найдите magic number и строковые константы. Попробуйте `strings file` для сравнения.
    
    **Задание 3.** Используйте `bat` для просмотра файла с подсветкой синтаксиса. Сравните с `cat` и `less` — в каких сценариях какой инструмент удобнее?

!!! tip "Следующая глава"
    Изучили инструменты просмотра и редактирования. Теперь рассмотрим **языки программирования** и их средства для потоковой обработки → [Языки программирования](30-languages.md)
