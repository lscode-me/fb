# Файлы: missing manual

Книга о файлах, форматах данных и инструментах работы с ними. Исходники в Markdown, сборка через MkDocs.

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install mkdocs-material
mkdocs serve
```

## Публикация на GitHub Pages

В репозитории настроен workflow `.github/workflows/gh-pages.yml` для автоматической публикации при пуше в `main`.

## Структура

- `docs/` — исходники
- `docs/chapters/` — главы и подглавы
- `docs/assets/` — изображения, схемы, стили
- `mkdocs.yml` — конфигурация сайта
