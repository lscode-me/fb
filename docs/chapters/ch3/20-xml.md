# Глава 20. XML: Extensible Markup Language

## Введение

**XML** (Extensible Markup Language) — универсальный язык разметки для хранения и передачи структурированных данных. Хотя JSON во многом вытеснил XML в веб-API, XML остаётся стандартом в корпоративных системах, документах (DOCX, SVG) и конфигурациях (Maven, Android).

---

## 20.1 Синтаксис XML

### Базовая структура

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
    <element attribute="value">Содержимое</element>
    <empty-element/>
    <!-- Комментарий -->
</root>
```

### Элементы и атрибуты

```xml
<book isbn="978-3-16-148410-0">
    <title>The Great Book</title>
    <author>John Doe</author>
    <price currency="USD">29.99</price>
    <chapters>
        <chapter number="1">Introduction</chapter>
        <chapter number="2">Getting Started</chapter>
    </chapters>
</book>
```

### Правила XML

1. **Один корневой элемент** — весь документ внутри одного элемента
2. **Закрытые теги** — `<tag></tag>` или `<tag/>`
3. **Регистрозависимость** — `<Tag>` ≠ `<tag>`
4. **Правильная вложенность** — `<a><b></b></a>`, не `<a><b></a></b>`
5. **Кавычки для атрибутов** — `attr="value"` или `attr='value'`

### Экранирование

```xml
<text>
    &lt;   <!-- < -->
    &gt;   <!-- > -->
    &amp;  <!-- & -->
    &quot; <!-- " -->
    &apos; <!-- ' -->
</text>

<!-- CDATA — без экранирования -->
<script>
<![CDATA[
    if (a < b && c > d) {
        console.log("OK");
    }
]]>
</script>
```

---

## 20.2 Пространства имён (Namespaces)

```xml
<?xml version="1.0"?>
<root xmlns:h="http://www.w3.org/TR/html4/"
      xmlns:f="http://example.com/furniture">
    
    <h:table>
        <h:tr>
            <h:td>Cell</h:td>
        </h:tr>
    </h:table>
    
    <f:table>
        <f:name>Coffee Table</f:name>
        <f:width>80</f:width>
    </f:table>
</root>
```

### Пространство имён по умолчанию

```xml
<html xmlns="http://www.w3.org/1999/xhtml">
    <body>
        <p>Все элементы в пространстве XHTML</p>
    </body>
</html>
```

---

## 20.3 DTD и XML Schema

### DTD (Document Type Definition)

```xml
<!DOCTYPE note [
    <!ELEMENT note (to, from, heading, body)>
    <!ELEMENT to (#PCDATA)>
    <!ELEMENT from (#PCDATA)>
    <!ELEMENT heading (#PCDATA)>
    <!ELEMENT body (#PCDATA)>
]>
<note>
    <to>Alice</to>
    <from>Bob</from>
    <heading>Reminder</heading>
    <body>Don't forget the meeting!</body>
</note>
```

### XML Schema (XSD)

```xml
<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="book">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="title" type="xs:string"/>
                <xs:element name="author" type="xs:string"/>
                <xs:element name="price" type="xs:decimal"/>
            </xs:sequence>
            <xs:attribute name="isbn" type="xs:string" use="required"/>
        </xs:complexType>
    </xs:element>
</xs:schema>
```

---

## 20.4 XPath — запросы к XML

XPath — язык для навигации по XML-документам:

```xml
<bookstore>
    <book category="fiction">
        <title>Harry Potter</title>
        <author>J.K. Rowling</author>
        <price>29.99</price>
    </book>
    <book category="tech">
        <title>Learning Python</title>
        <author>Mark Lutz</author>
        <price>49.99</price>
    </book>
</bookstore>
```

| XPath | Результат |
|-------|-----------|
| `/bookstore` | Корневой элемент |
| `//book` | Все элементы book |
| `//book/title` | Все title внутри book |
| `//book[@category='tech']` | book с атрибутом category="tech" |
| `//book[price>30]` | book с ценой > 30 |
| `//book[1]` | Первый book |
| `//book/title/text()` | Текстовое содержимое title |

---

## 20.5 XML в Python

### ElementTree (стандартная библиотека)

```python
import xml.etree.ElementTree as ET

# Парсинг из файла
tree = ET.parse('data.xml')
root = tree.getroot()

# Парсинг из строки
xml_string = '<root><item>value</item></root>'
root = ET.fromstring(xml_string)

# Навигация
for child in root:
    print(child.tag, child.attrib, child.text)

# Поиск элементов
for book in root.findall('book'):
    title = book.find('title').text
    price = float(book.find('price').text)
    print(f"{title}: ${price}")

# XPath (ограниченная поддержка)
for title in root.findall('.//title'):
    print(title.text)
```

### Создание XML

```python
import xml.etree.ElementTree as ET

root = ET.Element('bookstore')

book = ET.SubElement(root, 'book', category='tech')
title = ET.SubElement(book, 'title')
title.text = 'Learning Python'
price = ET.SubElement(book, 'price')
price.text = '49.99'

# Запись в файл
tree = ET.ElementTree(root)
ET.indent(tree, space='    ')  # Python 3.9+
tree.write('output.xml', encoding='utf-8', xml_declaration=True)
```

### lxml — расширенная библиотека

```python
from lxml import etree

# Парсинг с полной поддержкой XPath
tree = etree.parse('data.xml')

# XPath запросы
titles = tree.xpath('//book[@category="tech"]/title/text()')

# Валидация по XSD
schema = etree.XMLSchema(etree.parse('schema.xsd'))
is_valid = schema.validate(tree)

# XSLT трансформация
xslt = etree.parse('transform.xsl')
transform = etree.XSLT(xslt)
result = transform(tree)
```

---

## 20.6 XSLT — трансформация XML

XSLT преобразует XML в другие форматы:

```xml
<!-- transform.xsl -->
<?xml version="1.0"?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template match="/bookstore">
        <html>
            <body>
                <h1>Books</h1>
                <ul>
                    <xsl:for-each select="book">
                        <li>
                            <xsl:value-of select="title"/>
                            - $<xsl:value-of select="price"/>
                        </li>
                    </xsl:for-each>
                </ul>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
```

---

## 20.7 Инструменты командной строки

### xmllint

```bash
# Валидация
xmllint --noout data.xml

# Валидация по схеме
xmllint --schema schema.xsd data.xml

# Форматирование
xmllint --format data.xml

# XPath запрос
xmllint --xpath "//title/text()" data.xml
```

### xq (yq для XML)

```bash
# Извлечение данных
xq '.bookstore.book[0].title' data.xml

# Конвертация в JSON
xq '.' data.xml
```

### xsltproc — XSL-трансформации из командной строки

`xsltproc` — CLI-инструмент для применения XSLT-трансформаций к XML-документам:

```bash
# Установка
$ apt install xsltproc         # Debian/Ubuntu
$ brew install libxslt         # macOS (обычно уже есть)

# Применить трансформацию
$ xsltproc style.xsl data.xml > output.html

# С параметрами
$ xsltproc --param title "'My Title'" style.xsl data.xml

# В файл
$ xsltproc -o result.html style.xsl data.xml
```

!!! tip "xpath через xmllint"
    `xmllint --xpath` (cм. выше) — это самый простой способ выполнить XPath-запрос из shell.
    Для более сложных задач используйте `xsltproc` или Python-библиотеку `lxml`.

---

## 20.8 XML vs JSON

| Характеристика | XML | JSON |
|----------------|-----|------|
| Читаемость | Средняя | Высокая |
| Размер | Больше | Меньше |
| Комментарии | Да | Нет |
| Атрибуты | Да | Нет (только свойства) |
| Схемы | XSD, DTD | JSON Schema |
| Namespaces | Да | Нет |
| Смешанный контент | Да | Нет |
| Парсинг | Сложнее | Проще |

---

## 20.9 Подводные камни и edge cases

### XXE-атаки (XML External Entity)

!!! danger "Уязвимость"
    XML поддерживает внешние сущности (еntity), которые могут читать локальные файлы.

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<data>&xxe;</data>  <!-- вставит содержимое /etc/passwd! -->
```

```python
# ❗ Небезопасно: стандартный парсер может быть уязвим
from xml.etree.ElementTree import parse  # ❗

# ✅ Безопасно: defusedxml блокирует XXE
import defusedxml.ElementTree as ET
tree = ET.parse('data.xml')  # XXE заблокирована
```

### Billion Laughs (атака ‘биллион смехов’)

```xml
<!-- Экспоненциальное раскрытие — пожирает память -->
<!ENTITY lol "lol">
<!ENTITY lol2 "&lol;&lol;&lol;...">
```

### Кодировка

XML по умолчанию — UTF-8, но старые документы могут использовать другие. Всегда проверяйте `<?xml version="1.0" encoding="..."?>`.

---

## Резюме

| Характеристика | Значение |
|----------------|----------|
| Расширение | `.xml` |
| MIME-тип | `application/xml`, `text/xml` |
| Кодировка | UTF-8 (по умолчанию) |
| Комментарии | `<!-- комментарий -->` |
| Применение | Документы, конфигурации, SOAP, RSS, SVG |


??? question "Упражнения"
    **Задание 1.** Напишите XPath-запрос для извлечения всех заголовков из RSS-ленты (формат XML). Используйте `lxml.etree.parse()` и `.xpath()`.
    
    **Задание 2.** Создайте XML с namespace и прочитайте элементы через `ElementTree`. Что меняется при обращении к элементам с пространством имён?
    
    **Задание 3.** Конвертируйте XML в JSON (через `xmltodict`) и обратно. Какие данные теряются при конвертации? Атрибуты, порядок элементов?

!!! tip "Следующая глава"
    Завершили текстовые форматы. Перейдём к **бинарной сериализации** — Protobuf, MessagePack → [Бинарная сериализация](21-binary-serialization.md)
