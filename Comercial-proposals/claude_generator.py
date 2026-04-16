"""
Генератор текстов КП через Claude API.
Создаёт концепцию, программу по дням и описание отеля на русском языке.
"""
import anthropic
import os
import json
import re
from pathlib import Path


_KB_PATH = Path(__file__).parent / 'knowledge_base' / 'activities_russia.json'


def _load_activities(params: dict, max_items: int = 8) -> list[dict]:
    """Загружает и фильтрует активности из базы под параметры запроса."""
    if not _KB_PATH.exists():
        return []

    with open(_KB_PATH, encoding='utf-8') as f:
        activities = json.load(f)

    activity_focus = [t.lower() for t in (params.get('activity_focus') or [])]
    pace = params.get('pace', 'Умеренный')
    event_type = params.get('event_type', '')
    industry = (params.get('industry') or '').lower()

    # Тег-фильтры по параметрам
    boost_tags: set[str] = set()
    if 'культура' in activity_focus or 'история' in activity_focus:
        boost_tags.update(['культура', 'традиции', 'история'])
    if 'гастрономия' in activity_focus:
        boost_tags.update(['гастрономия', 'суши', 'мясо', 'рынок'])
    if 'шопинг' in activity_focus or 'шоппинг' in activity_focus:
        boost_tags.add('шоппинг')
    if 'велнес' in activity_focus or 'онсэн' in activity_focus:
        boost_tags.update(['велнес', 'онсэн'])
    if 'технологии' in activity_focus:
        boost_tags.update(['технологии', 'wow'])
    if 'конференция' in event_type.lower():
        boost_tags.update(['конференц', 'тихий'])
    if any(k in industry for k in ['it', 'tech', 'технолог']):
        boost_tags.update(['технологии', 'wow'])
    if any(k in industry for k in ['фарма', 'медиц']):
        boost_tags.update(['велнес', 'онсэн'])

    # Исключить не-для-всех при расслабленном темпе
    exclude_tags: set[str] = set()
    if pace == 'Расслабленный':
        exclude_tags.update(['насыщенный', 'раннее утро'])
    if pace == 'Насыщенный':
        exclude_tags.update(['тихий'])

    def score(a: dict) -> int:
        tags = set(t.lower() for t in a.get('tags', []))
        if tags & exclude_tags:
            return -1
        s = len(tags & boost_tags) * 2
        if 'must-have' in tags:
            s += 3
        if 'не для всех' in tags:
            s -= 2
        return s

    scored = sorted(activities, key=score, reverse=True)
    return [a for a in scored if score(a) >= 0][:max_items]


def _format_activities_for_prompt(activities: list[dict]) -> str:
    """Форматирует список активностей для вставки в промпт."""
    if not activities:
        return ''
    lines = ['АКТИВНОСТИ ИЗ БАЗЫ (используй их в программе, адаптируй по контексту):']
    for a in activities:
        lines.append(f"• {a['name']} [{a['type']}] — {a['why_russia']} | Длительность: {a.get('duration_hours', '?')} ч.")
    return '\n'.join(lines)


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

    prompt = f"""Ты — эксперт по Японии с опытом 15+ лет в корпоративном туризме.
Составляешь программы с нестандартным взглядом как редакторы Monocle.
Выбираешь гастрономию как Anthony Bourdain — без туристических ловушек.
Культурные моменты отбираешь как куратор японского павильона на Венецианской биеннале.

Скорректируй программу корпоративного тура согласно комментарию менеджера.

ТЕКУЩАЯ ПРОГРАММА (JSON):
{current_json}

ПАРАМЕТРЫ ГРУППЫ:
- Компания: {params['company_name']}
- Количество человек: {params['pax']}
- Состав номеров: {room_desc}
- Дней: {params['days']}
- Тип мероприятия: {params['event_type']}
- Отрасль/ЦА: {params.get('industry', '')}
- Фокус активностей: {', '.join(params.get('activity_focus') or []) or 'не задан'}
- Темп: {params.get('pace', 'Умеренный')}

КОММЕНТАРИЙ МЕНЕДЖЕРА — что изменить:
{corrections}

ЗАДАЧА: Скорректируй программу согласно комментарию. Сохрани ту же структуру JSON.
Не меняй то, что в комментарии не упомянуто.
Верни ТОЛЬКО валидный JSON без пояснений.

ПУНКТУАЦИЯ (критично):
- Тире (—) только в определениях («X — это Y») и как разделитель расписания («09:00 — завтрак»)
- НЕ ставить тире вместо запятой или в середине описательных предложений
- Запрещено: «незабываемый», «уникальный», «погружение», «впечатления»
- Конкретика, факты, детали

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

    activity_focus = params.get('activity_focus') or []
    focus_note = f"- Фокус активностей: {', '.join(activity_focus)}" if activity_focus else ''
    pace = params.get('pace', 'Умеренный')
    pace_hints = {
        'Насыщенный': 'максимум активностей, плотный график, 4-5 объектов в день',
        'Умеренный': 'сбалансированный ритм, 2-3 активности в день, есть свободное время',
        'Расслабленный': 'неторопливый темп, 1-2 активности, много свободного времени и отдыха',
    }
    pace_note = f"- Темп программы: {pace} ({pace_hints.get(pace, '')})"

    # Загружаем релевантные активности из базы
    kb_activities = _load_activities(params, max_items=8)
    activities_block = _format_activities_for_prompt(kb_activities)

    conf_note = ''
    if params.get('include_conference'):
        conf_note = f"- Конференц-блок запланирован на день {params.get('conference_day', 2)} программы"

    days = params['days']

    prompt = f"""Ты — эксперт по Японии с опытом 15+ лет в корпоративном туризме.
Составляешь программы с нестандартным взглядом как редакторы Monocle — они всегда находят то, что мимо туристических карт.
Выбираешь гастрономию как Anthony Bourdain — никаких туристических ловушек, только места где едят сами японцы.
Отбираешь культурные моменты как куратор японского павильона на Венецианской биеннале — контраст, неожиданный угол, что-то что невозможно забыть.

Составь ЧЕРНОВИК-СХЕМУ программы корпоративного тура — для обсуждения с клиентом.

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
{focus_note}
{pace_note}
- Особые пожелания: {params.get('special_requests') or 'нет'}
{industry_hint}

{activities_block}

ЗАДАЧА: Верни ТОЛЬКО валидный JSON (без пояснений, без markdown):

{{
  "concept_title": "Заголовок концепции — яркий, образный, 5–8 слов. Пример: «Токио без фильтров: скорость, вкус, тишина»",
  "days": [
    {{
      "day_num": 1,
      "title": "День 1 — название-образ (3–5 слов, не просто «Прибытие»)",
      "morning": "ЧЧ:ММ — Место: 1 строчка с конкретикой",
      "afternoon": "ЧЧ:ММ — Место: 1 строчка с конкретикой",
      "evening": "ЧЧ:ММ — Ужин: тип + 1 деталь"
    }}
  ]
}}

ФОРМАТ КАЖДОГО ПОЛЯ morning/afternoon/evening — строго одна строчка:
«ЧЧ:ММ — [Место/Активность]: [1 яркая деталь или неожиданный угол]»
Примеры:
  «09:00 — TeamLab Planets: искусство, в которое входишь по щиколотку в воду»
  «14:30 — Янака: токийская деревня, которой 300 лет — без туристов и без суеты»
  «20:00 — Тэппаньяки в Синдзюку: повар, огонь, 8 гостей — и молчать невозможно»

ПРАВИЛА:
- Язык: только русский
- Никакой воды. Запрещено: «незабываемый», «уникальный», «погружение», «впечатления», «незабываемые моменты»
- Конкретика: реальные места, цифры, детали, которые агент может запомнить и пересказать клиенту
- Реальные места Токио (Гиндза, Сибуя, Синдзюку, Асакуса, Одайба, Янака, Уэно, Дайканяма, Накамегуро и др.)
- Названия дней — образные, не «День 1. Прибытие», а «День 1 — Токио с первого взгляда»
- День 1: утро — трансфер из аэропорта и заселение; остальное — по программе
- Последний день: вечер — трансфер в аэропорт
- {'День ' + str(params.get('conference_day', 2)) + ': утро — конференция, деловые сессии; вечер — праздничный ужин' if params.get('include_conference') else 'Конференц-блока нет'}
- Сгенерируй ровно {days} объектов в days
- Цены не упоминать

ГАСТРОНОМИЯ (распредели по дням):
- Один ужин: суши или якинику / тэппаньяки
- Один ужин: буфет в отеле или панорамный ресторан
- Один ужин: европейский (итальянский или французский)
- Один момент: рыбный рынок, стрит-фуд или деликатесы"""

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
        'concept_title': f'Япония для {params["company_name"]}',
        'days': [
            {
                'day_num': i + 1,
                'title': f'День {i + 1}',
                'morning': 'Трансфер и заселение.',
                'afternoon': 'Программа дня.',
                'evening': 'Ужин.',
            }
            for i in range(days)
        ],
    }


def enrich_texts(params: dict, program: dict) -> dict:
    """
    Второй вызов Claude — только тексты для PPT.
    Принимает утверждённую структуру программы.
    Возвращает program с добавленными полями:
    concept_text, day.description, hotel_description, closing_note, highlights.
    """
    client = _get_client()

    # Формируем читаемый пересказ программы
    days_summary = []
    for d in program.get('days', []):
        days_summary.append(
            f"День {d['day_num']} «{d.get('title', '')}»:\n"
            f"  Утро: {d.get('morning', '')}\n"
            f"  День: {d.get('afternoon', '')}\n"
            f"  Вечер: {d.get('evening', '')}"
        )
    days_text = '\n\n'.join(days_summary)

    industry = params.get('industry') or 'корпоративные клиенты'
    event_map = {
        'Инсентив': 'инсентив-тур',
        'Конференция': 'корпоративная конференция',
        'Смешанный': 'конференция + инсентив',
    }
    event_desc = event_map.get(params.get('event_type', ''), params.get('event_type', ''))

    prompt = f"""Ты — копирайтер для luxury travel. Специализация: корпоративный туризм, MICE, русскоязычная аудитория.
Твой стиль: точность редактора National Geographic плюс живость Condé Nast Traveller Russia.
Не пишешь рекламно и не продаёшь в лоб. Пишешь так, чтобы агент сказал клиенту: «Слушай, а ты знаешь, что...»

УТВЕРЖДЁННАЯ ПРОГРАММА:
{days_text}

ГРУППА:
- Компания: {params['company_name']}
- {params['pax']} человек, {event_desc}
- Отрасль: {industry}
- Отель: {params.get('hotel_level', '5*')} в Токио
- Даты: {params.get('dates') or 'уточняются'}

ЗАДАЧА: написать тексты для слайдов презентации. Верни ТОЛЬКО валидный JSON:

{{
  "concept_title": "5–8 слов. Образный заголовок всего тура для этой конкретной группы. Не банальный.",
  "concept_text": "3–4 предложения. Почему Япония и почему для этих людей. Один неожиданный факт или контраст. Коротко, ритмично. Без «незабываемого» и «погружения».",
  "day_descriptions": {{
    "1": "2–3 предложения. Атмосфера дня, что почувствуют. Конкретный образ.",
    "2": "...",
    "3": "..."
  }},
  "hotel_description": "2–3 предложения. Атмосфера, расположение, одна деталь которая запомнится.",
  "closing_note": "1–2 предложения. Финальный образ. Не мотивационный плакат.",
  "highlights": [
    {{
      "title": "Название — 2–4 слова, без глагола",
      "category": "Гастрономия / Культура / Технологии / Природа / Велнес",
      "day_ref": "День X",
      "description": "5–6 предложений. Что это такое, история места, почему работает для корпоративной группы, один факт который агент запомнит. Сенсорная деталь: запах, звук, свет.",
      "photo_query": "english photo search query, 3–5 words, specific place or scene"
    }}
  ]
}}

АУДИТОРИЯ И ТОН:
Читатель — директор по маркетингу или HR-директор крупной компании. Он летал бизнес-классом, был в хороших отелях. Его не удивишь «экзотикой». Пиши как умный собеседник, который знает Японию изнутри и рассказывает о ней спокойно и точно. Тон: сдержанное восхищение, уверенность, негромкое изящество.

ЗАПРЕЩЕНО:
- Физически грубые образы: «ритм бьёт в рёбра», «пот», «адреналин», «драйв», «захватывает дух» в спортивном смысле
- Восклицательные интонации и пафос
- Туристические штампы: «сердце города», «колыбель культуры», «перенесёт вас в другую эпоху»
- Слова: «незабываемый», «уникальный», «погружение», «впечатления», «атмосфера» (без конкретики), «магия»

РАЗРЕШЕНО И ПРИВЕТСТВУЕТСЯ:
- Тихие, точные образы: свет, тишина, запах дерева, медленный жест, пауза
- Конкретные факты с цифрами: «230 мишленовских ресторанов», «1300 лет», «47-й этаж»
- Наблюдение от первого лица (но без «я»): «В шесть утра здесь никого нет. Только рыбные прилавки и запах льда.»
- Короткие предложения, которые дают паузу для осмысления

ПУНКТУАЦИЯ:
- Тире только в определениях («Omotenashi — это философия») и расписании («09:00 — завтрак»)
- Никаких тире вместо запятой и в середине предложений
- day_descriptions должны содержать ключ для каждого дня из программы (1, 2, 3...)"""

    response = client.messages.create(
        model='claude-opus-4-6',
        max_tokens=4000,
        messages=[{'role': 'user', 'content': prompt}]
    )

    text = response.content[0].text.strip()
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            enriched = json.loads(json_match.group())
            # Вливаем тексты в структуру программы
            result = dict(program)
            result['concept_title']    = enriched.get('concept_title', program.get('concept_title', ''))
            result['concept_text']     = enriched.get('concept_text', '')
            result['hotel_description'] = enriched.get('hotel_description', '')
            result['closing_note']     = enriched.get('closing_note', '')
            result['highlights']       = enriched.get('highlights', [])

            day_descs = enriched.get('day_descriptions', {})
            for day in result.get('days', []):
                key = str(day['day_num'])
                day['description'] = day_descs.get(key, '')

            return result
        except json.JSONDecodeError:
            pass

    return program  # fallback — возвращаем без обогащения
