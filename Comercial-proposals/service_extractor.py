"""
Извлекает сервисы из утверждённой программы для формирования сметы.

Логика:
  1. Для каждого дня разбираем текст morning/afternoon/evening
  2. По ключевым словам определяем платные позиции
  3. Ищем цену в прайс-листе (Japan-rates-sample.xlsx)
  4. Если цены нет → ставим 0 (менеджер заполнит вручную)
"""
import re
from rates_loader import load_price_dict

# ── Ключевые слова → (название сервиса, тип количества) ───────────────────────
# qty_type: 'pax' | 'pax+1' | '1'
# Порядок важен: более конкретные совпадения — первыми

ACTIVITY_KEYWORDS = [
    # Транспорт
    (['синкансэн', 'shinkansen'],
     'Синкансэн (билет)',                    'pax'),
    (['романсукар', 'romancecar'],
     'Romancecar (билет)',                   'pax'),

    # Активности с билетами
    (['teamlab'],
     'Входные билеты: TeamLab Planets',      'pax'),
    (['тодайдзи', 'todaiji'],
     'Входные билеты: Храм Тодайдзи',        'pax'),
    (['кинкакудзи', 'kinkakuji', 'золотой павильон'],
     'Входные билеты: Кинкакудзи',           'pax'),
    (['рёандзи', 'ryoanji'],
     'Входные билеты: Сад Рёандзи',          'pax'),
    (['фусими инари', 'fushimi inari'],
     'Входные билеты: Фусими Инари',         'pax'),

    # Мастер-классы
    (['мастер-класс каллиграф', 'каллиграф'],
     'Мастер-класс: каллиграфия',            'pax'),
    (['мастер-класс икэбан', 'икэбан'],
     'Мастер-класс: икэбана',                'pax'),
    (['мастер-класс тайко', 'тайко'],
     'Мастер-класс: тайко',                  'pax'),
    (['чайная церемония'],
     'Чайная церемония',                     'pax'),
    (['мастер-класс'],
     'Мастер-класс (опция)',                 'pax'),

    # Питание (ПОСЛЕ активностей, чтобы "обед у Тайко" не попал в обед)
    (['обед'],
     'Обед',                                 'pax'),
    (['ужин'],
     'Ужин',                                 'pax'),
    (['напитки', 'drinks'],
     'Напитки',                              'pax'),
]

# Конференц-сервисы — добавляются целым блоком в день конференции
CONFERENCE_SERVICES = [
    ('Аренда конференц-зала 09:00–16:00', '1'),
    ('Переводчик',                         '1'),
    ('Кофе-брейк',                         'pax'),
    ('Ассистент (полный день)',             '1'),
    ('Обед для переводчиков',              '1'),
]


def _qty(qty_type: str, pax: int) -> int:
    if qty_type == 'pax':
        return pax
    if qty_type == 'pax+1':
        return pax + 1
    if qty_type == 'pax+2':
        return pax + 2
    try:
        return int(qty_type)
    except ValueError:
        return 1


def _svc(service_name: str, qty: int, days_count: int,
         prices: dict, comment: str = '') -> dict:
    """Формирует строку сервиса для Excel."""
    price = prices.get(service_name, 0)
    note = comment
    if not note and price == 0:
        note = 'цена уточняется'
    return {
        'type':            'service',
        'day':             '',          # заполняется в extract_services
        'service':         service_name,
        'q':               qty,
        'days':            days_count,
        'price_per_unit':  price,
        'total':           round(qty * days_count * price, 2),
        'comments':        note,
    }


def extract_services(content: dict, params: dict) -> list:
    """
    Разбирает утверждённую программу и возвращает список сервисов
    в том же формате, что load_japan_rates() — day_header + service записи.
    """
    prices  = load_price_dict()
    pax     = params['pax']
    days    = content.get('days', [])
    n_days  = len(days)
    conf_day = params.get('conference_day', 2) if params.get('include_conference') else -1

    result = []

    for day_data in days:
        day_num   = day_data.get('day_num', 1)
        title     = day_data.get('title', f'День {day_num}')
        is_first  = (day_num == 1)
        is_last   = (day_num == n_days)
        is_conf   = (day_num == conf_day)

        # ── Заголовок дня ──────────────────────────────────────────────────────
        result.append({'type': 'day_header', 'day': title, 'day_num': day_num})

        # Полный текст дня (нижний регистр для поиска)
        full_text = ' '.join([
            day_data.get('morning', ''),
            day_data.get('afternoon', ''),
            day_data.get('evening', ''),
        ]).lower()

        has_shinkansen = any(kw in full_text for kw in ['синкансэн', 'shinkansen'])
        has_afternoon  = len(day_data.get('afternoon', '').strip()) > 20

        # ── Трансфер ───────────────────────────────────────────────────────────
        if is_first:
            s = _svc('Трансфер из аэропорта', 1, 1, prices, 'прилёт')
            s['day'] = title
            result.append(s)

        if is_last:
            s = _svc('Трансфер в аэропорт', 1, 1, prices, 'вылет')
            s['day'] = title
            result.append(s)

        # ── Гид и автобус ──────────────────────────────────────────────────────
        # День 1: гид только если есть программа после заселения
        # Последний день: гид только если есть программа до вылета
        need_guide = True
        if is_first and not has_afternoon:
            need_guide = False

        if need_guide:
            s = _svc('Гид (полный день)', pax + 1, 1, prices)
            s['day'] = title
            result.append(s)

            # Ужин для гида — только если в программе есть ужин
            if 'ужин' in full_text:
                s = _svc('Ужин для гида', 1, 1, prices)
                s['day'] = title
                result.append(s)
            elif 'обед' in full_text:
                s = _svc('Обед и ужин для гида', 1, 1, prices)
                s['day'] = title
                result.append(s)

        # Автобус — всегда кроме дней когда всё перемещение на синкансэне
        # (на синкансэн-день автобус всё равно нужен до/от вокзала)
        s = _svc('Автобус (большой)', 1, 1, prices)
        s['day'] = title
        result.append(s)

        # ── Синкансэн ──────────────────────────────────────────────────────────
        if has_shinkansen:
            s = _svc('Синкансэн (билет)', pax, 1, prices)
            s['day'] = title
            result.append(s)

        # ── Активности по ключевым словам ──────────────────────────────────────
        used = set()
        for keywords, svc_name, qty_type in ACTIVITY_KEYWORDS:
            if any(kw in full_text for kw in keywords):
                if svc_name not in used:
                    used.add(svc_name)
                    s = _svc(svc_name, _qty(qty_type, pax), 1, prices)
                    s['day'] = title
                    result.append(s)

        # ── Конференц-блок ──────────────────────────────────────────────────────
        if is_conf:
            for svc_name, qty_type in CONFERENCE_SERVICES:
                s = _svc(svc_name, _qty(qty_type, pax), 1, prices)
                s['day'] = title
                result.append(s)

    # ── Дополнительные опции (Прочее) — пустой раздел как placeholder ──────────
    result.append({'type': 'day_header', 'day': 'Прочее', 'day_num': n_days + 1})

    return result
