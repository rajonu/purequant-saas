"""Stateless, short-lived Telegram-to-scanner access tokens.

This module is intentionally isolated from payment and signal dispatch code.
Set SCANNER_GATE_SECRET in both the bot and scanner environments before use.
"""

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, Optional

TOKEN_TTL_SECONDS = 900


def _secret() -> bytes:
    value = os.getenv("SCANNER_GATE_SECRET", "").strip()
    if len(value) < 32:
        raise RuntimeError("SCANNER_GATE_SECRET must be at least 32 characters")
    return value.encode("utf-8")


def issue_token(telegram_user_id: int, ttl_seconds: int = TOKEN_TTL_SECONDS, now: Optional[int] = None) -> str:
    issued_at = int(time.time() if now is None else now)
    payload = {"uid": int(telegram_user_id), "iat": issued_at, "exp": issued_at + int(ttl_seconds)}
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    body = base64.urlsafe_b64encode(raw).rstrip(b"=")
    signature = hmac.new(_secret(), body, hashlib.sha256).digest()
    sig = base64.urlsafe_b64encode(signature).rstrip(b"=")
    return f"{body.decode('ascii')}.{sig.decode('ascii')}"


def verify_token(token: str, now: Optional[int] = None) -> Optional[Dict[str, Any]]:
    try:
        body_text, sig_text = token.split(".", 1)
        body = body_text.encode("ascii")
        expected = hmac.new(_secret(), body, hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(sig_text + "===")
        if not hmac.compare_digest(expected, supplied):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body + b"===").decode("utf-8"))
        current = int(time.time() if now is None else now)
        if current >= int(payload["exp"]):
            return None
        if int(payload["uid"]) <= 0:
            return None
        return payload
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, UnicodeError):
        return None
