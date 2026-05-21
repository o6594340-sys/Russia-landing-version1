# Tozai Tours — KP Generator

## Деплой
- **Railway (production):** https://russia-landing-version1-production.up.railway.app
- **Локально:** http://localhost:5000
- **GitHub:** https://github.com/o6594340-sys/Russia-landing-version1

## Стек
Flask + Claude API (claude-sonnet-4-6) + openpyxl + python-pptx

## Структура
- `app.py` — Flask routes
- `claude_generator.py` — генерация программы через Claude
- `excel_generator.py` — смета в xlsx
- `ppt_generator.py` — презентация в pptx
- `rates_loader.py` — тарифы из Japan-rates-sample.xlsx
- `service_extractor.py` — парсинг программы → строки сметы
- `templates/index.html` — весь фронтенд (vanilla JS)

## Деплой на Railway
Root directory: `Comercial-proposals`
Env var: `ANTHROPIC_API_KEY`
