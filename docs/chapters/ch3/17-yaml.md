---
title: YAML — полное руководство по формату
description: Синтаксис YAML, типы данных, anchors и aliases. Примеры для Kubernetes, Docker Compose, GitHub Actions. Сравнение с JSON и TOML.
---

# Глава 17. YAML: Yet Another Markup Language

## Введение

**YAML** (YAML Ain't Markup Language) — формат сериализации данных, ориентированный на читаемость человеком. Широко используется для конфигурационных файлов (Kubernetes, Docker Compose, Ansible, GitHub Actions).

---

## 17.1 Синтаксис YAML

### Базовые типы

```yaml
# Строки
name: Alice
quoted: "Hello, World"
single_quoted: 'Don''t escape'
multiline: |
  This is a
  multiline string
folded: >
  This will be
  folded into one line

# Числа
integer: 42
float: 3.14159
scientific: 1.0e+6
hex: 0xFF
octal: 0o755

# Булевы значения
active: true
disabled: false
yes_value: yes    # Осторожно: yes/no → true/false
no_value: no

# Null
empty: null
also_null: ~
implicit_null:

# Дата и время
date: 2024-01-15
datetime: 2024-01-15T10:30:00Z
```

### Коллекции

```yaml
# Список (массив)
fruits:
  - apple
  - banana
  - cherry

# Inline список
colors: [red, green, blue]

# Словарь (объект)
person:
  name: Alice
  age: 30
  city: Moscow

# Inline словарь
point: {x: 10, y: 20}

# Вложенные структуры
users:
  - name: Alice
    email: alice@example.com
    roles:
      - admin
      - user
  - name: Bob
    email: bob@example.com
    roles:
      - user
```

---

## 17.2 Особенности YAML

### Отступы имеют значение

```yaml
# Это вложенный объект
parent:
  child: value

# Это ДВА ключа на одном уровне (ОШИБКА)
parent:
child: value  # child не является дочерним для parent
```

### Якоря и алиасы

```yaml
# Определение якоря
defaults: &defaults
  adapter: postgres
  host: localhost
  port: 5432

# Использование алиаса
development:
  <<: *defaults
  database: dev_db

production:
  <<: *defaults
  host: prod-server.com
  database: prod_db

# Результат для development:
# adapter: postgres
# host: localhost
# port: 5432
# database: dev_db
```

### Многодокументные файлы

```yaml
---
# Документ 1
name: first
value: 1
---
# Документ 2
name: second
value: 2
...
```

### Явные типы

```yaml
# Принудительное приведение типов
explicit_string: !!str 123
explicit_int: !!int "456"
explicit_float: !!float "3.14"
explicit_bool: !!bool "yes"
```

---

## 17.3 Подводные камни YAML

### Проблема "Norway"

```yaml
# Эти значения интерпретируются как boolean!
country: NO      # → false (не "NO")
answer: yes      # → true
enabled: on      # → true
disabled: off    # → false

# Решение: кавычки
country: "NO"
answer: "yes"
```

### Неочевидные строки

```yaml
# Это число с плавающей точкой, не версия!
version: 1.10    # → 1.1

# Решение
version: "1.10"

# Это время, не строка!
time: 12:30      # → 45000 (секунды!)

# Решение
time: "12:30"
```

### Безопасность

```yaml
# Потенциально опасный YAML (Python yaml.load)
!!python/object/apply:os.system
  args: ['rm -rf /']
```

!!! danger "Используйте safe_load!"
    Всегда используйте `yaml.safe_load()` вместо `yaml.load()` для недоверенных данных.

---

## 17.4 YAML в Python

### Библиотека PyYAML

```python
import yaml

# Чтение YAML
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Запись YAML
data = {'name': 'Alice', 'scores': [95, 87, 92]}

with open('output.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
```

### Многодокументные файлы

```python
# Чтение всех документов
with open('multi.yaml', 'r') as f:
    documents = list(yaml.safe_load_all(f))

# Запись нескольких документов
docs = [{'name': 'first'}, {'name': 'second'}]
with open('multi.yaml', 'w') as f:
    yaml.dump_all(docs, f)
```

### Кастомные типы

```python
from datetime import datetime
import yaml

# Представитель для datetime
def datetime_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:timestamp', 
                                   data.isoformat())

yaml.add_representer(datetime, datetime_representer)

data = {'created': datetime.now()}
print(yaml.dump(data))
```

---

## 17.5 YAML vs JSON

| Характеристика | YAML | JSON |
|----------------|------|------|
| Читаемость | Высокая | Средняя |
| Комментарии | Да (`#`) | Нет |
| Многострочные строки | Да | Нет (только `\n`) |
| Типы данных | Расширенные | Базовые (6) |
| Безопасность | Требует осторожности | Безопасен |
| Парсинг | Медленнее | Быстрее |
| Совместимость | JSON — подмножество YAML | — |

```yaml
# Любой JSON — валидный YAML
{"name": "Alice", "age": 30}
```

Но **не наоборот!** Многие возможности YAML не имеют аналогов в JSON:

```yaml
# Это валидный YAML, но НЕ валидный JSON:

# 1. Комментарии (в JSON их нет)
name: Alice  # имя пользователя

# 2. Якоря и ссылки (нет в JSON)
defaults: &defaults
  timeout: 30
  retries: 3
production:
  <<: *defaults
  timeout: 60

# 3. Многострочные строки (в JSON только \n)
description: |
  Это многострочный
  текст с переносами.

# 4. Необычные типы (в JSON только 6 базовых)
date: 2026-02-14
empty: ~
```

```bash
# Проверьте сами: конвертируйте YAML в JSON и обратно
$ yq -o=json '.' config.yaml    # YAML → JSON (комментарии и якоря теряются!)
$ cat data.json | yq -P '.'     # JSON → YAML (всегда работает)
```

---

## 17.6 Инструменты командной строки

### yq — jq для YAML

```bash
# Чтение поля
yq '.name' config.yaml

# Изменение значения
yq '.version = "2.0"' config.yaml

# Конвертация YAML → JSON
yq -o=json '.' config.yaml

# Конвертация JSON → YAML
cat data.json | yq -P '.'
```

### Валидация

```bash
# Проверка синтаксиса
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# yamllint
yamllint config.yaml
```

---

## Резюме

| Характеристика | Значение |
|----------------|----------|
| Расширение | `.yaml`, `.yml` |
| MIME-тип | `application/yaml` |
| Кодировка | UTF-8 |
| Комментарии | Да (`#`) |
| Применение | Конфигурации, DevOps, IaC |


??? question "Упражнения"
    **Задание 1.** Создайте YAML-файл с якорями и алиасами (`&` и `*`). Загрузите в Python через `yaml.safe_load()` и убедитесь, что ссылки разрешились.
    
    **Задание 2.** Продемонстрируйте «Norway problem»: значение `NO` может интерпретироваться как boolean `false`. Как это предотвратить?
    
    **Задание 3.** Конвертируйте JSON-файл в YAML и обратно через CLI (`yq`) или Python. Убедитесь, что данные не потерялись.

!!! tip "Следующая глава"
    Разобрались с YAML. Теперь — **конфигурационные форматы** TOML и INI → [TOML и INI](18-toml-ini.md)
