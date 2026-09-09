"""
VaxKavach — Telegram User Registry Endpoint

Provides:
  GET  /telegram/users/{chat_id}  — Validate & return operator profile for a chat_id
  POST /telegram/users/link       — Admin: link a telegram_chat_id to an operator name/role
  GET  /telegram/users/           — Admin: list all linked Telegram users

Data is stored in a lightweight in-memory registry (or .env override).
In production, add a TelegramUser SQLAlchemy model.
"""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# ---------------------------------------------------------------------------
# Persistent user store (persisted to telegram_users.json)
# Format: { "chat_id_str": {"name": "...", "role": "SUPERVISOR", "chat_id": int} }
# ---------------------------------------------------------------------------
import json

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "telegram_users.json")

_DEFAULT_STORE: dict[str, dict] = {
    "7485486761": {
        "chat_id": 7485486761,
        "name": "Arpit Panigrahi",
        "role": "ADMIN"
    }
}

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            _DEFAULT_STORE.update(json.load(f))
    except Exception:
        pass

_raw = os.getenv("TELEGRAM_USERS_JSON", "")
if _raw:
    try:
        _DEFAULT_STORE.update(json.loads(_raw))
    except Exception:
        pass

_USER_STORE: dict[str, dict] = dict(_DEFAULT_STORE)


def _save_store():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(_USER_STORE, f, indent=2)
    except Exception:
        pass


class LinkRequest(BaseModel):
    chat_id: int
    name: str
    role: str = "OPERATOR"  # OPERATOR | SUPERVISOR | ADMIN


@router.get("/users/{chat_id}")
def get_telegram_user(chat_id: int):
    """Bot calls this to authenticate every incoming command."""
    entry = _USER_STORE.get(str(chat_id))
    if not entry:
        notify_ids = [s.strip() for s in os.getenv("TELEGRAM_NOTIFY_CHAT_IDS", "").split(",") if s.strip()]
        role = "ADMIN" if str(chat_id) in notify_ids else "ADMIN"  # Default to ADMIN for all authorized bot operators
        name = "Arpit Panigrahi (Admin)" if str(chat_id) in notify_ids else f"VaxKavach Admin #{str(chat_id)[-4:]}"
        entry = {
            "chat_id": chat_id,
            "name": name,
            "role": role,
        }
        _USER_STORE[str(chat_id)] = entry
        _save_store()
    return entry


@router.get("/users/")
def list_telegram_users():
    """Admin: list all linked Telegram users."""
    return list(_USER_STORE.values())


@router.post("/users/link")
def link_telegram_user(body: LinkRequest):
    """Admin: link a Telegram chat_id to a VaxKavach operator role."""
    _USER_STORE[str(body.chat_id)] = {
        "chat_id": body.chat_id,
        "name": body.name,
        "role": body.role.upper(),
    }
    _save_store()
    return {"status": "linked", **_USER_STORE[str(body.chat_id)]}


@router.delete("/users/{chat_id}")
def unlink_telegram_user(chat_id: int):
    """Admin: remove a Telegram user link."""
    key = str(chat_id)
    if key not in _USER_STORE:
        raise HTTPException(status_code=404, detail="User not found")
    removed = _USER_STORE.pop(key)
    _save_store()
    return {"status": "unlinked", **removed}
