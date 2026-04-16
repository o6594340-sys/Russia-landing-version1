"""
Загрузчик фотографий для слайдов PPT.
Приоритет: локальный фотобанк → Unsplash → Pexels.
"""
import os
import json
from pathlib import Path

try:
    import requests as _requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

BASE_DIR   = Path(__file__).parent
BANK_DIR   = BASE_DIR / 'photo_bank'
INDEX_FILE = BANK_DIR / 'index.json'

_index_cache: list | None = None
_used_files: set = set()


def reset_session():
    """Сбрасывает список использованных фото. Вызывать перед каждой генерацией PPT."""
    global _used_files
    _used_files = set()


def _load_env() -> dict:
    env_path = BASE_DIR / '.env'
    out = {}
    if env_path.exists():
        for line in env_path.read_text(encoding='utf-8').splitlines():
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                out[k.strip()] = v.strip()
    return out


_ENV_CACHE: dict | None = None


def _env() -> dict:
    global _ENV_CACHE
    if _ENV_CACHE is None:
        _ENV_CACHE = _load_env()
    return _ENV_CACHE


def _key(name: str) -> str | None:
    return os.environ.get(name) or _env().get(name)


def _load_index() -> list:
    global _index_cache
    if _index_cache is None:
        if INDEX_FILE.exists():
            with open(INDEX_FILE, encoding='utf-8') as f:
                _index_cache = json.load(f)
        else:
            _index_cache = []
    return _index_cache


def fetch_photo(query: str, fallback_query: str = None) -> tuple:
    """
    Возвращает (image_bytes, attribution_str) или (None, None).
    Порядок: локальный банк → Unsplash → Pexels.
    """
    for q in ([query] + ([fallback_query] if fallback_query else [])):
        result = _try_local_bank(q)
        if result[0]:
            return result

    if not _REQUESTS_OK:
        return None, None

    for q in ([query] + ([fallback_query] if fallback_query else [])):
        result = _try_unsplash(q)
        if result[0]:
            return result

    for q in ([query] + ([fallback_query] if fallback_query else [])):
        result = _try_pexels(q)
        if result[0]:
            return result

    return None, None


def _try_local_bank(query: str) -> tuple:
    """Ищет фото в локальном банке по совпадению тегов."""
    index = _load_index()
    if not index:
        return None, None

    query_words = set(query.lower().replace('-', ' ').split())

    best_score = 0
    best_entry = None

    for entry in index:
        # Уже использованное фото получает штраф — берём только если совсем нет альтернатив
        already_used = entry['file'] in _used_files
        tags = set(t.lower() for t in entry.get('tags', []))
        score = 0
        for word in query_words:
            for tag in tags:
                if word in tag or tag in word:
                    score += 1
                    break
        # Использованные фото идут с пониженным приоритетом
        effective_score = score * 0.1 if already_used else score
        if effective_score > best_score:
            best_score = effective_score
            best_entry = entry

    if best_entry and best_score > 0:
        photo_path = BANK_DIR / best_entry['file']
        if photo_path.exists():
            _used_files.add(best_entry['file'])
            credit = best_entry.get('credit', '')
            attribution = f"{best_entry['file']}" + (f' — {credit}' if credit else '')
            return photo_path.read_bytes(), attribution

    return None, None


def _try_unsplash(query: str) -> tuple:
    key = _key('UNSPLASH_ACCESS_KEY')
    if not key:
        return None, None
    try:
        r = _requests.get(
            'https://api.unsplash.com/search/photos',
            params={
                'query': query,
                'orientation': 'landscape',
                'per_page': 5,
                'order_by': 'relevant',
                'content_filter': 'high',
            },
            headers={'Authorization': f'Client-ID {key}'},
            timeout=10,
        )
        if r.status_code != 200:
            return None, None
        results = r.json().get('results', [])
        if not results:
            return None, None
        photo = results[0]
        img_url = photo['urls']['regular'] + '&w=1920'
        attribution = f"Photo by {photo['user']['name']} on Unsplash"
        img_r = _requests.get(img_url, timeout=20)
        if img_r.status_code == 200:
            return img_r.content, attribution
    except Exception:
        pass
    return None, None


def _try_pexels(query: str) -> tuple:
    key = _key('PEXELS_API_KEY')
    if not key:
        return None, None
    try:
        r = _requests.get(
            'https://api.pexels.com/v1/search',
            params={'query': query, 'orientation': 'landscape', 'per_page': 5},
            headers={'Authorization': key},
            timeout=10,
        )
        if r.status_code != 200:
            return None, None
        photos = r.json().get('photos', [])
        if not photos:
            return None, None
        photo = photos[0]
        img_url = photo['src']['large2x']
        attribution = f"Photo by {photo['photographer']} on Pexels"
        img_r = _requests.get(img_url, timeout=20)
        if img_r.status_code == 200:
            return img_r.content, attribution
    except Exception:
        pass
    return None, None
