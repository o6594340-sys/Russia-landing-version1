"""
photo_bank.py — резолвер фотографий с типизацией слотов.

Цепочка поиска для каждого слота:
  1. photo_bank/{object_slug}/{slot_filename}  — вручную загруженное фото
  2. photo_cache/{slot_type}_{object_slug}.jpg — кэш из Unsplash
  3. Unsplash API                               — скачиваем и кэшируем
  4. photos/{random}                            — fallback из оригинальных PPT

Типы слотов:
  HOTEL_EXTERIOR      — фасад / главный вход
  HOTEL_ROOM          — интерьер номера (лучшая категория)
  HOTEL_AMENITY       — бассейн / бар / лаундж / панорамный ресторан
  RESTAURANT_INTERIOR — зал, атмосфера, вечерняя подача
  RESTAURANT_DISH     — фирменное блюдо крупным планом
  RESTAURANT_SERVICE  — процесс подачи / сервис
  ACTIVITY_HERO       — один сильный кадр (полная ширина)
  ACTIVITY_LOCATION   — широкий план места
  ACTIVITY_PEOPLE     — люди в процессе активности
  COVER               — обложечный панорамный кадр
  SEPARATOR           — разделитель раздела (панорама без текста)
  CITY_OVERVIEW       — городской вид / аэросъёмка
"""

import os
import re
import random
from pathlib import Path

try:
    import requests as _req
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

# ── Пути ──────────────────────────────────────────────────────────────────────

_ROOT      = Path(__file__).parent
_BANK      = _ROOT / "photo_bank"    # вручную загруженные фото
_CACHE     = _ROOT / "photo_cache"   # авто-кэш из Unsplash
_FALLBACK  = _ROOT / "photos"        # извлечённые из оригинальных PPT

_BANK.mkdir(exist_ok=True)
_CACHE.mkdir(exist_ok=True)

# ── Имена файлов для каждого типа слота ───────────────────────────────────────

SLOT_FILENAME = {
    "HOTEL_EXTERIOR":      "exterior.jpg",
    "HOTEL_ROOM":          "room.jpg",
    "HOTEL_AMENITY":       "amenity.jpg",
    "RESTAURANT_INTERIOR": "interior.jpg",
    "RESTAURANT_DISH":     "dish.jpg",
    "RESTAURANT_SERVICE":  "service.jpg",
    "ACTIVITY_HERO":       "hero.jpg",
    "ACTIVITY_LOCATION":   "location.jpg",
    "ACTIVITY_PEOPLE":     "people.jpg",
    "COVER":               "cover.jpg",
    "SEPARATOR":           "separator.jpg",
    "CITY_OVERVIEW":       "overview.jpg",
}

# ── Шаблоны Unsplash-запросов по типу слота ───────────────────────────────────

SLOT_QUERY_TEMPLATE = {
    "HOTEL_EXTERIOR":      "{name} hotel exterior facade entrance",
    "HOTEL_ROOM":          "{name} hotel deluxe room interior bed",
    "HOTEL_AMENITY":       "{name} hotel rooftop pool bar lounge",
    "RESTAURANT_INTERIOR": "{name} restaurant interior dining atmosphere evening",
    "RESTAURANT_DISH":     "{name} restaurant signature dish food photography",
    "RESTAURANT_SERVICE":  "{name} restaurant chef service tableside",
    "ACTIVITY_HERO":       "{name} {city} landmark scenic",
    "ACTIVITY_LOCATION":   "{name} {city} wide view panorama",
    "ACTIVITY_PEOPLE":     "{name} {city} experience visitors",
    "COVER":               "{city} skyline aerial panorama",
    "SEPARATOR":           "{city} street architecture scenic",
    "CITY_OVERVIEW":       "{city} cityscape aerial overview",
}

# ── Предупреждения о заглушках ────────────────────────────────────────────────

_warnings: list[str] = []

def get_warnings() -> list[str]:
    return list(_warnings)

def clear_warnings():
    _warnings.clear()


# ── Главная функция ───────────────────────────────────────────────────────────

def get_photo(slot_type: str, name: str = "", city: str = "Shanghai") -> str:
    """
    Возвращает путь к файлу фото.

    slot_type — один из типов (HOTEL_EXTERIOR, RESTAURANT_DISH и т.д.)
    name      — название объекта (отель, ресторан, активность)
    city      — город (для контекста запроса)
    """
    slug = _slugify(name) if name else None
    filename = SLOT_FILENAME.get(slot_type, "photo.jpg")

    # 1. Вручную загруженное фото в photo_bank
    if slug:
        manual = _BANK / slug / filename
        if manual.exists():
            return str(manual)

    # 2. Кэш из Unsplash
    cache_key = f"{slot_type}_{slug}" if slug else slot_type
    cached = _CACHE / f"{_slugify(cache_key)}.jpg"
    if cached.exists():
        return str(cached)

    # 3. Загружаем с Unsplash
    query = _build_query(slot_type, name, city)
    if _HAS_REQUESTS and query:
        data = _try_unsplash(query) or _try_pexels(query)
        if data:
            cached.write_bytes(data)
            print(f"  cached [{slot_type}] {name or city} <- \"{query}\"")
            return str(cached)

    # 4. Fallback — случайное фото из оригинальных PPT (с предупреждением)
    _warnings.append(
        f"PLACEHOLDER [{slot_type}] '{name}' — загрузи реальное фото в "
        f"photo_bank/{slug or 'unknown'}/{filename}"
    )
    fallback_files = (
        list(_FALLBACK.glob("*.jpg")) +
        list(_FALLBACK.glob("*.jpeg")) +
        list(_FALLBACK.glob("*.png"))
    )
    if fallback_files:
        return str(random.choice(fallback_files))
    return None


# ── Вспомогательные функции ───────────────────────────────────────────────────

def _slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:60]


def _build_query(slot_type: str, name: str, city: str) -> str:
    template = SLOT_QUERY_TEMPLATE.get(slot_type, "{name} {city} travel")
    return template.format(name=name, city=city).strip()


def _load_key(name: str) -> str | None:
    val = os.environ.get(name)
    if val:
        return val
    env_path = _ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip()
    return None


def _try_unsplash(query: str) -> bytes | None:
    key = _load_key("UNSPLASH_ACCESS_KEY")
    if not key:
        return None
    try:
        r = _req.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": query,
                "orientation": "landscape",
                "per_page": 5,
                "order_by": "relevant",
                "content_filter": "high",
            },
            headers={"Authorization": f"Client-ID {key}"},
            timeout=10,
        )
        if r.status_code != 200:
            return None
        results = r.json().get("results", [])
        if not results:
            return None
        img_url = results[0]["urls"]["regular"] + "&w=1920"
        img_r = _req.get(img_url, timeout=20)
        return img_r.content if img_r.status_code == 200 else None
    except Exception:
        return None


def _try_pexels(query: str) -> bytes | None:
    key = _load_key("PEXELS_API_KEY")
    if not key:
        return None
    try:
        r = _req.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "orientation": "landscape", "per_page": 5},
            headers={"Authorization": key},
            timeout=10,
        )
        if r.status_code != 200:
            return None
        photos = r.json().get("photos", [])
        if not photos:
            return None
        img_url = photos[0]["src"]["large2x"]
        img_r = _req.get(img_url, timeout=20)
        return img_r.content if img_r.status_code == 200 else None
    except Exception:
        return None
