# Глава 46. HTTP для работы с файлами

## Введение

**HTTP** (Hypertext Transfer Protocol) — основной протокол веба, который активно используется для передачи файлов. От простого скачивания до REST API и потокового видео — HTTP везде.

---

## 46.1 HTTP для передачи файлов

### Базовые методы

```
GET     — получить файл (скачивание)
POST    — отправить данные (upload форм)
PUT     — загрузить/заменить файл
DELETE  — удалить файл
HEAD    — получить метаданные без тела
```

### Заголовки для файлов

```http
# Запрос
GET /files/document.pdf HTTP/1.1
Host: example.com
Accept: application/pdf
Range: bytes=0-1023

# Ответ
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Length: 1048576
Content-Disposition: attachment; filename="document.pdf"
Accept-Ranges: bytes
ETag: "abc123"
Last-Modified: Wed, 15 Jan 2024 10:30:00 GMT
```

---

## 46.2 Скачивание файлов

### curl

```bash
# Простое скачивание
curl -O https://example.com/file.zip

# Сохранить с другим именем
curl -o myfile.zip https://example.com/file.zip

# Продолжить прерванное скачивание
curl -C - -O https://example.com/large.iso

# Скачать несколько файлов
curl -O https://example.com/file1.zip -O https://example.com/file2.zip

# Показать прогресс
curl --progress-bar -O https://example.com/file.zip

# Следовать редиректам
curl -L -O https://example.com/redirect-to-file

# С авторизацией
curl -u user:password -O https://example.com/protected/file.zip

# Bearer token
curl -H "Authorization: Bearer TOKEN" -O https://api.example.com/file
```

### wget

```bash
# Базовое скачивание
wget https://example.com/file.zip

# Продолжить прерванное
wget -c https://example.com/large.iso

# Рекурсивное скачивание сайта
wget -r -np -k https://example.com/docs/

# Скачать все PDF
wget -r -A "*.pdf" https://example.com/

# Фоновый режим
wget -b https://example.com/huge.iso

# Зеркалирование
wget --mirror --convert-links --page-requisites https://example.com/
```

### aria2 (многопоточные загрузки)

```bash
# Многопоточное скачивание
aria2c -x 16 https://example.com/large.iso

# Несколько источников
aria2c https://mirror1.com/file.iso https://mirror2.com/file.iso

# BitTorrent + HTTP
aria2c example.torrent

# Metalink
aria2c file.metalink
```

---

## 46.3 Range Requests (докачка)

### Запрос части файла

```bash
# Первые 1000 байт
curl -H "Range: bytes=0-999" https://example.com/file.zip

# С байта 1000 до конца
curl -H "Range: bytes=1000-" https://example.com/file.zip

# Последние 500 байт
curl -H "Range: bytes=-500" https://example.com/file.zip
```

### Проверка поддержки Range

```bash
# HEAD запрос
curl -I https://example.com/file.zip | grep -i accept-ranges

# Accept-Ranges: bytes  — поддерживается
# Accept-Ranges: none   — не поддерживается
```

### Параллельное скачивание

```bash
# Используя aria2
aria2c -x 8 -s 8 https://example.com/large.iso

# -x 8: макс. соединений на сервер
# -s 8: разделить на 8 частей
```

---

## 46.4 Загрузка файлов (Upload)

### POST multipart/form-data

```bash
# Загрузка файла
curl -F "file=@document.pdf" https://example.com/upload

# Несколько файлов
curl -F "file1=@doc1.pdf" -F "file2=@doc2.pdf" https://example.com/upload

# С дополнительными полями
curl -F "file=@photo.jpg" -F "title=My Photo" https://example.com/upload
```

### PUT (прямая загрузка)

```bash
# Загрузка с PUT
curl -X PUT -T file.txt https://example.com/files/file.txt

# С Content-Type
curl -X PUT -H "Content-Type: application/json" \
    -T data.json https://example.com/api/data.json

# Presigned URL (S3 стиль)
curl -X PUT -T file.zip "https://bucket.s3.amazonaws.com/path?signature=xxx"
```

### Chunked Upload

```bash
# Для больших файлов
curl -X POST \
    -H "Transfer-Encoding: chunked" \
    -H "Content-Type: application/octet-stream" \
    --data-binary @largefile.zip \
    https://example.com/upload
```

---

## 46.5 REST API для файлов

### Python requests

```python
import requests

# Скачивание
response = requests.get('https://example.com/file.zip')
with open('file.zip', 'wb') as f:
    f.write(response.content)

# Потоковое скачивание (для больших файлов)
with requests.get('https://example.com/large.iso', stream=True) as r:
    r.raise_for_status()
    with open('large.iso', 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

# Загрузка файла
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'https://example.com/upload',
        files={'file': ('document.pdf', f, 'application/pdf')}
    )

# С прогрессом (tqdm)
from tqdm import tqdm

response = requests.get(url, stream=True)
total = int(response.headers.get('content-length', 0))

with open('file.zip', 'wb') as f, tqdm(total=total, unit='B', unit_scale=True) as pbar:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
        pbar.update(len(chunk))
```

### httpx (async)

```python
import httpx
import asyncio

async def download_file(url, filename):
    async with httpx.AsyncClient() as client:
        async with client.stream('GET', url) as response:
            with open(filename, 'wb') as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)

asyncio.run(download_file('https://example.com/file.zip', 'file.zip'))
```

---

## 46.6 Content-Type и MIME

### Основные MIME типы для файлов

| MIME Type | Расширения |
|-----------|------------|
| text/plain | .txt |
| text/html | .html, .htm |
| text/css | .css |
| text/javascript | .js |
| application/json | .json |
| application/xml | .xml |
| application/pdf | .pdf |
| application/zip | .zip |
| application/gzip | .gz |
| image/jpeg | .jpg, .jpeg |
| image/png | .png |
| image/gif | .gif |
| image/webp | .webp |
| audio/mpeg | .mp3 |
| video/mp4 | .mp4 |
| application/octet-stream | Любой бинарный |

### Content-Disposition

```http
# Скачать как файл (не открывать в браузере)
Content-Disposition: attachment; filename="report.pdf"

# Показать inline (если возможно)
Content-Disposition: inline; filename="image.png"

# С кодировкой имени (UTF-8)
Content-Disposition: attachment; filename*=UTF-8''%D0%B4%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82.pdf
```

---

## 46.7 Кэширование

### Заголовки кэширования

```http
# Время жизни кэша
Cache-Control: max-age=3600   # 1 час
Cache-Control: public, max-age=31536000  # 1 год (статика)
Cache-Control: no-cache       # Всегда проверять
Cache-Control: no-store       # Не кэшировать

# ETag (версия файла)
ETag: "abc123def456"

# Last-Modified
Last-Modified: Wed, 15 Jan 2024 10:30:00 GMT
```

### Условные запросы

```bash
# Проверить, изменился ли файл
curl -H "If-None-Match: \"abc123\"" https://example.com/file.js
# 304 Not Modified — файл не изменился

curl -H "If-Modified-Since: Wed, 15 Jan 2024 10:30:00 GMT" https://example.com/file.js
# 304 Not Modified — файл не изменился
```

---

## 46.8 Потоковая передача

### Server-Sent Events (SSE)

```bash
# Поток событий
curl -N https://example.com/events

# Ответ:
# data: {"message": "update 1"}
#
# data: {"message": "update 2"}
```

```python
# Python клиент
import sseclient
import requests

response = requests.get('https://example.com/events', stream=True)
client = sseclient.SSEClient(response)

for event in client.events():
    print(event.data)
```

### Chunked Transfer Encoding

```http
HTTP/1.1 200 OK
Transfer-Encoding: chunked

5
Hello
6
 World
0

```

---

## 46.9 gRPC и protobuf

### Бинарные API

```protobuf
// file_service.proto
service FileService {
  rpc Upload(stream FileChunk) returns (UploadResponse);
  rpc Download(FileRequest) returns (stream FileChunk);
}

message FileChunk {
  bytes data = 1;
  string filename = 2;
}
```

```python
# gRPC клиент
import grpc
import file_service_pb2_grpc as pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = pb2_grpc.FileServiceStub(channel)

# Скачивание
for chunk in stub.Download(pb2.FileRequest(filename='data.bin')):
    file.write(chunk.data)
```

---

## 46.10 HTTP/2 и HTTP/3

### Преимущества для файлов

```
HTTP/1.1:
┌─────────────┐     ┌─────────────┐
│  Request 1  │ ──▶ │  Response 1  │
├─────────────┤     ├─────────────┤
│  Request 2  │ ──▶ │  Response 2  │ (ждёт Request 1)
└─────────────┘     └─────────────┘

HTTP/2:
┌─────────────────────────────────────┐
│  Stream 1: Request  ──▶  Response   │
│  Stream 2: Request  ──▶  Response   │ (параллельно!)
│  Stream 3: Request  ──▶  Response   │
└─────────────────────────────────────┘

HTTP/3 (QUIC):
- Ещё быстрее (UDP вместо TCP)
- Нет Head-of-line blocking
- Быстрые переподключения
```

```bash
# curl с HTTP/2
curl --http2 -O https://example.com/file.zip

# curl с HTTP/3
curl --http3 -O https://example.com/file.zip
```

---

## Резюме

| Задача | Инструмент | Команда |
|--------|------------|---------|
| Скачать файл | curl | `curl -O URL` |
| Докачать файл | curl | `curl -C - -O URL` |
| Рекурсивное скачивание | wget | `wget -r URL` |
| Многопоточная загрузка | aria2 | `aria2c -x 16 URL` |
| Загрузить файл | curl | `curl -F "file=@f.zip" URL` |
| REST API | requests | `requests.get(url)` |

```
HTTP = универсальный протокол для файлов
     = скачивание + загрузка + API
     = Range requests для докачки
     = Кэширование для производительности
```

??? question "Упражнения"
    **Задание 1.** Скачайте большой файл с поддержкой докачки: `curl -C - -O URL`. Прервите и продолжите. Проверьте заголовок `Accept-Ranges` на сервере.
    
    **Задание 2.** Реализуйте multipart upload на Python: отправьте файл на сервер через `requests.post(url, files=...)`. Проверьте Content-Type заголовок.
    
    **Задание 3.** Напишите Python HTTP-сервер для раздачи файлов с поддержкой Range requests (частичного скачивания). Протестируйте через `curl -r 0-99`.

!!! tip "Следующая глава"
    Как устроено **Git — файловая система поверх файловой системы** → [Git как ФС](47-git-fs.md)
