"""
Генератор PPT-презентации для КП.
Структура: Титул → Концепция → Дни программы → Размещение
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pathlib import Path
import io

BASE_DIR = Path(__file__).parent

# ── Цвета ────────────────────────────────────────────────────────────────────
class C:
    RED   = RGBColor(0xBC, 0x00, 0x2D)   # Японский красный
    DARK  = RGBColor(0x1C, 0x1C, 0x1E)   # Почти чёрный
    GOLD  = RGBColor(0xC5, 0xA0, 0x28)   # Золото
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    LIGHT = RGBColor(0xF7, 0xF5, 0xF2)   # Очень светлый беж
    GRAY  = RGBColor(0x77, 0x77, 0x77)
    MGRAY = RGBColor(0xDD, 0xDD, 0xDD)


# ── Утилиты ──────────────────────────────────────────────────────────────────

def _bg(slide, color: RGBColor):
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = color


def _rect(slide, left, top, width, height, fill: RGBColor, line=False):
    shp = slide.shapes.add_shape(1, Inches(left), Inches(top), Inches(width), Inches(height))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if not line:
        shp.line.fill.background()
    return shp


def _txt(slide, text, left, top, width, height,
         size=12, bold=False, italic=False,
         color: RGBColor = C.DARK,
         align=PP_ALIGN.LEFT,
         wrap=True):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = 'Arial'
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return box


def _multiline(slide, paragraphs, left, top, width, height,
               size=11, color: RGBColor = C.DARK, line_gap=True):
    """Добавляет несколько абзацев в один текстбокс."""
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True

    first = True
    for para in paragraphs:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()

        p.space_before = Pt(4) if line_gap and not first else Pt(0)
        run = p.add_run()
        run.text = para
        run.font.name = 'Arial'
        run.font.size = Pt(size)
        run.font.color.rgb = color
    return box


def _logo(slide):
    logo_path = BASE_DIR / 'static' / 'tozai_logo.png'
    if logo_path.exists():
        slide.shapes.add_picture(str(logo_path), Inches(0.5), Inches(6.85), height=Inches(0.42))


def _footer(slide, text='TOZAI TOURS  |  DMC Japan  |  Tozai-tours.com'):
    _rect(slide, 0, 7.18, 13.33, 0.32, C.DARK)
    _txt(slide, text, 0.5, 7.2, 9.0, 0.28, size=7, color=C.GRAY, align=PP_ALIGN.LEFT)


# ── Слайд 1: Титул ───────────────────────────────────────────────────────────

def _slide_title(prs, params):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank

    _bg(slide, C.DARK)

    # Левая красная полоса
    _rect(slide, 0, 0, 0.28, 7.5, C.RED)

    # Золотая линия вверху
    _rect(slide, 0.28, 0.0, 13.05, 0.06, C.GOLD)

    # Золотая линия внизу
    _rect(slide, 0.28, 7.14, 13.05, 0.06, C.GOLD)

    # Основной заголовок
    _txt(slide, 'ЯПОНИЯ.  ТОКИО.',
         0.7, 1.4, 11.8, 1.4,
         size=52, bold=True, color=C.WHITE)

    # Имя компании
    _txt(slide, params['company_name'],
         0.7, 3.0, 11.8, 0.9,
         size=26, bold=False, color=C.GOLD)

    # Детали
    room_ru = 'одноместное' if params['room_type'] == 'SGL' else 'двухместное'
    conf_str = '  ·  с конференцией' if params.get('include_conference') else ''
    details = (f"{params['event_type']}{conf_str}  ·  {params['pax']} чел.  ·  "
               f"{params['days']} дней  ·  отель {params['hotel_level']}  ·  {room_ru}")
    if params.get('dates'):
        details += f"  ·  {params['dates']}"

    _txt(slide, details,
         0.7, 4.1, 12.0, 0.55,
         size=12, color=C.WHITE)

    # Лого
    _logo(slide)

    # Доп. надпись справа снизу
    _txt(slide, 'Destination Management Company', 10.5, 6.9, 2.6, 0.35,
         size=7, italic=True, color=C.GRAY, align=PP_ALIGN.RIGHT)


# ── Слайд 2: Концепция ────────────────────────────────────────────────────────

def _slide_concept(prs, content):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    _bg(slide, C.WHITE)

    # Шапка
    _rect(slide, 0, 0, 13.33, 1.35, C.DARK)
    _rect(slide, 0, 0, 0.28, 1.35, C.RED)

    _txt(slide, 'КОНЦЕПЦИЯ',
         0.5, 0.1, 5.0, 0.32,
         size=8, bold=True, color=C.GOLD)

    title = content.get('concept_title', 'Почему именно Япония?')
    _txt(slide, title,
         0.5, 0.45, 12.5, 0.82,
         size=22, bold=True, color=C.WHITE)

    # Текст концепции
    concept_text = content.get('concept_text', '')
    paras = [p.strip() for p in concept_text.split('\n') if p.strip()]
    if not paras:
        paras = [concept_text]

    _multiline(slide, paras,
               0.55, 1.5, 12.3, 5.4,
               size=12, color=C.DARK)

    # Нижняя полоса
    _rect(slide, 0, 7.18, 13.33, 0.32, C.LIGHT)
    _logo(slide)
    _txt(slide, 'TOZAI TOURS  |  DMC Japan',
         3.5, 7.21, 7.0, 0.28, size=7, color=C.GRAY, align=PP_ALIGN.CENTER)


# ── Слайд: День программы ─────────────────────────────────────────────────────

def _slide_day(prs, day_data):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide, C.WHITE)

    # Шапка
    _rect(slide, 0, 0, 13.33, 1.2, C.DARK)
    _rect(slide, 0, 0, 0.28, 1.2, C.RED)

    _txt(slide, 'ПРОГРАММА',
         0.5, 0.08, 4.0, 0.3,
         size=8, bold=True, color=C.GOLD)

    title = day_data.get('title', f'День {day_data["day_num"]}')
    _txt(slide, title,
         0.5, 0.38, 12.5, 0.76,
         size=21, bold=True, color=C.WHITE)

    # Три секции: утро / день / вечер
    sections = [
        ('УТРО',    day_data.get('morning', ''),   C.GOLD,  1.35),
        ('ДЕНЬ',    day_data.get('afternoon', ''),  C.RED,   3.1),
        ('ВЕЧЕР',   day_data.get('evening', ''),    C.DARK,  4.85),
    ]

    for label, text, label_color, y in sections:
        # Цветной лейбл
        _rect(slide, 0.35, y, 1.45, 0.28, label_color)
        _txt(slide, label,
             0.35, y, 1.45, 0.28,
             size=8, bold=True, color=C.WHITE, align=PP_ALIGN.CENTER)

        # Текст
        if text:
            paras = [p.strip() for p in text.split('\n') if p.strip()]
            _multiline(slide, paras if paras else [text],
                       2.0, y - 0.05, 11.0, 1.55,
                       size=11, color=C.DARK, line_gap=False)

    # Нижняя полоса
    _rect(slide, 0, 7.18, 13.33, 0.32, C.LIGHT)
    _logo(slide)
    _txt(slide, 'TOZAI TOURS  |  DMC Japan',
         3.5, 7.21, 7.0, 0.28, size=7, color=C.GRAY, align=PP_ALIGN.CENTER)


# ── Слайд: Размещение ─────────────────────────────────────────────────────────

def _slide_hotels(prs, params, content):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide, C.WHITE)

    # Шапка
    _rect(slide, 0, 0, 13.33, 1.2, C.DARK)
    _rect(slide, 0, 0, 0.28, 1.2, C.RED)

    _txt(slide, 'РАЗМЕЩЕНИЕ',
         0.5, 0.08, 4.0, 0.3, size=8, bold=True, color=C.GOLD)

    _txt(slide, f'Отели {params["hotel_level"]} — Токио',
         0.5, 0.38, 12.5, 0.76,
         size=21, bold=True, color=C.WHITE)

    # Описание отеля
    hotel_desc = content.get('hotel_description', '')
    paras = [p.strip() for p in hotel_desc.split('\n') if p.strip()]
    _multiline(slide, paras if paras else [hotel_desc],
               0.55, 1.35, 8.5, 2.5, size=12, color=C.DARK)

    # Параметры размещения
    room_ru = 'одноместные' if params['room_type'] == 'SGL' else 'двухместные'
    nights = params['days'] - 1
    details = [
        f"Тип номеров:  {params['room_type']} ({room_ru})",
        f"Количество ночей:  {nights}",
        f"Уровень:  {params['hotel_level']}",
        f"Количество номеров:  {'~' + str(params['pax']) if params['room_type'] == 'SGL' else '~' + str(params['pax'] // 2 + params['pax'] % 2)}",
    ]
    _multiline(slide, details,
               0.55, 4.05, 8.0, 2.0, size=11, color=C.GRAY)

    # Финальный аккорд
    closing = content.get('closing_note', '')
    if closing:
        _rect(slide, 0.4, 5.95, 12.55, 0.95, C.LIGHT)
        paras_c = [p.strip() for p in closing.split('\n') if p.strip()]
        _multiline(slide, paras_c,
                   0.65, 6.0, 12.0, 0.85, size=11, color=C.DARK)

    # Нижняя полоса
    _rect(slide, 0, 7.18, 13.33, 0.32, C.LIGHT)
    _logo(slide)
    _txt(slide, 'TOZAI TOURS  |  DMC Japan',
         3.5, 7.21, 7.0, 0.28, size=7, color=C.GRAY, align=PP_ALIGN.CENTER)


# ── Главная функция ───────────────────────────────────────────────────────────

def create_ppt(params: dict, content: dict, services: list) -> bytes:
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    _slide_title(prs, params)
    _slide_concept(prs, content)

    for day_data in content.get('days', []):
        _slide_day(prs, day_data)

    _slide_hotels(prs, params, content)

    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.read()
