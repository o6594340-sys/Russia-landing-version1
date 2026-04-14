"""
text_generator.py — генерация текстов для PPT через Claude API.

Один запрос → все тексты презентации, написанные под конкретного клиента.
Тексты продающие, живые, адаптированы под профиль группы.

Использование:
    from text_generator import generate_texts
    texts = generate_texts(proposal)
"""

import json
import os
from pathlib import Path
import anthropic
from dotenv import load_dotenv

load_dotenv()


# ── Промпт ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Ты — опытный копирайтер DMC-компании Cathay DMC, специализирующейся на корпоративных турах в Китай.

Твоя задача — писать тексты для PPT-презентаций (proposals) для MICE-агентств и корпоративных клиентов.

Стиль:
- Живой, конкретный, продающий — не туристический буклет
- Каждое описание отвечает на вопрос клиента: "зачем это моей группе?"
- Избегай штампов: "уникальный", "незабываемый", "богатая история"
- Используй детали: метры, годы, имена, факты — они создают доверие
- Тон: уверенный профессионал, не рекламный агент
- Язык: русский, деловой но живой
- Длина описаний: 2-4 предложения на слайд, не больше

Отвечай ТОЛЬКО валидным JSON без markdown-блоков."""


def generate_texts(proposal: dict) -> dict:
    """
    Генерирует все тексты презентации через Claude API.

    proposal — словарь с данными о туре (см. структуру ниже)
    Возвращает словарь с готовыми текстами для каждого слайда.
    """
    prompt = _build_prompt(proposal)

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0]

    return json.loads(raw)


def _build_prompt(p: dict) -> str:
    client      = p.get("client", "Клиент")
    agency      = p.get("agency", "")
    pax         = p.get("pax_total", "")
    destination = p.get("destination", "Шанхай")
    dates       = p.get("dates", "")
    season      = p.get("season", "")
    profile     = p.get("group_profile", "")
    hotels      = p.get("hotels", [])
    days        = p.get("days", [])

    hotels_json = json.dumps(hotels, ensure_ascii=False, indent=2)
    days_json   = json.dumps(days,   ensure_ascii=False, indent=2)

    return f"""Напиши все тексты для PPT-proposal по следующим данным тура.

ДАННЫЕ ТУРА:
- Клиент: {client}{f' / агентство: {agency}' if agency else ''}
- Количество участников: {pax} чел.
- Направление: {destination}
- Даты: {dates}
- Сезон: {season}
- Профиль группы: {profile}

ОТЕЛИ:
{hotels_json}

ПРОГРАММА ПО ДНЯМ:
{days_json}

Верни JSON строго по этой схеме:

{{
  "cover_title": "3-строчный заголовок обложки\\nна русском\\nдля этого клиента",

  "why_china": {{
    "title": "заголовок слайда (почему Китай именно сейчас / в этот сезон)",
    "description": "2-3 предложения. Конкретно про этот месяц и этот маршрут. Что делает именно этот момент лучшим для группы."
  }},

  "route_description": "Одна строка с маршрутом в формате: Дата — Город (событие) → Дата — Город → ...",

  "bridge_bullets": [
    "5 буллетов о концепции программы. Каждый — конкретный аргумент под профиль этой группы.",
    "буллет 2",
    "буллет 3",
    "буллет 4",
    "буллет 5"
  ],

  "gastronomy_title": "Заголовок слайда гастрономии (2-3 слова)",
  "gastronomy_subtitle": "Подзаголовок — одна строка о гастрономической концепции тура",

  "days": [
    {{
      "day_num": 1,
      "activities": [
        {{
          "name": "название активности (как в программе)",
          "slide_title": "заголовок слайда (краткий, до 40 символов)",
          "description": "2-3 предложения. Конкретные детали. Почему это важно для этой группы."
        }}
      ],
      "restaurants": [
        {{
          "name": "название ресторана",
          "slide_title": "заголовок слайда (Обед/Ужин — Название)",
          "description": "2-3 предложения. Атмосфера + фирменное блюдо + что включено.",
          "cuisine": "тип кухни",
          "format": "формат подачи"
        }}
      ]
    }}
  ],

  "hotels": [
    {{
      "name": "название отеля (как в данных)",
      "description": "2-3 предложения. Локация + главное преимущество для группы + что выделяет среди других."
    }}
  ]
}}"""


# ── Тестовый запуск ───────────────────────────────────────────────────────────

SAMPLE_PROPOSAL = {
    "client":       "ТЕХНОНИКОЛЬ",
    "agency":       "RUSMICE",
    "pax_total":    35,
    "destination":  "Шанхай + Сучжоу",
    "dates":        "13–17 апреля 2026",
    "season":       "апрель (начало весны, цветение садов)",
    "group_profile": (
        "30 дилеров + 5 сотрудников компании. "
        "Инженеры и владельцы бизнеса, 40–45 лет, первая поездка в Китай. "
        "Интерес к современным технологиям и урбанизму. "
        "Важен комфортный темп без перегрузок."
    ),
    "hotels": [
        {"name": "Courtyard by Marriott Shanghai Central", "stars": 4,
         "location": "рядом с ж/д вокзалом, 10 мин до Бунда", "rooms": 451},
        {"name": "Shanghai Marriott Marquis City Centre", "stars": 5,
         "location": "центр, у Нанкинского проспекта", "rooms": 720},
        {"name": "The Portman Ritz-Carlton Shanghai", "stars": 5,
         "location": "деловой район Цзинъань", "rooms": 578},
    ],
    "days": [
        {
            "day": 1, "date": "13 апреля", "city": "Шанхай",
            "activities": [
                {"name": "Прилёт. Трансфер в отель",
                 "note": "встреча в аэропорту Пудун, трансфер на автобусе"}
            ],
            "restaurants": []
        },
        {
            "day": 2, "date": "14 апреля", "city": "Шанхай",
            "activities": [
                {"name": "The People's Park",
                 "note": "98 000 кв.м в центре города, утренний тайчи, шанхайцы"},
                {"name": "Shanghai History Museum",
                 "note": "история 6000 лет, колониальный Шанхай, здание таможни"},
                {"name": "The Bund",
                 "note": "набережная Вайтань, ар-деко + Пудун напротив"},
                {"name": "Huangpu River Cruise",
                 "note": "прогулка на теплоходе, закатный Шанхай"},
            ],
            "restaurants": [
                {"name": "ROOF 325", "type": "обед",
                 "note": "европейская кухня на крыше, вид на Бунд"},
                {"name": "Lost Heaven on the Bund", "type": "ужин",
                 "note": "юньнаньская кухня, живая музыка, 2 бокала вина"},
            ]
        },
        {
            "day": 3, "date": "15 апреля", "city": "Сучжоу",
            "activities": [
                {"name": "Suzhou Museum",
                 "note": "архитектор И.М. Пэй, 30 000 экспонатов"},
                {"name": "Master of Nets Garden",
                 "note": "сад ЮНЕСКО, эпоха Южной Сун, пруды и павильоны"},
                {"name": "Chinese seal engraving masterclass",
                 "note": "мастер из общества Силин, каждый делает свою печать"},
            ],
            "restaurants": [
                {"name": "Restaurant Mulan", "type": "обед",
                 "note": "чжэцзянская кухня, банкетный формат"},
                {"name": "MeiLongZhen Restaurant", "type": "ужин",
                 "note": "основан в 1938, белка-рыба, 2 бокала вина"},
            ]
        },
        {
            "day": 4, "date": "16 апреля", "city": "Шанхай",
            "activities": [
                {"name": "French Concession",
                 "note": "платановые аллеи, кафе 1920-х, виллы"},
                {"name": "Xintiandi",
                 "note": "шикумэнь + современность, бутики, галереи"},
            ],
            "restaurants": [
                {"name": "Il Teatro", "type": "обед",
                 "note": "итальянский в сердце Xintiandi"},
                {"name": "Gongyan Imperial Feast", "type": "ужин",
                 "note": "иммерсивный банкет, живые выступления, 2 бокала вина"},
            ]
        },
        {
            "day": 5, "date": "17 апреля", "city": "Шанхай",
            "activities": [
                {"name": "Трансфер в аэропорт",
                 "note": "гид сопровождает до вылета"}
            ],
            "restaurants": []
        },
    ]
}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    print("Генерирую тексты через Claude API...")
    texts = generate_texts(SAMPLE_PROPOSAL)

    out_path = Path(__file__).parent / "sample_texts.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)

    print(f"\nСохранено в: {out_path}")
    print("\n── ОБЛОЖКА ──────────────────────────────────")
    print(texts.get("cover_title"))
    print("\n── ПОЧЕМУ КИТАЙ ─────────────────────────────")
    print(texts.get("why_china", {}).get("title"))
    print(texts.get("why_china", {}).get("description"))
    print("\n── КОНЦЕПЦИЯ (буллеты) ──────────────────────")
    for b in texts.get("bridge_bullets", []):
        print(f"  • {b}")
    print("\n── ДЕНЬ 2 — БУНД ────────────────────────────")
    day2 = next((d for d in texts.get("days", []) if d.get("day_num") == 2), {})
    for a in day2.get("activities", []):
        if "Bund" in a.get("name", ""):
            print(f"  [{a['slide_title']}]")
            print(f"  {a['description']}")
