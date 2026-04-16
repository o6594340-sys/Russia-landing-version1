"""
Генератор PPT-презентации для КП.
Дизайн: Washi & Red — тёплая тема, Georgia + Arial, фото через API.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
from pathlib import Path
import io

from photo_fetcher import fetch_photo, reset_session
from PIL import Image as _PILImage

BASE_DIR = Path(__file__).parent

W = 13.33   # slide width  (inches)
H = 7.5     # slide height (inches)
M = 0.83    # margin       (inches)


# ── Палитра Washi & Red ──────────────────────────────────────────────────────
class C:
    BEIGE  = RGBColor(0xF7, 0xF4, 0xEF)   # Warm washi beige (content bg)
    INDIGO = RGBColor(0xC8, 0x10, 0x2E)   # Japanese red (accent)
    GOLD   = RGBColor(0xA8, 0x89, 0x5A)   # Matte gold
    DARK   = RGBColor(0x1A, 0x0A, 0x0D)   # Deep dark (title/closing bg)
    INK    = RGBColor(0x1C, 0x1C, 0x1E)   # Body text
    WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
    MIST   = RGBColor(0xE8, 0xE4, 0xDC)   # Light divider stripe
    STONE  = RGBColor(0x76, 0x76, 0x76)   # Secondary/caption text
    GHOST  = RGBColor(0xDE, 0xDA, 0xD2)   # Ghost day numbers


# ── Низкоуровневые утилиты ────────────────────────────────────────────────────

def _bg(slide, color: RGBColor):
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = color


def _rect(slide, left, top, width, height, fill: RGBColor):
    shp = slide.shapes.add_shape(
        1, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.fill.background()
    return shp


def _set_alpha(shape, opacity: float):
    """Устанавливает прозрачность заливки фигуры. opacity: 0.0–1.0."""
    spPr = shape._element.spPr
    solid = spPr.find(qn('a:solidFill'))
    if solid is None:
        return
    for tag in ('a:srgbClr', 'a:sysClr', 'a:schemeClr'):
        clr = solid.find(qn(tag))
        if clr is not None:
            for a in clr.findall(qn('a:alpha')):
                clr.remove(a)
            alpha = etree.SubElement(clr, qn('a:alpha'))
            alpha.set('val', str(int(opacity * 100000)))
            break


def _line(slide, left, top, width, color: RGBColor, thickness_pt=1.0):
    """Тонкая горизонтальная линия."""
    shp = slide.shapes.add_shape(
        1, Inches(left), Inches(top), Inches(width), Pt(thickness_pt)
    )
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    return shp


def _txt(slide, text, left, top, width, height,
         size=12, bold=False, italic=False,
         color: RGBColor = C.INK,
         align=PP_ALIGN.LEFT,
         font='Arial'):
    box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return box


def _multiline(slide, paragraphs: list, left, top, width, height,
               size=11, color: RGBColor = C.INK,
               bold=False, italic=False, font='Arial',
               line_spacing=1.4, space_before=0):
    box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = box.text_frame
    tf.word_wrap = True

    for i, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if space_before and i > 0:
            p.space_before = Pt(space_before)
        from pptx.util import Pt as _Pt
        from pptx.oxml.ns import qn as _qn
        from lxml import etree as _etree
        # Set line spacing
        pPr = p._p.get_or_add_pPr()
        lnSpc = _etree.SubElement(pPr, _qn('a:lnSpc'))
        spcPct = _etree.SubElement(lnSpc, _qn('a:spcPct'))
        spcPct.set('val', str(int(line_spacing * 100000)))

        run = p.add_run()
        run.text = para
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
    return box


def _cover_crop(img_bytes: bytes, target_w_in: float, target_h_in: float,
                dpi: int = 150) -> bytes:
    """
    Обрезает фото под нужные пропорции без растяжения (как cover в CSS).
    Масштабирует так чтобы заполнить область, лишнее обрезает по центру.
    """
    target_w_px = int(target_w_in * dpi)
    target_h_px = int(target_h_in * dpi)
    target_ratio = target_w_px / target_h_px

    img = _PILImage.open(io.BytesIO(img_bytes)).convert('RGB')
    src_w, src_h = img.size
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        # Фото шире нужного — подгоняем по высоте, обрезаем по ширине
        new_h = target_h_px
        new_w = int(src_w * target_h_px / src_h)
    else:
        # Фото выше нужного — подгоняем по ширине, обрезаем по высоте
        new_w = target_w_px
        new_h = int(src_h * target_w_px / src_w)

    img = img.resize((new_w, new_h), _PILImage.LANCZOS)

    left = (new_w - target_w_px) // 2
    top  = (new_h - target_h_px) // 2
    img  = img.crop((left, top, left + target_w_px, top + target_h_px))

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=90)
    buf.seek(0)
    return buf.read()


def _photo(slide, img_bytes: bytes, left, top, width, height):
    """Вставляет фото из bytes с правильными пропорциями (cover-crop)."""
    cropped = _cover_crop(img_bytes, width, height)
    stream = io.BytesIO(cropped)
    return slide.shapes.add_picture(
        stream, Inches(left), Inches(top), Inches(width), Inches(height)
    )


def _photo_bg(slide, img_bytes: bytes, overlay_color: RGBColor = C.DARK,
              overlay_opacity: float = 0.62):
    """Полноэкранное фото + полупрозрачный оверлей."""
    _photo(slide, img_bytes, 0, 0, W, H)
    overlay = _rect(slide, 0, 0, W, H, overlay_color)
    _set_alpha(overlay, overlay_opacity)


def _label(slide, text: str, left, top, width=4.0, color: RGBColor = C.INDIGO):
    """Метка верхнего уровня — маленький жирный текст ALL CAPS."""
    _txt(slide, text.upper(), left, top, width, 0.28,
         size=8, bold=True, color=color, font='Arial')


def _logo(slide, right_align=False):
    logo_path = BASE_DIR / 'static' / 'tozai_logo.png'
    if not logo_path.exists():
        return
    logo_h = Inches(0.38)
    logo_w = Inches(1.4)
    left = Inches(W - M - 1.4) if right_align else Inches(M)
    slide.shapes.add_picture(
        str(logo_path), left, Inches(H - 0.62), logo_w, logo_h
    )


def _footer_bar(slide, text='TOZAI TOURS  ·  DMC Japan  ·  tozai-tours.com'):
    """Тонкая нижняя полоска с текстом."""
    _rect(slide, 0, H - 0.28, W, 0.28, C.MIST)
    _txt(slide, text, M, H - 0.27, W - M * 2, 0.24,
         size=7, color=C.STONE, align=PP_ALIGN.CENTER)


# ── Слайд 1: Титул ───────────────────────────────────────────────────────────

def _slide_title(prs, params: dict, credits: list):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Фото фон или тёмная заливка
    img, attr = fetch_photo('Japan aerial landscape', 'Mount Fuji sunrise')
    if img:
        _photo_bg(slide, img, C.DARK, overlay_opacity=0.58)
        if attr:
            credits.append(attr)
    else:
        _bg(slide, C.DARK)

    # Золотые горизонтальные линии
    _rect(slide, M, 0.55, W - M * 2, 0.03, C.GOLD)
    _rect(slide, M, H - 0.65, W - M * 2, 0.03, C.GOLD)

    # Метка сверху
    _label(slide, 'Коммерческое предложение', M, 0.22, 5.0, C.GOLD)

    # Главный заголовок
    _txt(slide, 'ЯПОНИЯ  ·  ТОКИО',
         M, 1.3, 10.5, 1.6,
         size=54, bold=True, color=C.WHITE, font='Georgia')

    # Имя компании
    _txt(slide, params['company_name'],
         M, 3.1, 10.5, 0.9,
         size=24, italic=True, color=C.GOLD, font='Georgia')

    # Детали
    twn = params.get('twn', 0)
    sgl = params.get('sgl', 0)
    room_parts = []
    if twn:
        room_parts.append(f'{twn} Twin')
    if sgl:
        room_parts.append(f'{sgl} Single')
    room_str = '  ·  '.join(room_parts) if room_parts else 'номера уточняются'
    conf = '  ·  с конференцией' if params.get('include_conference') else ''
    details = (f"{params['event_type']}{conf}  ·  {params['pax']} чел.  ·  "
               f"{params['days']} дней  ·  отель {params['hotel_level']}  ·  {room_str}")
    if params.get('dates'):
        details += f"  ·  {params['dates']}"

    _txt(slide, details, M, 4.2, 11.5, 0.5,
         size=11, color=RGBColor(0xCC, 0xC9, 0xC2), font='Arial')

    # Логотип и подпись
    _logo(slide, right_align=True)
    _txt(slide, 'Destination Management Company',
         M, H - 0.62, 5.0, 0.38,
         size=8, italic=True, color=C.STONE)


# ── Слайд 2: Почему Япония ────────────────────────────────────────────────────

_WHY_JAPAN = [
    'Omotenashi: японский сервис не знает аналогов в мире. Ваша группа почувствует себя гостями, а не туристами.',
    'Контраст, который не стирается: 1300 лет истории и передовые технологии в одном городе.',
    'Страна без случайностей: пунктуальность, безопасность, чистота. Программа работает как часы.',
    'Гастрономия без компромиссов: 230 мишленовских ресторанов в Токио. Больше, чем в Париже.',
    'Самый высокий NPS среди инсентив-направлений: участники после Японии становятся её послами.',
]


def _slide_why_japan(prs, credits: list):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    photo_w = W * 0.52
    text_x = photo_w + 0.1

    # Фото слева
    img, attr = fetch_photo('Japan modern traditional contrast', 'Torii gate forest path')
    if img:
        _photo(slide, img, 0, 0, photo_w, H)
        if attr:
            credits.append(attr)
    else:
        _rect(slide, 0, 0, photo_w, H, C.INDIGO)

    # Правая панель — беж
    _bg(slide, C.BEIGE)
    # Перекрываем фото с правой стороны чистым фоном
    _rect(slide, photo_w, 0, W - photo_w, H, C.BEIGE)

    # Тонкая индиго полоска-разделитель
    _rect(slide, photo_w, 0, 0.04, H, C.INDIGO)

    # Метка
    _label(slide, 'Почему Япония', text_x, 1.2, 5.0, C.INDIGO)
    _line(slide, text_x, 1.6, W - text_x - M * 0.5, C.GOLD, 1.5)

    # Заголовок
    _txt(slide, 'Страна, которая\nменяет команды',
         text_x, 1.7, W - text_x - M * 0.5, 1.4,
         size=22, bold=True, color=C.INK, font='Georgia')

    # Пункты
    _multiline(slide, _WHY_JAPAN,
               text_x, 3.25, W - text_x - M * 0.5, 3.5,
               size=10.5, color=C.INK, font='Arial',
               line_spacing=1.55, space_before=5)

    _footer_bar(slide)
    _logo(slide, right_align=True)


# ── Слайд 3: Концепция ────────────────────────────────────────────────────────

def _slide_concept(prs, content: dict, credits: list):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide, C.BEIGE)

    # Полоса сверху
    _rect(slide, 0, 0, W, 1.15, C.INDIGO)

    # Метка и заголовок в полосе
    _label(slide, 'Концепция', M, 0.12, 4.0, C.GOLD)
    title = content.get('concept_title', 'Токио — место силы вашей команды')
    _txt(slide, title, M, 0.38, W - M * 2 - 0.5, 0.72,
         size=20, bold=True, color=C.WHITE, font='Georgia')

    # Декоративный ghost-элемент (кавычка)
    _txt(slide, '«',
         W - 2.8, 0.9, 2.5, 2.5,
         size=160, bold=False, color=C.GHOST, font='Georgia')

    # Текст концепции
    concept_text = content.get('concept_text', '')
    paras = [p.strip() for p in concept_text.split('\n') if p.strip()]
    if not paras:
        paras = [concept_text]

    _multiline(slide, paras,
               M, 1.35, W - M * 2 - 1.5, 5.5,
               size=13, color=C.INK, font='Arial',
               line_spacing=1.65)

    _line(slide, M, 6.75, 3.0, C.GOLD, 1.5)
    _footer_bar(slide)
    _logo(slide, right_align=True)


# ── Слайд: День программы ─────────────────────────────────────────────────────

_DAY_PHOTOS = {
    1: ('Tokyo street night neon', 'Tokyo alley lantern'),
    2: ('Shibuya crossing aerial Tokyo', 'Tokyo modern street'),
    3: ('Kyoto temple autumn', 'Japanese temple morning light'),
    4: ('Japanese ryokan interior tatami', 'tatami room traditional Japan'),
    5: ('Japan zen garden', 'Kyoto bamboo forest morning'),
    6: ('Mount Fuji reflection lake', 'Japan nature landscape'),
    7: ('Japan sunset golden hour', 'Tokyo panorama night'),
}


def _slide_day(prs, day_data: dict, credits: list):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    day_num = day_data.get('day_num', 1)

    # 1. Полноэкранное фото фон
    q1, q2 = _DAY_PHOTOS.get(day_num, ('Japan landscape', 'Tokyo street'))
    img, attr = fetch_photo(q1, q2)
    if img:
        _photo(slide, img, 0, 0, W, H)
        if attr:
            credits.append(attr)
    else:
        _bg(slide, C.DARK)

    # 2. Тёмная полоса-шапка сверху
    top = _rect(slide, 0, 0, W, 1.55, C.DARK)
    _set_alpha(top, 0.80)

    # 3. Тёмная панель снизу для расписания
    bot = _rect(slide, 0, H - 3.1, W, 3.1, C.DARK)
    _set_alpha(bot, 0.88)

    # 4. Красная акцентная линия под шапкой
    _rect(slide, M, 1.55, W - M * 2, 0.03, C.INDIGO)

    # 5. Метка и заголовок в шапке
    _label(slide, 'Программа', M, 0.14, 4.0, C.GOLD)
    title = day_data.get('title', f'День {day_num}')
    _txt(slide, title, M, 0.42, W - M * 2 - 1.5, 0.95,
         size=22, bold=True, color=C.WHITE, font='Georgia')

    # 6. Ghost номер дня (в зоне фото)
    _txt(slide, str(day_num).zfill(2),
         W - 3.0, 0.55, 2.6, 2.6,
         size=120, bold=True, color=C.GHOST, font='Georgia')

    # 7. Живое описание дня поверх фото
    description = day_data.get('description', '')
    if description:
        desc_bg = _rect(slide, M - 0.1, 1.72, W - M * 2 + 0.2, 1.05, C.DARK)
        _set_alpha(desc_bg, 0.40)
        _txt(slide, description,
             M, 1.80, W - M * 2 - 0.3, 0.95,
             size=13.5, italic=True, color=C.WHITE, font='Georgia')

    # 8. Три колонки расписания внизу
    col_w = (W - M * 2 - 0.2) / 3
    sections = [
        ('Утро',  day_data.get('morning', ''),   C.INDIGO,                       C.WHITE),
        ('День',  day_data.get('afternoon', ''), C.GOLD,                         C.INK),
        ('Вечер', day_data.get('evening', ''),   RGBColor(0x3A, 0x3A, 0x3A),    C.WHITE),
    ]

    for i, (label_text, text, badge_fill, badge_text_color) in enumerate(sections):
        x = M + i * (col_w + 0.1)
        y_badge = H - 2.95

        # Тонкий разделитель между колонками
        if i > 0:
            _rect(slide, x - 0.06, y_badge, 0.02, 2.75, RGBColor(0x55, 0x55, 0x55))

        # Бейдж
        _rect(slide, x, y_badge, 1.05, 0.27, badge_fill)
        _txt(slide, label_text.upper(),
             x, y_badge, 1.05, 0.27,
             size=7.5, bold=True, color=badge_text_color,
             align=PP_ALIGN.CENTER, font='Arial')

        # Текст расписания
        if text:
            paras = [p.strip() for p in text.split('\n') if p.strip()]
            _multiline(slide, paras if paras else [text],
                       x, y_badge + 0.34, col_w - 0.05, 2.5,
                       size=9.5, color=RGBColor(0xE0, 0xDD, 0xD8),
                       font='Arial', line_spacing=1.5)

    _logo(slide, right_align=True)


# ── Слайд: Хайлайт (витрина активности) ──────────────────────────────────────

def _slide_highlight(prs, hl: dict, credits: list):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # 1. Полноэкранное фото
    query = hl.get('photo_query', hl.get('title', 'Japan'))
    img, attr = fetch_photo(query, query)
    if img:
        _photo(slide, img, 0, 0, W, H)
        if attr:
            credits.append(attr)
    else:
        _bg(slide, C.DARK)

    # 2. Градиентный оверлей: левая тёмная полоса для текста
    panel_w = W * 0.54
    panel = _rect(slide, 0, 0, panel_w, H, C.DARK)
    _set_alpha(panel, 0.82)

    # 3. Правая сторона — лёгкое затемнение чтобы фото не резало
    right_vignette = _rect(slide, panel_w, 0, W - panel_w, H, C.DARK)
    _set_alpha(right_vignette, 0.18)

    # 4. Красная вертикальная полоска-акцент
    _rect(slide, panel_w - 0.04, 0, 0.04, H, C.INDIGO)

    # 5. Категория + отсылка к дню
    category = hl.get('category', '')
    day_ref  = hl.get('day_ref', '')
    label_text = f'{category}  ·  {day_ref}' if category and day_ref else category or day_ref
    if label_text:
        _label(slide, label_text, M, 1.0, panel_w - M * 2, C.GOLD)

    # 6. Заголовок — крупно
    title = hl.get('title', '')
    _txt(slide, title,
         M, 1.35, panel_w - M * 1.5, 1.6,
         size=30, bold=True, color=C.WHITE, font='Georgia')

    # 7. Тонкая линия под заголовком
    _line(slide, M, 3.1, panel_w - M * 2, C.INDIGO, 1.5)

    # 8. Описание
    description = hl.get('description', '')
    if description:
        paras = [p.strip() for p in description.split('\n') if p.strip()]
        _multiline(slide, paras,
                   M, 3.25, panel_w - M * 1.5, 3.6,
                   size=11.5, color=RGBColor(0xE0, 0xDD, 0xD8),
                   font='Arial', line_spacing=1.65)

    _logo(slide, right_align=False)


# ── Слайд: Размещение ─────────────────────────────────────────────────────────

def _slide_hotels(prs, params: dict, content: dict, credits: list):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    photo_w = W * 0.48
    text_x = photo_w + 0.12

    # Фото слева
    img, attr = fetch_photo('Japanese hotel luxury interior', 'Tokyo luxury hotel lobby')
    if img:
        _photo(slide, img, 0, 0, photo_w, H)
        if attr:
            credits.append(attr)
    else:
        _rect(slide, 0, 0, photo_w, H, C.INDIGO)

    _bg(slide, C.BEIGE)
    _rect(slide, photo_w, 0, W - photo_w, H, C.BEIGE)
    _rect(slide, photo_w, 0, 0.04, H, C.INDIGO)

    # Метка и заголовок
    _label(slide, 'Размещение', text_x, 1.0, 5.0, C.INDIGO)
    _line(slide, text_x, 1.4, W - text_x - M * 0.5, C.GOLD, 1.5)
    _txt(slide, f'Отели {params["hotel_level"]} — Токио',
         text_x, 1.5, W - text_x - 0.5, 0.9,
         size=20, bold=True, color=C.INK, font='Georgia')

    # Описание
    hotel_desc = content.get('hotel_description', '')
    paras = [p.strip() for p in hotel_desc.split('\n') if p.strip()]
    _multiline(slide, paras if paras else [hotel_desc],
               text_x, 2.55, W - text_x - 0.5, 2.0,
               size=11.5, color=C.INK, font='Arial', line_spacing=1.55)

    # Параметры
    twn = params.get('twn', 0)
    sgl = params.get('sgl', 0)
    room_parts = []
    if twn:
        room_parts.append(f'{twn} Twin-номеров')
    if sgl:
        room_parts.append(f'{sgl} Single-номеров')
    room_str = ' + '.join(room_parts) if room_parts else 'уточняется'
    nights = params['days'] - 1

    params_lines = [
        f'Состав номеров  —  {room_str}',
        f'Количество ночей  —  {nights}',
        f'Гостей  —  {params["pax"]} человек',
    ]
    if params.get('hotel_a_name'):
        params_lines.append(f'Вариант А  —  {params["hotel_a_name"]}')
    if params.get('hotel_b_name'):
        params_lines.append(f'Вариант Б  —  {params["hotel_b_name"]}')

    _multiline(slide, params_lines,
               text_x, 4.7, W - text_x - 0.5, 1.8,
               size=10, color=C.STONE, font='Arial',
               line_spacing=1.6, space_before=4)

    # Финальный аккорд
    closing = content.get('closing_note', '')
    if closing:
        _rect(slide, text_x - 0.15, 6.3, W - text_x, 0.85, C.MIST)
        _txt(slide, closing, text_x, 6.35, W - text_x - 0.3, 0.75,
             size=10, italic=True, color=C.INK, font='Georgia')

    _footer_bar(slide)
    _logo(slide, right_align=True)


# ── Слайд: Финал / Контакты ───────────────────────────────────────────────────

# Контакты подставляются при первом вызове из Tozai ОБЩАЯ.pptx,
# или используется значение по умолчанию.
_DEFAULT_CONTACTS = {
    'name': 'Mr. Hiroshi Suhara',
    'title': 'MICE Director · Tozai Tours DMC Japan',
    'email': 'suhara@tozaitours.com',
    'phone': '+81 3 6403 4816',
    'web': 'tozai-tours.com',
}

_CONTACTS: dict | None = None


def set_contacts(contacts: dict):
    """Вызывается из app.py после парсинга контактов из ОБЩАЯ.pptx."""
    global _CONTACTS
    _CONTACTS = contacts


def _get_contacts() -> dict:
    return _CONTACTS or _DEFAULT_CONTACTS


def _slide_closing(prs, params: dict, credits: list):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Фото фон или тёмная заливка
    img, attr = fetch_photo('Japan zen minimalist garden', 'Japan morning mist landscape')
    if img:
        _photo_bg(slide, img, C.DARK, overlay_opacity=0.68)
        if attr:
            credits.append(attr)
    else:
        _bg(slide, C.DARK)

    # Декоративные линии
    _rect(slide, M, 0.55, W - M * 2, 0.03, C.GOLD)
    _rect(slide, M, H - 0.65, W - M * 2, 0.03, C.GOLD)

    # Главный заголовок
    _txt(slide, 'Создадим это\nвместе?',
         M, 1.1, 8.0, 2.4,
         size=46, bold=True, color=C.WHITE, font='Georgia')

    # Подзаголовок
    _txt(slide, f'Готовы разработать программу для {params["company_name"]}',
         M, 3.6, 9.0, 0.65,
         size=16, italic=True, color=C.GOLD, font='Georgia')

    # Контакты
    c = _get_contacts()
    contact_lines = []
    if c.get('name'):
        contact_lines.append(c['name'])
    if c.get('title'):
        contact_lines.append(c['title'])
    if c.get('email'):
        contact_lines.append(c['email'])
    if c.get('phone'):
        contact_lines.append(c['phone'])
    if c.get('web'):
        contact_lines.append(c['web'])

    _multiline(slide, contact_lines,
               M, 4.45, 7.0, 1.8,
               size=12, color=RGBColor(0xCC, 0xC9, 0xC2),
               font='Arial', line_spacing=1.7)

    # Дисклеймер
    _txt(slide,
         'Международные перелёты не включены. Цены предварительные, подтверждаются при бронировании.',
         M, H - 1.05, 10.0, 0.45,
         size=7.5, italic=True, color=C.STONE)

    _logo(slide, right_align=True)


# ── Слайд: Фотокредиты (скрытый) ─────────────────────────────────────────────

def _slide_credits(prs, credits: list):
    if not credits:
        return
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide, C.WHITE)
    _label(slide, 'Photo Credits', M, M, 5.0, C.STONE)
    unique = list(dict.fromkeys(credits))
    _multiline(slide, unique,
               M, M + 0.4, W - M * 2, H - M * 2,
               size=9, color=C.STONE, font='Arial', line_spacing=1.6)
    # Скрываем слайд (атрибут show="0")
    slide._element.set('show', '0')


# ── Главная функция ───────────────────────────────────────────────────────────

def create_ppt(params: dict, content: dict, services: list) -> bytes:
    reset_session()  # каждая новая презентация — свежий пул фото

    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)

    credits: list = []

    _slide_title(prs, params, credits)
    _slide_why_japan(prs, credits)
    _slide_concept(prs, content, credits)

    for day_data in content.get('days', []):
        _slide_day(prs, day_data, credits)

    for hl in content.get('highlights', []):
        _slide_highlight(prs, hl, credits)

    _slide_hotels(prs, params, content, credits)
    _slide_closing(prs, params, credits)
    _slide_credits(prs, credits)

    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.read()
