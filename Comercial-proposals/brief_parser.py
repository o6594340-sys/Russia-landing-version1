"""
Парсер брифа: читает PDF / DOCX / TXT и извлекает параметры запроса через Claude.
"""
import os
import re
import json
from pathlib import Path


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Извлекает текст из файла по расширению."""
    ext = Path(filename).suffix.lower()

    if ext == '.pdf':
        import io
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or '' for page in reader.pages]
        return '\n'.join(pages).strip()

    elif ext in ('.docx', '.doc'):
        import io
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return '\n'.join(paragraphs).strip()

    elif ext in ('.txt', '.text'):
        for enc in ('utf-8', 'cp1251', 'latin-1'):
            try:
                return file_bytes.decode(enc).strip()
            except UnicodeDecodeError:
                continue
        return file_bytes.decode('utf-8', errors='replace').strip()

    else:
        # Попробуем как текст
        try:
            return file_bytes.decode('utf-8', errors='replace').strip()
        except Exception:
            return ''


def parse_brief(file_bytes: bytes, filename: str) -> dict:
    """
    Читает бриф и возвращает словарь с извлечёнными полями формы.
    Поля которые не нашли — None или пустая строка.
    """
    import anthropic

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            for line in env_path.read_text(encoding='utf-8').splitlines():
                if line.startswith('ANTHROPIC_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break

    text = extract_text(file_bytes, filename)

    if not text:
        return {'error': 'Не удалось прочитать текст из файла'}

    # Обрезаем до 8000 символов чтобы не перегружать промпт
    text_truncated = text[:8000]

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Ты помогаешь заполнить форму запроса для DMC-компании по организации корпоративного тура в Японию.

Прочитай следующий бриф клиента и извлеки из него параметры. Если параметр не указан — верни null.

БРИФ:
---
{text_truncated}
---

Верни ТОЛЬКО валидный JSON без пояснений:
{{
  "company_name": "Название компании клиента или организатора (строка или null)",
  "industry": "Отрасль / сфера деятельности (строка или null)",
  "event_type": "Тип мероприятия: одно из 'Инсентив', 'Конференция', 'Смешанный' (или null если неясно)",
  "twn": "Количество двухместных (twin) номеров (число или null)",
  "sgl": "Количество одноместных (single) номеров (число или null)",
  "pax": "Общее количество участников (число или null)",
  "days": "Количество дней программы (число или null)",
  "dates": "Примерные даты поездки (строка или null)",
  "hotel_level": "Уровень отеля: '4*', '4*+' или '5*' (или null)",
  "include_conference": "Есть ли конференц-блок: true или false (или null)",
  "conference_day": "На какой день запланирована конференция (число или null)",
  "special_requests": "Особые пожелания, требования, интересы группы (строка или null)"
}}

Правила:
- company_name: ищи название компании-клиента, не агентства
- pax: если указано только кол-во номеров — посчитай сам (twin × 2 + single)
- twn/sgl: если написано просто "30 человек двухместно" — twn=15, sgl=0
- event_type: "инсентив", "стимулирующая поездка", "награждение" → 'Инсентив'; "конференция", "форум", "съезд" → 'Конференция'; если и то и другое → 'Смешанный'
- special_requests: собери все пожелания, требования к программе, интересы группы в одну строку"""

    response = client.messages.create(
        model='claude-opus-4-6',
        max_tokens=1000,
        messages=[{'role': 'user', 'content': prompt}]
    )

    text_resp = response.content[0].text.strip()
    json_match = re.search(r'\{[\s\S]*\}', text_resp)
    if json_match:
        try:
            result = json.loads(json_match.group())
            # Убираем null-значения — оставляем только найденное
            return {k: v for k, v in result.items() if v is not None}
        except json.JSONDecodeError:
            pass

    return {'error': 'Не удалось разобрать ответ системы'}
