# Настройка бота для визиток

## Шаг 1 — Telegram Bot Token

1. В Telegram найди @BotFather
2. Отправь `/newbot`
3. Придумай имя и username для бота
4. Скопируй полученный токен

## Шаг 2 — Anthropic API Key

1. Зайди на console.anthropic.com
2. API Keys → Create Key
3. Скопируй ключ

## Шаг 3 — Google Sheets API

### 3.1 Создать проект в Google Cloud
1. Зайди на console.cloud.google.com
2. Создай новый проект (например "business-card-bot")
3. Включи два API:
   - Google Sheets API
   - Google Drive API
   (Поиск по названию → Enable)

### 3.2 Создать Service Account
1. IAM & Admin → Service Accounts → Create Service Account
2. Имя: `bot-service-account` (любое)
3. Нажми Create → Done (роли пропусти)
4. Открой созданный аккаунт → вкладка Keys
5. Add Key → Create new key → JSON → Download
6. Переименуй скачанный файл в `credentials.json`
7. Положи его в папку с ботом

### 3.3 Создать Google Таблицу
1. Создай новую таблицу на drive.google.com
2. Скопируй ID из URL:
   `https://docs.google.com/spreadsheets/d/`**`ВОТ_ЭТО_ID`**`/edit`
3. Нажми «Поделиться» → вставь email сервис-аккаунта (из credentials.json, поле `client_email`)
4. Дай права «Редактор»

## Шаг 4 — Настройка .env

```bash
cp .env.example .env
```

Открой `.env` и заполни:
```
TELEGRAM_TOKEN=токен_от_BotFather
ANTHROPIC_API_KEY=твой_anthropic_ключ
SPREADSHEET_ID=id_таблицы
```

## Шаг 5 — Установка и запуск

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить бота
python bot.py
```

## Шаг 6 — Регистрация пользователей

Каждая участница должна:
1. Найти бота в Telegram по username
2. Нажать /start
3. Ввести свой код (OKH / NSH / DI / AE)

После этого — просто отправляй фото визиток!

---

## Как работает бот

1. Участница отправляет фото визитки
2. Бот распознаёт данные через Claude Vision AI
3. Проверяет дубликаты:
   - **Та же компания + тот же контакт** → уведомляет о дубликате, не добавляет
   - **Та же компания + другой контакт** → добавляет как новую строку
   - **Новая компания** → добавляет
4. Записывает в таблицу и подтверждает

### Столбцы таблицы
| Название компании | Сайт | Страна/Регион | Тип компании | Контактное лицо | Email | Телефон | Добавил |
