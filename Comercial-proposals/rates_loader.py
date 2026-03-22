"""
Загрузчик тарифов из Japan-rates-sample.xlsx
Масштабирует цены под заданное количество человек
"""
import openpyxl
from pathlib import Path

BASE_DIR = Path(__file__).parent
SAMPLE_PAX = 30  # Кол-во человек в исходном файле

# Перевод названий сервисов на русский
SERVICE_RU = {
    'Guide': 'Гид (полный день)',
    'Large-sized bus': 'Автобус (большой)',
    'Lunch': 'Обед',
    'Drinks': 'Напитки',
    'Entrance tickets': 'Входные билеты',
    'Dinner': 'Ужин',
    'Dinner for a guide': 'Ужин для гида',
    'Dinner for an assistant': 'Ужин для ассистента',
    'Lunch and dinner for a guide': 'Обед и ужин для гида',
    'Lunch and dinner for an assistant': 'Обед и ужин для ассистента',
    'Rental of conference room, 14:00-16:00': 'Аренда конференц-зала 14:00–16:00',
    'Interpreter': 'Переводчик',
    'Conference room rental, 09:00-16:00': 'Аренда конференц-зала 09:00–16:00',
    'Coffee break': 'Кофе-брейк',
    'Operators': 'Операторы',
    'Whispering system': 'Система синхронного перевода',
    'LED Screen': 'LED-экран (аренда)',
    'Additional equipment': 'Дополнительное оборудование',
    'Roll-ups': 'Ролл-апы',
    'Assistant': 'Ассистент (полный день)',
    'Lunch for interpreters': 'Обед для переводчиков',
}

# Перевод названий дней
DAY_RU = {
    'Day 1, Arrival to Haneda  airport  and transfer to the hotel': 'День 1. Прилёт в аэропорт Ханэда, трансфер в отель.',
    'Day 2, Tokyo': 'День 2. Токио.',
    'Day 3. Tokyo': 'День 3. Токио.',
    'Day 4.  Tokyo and transfer to Haneda Airport': 'День 4. Токио. Трансфер в аэропорт Ханэда.',
    'Other': 'Прочее',
}

# Перевод комментариев
COMMENT_RU = {
    '9:00-21:00': '9:00–21:00',
    '9:00-16:00': '9:00–16:00',
    '16:00-21:00': '16:00–21:00',
    '10:00-20:00': '10:00–20:00',
    'glass of  wine': 'бокал вина',
    'Premium restaurant': 'премиальный ресторан',
    '2 glasses of wine': '2 бокала вина',
    'wine glass': 'бокал вина',
    'Grass of wine': 'бокал вина',
    'Sushi restaurant': 'суши-ресторан',
    'Museum of Digital Arts': 'Музей цифрового искусства (teamLab)',
    'In the same room as conference': 'в зале конференции',
    'Free soft drinks, 1.5h': 'безалкогольные напитки, 1,5 ч.',
    'Consequitive interpretation, 3h': 'последовательный перевод, 3 ч.',
    'Simultaneous interpretation, 6h': 'синхронный перевод, 6 ч.',
    '222 sq.m, Basic sound equipment, screen 120 inches, projector, 4 mikes':
        '222 кв.м, базовое аудиооборудование, экран 120", проектор, 4 микрофона',
    'basic sound eqipment, screen, projector, 3 mikes':
        'базовое аудиооборудование, экран, проектор, 3 микрофона',
    'coffee/tea, sandwiches': 'кофе/чай, сэндвичи',
    'For 40 pax, preliminary': 'для 40 чел., предварительно',
    'Rental, preliminary': 'аренда, предварительно',
    'Navigation,sound, wi-fi, price is not available': 'навигация, звук, Wi-Fi — цена уточняется',
    '850x2000': '850×2000 мм',
}

CONFERENCE_KEYWORDS = [
    'conference room', 'interpreter', 'whispering', 'led screen',
    'operator', 'coffee break', 'lunch for interpreter',
]


def _is_conference_item(service: str) -> bool:
    s = service.lower()
    return any(kw in s for kw in CONFERENCE_KEYWORDS)


def _translate_service(name: str) -> str:
    name = name.strip()
    return SERVICE_RU.get(name, name)


def _translate_day(name: str) -> str:
    name = name.strip()
    return DAY_RU.get(name, name)


def _translate_comment(comment: str) -> str:
    if not comment:
        return ''
    comment = comment.strip()
    return COMMENT_RU.get(comment, comment)


def load_japan_rates(pax: int, days_count: int, include_conference: bool = True) -> list:
    """
    Возвращает список сервисов из Japan-rates-sample.xlsx,
    масштабированных под pax человек и days_count дней.

    Структура каждого элемента:
      {'type': 'day_header', 'day': str, 'day_num': int}
    или
      {'type': 'service', 'day': str, 'day_num': int,
       'service': str, 'q': int, 'days': int,
       'price_per_unit': float, 'total': float, 'comments': str}
    """
    wb = openpyxl.load_workbook(BASE_DIR / 'Japan-rates-sample.xlsx', data_only=True)
    ws = wb.active

    result = []
    current_day = None
    current_day_num = 0
    in_other = False

    for row in ws.iter_rows(min_row=9, values_only=True):
        service_raw = row[2]
        q_raw = row[3]
        n_days = row[4]
        price = row[5]
        comment_raw = row[7]

        if not service_raw:
            continue

        service_raw = str(service_raw).strip()
        if not service_raw:
            continue

        # --- Day header ---
        is_day_header = service_raw.startswith('Day') or service_raw == 'Other'
        if is_day_header:
            if service_raw == 'Other':
                in_other = True
                current_day = 'Other'
                current_day_num += 1
            else:
                in_other = False
                current_day_num += 1
                if current_day_num > days_count:
                    # For "Other" section — still include it even after days_count
                    # We'll hit 'Other' row separately
                    continue
                current_day = service_raw

            result.append({
                'type': 'day_header',
                'day': _translate_day(service_raw),
                'day_num': current_day_num,
            })
            continue

        # --- Skip if no day context or beyond requested days ---
        if current_day is None:
            continue
        if not in_other and current_day_num > days_count:
            continue

        # --- Skip zero-price items ---
        if price is None or price == 0:
            continue

        # --- Skip conference items if not needed ---
        if _is_conference_item(service_raw) and not include_conference:
            continue

        # --- Scale quantity ---
        if q_raw == SAMPLE_PAX:
            new_q = pax
        elif q_raw == SAMPLE_PAX + 1:
            new_q = pax + 1
        else:
            new_q = q_raw if q_raw is not None else 1

        n_days = n_days if n_days else 1
        total = new_q * n_days * price

        result.append({
            'type': 'service',
            'day': _translate_day(current_day),
            'day_num': current_day_num,
            'service': _translate_service(service_raw),
            'q': new_q,
            'days': n_days,
            'price_per_unit': round(price, 2),
            'total': round(total, 2),
            'comments': _translate_comment(str(comment_raw) if comment_raw else ''),
        })

    return result
