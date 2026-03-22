"""
Генератор текстов КП через Claude API.
Создаёт концепцию, программу по дням и описание отеля на русском языке.
"""
import anthropic
import os
import json
import re
from pathlib import Path


def _get_client() -> anthropic.Anthropic:
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            for line in env_path.read_text(encoding='utf-8').splitlines():
                if line.startswith('ANTHROPIC_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    if not api_key:
        raise ValueError('ANTHROPIC_API_KEY не задан')
    return anthropic.Anthropic(api_key=api_key)


def refine_program(params: dict, current_content: dict, corrections: str) -> dict:
    """Корректирует программу согласно комментарию менеджера."""
    client = _get_client()

    current_json = json.dumps(current_content, ensure_ascii=False, indent=2)

    twn = params.get('twn', 0)
    sgl = params.get('sgl', 0)
    room_parts = []
    if twn: room_parts.append(f'{twn} Twin-номеров')
    if sgl: room_parts.append(f'{sgl} Single-номеров')
    room_desc = ', '.join(room_parts) if room_parts else 'размещение уточняется'

    prompt = f"""Ты составляешь программу корпоративного тура в Японию для DMC Tozai Tours.

ТЕКУЩАЯ ПРОГРАММА (JSON):
{current_json}

ПАРАМЕТРЫ ГРУППЫ:
- Компания: {params['company_name']}
- Количество человек: {params['pax']}
- Состав номеров: {room_desc}
- Дней: {params['days']}
- Тип мероприятия: {params['event_type']}
- Отрасль/ЦА: {params.get('industry', '')}

КОММЕНТАРИЙ МЕНЕДЖЕРА — что изменить:
{corrections}

ЗАДАЧА: Скорректируй программу согласно комментарию. Сохрани ту же структуру JSON.
Не меняй то, что в комментарии не упомянуто.
Верни ТОЛЬКО валидный JSON без пояснений.

ТАЙМИНГ: Сохраняй конкретное время в каждой активности (08:30, 10:00, 13:00 и т.д.).

ПРАВИЛА ГАСТРОНОМИИ (соблюдай при корректировке ужинов):
- Обязательно включить: суши-ресторан, тэппаньяки ИЛИ якинику (японская кухня)
- Один ужин — шикарный шведский стол (buffet) в отеле или ресторане
- Один ужин — европейский ресторан (итальянский или французский)
- Одна неформальная гастрономическая история: рыбный рынок, стрит-фуд, местные деликатесы
- Каждый ужин описывай: тип ресторана, атмосфера, 2-3 блюда, ощущение"""

    response = client.messages.create(
        model='claude-opus-4-6',
        max_tokens=5000,
        messages=[{'role': 'user', 'content': prompt}]
    )

    text = response.content[0].text.strip()
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    return current_content  # fallback — возвращаем без изменений


def generate_program(params: dict) -> dict:
    """
    Генерирует текст программы КП через Claude.

    Возвращает dict:
      concept_title, concept_text, days[], hotel_description, closing_note
    """
    client = _get_client()

    event_map = {
        'Инсентив': 'инсентив-тур (мотивационная поездка, максимум впечатлений и уникального опыта)',
        'Конференция': 'корпоративная конференция с деловой программой',
        'Смешанный': 'смешанный формат: деловая конференция + инсентив-программа',
    }
    event_desc = event_map.get(params['event_type'], params['event_type'])

    twn = params.get('twn', 0)
    sgl = params.get('sgl', 0)
    room_parts = []
    if twn: room_parts.append(f'{twn} Twin-номеров (двухместных)')
    if sgl: room_parts.append(f'{sgl} Single-номеров (одноместных)')
    room_desc = ', '.join(room_parts) if room_parts else 'размещение уточняется'

    industry = params.get('industry') or 'корпоративные клиенты'
    industry_note_map = {
        'it': 'Особый акцент: технологическое лидерство Японии (TeamLab, роботы, Акихабара), параллели с цифровой трансформацией.',
        'фарма': 'Особый акцент: японская философия здоровья и долголетия, онсэн-культура, вэллнес-активности.',
        'банк': 'Особый акцент: эксклюзивный и приватный формат, закрытые клубы, церемониальность японского этикета.',
        'ритейл': 'Особый акцент: японская рыночная культура, уникальный потребительский опыт, Цукидзи, универмаги Гиндзы.',
    }
    industry_hint = ''
    for key, hint in industry_note_map.items():
        if key in industry.lower():
            industry_hint = hint
            break

    conf_note = ''
    if params.get('include_conference'):
        conf_note = f"- Конференц-блок запланирован на день {params.get('conference_day', 2)} программы"

    days = params['days']

    prompt = f"""Ты опытный MICE-специалист и копирайтер DMC компании Tozai Tours (Япония).
Составь текст для коммерческого предложения для корпоративной группы.

ПАРАМЕТРЫ:
- Компания клиента: {params['company_name']}
- Направление: Япония, Токио
- Количество человек: {params['pax']}
- Состав номеров: {room_desc}
- Количество дней: {days}
- Даты: {params.get('dates') or 'уточняются'}
- Тип мероприятия: {event_desc}
- Отрасль / целевая аудитория: {industry}
- Уровень отеля: {params['hotel_level']}
{conf_note}
- Особые пожелания: {params.get('special_requests') or 'нет'}
{industry_hint}

ЗАДАЧА: Верни ТОЛЬКО валидный JSON (без пояснений, без markdown) следующей структуры:

{{
  "concept_title": "Заголовок концепции (5-12 слов). Образный, с игрой слов. Пример: 'Японский импульс: там, где традиции встречают будущее'",
  "concept_text": "2-3 абзаца через \\n\\n (итого 180-220 слов). Почему Япония идеальна для ЭТОЙ аудитории и ЭТОГО формата мероприятия. Живо, образно, с конкретикой (ощущения, контрасты Японии, связь с профессиональной спецификой ЦА). Не канцелярский текст.",
  "days": [
    {{
      "day_num": 1,
      "title": "День 1. Прибытие в Токио",
      "morning": "08:30 — трансфер из аэропорта Ханэда/Нарита, первые впечатления от города, заселение в отель.",
      "afternoon": "13:00 — первое знакомство с Токио: конкретные районы, активности, атмосфера (3-4 предложения).",
      "evening": "19:30 — ужин: тип ресторана (кайсэки, якинику, тэппаньяки и т.д.), атмосфера, 2-3 блюда, ощущение (2-3 предложения)."
    }}
  ],
  "hotel_description": "2-3 предложения. Уровень отеля {params['hotel_level']} в Токио: атмосфера, сервис, расположение, что это даёт гостям.",
  "closing_note": "1-2 предложения. Финальный аккорд: какой след оставит эта поездка, что участники увезут с собой."
}}

ПРАВИЛА:
- Язык: только русский
- Стиль: профессиональный, живой, вдохновляющий, "вкусный" — никакого канцелярского языка
- Конкретика: реальные места Токио (Гиндза, Сибуя, Синдзюку, Асакуса, Одайба, Янака, Уэно и др.)
- День 1 всегда начинается с прилёта и трансфера в отель
- Последний день включает трансфер в аэропорт
- {'День ' + str(params.get('conference_day', 2)) + ': включи конференц-блок (утро — конференция в зале отеля, деловые сессии, нетворкинг-обед; вечер — праздничный ужин по итогам)' if params.get('include_conference') else 'Конференц-блока нет — делай упор на впечатления, командный дух, уникальный опыт'}
- Сгенерируй ровно {days} объектов в массиве days
- В тексте НЕ упоминай конкретные цены

ТАЙМИНГ: Для каждого дня добавь конкретное время к каждой активности (08:30, 10:00, 13:00 и т.д.) в поле morning/afternoon/evening.

ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА ГАСТРОНОМИИ:
- Обязательно включить: суши-ресторан, тэппаньяки ИЛИ якинику (японская кухня)
- Один ужин — шикарный шведский стол (buffet) в отеле или ресторане
- Один ужин — европейский ресторан (итальянский или французский)
- Одна неформальная гастрономическая история: рыбный рынок, стрит-фуд, местные деликатесы
- Каждый ужин описывай: тип ресторана, атмосфера, 2-3 блюда, ощущение"""

    response = client.messages.create(
        model='claude-opus-4-6',
        max_tokens=6000,
        messages=[{'role': 'user', 'content': prompt}]
    )

    text = response.content[0].text.strip()

    # Extract JSON (handle possible markdown code blocks)
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Fallback
    return {
        'concept_title': f'Япония для {params["company_name"]} — место силы вашей команды',
        'concept_text': 'Япония — страна, где древние традиции и ультрасовременные технологии существуют в идеальном балансе. Это уникальная среда для корпоративного мероприятия, которое запомнится на годы.',
        'days': [
            {
                'day_num': i + 1,
                'title': f'День {i + 1}',
                'morning': 'Программа утра.',
                'afternoon': 'Программа дня.',
                'evening': 'Программа вечера.',
            }
            for i in range(days)
        ],
        'hotel_description': f'Отель уровня {params["hotel_level"]} в самом сердце Токио — безупречный сервис и стратегическое расположение.',
        'closing_note': 'Япония оставляет след в каждом. Ваша команда вернётся с зарядом на годы вперёд.',
    }
