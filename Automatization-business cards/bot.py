import os
import json
import logging
import base64
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes
)
from dotenv import load_dotenv
import anthropic
import pickle
import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_OAUTH_FILE = os.getenv("GOOGLE_OAUTH_FILE", "oauth_credentials.json")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME", "Визитки")

VALID_CODES = {
    "OKH": "Ольга",
    "NSH": "Надя",
    "DI": "Даша",
    "AE": "Настя",
}

NAME_TO_CODE = {
    "ОЛЬГА": "OKH",
    "НАДЯ": "NSH",
    "НАДЕЖДА": "NSH",
    "ДАША": "DI",
    "ДАРЬЯ": "DI",
    "НАСТЯ": "AE",
    "АНАСТАСИЯ": "AE",
}

USERS_FILE = "users.json"

COLUMNS = [
    "Название компании",
    "Сайт",
    "Страна/Регион",
    "Тип компании",
    "Контактное лицо",
    "Должность",
    "Email",
    "Контактный телефон",
    "Канал знакомства",
    "Добавил",
]


# ── User registry ────────────────────────────────────────────────────────────

def load_users() -> dict:
    if Path(USERS_FILE).exists():
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users: dict) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


# ── Google Sheets ─────────────────────────────────────────────────────────────

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
TOKEN_FILE = "token.pickle"


def get_google_creds() -> Credentials:
    import asyncio
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    creds = None
    if Path(TOKEN_FILE).exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_OAUTH_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return creds


def get_sheet() -> gspread.Worksheet:
    creds = get_google_creds()
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    try:
        sheet = spreadsheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=1000, cols=len(COLUMNS))
        sheet.append_row(COLUMNS)
    return sheet


def check_duplicate(sheet: gspread.Worksheet, company: str, contact: str) -> str | None:
    """
    Returns:
      'full'    — same company AND same contact person (skip)
      'company' — same company but different contact (add with note)
      None      — completely new record
    """
    records = sheet.get_all_records()
    company_l = company.lower().strip()
    contact_l = contact.lower().strip()

    for r in records:
        rec_company = str(r.get("Название компании", "")).lower().strip()
        rec_contact = str(r.get("Контактное лицо", "")).lower().strip()
        if rec_company == company_l:
            if rec_contact == contact_l:
                return "full"
            return "company"
    return None


# ── Claude Vision ─────────────────────────────────────────────────────────────

PROMPT = """Внимательно изучи фото. На нём может быть одна или несколько визиток.

Извлеки данные КАЖДОЙ визитки и верни JSON-массив:

[
  {
    "company_name": "название компании",
    "website": "сайт (только домен без протокола, например: example.com)",
    "country_region": "страна и/или регион/город",
    "company_type": "Отель" | "DMC" | "Другой поставщик услуг",
    "contact_person": "Фамилия Имя",
    "position": "должность контактного лица",
    "email": "email",
    "phone": "телефон с кодом страны если указан"
  }
]

Правила:
- Если на фото одна визитка — верни массив из одного элемента
- Если поле не найдено — оставь пустую строку ""
- company_type: "Отель" для hotel/resort/гостиница, "DMC" для DMC/incoming agency/туроператор, иначе "Другой поставщик услуг"
- Данные вноси на языке визитки; если несколько языков — предпочти английский
- Верни ТОЛЬКО JSON-массив, без пояснений и markdown"""


def extract_card_data(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
    )

    text = response.content[0].text.strip()
    # Strip possible markdown fences
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1].lstrip("json").strip() if len(parts) > 1 else text
    result = json.loads(text)
    # Always return a list
    if isinstance(result, dict):
        return [result]
    return result


# ── Formatting ────────────────────────────────────────────────────────────────

def format_card(data: dict) -> str:
    def v(key):
        return data.get(key) or "—"

    return (
        f"🏢 {v('company_name')}\n"
        f"🌐 {v('website')}\n"
        f"📍 {v('country_region')}\n"
        f"🏷 {v('company_type')}\n"
        f"👤 {v('contact_person')}\n"
        f"✉️ {v('email')}\n"
        f"📞 {v('phone')}"
    )


# ── Handlers ──────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    uid = str(update.effective_user.id)
    if uid in users:
        alias = users[uid]
        name = VALID_CODES[alias]
        await update.message.reply_text(
            f"Привет, {name}! Ты зарегистрирована как {alias}.\n"
            f"Просто отправь фото визитки — занесу данные в таблицу."
        )
    else:
        await update.message.reply_text(
            "Привет! Напиши своё имя:\n\n"
            "Ольга\n"
            "Надя\n"
            "Даша\n"
            "Настя"
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    uid = str(update.effective_user.id)
    text = update.message.text.strip().upper()

    if uid not in users:
        code = NAME_TO_CODE.get(text) or (text if text in VALID_CODES else None)
        if code:
            users[uid] = code
            save_users(users)
            name = VALID_CODES[code]
            await update.message.reply_text(
                f"Готово, {name}! Отправляй фото визиток — буду заносить в таблицу автоматически. 📋"
            )
        else:
            await update.message.reply_text(
                "Не узнала тебя. Напиши своё имя: Ольга, Надя, Даша или Настя"
            )
    elif context.user_data.get("pending_cards"):
        # Waiting for meeting channel answer
        channel = update.message.text.strip()
        context.user_data["channel"] = channel
        pending = context.user_data.pop("pending_cards")
        cards = pending["cards"]
        alias = pending["alias"]

        try:
            sheet = get_sheet()
        except Exception as e:
            logger.error(f"Sheets error: {e}")
            await update.message.reply_text("Ошибка подключения к Google Таблице.")
            return

        added, skipped = [], []
        for data in cards:
            company = data.get("company_name", "")
            contact = data.get("contact_person", "")
            dup = check_duplicate(sheet, company, contact)
            if dup == "full":
                skipped.append(data.get("company_name", "?"))
                continue
            row = [
                data.get("company_name", ""),
                data.get("website", ""),
                data.get("country_region", ""),
                data.get("company_type", ""),
                data.get("contact_person", ""),
                data.get("position", ""),
                data.get("email", ""),
                data.get("phone", ""),
                channel,
                alias,
            ]
            try:
                sheet.append_row(row)
                added.append(data)
            except Exception as e:
                logger.error(f"Append error: {e}")

        reply = f"✅ Добавлено {len(added)} из {len(cards)} визитк(и). 📍 {channel}\n\n"
        reply += "\n\n---\n\n".join(format_card(d) for d in added)
        if skipped:
            reply += f"\n\n⚠️ Пропущены дубликаты: {', '.join(skipped)}"
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text(
            "Отправь фото визитки — занесу в таблицу."
        )


async def _process_image(update: Update, context: ContextTypes.DEFAULT_TYPE, image_bytes: bytes, mime_type: str, alias: str):
    """Core logic: OCR → dedup → ask channel → write to sheet."""
    await update.message.reply_text("Читаю визитки…")

    try:
        cards = extract_card_data(image_bytes, mime_type)
    except Exception as e:
        logger.error(f"Vision error: {e}")
        await update.message.reply_text(
            "Не удалось распознать визитку. Попробуй сфотографировать чётче."
        )
        return

    try:
        sheet = get_sheet()
    except Exception as e:
        logger.error(f"Sheets error: {e}")
        await update.message.reply_text("Ошибка подключения к Google Таблице.")
        return

    channel = context.user_data.get("channel")

    if not channel:
        # Save all cards as pending, ask for channel once
        context.user_data["pending_cards"] = {"cards": cards, "alias": alias}
        preview = "\n\n---\n\n".join(format_card(c) for c in cards)
        count = len(cards)
        await update.message.reply_text(
            f"Распознала {count} визитк(и):\n\n{preview}\n\n"
            f"Где познакомились? (например: ITB 2026, Sales call, WTM London…)"
        )
        return

    # Channel already known — save all cards immediately
    added, skipped = [], []
    for data in cards:
        company = data.get("company_name", "")
        contact = data.get("contact_person", "")
        dup = check_duplicate(sheet, company, contact)
        if dup == "full":
            skipped.append(data.get("company_name", "?"))
            continue
        row = [
            data.get("company_name", ""),
            data.get("website", ""),
            data.get("country_region", ""),
            data.get("company_type", ""),
            data.get("contact_person", ""),
            data.get("position", ""),
            data.get("email", ""),
            data.get("phone", ""),
            channel,
            alias,
        ]
        try:
            sheet.append_row(row)
            added.append(data)
        except Exception as e:
            logger.error(f"Append error: {e}")

    reply = f"✅ Добавлено {len(added)} из {len(cards)} визитк(и). 📍 {channel}\n\n"
    reply += "\n\n---\n\n".join(format_card(d) for d in added)
    if skipped:
        reply += f"\n\n⚠️ Пропущены дубликаты: {', '.join(skipped)}"
    await update.message.reply_text(reply)


async def cmd_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = " ".join(context.args).strip()
    if args:
        context.user_data["channel"] = args
        await update.message.reply_text(f"Теперь записываю канал как: {args}")
    else:
        current = context.user_data.get("channel", "не задан")
        await update.message.reply_text(
            f"Текущий канал: {current}\n\n"
            f"Чтобы сменить, напиши: /channel ITB 2026"
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    uid = str(update.effective_user.id)
    if uid not in users:
        await update.message.reply_text("Сначала введи /start и зарегистрируйся.")
        return

    photo = update.message.photo[-1]  # highest resolution
    file = await context.bot.get_file(photo.file_id)
    image_bytes = bytes(await file.download_as_bytearray())
    await _process_image(update, context, image_bytes, "image/jpeg", users[uid])


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos sent as files (uncompressed)."""
    users = load_users()
    uid = str(update.effective_user.id)
    if uid not in users:
        await update.message.reply_text("Сначала введи /start и зарегистрируйся.")
        return

    doc = update.message.document
    mime = doc.mime_type or "image/jpeg"
    if not mime.startswith("image/"):
        await update.message.reply_text("Пожалуйста, отправь фото визитки.")
        return

    file = await context.bot.get_file(doc.file_id)
    image_bytes = bytes(await file.download_as_bytearray())
    await _process_image(update, context, image_bytes, mime, users[uid])


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())
    logger.info("Authorizing Google…")
    get_google_creds()
    logger.info("Google authorized.")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("channel", cmd_channel))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info("Bot is running…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
