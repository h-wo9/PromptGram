import base64
import binascii
from datetime import datetime

from app.models import Prompt


def encode_cursor(prompt: Prompt, sort: str) -> str:
    if sort == "popular":
        raw = f"p:{prompt.like_count}:{prompt.id}"
    else:
        raw = f"l:{prompt.created_at.isoformat()}:{prompt.id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str, sort: str) -> tuple | None:
    """(key, id) 반환. 잘못된/정렬 불일치 cursor는 None."""
    try:
        raw = base64.urlsafe_b64decode(cursor.encode()).decode()
        kind, rest = raw.split(":", 1)
        key, id_str = rest.rsplit(":", 1)
        if kind == "p" and sort == "popular":
            return int(key), int(id_str)
        if kind == "l" and sort == "latest":
            return datetime.fromisoformat(key), int(id_str)
    except (ValueError, binascii.Error, UnicodeDecodeError):
        pass
    return None
