# Hana — Tokyo Travel Concierge Bot 🗼

A Telegram concierge bot for Arab tourists visiting Tokyo. Powered by **Claude AI** with live web search.

## Features

- Answers only about **Tokyo** (hotels, restaurants, attractions, transport, masterclasses, halal food, etc.)
- **Always responds in English**, even if the user writes in Arabic or any other language
- **Concierge mode** — informs and guides, never sells or pushes bookings
- Friendly, relaxed tone with light use of emojis
- Asks 1–2 short clarifying questions when a query is unclear
- Remembers conversation context within a session
- Live web search for up-to-date info (opening hours, current events, etc.)

## Setup

### 1. Prerequisites

- Python 3.10+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- A Google Gemini API Key (free — from [aistudio.google.com/apikey](https://aistudio.google.com/apikey))

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:
```
TELEGRAM_BOT_TOKEN=your_token_here
GOOGLE_API_KEY=your_key_here
```

### 4. Run the bot

```bash
python bot.py
```

## Project structure

```
travel-assistant-bot/
├── bot.py            # Main bot logic (Telegram handlers + Claude API calls)
├── prompts.py        # System prompt defining Hana's persona and rules
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variable template
├── .gitignore
└── README.md
```

## Bot commands

| Command  | Description                    |
|----------|--------------------------------|
| `/start` | Welcome message + intro        |
| `/help`  | List of topics + commands      |
| `/clear` | Reset conversation history     |

## Customisation

- **Persona & rules** — edit `prompts.py` to change Hana's personality, scope, or language rules
- **History length** — change `MAX_HISTORY` in `bot.py` (default: 20 messages)
- **Model** — change `model=` in `ask_claude()` in `bot.py`
- **Web search uses** — change `max_uses` in the tools list in `ask_claude()`

## Notes on web search

The bot uses Google Search grounding built into Gemini 2.0 Flash. This means it can fetch current data like opening hours, prices, and events — but always remind users to verify time-sensitive info on official websites.

## Deployment

For production, run the bot on a server (e.g., a VPS or cloud VM) using a process manager:

```bash
# Using screen
screen -S hana-bot
python bot.py

# Or using systemd / pm2 / supervisor for auto-restart
```

No webhook setup needed — the bot uses long-polling by default.
