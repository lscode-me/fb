# Глава 5. Файловые операции

## Введение

Мы изучили структуру файловой системы: inode, директории, ссылки. Теперь разберём **базовые операции** с файлами — как они работают на уровне ФС и какие команды их выполняют.

!!! note "Ключевое понимание"
    Файловые операции — это манипуляции с **inode** и **записями в директориях** (directory entries). Понимание этого объясняет многие "странности" поведения команд.

---

## 5.1 Создание файлов и директорий

### touch — создание файла или обновление времени

```bash
# Создать пустой файл (или обновить mtime существующего)
$ touch newfile.txt

# Создать несколько файлов
$ touch file1.txt file2.txt file3.txt

# Только обновить время доступа (atime)
$ touch -a file.txt

# Только обновить время модификации (mtime)
$ touch -m file.txt

# Установить конкретное время
$ touch -t 202602061200.00 file.txt    # YYYYMMDDhhmm.ss
$ touch -d "2026-02-06 12:00:00" file.txt
```

**Что происходит на уровне ФС:**

```
touch newfile.txt:
1. Если файл не существует:
   - Создаётся новый inode
   - В текущей директории добавляется запись (name → inode)
2. Если файл существует:
   - Обновляются timestamps в inode
```

### mkdir — создание директории

```bash
# Создать директорию
$ mkdir mydir

# Создать вложенные директории (родительские создаются автоматически)
$ mkdir -p path/to/nested/directory

# Создать с определёнными правами
$ mkdir -m 755 mydir
```

**Что происходит на уровне ФС:**

```
mkdir mydir:
1. Создаётся новый inode типа "directory"
2. В родительской директории добавляется запись (mydir → new_inode)
3. В новой директории создаются записи:
   - "."  → new_inode (сама на себя)
   - ".." → parent_inode (на родителя)
4. Link count родительской директории увеличивается на 1
```

```bash
# Демонстрация link count
$ ls -ld parent/
drwxr-xr-x 2 user user 4096 Feb  6 10:00 parent/
           ^
           link count = 2 (. и запись в родителе)

$ mkdir parent/child

$ ls -ld parent/
drwxr-xr-x 3 user user 4096 Feb  6 10:01 parent/
           ^
           link count = 3 (добавился .. от child)
```

### rmdir — удаление пустой директории

```bash
# Удалить пустую директорию
$ rmdir emptydir

# Удалить вложенные пустые директории
$ rmdir -p path/to/empty/dirs
```

!!! warning "Только пустые директории"
    `rmdir` удаляет только **пустые** директории (содержащие только `.` и `..`).
    Для непустых используйте `rm -r`.

---

## 5.2 Копирование: cp

### Базовое использование

```bash
# Копировать файл
$ cp source.txt dest.txt

# Копировать в директорию
$ cp file.txt /path/to/directory/

# Копировать несколько файлов в директорию
$ cp file1.txt file2.txt /path/to/directory/

# Рекурсивное копирование директории
$ cp -r sourcedir/ destdir/
```

### Важные опции

```bash
# Сохранить атрибуты (права, владельца, timestamps)
$ cp -p file.txt copy.txt

# Сохранить всё (включая xattr, ACL)
$ cp -a sourcedir/ destdir/    # эквивалент -dR --preserve=all

# Интерактивный режим (спрашивать перед перезаписью)
$ cp -i file.txt existing.txt

# Не перезаписывать существующие
$ cp -n file.txt dest/

# Обновлять только если источник новее
$ cp -u file.txt dest/

# Показывать прогресс (verbose)
$ cp -v file.txt dest/
```

### Что происходит на уровне ФС

```
cp source.txt dest.txt:
1. Создаётся новый inode для dest.txt
2. Читаются данные из блоков source.txt
3. Данные записываются в новые блоки dest.txt
4. Метаданные копируются (если указаны опции -p/-a)
5. В директории создаётся запись dest.txt → new_inode

Результат: ДВА независимых файла с разными inode
```

```bash
# Проверка: разные inode
$ cp file.txt copy.txt
$ ls -li file.txt copy.txt
131074 -rw-r--r-- 1 user user 100 Feb  6 10:00 file.txt
131075 -rw-r--r-- 1 user user 100 Feb  6 10:01 copy.txt
^^^^^^                                        ^^^^^^^^
разные inode                                  разные файлы
```

### cp и ссылки

```bash
# По умолчанию cp следует за symlink (копирует содержимое)
$ ln -s original.txt link.txt
$ cp link.txt copy.txt
$ ls -l copy.txt
-rw-r--r-- 1 user user 100 Feb  6 10:00 copy.txt  # обычный файл!

# Скопировать сам symlink (не содержимое)
$ cp -P link.txt link_copy.txt
$ ls -l link_copy.txt
lrwxrwxrwx 1 user user 12 Feb  6 10:00 link_copy.txt -> original.txt

# При рекурсивном копировании: -a сохраняет symlinks
$ cp -a project/ backup/
```

### cp и hard links

```bash
# Создать hard link вместо копии (экономия места)
$ cp -l file.txt hardlink.txt

# Рекурсивно с hard links
$ cp -rl sourcedir/ destdir/
```

### cp и sparse files

```bash
# Sparse file — файл с "дырами" (нулевые блоки не занимают место)
$ truncate -s 1G sparse.img
$ ls -lh sparse.img
-rw-r--r-- 1 user user 1.0G Feb  6 10:00 sparse.img
$ du -h sparse.img
0       sparse.img    # Реально 0 байт на диске!

# cp по умолчанию может "развернуть" sparse file
$ cp sparse.img copy.img
$ du -h copy.img
1.0G    copy.img      # Теперь занимает 1 ГБ!

# Сохранить sparseness
$ cp --sparse=always sparse.img copy.img
$ du -h copy.img
0       copy.img      # Остался sparse
```

---

## 5.3 Перемещение и переименование: mv

### Базовое использование

```bash
# Переименовать файл
$ mv oldname.txt newname.txt

# Переместить в другую директорию
$ mv file.txt /path/to/directory/

# Переместить несколько файлов
$ mv file1.txt file2.txt /path/to/directory/

# Переименовать директорию
$ mv olddir/ newdir/
```

### Важные опции

```bash
# Интерактивный режим
$ mv -i file.txt existing.txt

# Не перезаписывать существующие
$ mv -n file.txt dest/

# Принудительно (без вопросов)
$ mv -f file.txt dest/

# Verbose
$ mv -v file.txt dest/
```

### Что происходит на уровне ФС

**Случай 1: Перемещение в пределах одной ФС (быстро!)**

```
mv /home/user/file.txt /home/user/docs/file.txt

1. В /home/user/docs добавляется запись file.txt → inode
2. Из /home/user удаляется запись file.txt
3. Данные НЕ копируются! inode остаётся тем же.

Это операция rename() — атомарная и мгновенная.
```

```bash
# Проверка: inode не меняется
$ ls -i file.txt
131074 file.txt

$ mv file.txt docs/

$ ls -i docs/file.txt
131074 docs/file.txt    # Тот же inode!
```

**Случай 2: Перемещение между разными ФС (медленно)**

```
mv /home/user/file.txt /mnt/usb/file.txt

1. Файл копируется (cp)
2. Оригинал удаляется (rm)
3. Это НЕ атомарная операция!

Если прервать посередине — файл может остаться в обоих местах
или потеряться.
```

!!! tip "Атомарность mv"
    В пределах одной ФС `mv` — **атомарная операция**. Это используется для безопасного обновления файлов:
    ```bash
    # Атомарное обновление конфига
    $ cp config.conf config.conf.new
    $ # ... редактируем config.conf.new ...
    $ mv config.conf.new config.conf   # Атомарная замена!
    ```

### mv и директории

```bash
# Переименование директории — мгновенное (в пределах ФС)
$ mv myproject/ project_v2/

# Перемещение директории между ФС — рекурсивное копирование + удаление
$ mv myproject/ /mnt/external/
```

---

## 5.4 Удаление: rm и unlink

### rm — удаление файлов

```bash
# Удалить файл
$ rm file.txt

# Удалить несколько файлов
$ rm file1.txt file2.txt file3.txt

# Интерактивный режим
$ rm -i file.txt

# Принудительно (без ошибок если файла нет)
$ rm -f file.txt

# Verbose
$ rm -v file.txt
```

### rm -r — рекурсивное удаление

```bash
# Удалить директорию со всем содержимым
$ rm -r mydir/

# Принудительно и рекурсивно (ОПАСНО!)
$ rm -rf mydir/
```

!!! danger "rm -rf"
    `rm -rf` — одна из самых опасных команд. Она:
    - Не спрашивает подтверждения
    - Не отправляет в корзину
    - Удаляет **безвозвратно**
    
    ```bash
    # НИКОГДА не делайте так:
    $ rm -rf /           # Удалит всю систему
    $ rm -rf ~           # Удалит домашнюю директорию
    $ rm -rf $UNDEFINED_VAR/*   # Если переменная пустая — удалит /*
    ```

### Что происходит на уровне ФС

```
rm file.txt:
1. Из директории удаляется запись file.txt
2. Link count inode уменьшается на 1
3. Если link count = 0 И файл не открыт:
   - inode помечается как свободный
   - Блоки данных помечаются как свободные
4. Если link count > 0:
   - Файл остаётся доступен по другим именам (hard links)
5. Если файл открыт процессом:
   - Файл удаляется из директории
   - Но inode и данные существуют, пока процесс не закроет файл
```

```bash
# Демонстрация: файл "удалён", но данные доступны
$ cat file.txt &    # Открыть файл в фоне
[1] 12345

$ rm file.txt       # Удалить файл
$ ls file.txt
ls: cannot access 'file.txt': No such file or directory

$ ls -l /proc/12345/fd/
lr-x------ 1 user user 64 Feb  6 10:00 3 -> '/home/user/file.txt (deleted)'
# Данные всё ещё доступны через /proc/PID/fd/3!
```

### unlink — низкоуровневое удаление

```bash
# unlink удаляет ровно одну запись в директории
$ unlink file.txt

# Отличие от rm:
# - unlink не работает с директориями
# - unlink не принимает опций
# - unlink — это прямой вызов syscall unlink()
```

```c
// Системный вызов
#include <unistd.h>

int unlink(const char *pathname);  // Удалить файл
int rmdir(const char *pathname);   // Удалить пустую директорию
```

---

## 5.5 Создание ссылок: ln

### Hard links

```bash
# Создать hard link
$ ln target.txt link.txt

# Проверить — тот же inode
$ ls -li target.txt link.txt
131074 -rw-r--r-- 2 user user 100 Feb  6 10:00 link.txt
131074 -rw-r--r-- 2 user user 100 Feb  6 10:00 target.txt
```

### Symbolic links

```bash
# Создать symlink
$ ln -s target.txt link.txt

# Symlink на директорию
$ ln -s /path/to/dir linkdir

# Принудительно перезаписать существующую ссылку
$ ln -sf new_target existing_link

# Относительный symlink
$ ln -s ../other/file.txt link.txt
```

### Подробнее о ссылках

!!! tip "Детальное изучение"
    Подробное описание hard links и symbolic links см. в предыдущей главе → [Ссылки](04-links.md)

---

## 5.6 Мультиплатформенность

=== "Linux"

    ```bash
    # GNU coreutils — стандартный набор
    $ cp --preserve=all src dst
    $ mv -v file.txt dest/
    $ rm -I *.txt    # Спросить один раз перед удалением многих файлов
    ```

=== "FreeBSD / OpenBSD"

    ```bash
    # BSD версии — немного другие опции
    $ cp -p src dst              # -p вместо --preserve
    $ rm -P file.txt             # Перезаписать перед удалением (безопасное удаление)
    
    # FreeBSD: флаги файлов
    $ chflags schg important.txt  # Сделать immutable
    $ rm important.txt
    rm: important.txt: Operation not permitted
    ```

=== "macOS"

    ```bash
    # BSD-based, но с расширениями
    $ cp -c file.txt copy.txt    # Использовать APFS clones (мгновенное копирование!)
    $ rm -P file.txt             # Secure delete
    
    # Работа с xattr при копировании
    $ cp -X file.txt copy.txt    # Не копировать extended attributes
    ```

=== "Windows (PowerShell)"

    ```powershell
    # PowerShell командлеты
    Copy-Item -Path src.txt -Destination dst.txt
    Move-Item -Path file.txt -Destination dest\
    Remove-Item -Path file.txt
    Remove-Item -Path dir\ -Recurse -Force
    
    # Создание ссылок
    New-Item -ItemType SymbolicLink -Path link.txt -Target target.txt
    New-Item -ItemType HardLink -Path hardlink.txt -Target target.txt
    ```

---

## 5.7 Атомарность и безопасность

### Атомарные операции

| Операция | Атомарная? | Примечание |
|----------|------------|------------|
| `mv` в пределах ФС | ✅ Да | Использует `rename()` |
| `mv` между ФС | ❌ Нет | `cp` + `rm` |
| `cp` | ❌ Нет | Может прерваться |
| `rm` | ✅ Да | Удаление одного файла |
| `ln` | ✅ Да | Создание ссылки |

### Паттерн безопасного обновления

```bash
# ❌ Плохо: прямая перезапись
$ echo "new content" > config.conf
# Если прервать — файл будет пустой или повреждённый

# ✅ Хорошо: атомарная замена
$ echo "new content" > config.conf.tmp
$ mv config.conf.tmp config.conf
# mv атомарен — либо старый файл, либо новый
```

### Python: атомарная запись

```python
import os
import tempfile

def atomic_write(path, content):
    """Атомарно записать содержимое в файл."""
    dir_name = os.path.dirname(path) or '.'
    
    # Создаём временный файл в той же директории
    fd, tmp_path = tempfile.mkstemp(dir=dir_name)
    try:
        os.write(fd, content.encode())
        os.fsync(fd)  # Убедиться, что данные на диске
        os.close(fd)
        os.rename(tmp_path, path)  # Атомарная замена
    except:
        os.unlink(tmp_path)
        raise
```

---

## 5.8 Практические рецепты

### Безопасное удаление с подтверждением

```bash
# Алиас для безопасного rm
alias rm='rm -i'

# Или использовать trash-cli (перемещает в корзину)
$ trash-put file.txt
$ trash-list
$ trash-restore
```

### Копирование с прогрессом

```bash
# rsync показывает прогресс
$ rsync -ah --progress source/ dest/

# pv для произвольных команд
$ pv largefile.iso > /dev/sdX
```

### Массовое переименование

```bash
# Переименовать *.txt в *.md
$ for f in *.txt; do mv "$f" "${f%.txt}.md"; done

# Или с помощью rename (perl-rename)
$ rename 's/\.txt$/.md/' *.txt

# mmv для паттернов
$ mmv '*.txt' '#1.md'
```

### Синхронизация директорий

```bash
# rsync — лучший инструмент
$ rsync -av --delete source/ dest/

# Только изменённые файлы
$ rsync -av --update source/ dest/
```

!!! info "rsync по сети"
    `rsync` также поддерживает синхронизацию между хостами через SSH или собственный протокол:
    ```bash
    $ rsync -avz source/ user@remote:/path/to/dest/
    ```
    Сетевая синхронизация — отдельная большая тема, выходящая за рамки этой книги.

### Быстрое удаление директории с множеством файлов

```bash
# rm -rf может быть ОЧЕНЬ медленным для миллионов файлов
$ time rm -rf huge_directory/
# ... минуты или часы ...

# rsync с пустой директорией — значительно быстрее!
$ mkdir /tmp/empty
$ rsync -a --delete /tmp/empty/ huge_directory/
$ rmdir huge_directory

# Почему быстрее?
# - rsync использует более эффективные системные вызовы
# - Меньше операций с метаданными директорий
# - Оптимизирован для работы с большим количеством файлов
```

!!! tip "Когда использовать rsync --delete"
    Если в директории **миллионы мелких файлов** (node_modules, кэши, временные файлы), 
    `rsync` с пустой директорией может быть заметно быстрее, чем `rm -rf` — в некоторых случаях в 2-5 раз.
    Разница зависит от файловой системы и характера данных. Основное преимущество `rsync` —
    более эффективная работа с метаданными директорий (меньше операций `stat` при обходе дерева).

---

## Резюме

| Команда | Действие | На уровне ФС |
|---------|----------|--------------|
| `touch` | Создать файл / обновить время | Создать inode + dentry |
| `mkdir` | Создать директорию | Создать inode (dir) + записи `.`, `..` |
| `cp` | Копировать | Новый inode + копия данных |
| `mv` (same FS) | Переместить | Изменить dentry (атомарно) |
| `mv` (cross FS) | Переместить | `cp` + `rm` (не атомарно) |
| `rm` | Удалить | Удалить dentry, уменьшить link count |
| `ln` | Hard link | Добавить dentry к существующему inode |
| `ln -s` | Symlink | Новый inode типа symlink |

!!! tip "Ключевые идеи"
    - `mv` в пределах ФС — **мгновенный** и **атомарный** (только изменение записи в директории)
    - `cp` создаёт **новый inode** — это независимый файл
    - `rm` удаляет **запись в директории**, не обязательно данные (если есть hard links)
    - Используйте **атомарную замену** (`mv`) для безопасного обновления файлов


??? question "Упражнения"
    **Задание 1.** Реализуйте «безопасное обновление» файла на Python: запишите данные во временный файл, затем атомарно переименуйте его (`os.replace()`).
    
    **Задание 2.** Сравните скорость копирования одного файла 100 МБ vs 10 000 файлов по 10 КБ (суммарно тоже 100 МБ). Используйте `time cp -r`. Объясните разницу.
    
    **Задание 3.** Напишите Python-скрипт, который находит и удаляет все файлы `.pyc` в проекте, используя `pathlib.Path.rglob()`.

!!! tip "Следующая глава"
    Файлы созданы и перемещены. Теперь разберёмся, **кто может их читать и изменять** → [Права доступа](06-permissions.md)
