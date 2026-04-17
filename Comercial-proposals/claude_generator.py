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

# ── Маршруты ──────────────────────────────────────────────────────────────────

ROUTES = {
    'tokyo': {
        'label': 'Только Токио',
        'cities': ['Токио'],
        'min_days': 2,
        'logistics': '',
        'city_notes': 'Вся программа в Токио и пригородах.',
    },
    'tokyo_hakone': {
        'label': 'Токио + Хаконэ',
        'cities': ['Токио', 'Хаконэ'],
        'min_days': 4,
        'logistics': 'Токио → Хаконэ: 1ч 30мин на Romancecar Odakyu. Хаконэ → Токио: тот же маршрут.',
        'city_notes': 'Токио — основная база. Хаконэ — 1-2 ночи: Фудзи, онсэн, горы. Переезд выделяется отдельным утром.',
    },
    'tokyo_kyoto': {
        'label': 'Токио + Киото',
        'cities': ['Токио', 'Киото'],
        'min_days': 5,
        'logistics': 'Токио → Киото: 2ч 15мин на Синкансэн Нодзоми. Переезд — отдельное утро.',
        'city_notes': 'Токио 2-3 дня, Киото 2-3 дня. Переезд показывать как активность (Синкансэн — сам по себе опыт).',
    },
    'tokyo_kyoto_nara': {
        'label': 'Токио + Киото + Нара',
        'cities': ['Токио', 'Киото', 'Нара'],
        'min_days': 6,
        'logistics': 'Токио → Киото: 2ч 15мин (Синкансэн). Киото → Нара: 45мин (Kintetsu). Нара — однодневная поездка из Киото, ночевка там же.',
        'city_notes': 'Токио 2-3 дня, Киото база 2-3 дня, Нара однодневный выезд из Киото.',
    },
    'tokyo_hakone_kyoto': {
        'label': 'Токио + Хаконэ + Киото',
        'cities': ['Токио', 'Хаконэ', 'Киото'],
        'min_days': 6,
        'logistics': 'Токио → Хаконэ: 1ч 30мин. Хаконэ → Киото: через Одавара на Синкансэн ~2ч 30мин.',
        'city_notes': 'Токио 2 дня, Хаконэ 1 ночь (Фудзи + онсэн), Киото 2-3 дня.',
    },
    'tokyo_hakone_kyoto_nara': {
        'label': 'Токио + Хаконэ + Киото + Нара',
        'cities': ['Токио', 'Хаконэ', 'Киото', 'Нара'],
        'min_days': 7,
        'logistics': 'Токио → Хаконэ: 1ч 30мин. Хаконэ → Киото: ~2ч 30мин. Киото → Нара: 45мин. Нара — выезд из Киото.',
        'city_notes': 'Полный маршрут. Хаконэ 1 ночь, Киото база 2-3 дня, Нара однодневный выезд.',
    },
}

DEFAULT_ROUTE = 'tokyo'


def detect_season(dates_str: str) -> tuple:
    """
    Определяет сезон по строке с датами.
    Возвращает (season, description, photo_style).
    season: 'spring' | 'summer' | 'autumn' | 'winter' | 'unknown'
    """
    if not dates_str:
        return 'unknown', '', ''

    text = dates_str.lower()

    seasons = [
        ('spring', ['март', 'апрел', 'май', 'мая', 'march', 'april', 'may', '-03-', '-04-', '-05-', '/03', '/04', '/05'],
         'Сезон: весна. Сакура цветёт конец марта — середина апреля. Тепло, много туристов в период цветения.',
         'sakura cherry blossom spring'),
        ('summer', ['июн', 'июл', 'август', 'june', 'july', 'august', '-06-', '-07-', '-08-', '/06', '/07', '/08'],
         'Сезон: лето. Жарко и влажно, сезон дождей в июне-июле. Фестивалей много. Зелень буйная.',
         'Japan summer green lush'),
        ('autumn', ['сентябр', 'октябр', 'ноябр', 'september', 'october', 'november', '-09-', '-10-', '-11-', '/09', '/10', '/11'],
         'Сезон: осень. Момидзи — алые клёны в октябре-ноябре. Прохладно, сухо. Лучший сезон для групп.',
         'Japan autumn momiji red leaves'),
        ('winter', ['декабр', 'январ', 'феврал', 'december', 'january', 'february', '-12-', '-01-', '-02-', '/12', '/01', '/02'],
         'Сезон: зима. Холодно. Лучший вид на Фудзи — небо чистое. Онсэны в приоритете.',
         'Japan winter snow Mount Fuji'),
    ]

    for season, keywords, description, photo_style in seasons:
        if any(kw in text for kw in keywords):
            return season, description, photo_style

    return 'unknown', '', 'Japan landscape'


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

    season, season_desc, season_photo = detect_season(params.get('dates', ''))

    season_note = f"""
СЕЗОННОСТЬ (строго соблюдать):
{season_desc}
- Активности, описания и примеры должны соответствовать сезону
- Весна: сакура уместна; Осень: момидзи уместен; Лето и зима: ни сакуру, ни момидзи не упоминать
- Гастрономия тоже сезонная: весна — тай-мэши и молодые овощи; осень — мацутакэ и сладкий картофель; зима — набэ и фугу; лето — унаги и холодный рамен
""" if season != 'unknown' else ''

    days = params['days']

    route_key = params.get('route', DEFAULT_ROUTE)
    route = ROUTES.get(route_key, ROUTES[DEFAULT_ROUTE])
    cities_str = ' → '.join(route['cities'])

    arrival   = params.get('arrival_city', 'Токио (Нарита / Ханэда)').strip()
    departure = params.get('departure_city', 'Токио (Нарита / Ханэда)').strip()

    openjaw_note = ''
    if departure and arrival and departure != arrival:
        openjaw_note = f"""
OPEN-JAW МАРШРУТ (прилёт и вылет из разных городов):
- Прилёт: {arrival}
- Вылет: {departure}
Это значит маршрут строится по прямой, без возврата в начальный город.
Если прилёт Токио, вылет Осака → порядок: Токио → [другие города] → Осака.
Последний день заканчивается в городе вылета или рядом с ним.
Осака при вылете оттуда можно добавить как финальный город (1 ночь): Дотонбори, уличная еда, закат над Осакским замком.
"""
    elif arrival:
        openjaw_note = f"- Прилёт и вылет: {arrival}"

    route_block = f"""
МАРШРУТ: {cities_str}
{openjaw_note}
Логистика: {route['logistics']}
Заметки: {route['city_notes']}
""" if len(route['cities']) > 1 else f"МАРШРУТ: Токио\n{openjaw_note}"

    prompt = f"""Ты — эксперт по Японии с опытом 15+ лет в корпоративном туризме.
Составляешь программы с нестандартным взглядом как редакторы Monocle — они всегда находят то, что мимо туристических карт.
Выбираешь гастрономию как Anthony Bourdain — никаких туристических ловушек, только места где едят сами японцы.
Отбираешь культурные моменты как куратор японского павильона на Венецианской биеннале — контраст, неожиданный угол, что-то что невозможно забыть.

Составь ЧЕРНОВИК-СХЕМУ программы корпоративного тура — для обсуждения с клиентом.

ПАРАМЕТРЫ:
- Компания клиента: {params['company_name']}
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

{route_block}

{activities_block}

ЗАДАЧА: Верни ТОЛЬКО валидный JSON (без пояснений, без markdown):

{{
  "concept_title": "Заголовок концепции — 5–8 слов, привязан к отрасли и компании. Пример для IT: «Токио: инженерное мышление в масштабе города»",
  "days": [
    {{
      "day_num": 1,
      "title": "День N — [конкретное место или активность] + [одна деталь-обещание]. Пример: «День 2 — рынок Цукидзи в 6 утра и тишина сада Хамарикю»",
      "morning": "ЧЧ:ММ — (~ХХ мин от отеля) Место: конкретика одной строкой",
      "afternoon": "ЧЧ:ММ — (~ХХ мин от предыдущей точки) Место: конкретика одной строкой",
      "evening": "ЧЧ:ММ — (~ХХ мин) Ужин: тип ресторана + 1 деталь"
    }}
  ]
}}

ФОРМАТ КАЖДОГО ПОЛЯ morning/afternoon/evening — строго одна строчка:
«ЧЧ:ММ — (~ХХ мин) [Место/Активность]: [1 конкретная деталь]»
Примеры:
  «09:00 — (~20 мин от отеля) TeamLab Planets: искусство, в которое входишь по щиколотку в воду»
  «14:30 — (~15 мин) Янака: токийская деревня, которой 300 лет, без туристов и суеты»
  «20:00 — (~10 мин) Тэппаньяки в Синдзюку: повар готовит в метре от гостей, восемь человек за столом»

ПРАВИЛА ПРОГРАММЫ:
- Язык: только русский
- Конкретика: реальные места, цифры, время в пути
- Заголовок дня — конкретное обещание. «День 3 — тишина сада Рёандзи» лучше чем «День 3 — Киото сквозь века»
- День 1: утро — трансфер из аэропорта и заселение; остальное по программе
- Последний день: вечер — трансфер в аэропорт
- В каждой строке morning/afternoon/evening указывай город в скобках: «(Токио)», «(Киото)», «(Нара)», «(Хаконэ)»

МУЛЬТИГОРОД (если маршрут включает несколько городов):
- День переезда: утро — Синкансэн или поезд с указанием времени в пути; после прибытия — 1-2 активности в новом городе
- Синкансэн сам по себе — часть программы: «09:00 — Синкансэн Нодзоми Токио→Киото (~2ч 15мин): панорамный вид на Фудзи из окна»
- Нара всегда однодневный выезд из Киото, ночевка в Киото
- Хаконэ: 1 ночь в рёкане с онсэном — отдельный день
- Распредели дни между городами реалистично исходя из {days} дней
- {'День ' + str(params.get('conference_day', 2)) + ': утро — конференция, деловые сессии; вечер — праздничный ужин' if params.get('include_conference') else 'Конференц-блока нет'}
- Сгенерируй ровно {days} объектов в days
- Цены не упоминать

ПЕРСОНАЛИЗАЦИЯ ПОД ОТРАСЛЬ (обязательно):
Программа должна отражать профессиональный контекст группы — не только в тексте, но и в выборе активностей.
- IT / технологии: включи TeamLab, роботизированные производства или Акихабара, проведи параллель с инженерной культурой Японии
- Фарма / медицина: онсэн, японская кухня долголетия, сад камней, утренняя практика
- Банки / финансы: закрытый чайный клуб, церемониальность японского этикета, эксклюзивный омакасе
- Ритейл: рынок Цукидзи, универмаги Исэтан / Гиндза Сикс, японский мерчандайзинг
- Если отрасль не указана: сделай программу универсальной, но содержательной

{season_note}
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
    season, season_desc, season_photo = detect_season(params.get('dates', ''))
    route_key = params.get('route', DEFAULT_ROUTE)
    route = ROUTES.get(route_key, ROUTES[DEFAULT_ROUTE])
    cities_str = ' → '.join(route['cities'])
    arrival   = params.get('arrival_city', '').strip()
    departure = params.get('departure_city', '').strip()
    flight_note = f"Прилёт: {arrival}, вылет: {departure}" if arrival or departure else ''

    prompt = f"""Ты — копирайтер для luxury travel. Специализация: корпоративный туризм, MICE, русскоязычная аудитория.
Твой стиль: точность редактора National Geographic плюс живость Condé Nast Traveller Russia.
Не пишешь рекламно и не продаёшь в лоб. Пишешь так, чтобы агент сказал клиенту: «Слушай, а ты знаешь, что...»

УТВЕРЖДЁННАЯ ПРОГРАММА:
{days_text}

ГРУППА:
- Компания: {params['company_name']}
- {params['pax']} человек, {event_desc}
- Отрасль: {industry}
- Маршрут: {cities_str}
- {flight_note}
- Отель: {params.get('hotel_level', '5*')}
- Даты: {params.get('dates') or 'уточняются'}
- Особые пожелания: {params.get('special_requests') or 'нет'}

СЕЗОННОСТЬ (строго):
{season_desc if season_desc else 'Даты не указаны — используй нейтральные образы без привязки к сезону.'}
- Тексты и photo_query для хайлайтов должны соответствовать сезону
- Никаких сакур в ноябре, никаких «осенних листьев» в апреле
- photo_query для сезонных слайдов: «{season_photo}» или более конкретный вариант

КАК ИСПОЛЬЗОВАТЬ ОТРАСЛЬ:
Каждый текст должен содержать хотя бы одну точку соприкосновения с профессиональным миром этих людей.
Не «Япония учит нас замедляться» — это для всех. А «Японские инженеры создали этот сад по тем же принципам, по которым вы пишете код: ничего лишнего» — это для IT.
Найди связь между тем, что они видят в Японии, и тем, чем занимаются каждый день.

ЗАДАЧА: написать тексты для слайдов презентации. Верни ТОЛЬКО валидный JSON:

{{
  "concept_title": "5–8 слов. Заголовок привязан к отрасли и компании — не про Японию вообще, а про то, что получат именно эти люди. Пример для IT: «Токио: инженерное мышление в масштабе города»",
  "concept_text": "3–4 предложения. Обязательно: упомяни отрасль или профессиональный контекст компании. Один неожиданный факт о Японии, который резонирует с их работой. Коротко, ритмично. Без «незабываемого» и «погружения».",
  "day_descriptions": {{
    "1": "2–3 предложения. Конкретный образ дня — что увидят, услышат, почувствуют. Одна деталь связанная с отраслью или характером группы.",
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
      "description": "5–6 предложений. Что это такое, история места, почему это важно для людей из этой отрасли, один факт который агент запомнит и перескажет клиенту.",
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
