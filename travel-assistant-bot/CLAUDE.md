# Hana — Tokyo Travel Concierge Bot

Telegram-бот консьерж для арабских туристов в Токио.

## Стек
- Python 3.13+
- python-telegram-bot 21.10
- Groq API (llama-3.3-70b-versatile) — бесплатный, работает в ЕС
- Запуск: `python bot.py`

## Важные детали
- AI провайдер: **Groq** (не Anthropic, не Google Gemini — оба не работают в Бельгии/ЕС на free tier)
- Ключи в `.env`: `TELEGRAM_BOT_TOKEN` и `GROQ_API_KEY`
- Python запускается как `python3` в этой среде
- asyncio fix для Python 3.14: `asyncio.set_event_loop(asyncio.new_event_loop())` перед `main()`
- Groq выдаёт UserWarning про Pydantic V1 на Python 3.14 — это норма, не ошибка

## Файлы
- `bot.py` — Telegram хендлеры + вызов Groq API
- `prompts.py` — системный промпт (личность Hana, правила поведения)
- `.env` — секретные ключи

## Персонаж
Имя **Hana**, отвечает только про Токио, всегда на английском, дружелюбный тон.
