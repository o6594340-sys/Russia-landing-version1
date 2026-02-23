"""
Japan Travel Concierge Bot — Hana
Telegram bot for tourists visiting Japan.
Auto-detects language and responds in the same language as the user.
Powered by Groq (Llama 3.3).
"""

import logging
import os
from collections import defaultdict

from dotenv import load_dotenv
from groq import Groq
from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    Update,
)
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from prompts import SYSTEM_PROMPT

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

conversation_history: dict[int, list] = defaultdict(list)
MAX_HISTORY = 20

client = Groq(api_key=GROQ_API_KEY)


def main_keyboard() -> ReplyKeyboardMarkup:
    """Bilingual quick-topic buttons."""
    buttons = [
        [KeyboardButton("🍜 Halal food / طعام حلال"), KeyboardButton("🏨 Hotels / فنادق")],
        [KeyboardButton("⛩️ Sights / معالم"), KeyboardButton("🚇 Transport / مواصلات")],
        [KeyboardButton("🎭 Experiences / تجارب"), KeyboardButton("💡 Tips / نصائح")],
        [KeyboardButton("📍 Share my location / أرسل موقعي", request_location=True)],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def trim_history(user_id: int) -> None:
    history = conversation_history[user_id]
    if len(history) > MAX_HISTORY:
        conversation_history[user_id] = history[-MAX_HISTORY:]


def ask_groq(user_id: int, user_message: str) -> str:
    conversation_history[user_id].append({"role": "user", "content": user_message})
    trim_history(user_id)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history[user_id]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        assistant_text = response.choices[0].message.content or (
            "I'm sorry, I couldn't find a good answer. Please try rephrasing! 😊"
        )
        conversation_history[user_id].append({"role": "assistant", "content": assistant_text})
        return assistant_text

    except Exception as e:
        logger.error("Groq API error: %s", e)
        return "I'm having a little trouble connecting — please try again in a moment! 🙏"


# ── Handlers ───────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    conversation_history[user_id] = []

    welcome = (
        "Hello! 👋 I'm **Hana**, your Japan concierge! 🗼🎌\n"
        "أهلاً! أنا **هانا**، كونسيرجك في اليابان! 🗼🎌\n\n"
        "Ask me anything about Japan — I'll reply in your language.\n"
        "اسألني أي شيء عن اليابان — سأرد بلغتك.\n\n"
        "🏨 Hotels · 🍜 Halal food · ⛩️ Sights · 🚇 Transport · 🎭 Experiences"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown", reply_markup=main_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "**Hana — Japan Concierge** 🗼\n\n"
        "I answer questions about Japan in your language:\n"
        "• Hotels, ryokans & neighborhoods\n"
        "• Halal & vegetarian restaurants\n"
        "• Attractions, temples, parks & events\n"
        "• Experiences: tea ceremony, kimono, sushi class...\n"
        "• Metro, IC cards, airport transfer\n"
        "• Practical tips for Muslim travelers\n\n"
        "/start — Restart\n"
        "/clear — Clear chat history\n"
        "/help — This message"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text("Done! 🧹 / تم! 🧹")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_text = update.message.text.strip()

    if not user_text:
        return

    logger.info("User %s: %s", user_id, user_text[:80])
    await update.effective_chat.send_action(ChatAction.TYPING)

    reply = ask_groq(user_id, user_text)

    if len(reply) > 4096:
        for chunk in [reply[i:i+4000] for i in range(0, len(reply), 4000)]:
            await update.message.reply_text(chunk, parse_mode="Markdown")
    else:
        try:
            await update.message.reply_text(reply, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(reply)


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    loc = update.message.location
    await update.effective_chat.send_action(ChatAction.TYPING)

    location_msg = (
        f"My current location: latitude {loc.latitude:.4f}, longitude {loc.longitude:.4f}. "
        "What are the nearest halal restaurants, sights, or transport options from here in Japan?"
    )
    reply = ask_groq(user_id, location_msg)

    try:
        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(reply)


async def handle_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "I can only read text messages — type your question! 😊\n"
        "أستطيع قراءة الرسائل النصية فقط — اكتب سؤالك! 😊"
    )


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in .env")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(~filters.TEXT & ~filters.COMMAND & ~filters.LOCATION, handle_unsupported))

    logger.info("Hana Japan Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()
