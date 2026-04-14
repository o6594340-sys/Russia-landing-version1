"""
parse_brief.py — парсинг брифа от агентства (Word или PDF) через Claude API.
Возвращает JSON с заполненными полями формы создания proposal.

Использование:
    python parse_brief.py "Brief_Japan sample.docx"
    python parse_brief.py brief.pdf
"""

import sys
import json
import pathlib
import anthropic
from dotenv import load_dotenv

load_dotenv()

# ── читаем файл ──────────────────────────────────────────────────────────────

def extract_text(filepath: str) -> str:
    path = pathlib.Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".docx":
        import docx2txt
        return docx2txt.process(filepath)

    elif suffix == ".pdf":
        import fitz  # pymupdf
        doc = fitz.open(filepath)
        return "\n".join(page.get_text() for page in doc)

    else:
        raise ValueError(f"Неподдерживаемый формат: {suffix}. Нужен .docx или .pdf")


# ── промпт ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Ты — ассистент менеджера DMC-компании, специализирующейся на турах в Китай.
Твоя задача — извлечь структурированные данные из брифа агентства и вернуть их в виде JSON.

Правила:
- Отвечай ТОЛЬКО валидным JSON, без пояснений и markdown-блоков
- Все текстовые поля заполняй на русском языке
- Если информация не найдена — ставь null
- Для поля confidence: "sure" = явно указано, "guess" = выведено из контекста, "missing" = не найдено
- Даты всегда в формате YYYY-MM-DD, если точная дата неизвестна — null
- Количество людей — только число, без текста
"""

USER_PROMPT_TEMPLATE = """Извлеки данные из следующего брифа и верни JSON строго по этой схеме:

{{
  "client_name": "название компании клиента",
  "agency_name": "название агентства (если указано)",
  "pax_total": число или null,
  "pax_sgl": число одноместных номеров или null,
  "pax_dbl": число двухместных номеров или null,
  "date_start": "YYYY-MM-DD или null",
  "date_end": "YYYY-MM-DD или null",
  "duration_days": число дней или null,
  "destination": "город/страна назначения",
  "budget_usd_per_person": число или null,
  "has_conference": true/false,
  "has_corporate_visit": true/false,
  "has_gala": true/false,
  "arrival_city": "город прилёта или null",
  "departure_city": "город вылета или null",
  "special_notes": "все особые пожелания, профиль группы, интересы — одним текстом",
  "confidence": {{
    "pax_total": "sure/guess/missing",
    "dates": "sure/guess/missing",
    "budget": "sure/guess/missing",
    "destination": "sure/guess/missing"
  }}
}}

Бриф:
---
{brief_text}
---"""


# ── основная функция ──────────────────────────────────────────────────────────

def parse_brief(filepath: str) -> dict:
    print(f"Читаю файл: {filepath}")
    text = extract_text(filepath)
    print(f"Извлечено {len(text)} символов текста\n")

    client = anthropic.Anthropic()

    print("Отправляю в Claude...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(brief_text=text)
            }
        ]
    )

    raw = message.content[0].text.strip()

    # убираем markdown-блоки если Claude всё же добавил
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw)
    return result


# ── запуск ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python parse_brief.py <путь_к_файлу>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = parse_brief(filepath)

    print("=" * 60)
    print("РЕЗУЛЬТАТ ПАРСИНГА:")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # сохраняем рядом с файлом
    out_path = pathlib.Path(filepath).with_suffix(".parsed.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nСохранено в: {out_path}")
