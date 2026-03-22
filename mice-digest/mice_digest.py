#!/usr/bin/env python3
"""MICE News Digest Agent — daily email digest via Claude + web search."""

import os
import resend
import anthropic
from datetime import datetime

# Configuration
RECIPIENT_EMAIL = "olgagonchar2806@gmail.com"
resend.api_key = os.environ["RESEND_API_KEY"]
NUM_NEWS = 8

SYSTEM_PROMPT = """Ты — редактор профессионального дайджеста для специалистов MICE-индустрии \
(Meetings, Incentives, Conferences, Exhibitions).

Твоя задача: найти 8 актуальных новостей и составить дайджест.

ТРЕБОВАНИЯ:
- Только MICE-тематика: ивенты, конгрессы, конференции, корпоративный туризм, \
инсентив-туры, выставки, конгресс-центры, MICE-технологии, туристическая инфраструктура \
для деловых мероприятий
- Глобальные новости + всё, что релевантно для российского MICE-рынка
- ИСКЛЮЧИТЬ: политику, светские события, гламур, новости не связанные с бизнесом
- Язык дайджеста: русский
- На каждую новость: 2-3 строки, сухо и по делу — только факты, без вводных слов

ФОРМАТ каждой новости:
**[Заголовок]**
2-3 строки с сутью. Источник: [название издания].

---
"""


def get_mice_news() -> str:
    """Fetch and summarize MICE news using Claude with web search."""
    client = anthropic.Anthropic()

    today = datetime.now().strftime("%d %B %Y")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"Сегодня {today}. Найди 8 свежих новостей для MICE-дайджеста. "
                "Ищи на английском и русском языках, используй несколько поисковых запросов:\n"
                "- MICE industry news 2025\n"
                "- meetings incentives conferences exhibitions news\n"
                "- corporate events travel industry\n"
                "- incentive travel trends\n"
                "- конгресс-туризм MICE новости\n"
                "- выставочная индустрия новости\n\n"
                "Составь дайджест из 8 новостей строго в указанном формате. "
                "Без вступлений и заключений — только 8 новостей."
            )
        }]
    )

    for block in response.content:
        if block.type == "text":
            return block.text

    return "Новости не найдены."


def send_email(digest_text: str) -> None:
    """Send the digest via Resend."""
    today = datetime.now().strftime("%d.%m.%Y")

    resend.Emails.send({
        "from": "MICE Дайджест <onboarding@resend.dev>",
        "to": RECIPIENT_EMAIL,
        "subject": f"MICE Дайджест — {today}",
        "text": digest_text,
    })

    print(f"Дайджест отправлен на {RECIPIENT_EMAIL}")


def main() -> None:
    print("Собираю MICE-новости...")
    digest = get_mice_news()
    print("Отправляю email...")
    send_email(digest)
    print("Готово.")


if __name__ == "__main__":
    main()
