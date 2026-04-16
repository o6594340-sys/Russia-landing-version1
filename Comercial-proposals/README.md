# Tozai Tours — Генератор КП (Япония)

Веб-приложение для автоматической генерации коммерческих предложений по корпоративным турам в Японию.
Генерирует презентацию PPT + смету Excel через 3-шаговый интерфейс.

---

## Запуск

Двойной клик на `start.bat` → открыть браузер: `http://localhost:5000`

Для показа клиентам из той же Wi-Fi сети: `http://192.168.31.70:5000`

---

## Флоу (3 шага)

1. **Заполнить форму** — вручную или загрузить бриф (PDF/Word) → автозаполнение через Claude
2. **Утвердить программу** — Claude генерирует черновик по дням, можно скорректировать
3. **Скачать файлы** — Excel-смета и PPT-презентация

---

## Структура файлов

| Файл | Назначение |
|------|-----------|
| `app.py` | Flask-сервер, порт 5000 |
| `claude_generator.py` | Генерация и корректировка программы через Claude API |
| `ppt_generator.py` | Генератор презентации .pptx |
| `excel_generator.py` | Генератор сметы .xlsx |
| `rates_loader.py` | Загрузка тарифов из Japan-rates-sample.xlsx |
| `brief_parser.py` | Парсинг брифа (PDF/Word) → автозаполнение формы |
| `photo_fetcher.py` | Загрузка фото: локальный банк → Unsplash → Pexels |
| `.env` | API-ключи (не в git) |

---

## Презентация PPT

### Дизайн: Washi & Red
- Фон: тёплый беж `#F7F4EF`
- Акцент: японский красный `#C8102E`
- Золото: `#A8895A`
- Тёмный (титул/финал): `#1A0A0D`
- Шрифты: Georgia (заголовки) + Arial (текст)

### Слайды
1. **Титул** — фото на весь экран, название компании, параметры группы
2. **Почему Япония** — 5 конкретных фактов без воды
3. **Концепция** — идея тура под конкретную аудиторию
4. **Дни программы** — полноэкранное фото + живое описание + расписание (Утро/День/Вечер)
5. **Хайлайты** — 3–4 витринных слайда под ключевые активности (большое фото + текст)
6. **Размещение** — описание отелей
7. **Финал / Контакты**

### Правила текста (зафиксированы в промпте)
- Тире только в определениях («X — это Y») и расписании («09:00 — завтрак»)
- Никаких тире вместо запятой — это ошибка английского стиля
- Запрещены слова: «незабываемый», «уникальный», «погружение», «впечатления»
- Конкретика: реальные места, цифры, факты

---

## Фотобанк

Папка `photo_bank/` — локальные фото в приоритете перед Unsplash/Pexels.

**Как добавить фото:**
1. Скачать фото (JNTO, официальные источники)
2. Положить в папку `photo_bank/`
3. Добавить запись в `photo_bank/index.json`:

```json
{
  "file": "имя_файла.jpg",
  "tags": ["тег1", "тег2", "тег3"],
  "credit": "источник"
}
```

**Текущие фото в банке:**

| Файл | Теги |
|------|------|
| `Kinkakuji.jpg` | kyoto, temple, traditional |
| `Maiko.jpg` | maiko, geisha, performance |
| `young maiko - 2 persons.jpg` | maiko, gala, entertainment |
| `maiko performace.jpg` | maiko, show, kabuki |
| `Momiji-Kyoto.jpg` | kyoto, autumn, temple |
| `Momiji-fuji.jpg` | fuji, autumn, landscape, cover |
| `momiji-Tokyo.jpg` | tokyo, autumn, street |
| `Nara park.jpg` | nara, deer, nature |
| `Shinkansen.jpg` | shinkansen, technology, modern |
| `experience- calligraphy.jpg` | calligraphy, culture, activity |
| `experience-ikebana.jpg` | ikebana, flower, wellness |
| `food- Fish market.jpeg` | fish market, tsukiji, gastronomy |
| `food-kaiseki.jpg` | kaiseki, sushi, luxury dinner |
| `food-yakitori.jpg` | yakitori, teppanyaki, grill |
| `taiko experience.jpg` | taiko, teambuilding, drums |
| `teamlab Tokyo.jpeg` | teamlab, digital art, technology |
| `sakura.jpeg` | sakura, spring, nature |
| `sakura flower.jpg` | sakura, flower, closing |
| `sakura-Tokyo.jpg` | sakura, tokyo, cover |

**Логика выбора:** система ищет фото по совпадению тегов с поисковым запросом слайда. Каждое фото используется только один раз на презентацию (повторы исключены).

---

## API-ключи (.env)

```
ANTHROPIC_API_KEY=...        # обязательно — генерация текстов
UNSPLASH_ACCESS_KEY=...      # опционально — запасной источник фото
PEXELS_API_KEY=...           # опционально — запасной источник фото
```

---

## Ценообразование

- Цены НЕТТО — агентство добавляет своё АК самостоятельно
- Валюта: USD
- Ориентир: $2 500–3 500 на человека
- Состав номеров: TWN (twin) + SGL (single), без DBL

## Модель Claude

`claude-opus-4-6` — используется для генерации и корректировки программы.
