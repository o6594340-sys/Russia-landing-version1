# China DMC — Proposal Automation Platform

Платформа для автоматизации подготовки proposal для DMC, специализирующегося на турах в Китай.

## Проблема

Подготовка одного proposal занимает 2-3 дня. В высокий сезон — 5-7 запросов в неделю. Конверсия теряется из-за медленного ответа. Маршруты типовые, но каждый раз всё делается вручную.

**Цель:** сократить время подготовки до 20-30 минут.

---

## Что делает система

На входе менеджер вводит параметры группы или загружает бриф от агентства.  
На выходе:

- Детальный расчёт стоимости (Excel, USD)
- Программа по дням с таймингом
- Презентация в PPT-стиле
- PDF + веб-ссылка для клиента

---

## Флоу менеджера

```
1. Новый запрос
   ├── Загрузить бриф (Word/PDF) → Claude парсит → форма заполняется автоматически
   └── Заполнить вручную

2. Форма создания proposal
   Обязательно: город/маршрут, даты, кол-во человек, кол-во SGL, кол-во DBL
   Опционально: город прилёта, город вылета, бюджет
   Галочки: конференция, корп.визит, гала-ужин
   Текст: особые пожелания

3. Генерация (асинхронно, уведомление по завершении)
   → подбор шаблона маршрута
   → генерация текстов программы (Claude API)
   → подбор отелей
   → расчёт стоимости
   → сборка PPT + Excel + PDF

4. Редактор proposal
   → правка текстов, замена активностей, смена отелей
   → ввод цен отелей по мере получения от поставщиков
   → автоматический пересчёт сметы

5. Экспорт и отправка
   → PDF, PPT, веб-ссылка для клиента
   → версии сохраняются (v1, v2, v3...)
```

---

## Структура proposal (PPT/PDF)

| # | Блок | Примечание |
|---|---|---|
| 1 | Обложка | Логотип DMC, название тура, даты, группа |
| 2 | Почему Китай сейчас | Привязка к сезону / событиям на даты поездки |
| 3 | Обзор маршрута | Карта + города + даты одним взглядом |
| 4 | Программа по дням | Фото + описание + тайминг по каждой активности |
| 5 | Отели | По городам, 3 варианта категорий |
| 6 | Гастрономия | Топ-рестораны из программы |
| 7 | Стоимость | Включено / не включено / цена на человека |
| 8 | Контакты DMC | |

### Опциональные модули (включаются галочкой)

- Конференц-зал + AV + обед в отеле
- Корпоративный визит (Huawei, Alibaba и др.)
- Гала-ужин / venue
- Альтернативные опции дня

---

## Что включено в стоимость (стандарт DMC)

**Всегда включено:**
- Отели (на базе завтрака)
- Обеды (вода + чай/кофе)
- Ужины (2 бокала вина + чай/кофе)
- Все трансферы по программе
- Гиды по программе
- Входные билеты по программе
- Активности (мастер-классы, тимбилдинги)

**Не включено** (зона агентства, не DMC):
- Авиабилеты
- Страховка
- Личные расходы, дополнительный алкоголь

**Виза:** для россиян в Китай не нужна.

---

## Excel — структура сметы

Валюта: **только USD**. В рубли переводит агентство самостоятельно.

### Разделы

```
РАЗМЕЩЕНИЕ
  Отель 1 — вариант базовый (4*)
    ├── SGL, Deluxe King, 33 sqm, завтрак  | room*night | 185 | 30 | 5 550
    └── TWN, Deluxe Twin, 33 sqm, завтрак  | room*night | 200 |  0 |     0
  Отель 2 — вариант стандарт (5*)
    ├── SGL, Deluxe King, 33 sqm, завтрак  | room*night | 285 |  0 |     0
    └── TWN, Deluxe Twin, 33 sqm, завтрак  | room*night | 310 |  0 |     0
  Отель 3 — вариант премиум (5* luxury)
    ├── SGL, Deluxe King, 44 sqm, завтрак  | room*night | 420 |  0 |     0
    └── TWN, Deluxe Twin, 44 sqm, завтрак  | room*night | 450 |  0 |     0
  ИТОГО РАЗМЕЩЕНИЕ

ТРАНСФЕРЫ
  Автобус 40 мест — аэропорт → отель      | рейс       | 320 |  1 |   320
  Автобус 40 мест — трансферы по программе| день       | 420 |  4 | 1 680
  ИТОГО ТРАНСФЕРЫ

ГИДЫ
  Русскоязычный гид — полный день         | день       | 350 |  5 | 1 750
  ИТОГО ГИДЫ

ПИТАНИЕ
  Ресторан Lost Heaven — обед             | pax        |  45 | 35 | 1 575
  Ресторан Gongyan — ужин                 | pax        |  95 | 35 | 3 325
  ...
  ИТОГО ПИТАНИЕ

АКТИВНОСТИ И ВХОДНЫЕ БИЛЕТЫ
  Шанхайская башня — входной билет        | pax        |  35 | 35 | 1 225
  Мастер-класс по резьбе печатей          | pax        |  55 | 35 | 1 925
  ...
  ИТОГО АКТИВНОСТИ

КОНФЕРЕНЦ-СЕРВИСЫ  ← только если модуль включён
  Аренда зала, Marriott, до 40 чел        | день       |1200 |  1 | 1 200
  AV-оборудование (проектор, микрофоны)   | комплект   | 400 |  1 |   400
  Обед в отеле — шведский стол            | pax        |  65 | 35 | 2 275
  ИТОГО КОНФЕРЕНЦИЯ

──────────────────────────────────────────────────────
GRAND TOTAL (USD)
ЦЕНА НА ЧЕЛОВЕКА (USD)
```

### Логика отелей в Excel

- Все 3 варианта отелей всегда присутствуют в смете
- В базовом варианте стоит реальное кол-во ночей, в остальных — 0
- SGL и TWN всегда идут отдельными строками, даже если кол-во = 0
- Агентство меняет 0 на нужное кол-во → смета пересчитывается автоматически
- Это позволяет агентству оптимизировать конфигурацию номеров под бюджет клиента

---

## Статусы proposal

```
Получен → В работе → Отправлен → Просмотрен → На правках → Выиграно / Проиграно
```

---

## Архитектура данных

### Фиксированные цены (хранятся в БД)
- Транспорт (тип, вместимость, цена/день)
- Гиды (язык, цена/день, по городам)
- Активности и входные билеты (цена/чел)
- Питание (ресторан, формат, цена/чел)

### Динамические цены
- Отели — кураторская база ~10 отелей на город, 5-6 городов (~50-60 записей)
- Хранится последняя известная цена по сезонам (low / high season)
- Менеджер обновляет цену одним кликом после ответа отеля
- ProposalLineItem хранит snapshot_price — цену на момент генерации

### Схема БД

```
City
  └── Hotel
        ├── name, stars, description, photos[]
        ├── year_built, room_count, has_pool
        └── RoomType
              ├── name, type (SGL/TWN), sqm
              ├── last_known_price_low, last_known_price_high
              └── price_updated_at

Activity  (контент-банк — переиспользуется между proposal)
  ├── city, category (экскурсия / ресторан / мастер-класс / шоу / корп.визит)
  ├── name, short_desc, full_desc, photos[]
  ├── duration_hours, price_per_pax
  └── tags [cultural, outdoor, corporate, gastronomy ...]

RouteTemplate  (шаблоны типовых маршрутов)
  ├── name, cities[], duration_days
  └── TemplateDay
        ├── day_number, city
        └── activities[]

Proposal
  ├── client_name, agency_name, pax_sgl, pax_dbl, dates
  ├── status [draft / sent / viewed / revision / won / lost]
  ├── deadline
  ├── modules { conference, gala, corporate_visit }
  └── ProposalDay
        ├── day_number, city
        ├── hotel_ids[] (3 варианта)
        ├── activities[]
        └── ProposalLineItem
              ├── section (accommodation / transfer / guide / fb / activity / conference)
              ├── service, description, unit
              ├── snapshot_price, qty
              └── is_active (false = строка есть но qty=0)
```

---

## Стек

| Слой | Технология |
|---|---|
| Backend | Python + FastAPI |
| База данных | PostgreSQL + Row-Level Security (мультитенантность) |
| Очередь задач | Celery + Redis |
| Frontend | React + Vite |
| PDF | Playwright (HTML → PDF) |
| PPT | python-pptx |
| LLM (тексты программы) | Claude API (claude-sonnet) |
| Хранилище файлов | Cloudflare R2 / Minio |

---

## Принципы расчёта

- Цены только в USD, только продажные
- Расчёт делает код, LLM только генерирует тексты программы
- ProposalLineItem хранит snapshot_price (цена на момент генерации, не текущая)
- Менеджер редактирует любой элемент — смета пересчитывается автоматически
- Генерация асинхронная, менеджер получает уведомление по завершении

---

## Монетизация

SaaS-подписка по seats (менеджерам), без лимита на кол-во proposal.  
Ориентир: $299-599/месяц за компанию.

---

## Текущее состояние реализации (апрель 2026)

### Что уже работает

| Скрипт | Что делает | Статус |
|---|---|---|
| `generate_ppt.py` | Генерирует PPT из proposal-словаря, 36 слайдов | Работает |
| `generate_quote.py` | Генерирует смету Excel (ТЕХНОНИКОЛЬ, 35 чел) | Работает |
| `text_generator.py` | Claude API → все тексты для всех слайдов | Работает |
| `photo_bank.py` | Резолвер фото с типизацией слотов + Unsplash/Pexels | Работает |
| `parse_brief.py` | Парсинг брифа от агентства через Claude | Работает |

### Структура слайдов (generate_ppt.py)

```
1.  Обложка                     ← cover_title от Claude API
2.  Почему Китай сейчас         ← why_china от Claude API
3.  Обзор маршрута              ← route_description от Claude API
4.  Концепция программы         ← bridge_bullets[5] от Claude API
5.  Гастрономия (вводный)       ← gastronomy_title / subtitle от Claude API
─── День 1 (сепаратор) ──────────
6.  Прилёт / трансфер
─── День 2 ──────────────────────
7.  The People's Park           ← 3 фото
8.  Shanghai History Museum     ← 1 фото
9.  Обед — ROOF 325             ← ресторан
10. The Bund                    ← 3 фото
11. Huangpu River Cruise        ← 2 фото
12. Ужин — Lost Heaven on Bund  ← ресторан
─── День 3 (Сучжоу) ────────────
13. Suzhou Museum               ← 3 фото
14. Master of Nets Garden       ← 1 фото
15. Обед — Restaurant Mulan     ← ресторан
16. Мастер-класс: гравировка    ← 1 фото
17. Ужин — MeiLongZhen          ← ресторан
─── День 4 ──────────────────────
18. French Concession           ← 3 фото
19. Xintiandi                   ← 3 фото
20. Обед — Il Teatro            ← ресторан
21. Ужин — Gongyan Imperial     ← ресторан
─── День 5 (сепаратор) ──────────
22. Вводный слайд размещения
23. Courtyard Marriott 4*       ← 3 фото + описание Claude API
24. Тип номера Courtyard
25. Marriott Marquis 5*         ← 3 фото + описание Claude API
26. Тип номера Marriott Marquis
27. Ritz-Carlton Shanghai 5*    ← 3 фото + описание Claude API
28. Тип номера Ritz-Carlton
29. Стоимость (включено / не включено)
30. Почему мы (social proof — кейсы)
31. Контакты
```

### Типы фото-слотов (photo_bank.py)

| Тип слота | Файл | Запрос к Unsplash |
|---|---|---|
| HOTEL_EXTERIOR | exterior.jpg | `{hotel} hotel exterior facade entrance` |
| HOTEL_ROOM | room.jpg | `{hotel} hotel deluxe room interior bed` |
| HOTEL_AMENITY | amenity.jpg | `{hotel} hotel rooftop pool bar lounge` |
| RESTAURANT_INTERIOR | interior.jpg | `{name} restaurant interior dining atmosphere evening` |
| RESTAURANT_DISH | dish.jpg | `{name} restaurant signature dish food photography` |
| ACTIVITY_HERO | hero.jpg | `{name} {city} landmark scenic` |
| ACTIVITY_LOCATION | location.jpg | `{name} {city} wide view panorama` |
| ACTIVITY_PEOPLE | people.jpg | `{name} {city} experience visitors` |
| COVER | cover.jpg | `{city} skyline aerial panorama` |
| CITY_OVERVIEW | overview.jpg | `{city} cityscape aerial overview` |

### Папки с фото-банком (photo_bank/)

Структура: `photo_bank/{object-slug}/{slot-filename}.jpg`

Созданные папки под ТЕХНОНИКОЛЬ-тур:
```
courtyard-by-marriott-shanghai-central/   exterior.jpg, room.jpg, amenity.jpg
shanghai-marriott-marquis-city-centre/    exterior.jpg, room.jpg, amenity.jpg
the-portman-ritz-carlton-shanghai/        exterior.jpg, room.jpg, amenity.jpg
lost-heaven-on-the-bund/                  interior.jpg, dish.jpg
meilongzhen-restaurant/                   interior.jpg, dish.jpg
restaurant-mulan/                         interior.jpg
gongyan-imperial-feast/                   interior.jpg
il-teatro/                                interior.jpg
master-of-nets-garden/                    hero.jpg, location.jpg
french-concession/                        location.jpg, people.jpg
the-bund/                                 hero.jpg, location.jpg, people.jpg
xintiandi/                                location.jpg, people.jpg
suzhou-museum/                            hero.jpg, location.jpg
huangpu-river-cruise/                     hero.jpg, people.jpg
chinese-cuisine-gourmet/                  dish.jpg  (обложка гастрономии)
```

**Приоритет поиска фото:**
1. `photo_bank/{slug}/{slot}.jpg` — загруженное вручную (лучшее качество)
2. `photo_cache/{slot_type}_{slug}.jpg` — авто-кэш из Unsplash/Pexels
3. Unsplash API → скачивает и кэширует
4. Pexels API → fallback
5. `photos/*.jpg` — случайное из оригинальных PPT (с предупреждением)

### JSON-схема текстов (text_generator.py)

```json
{
  "cover_title": "3-строчный заголовок",
  "why_china": { "title": "...", "description": "..." },
  "route_description": "13 апр — Шанхай → 15 апр — Сучжоу → ...",
  "bridge_bullets": ["буллет 1", "...", "буллет 5"],
  "gastronomy_title": "...",
  "gastronomy_subtitle": "...",
  "days": [
    {
      "day_num": 1,
      "activities": [{ "name": "...", "slide_title": "...", "description": "..." }],
      "restaurants": [{ "name": "...", "slide_title": "...", "description": "...", "cuisine": "...", "format": "..." }]
    }
  ],
  "hotels": [{ "name": "...", "description": "..." }]
}
```

---

## Примеры реальных документов

- `v4-MP-2610-SH-35PAX.pptx` — 72 слайда, полный proposal с опциями (ТЕХНОНИКОЛЬ, 35 чел)
- `P-2609-FST-SH-84PAX.pptx` — 31 слайд, программа тура Шанхай → Хуаншань → Ханчжоу (FSTravel, 84 чел)
- `Pv1-26-AUG-55PAX-SHANGHAI-SKNB.pptx` — 14 слайдов, отели + venue для гала-ужина
- `Qv1-26-AUG-55PAX-SHANGHAI-SKNB.xlsx` — полная смета, структура Excel (55 чел, Шанхай)
- `Brief_Japan sample.docx` — пример детального брифа от агентства (EN)
