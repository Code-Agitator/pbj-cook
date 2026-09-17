import base64
import hashlib
import hmac
import secrets


def hash_pin(pin: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 180_000)
    return f"pbkdf2_sha256$180000${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_pin(pin: str, encoded: str) -> bool:
    try:
        _, rounds, salt, expected = encoded.split("$", 3)
        actual = hashlib.pbkdf2_hmac("sha256", pin.encode(), base64.b64decode(salt), int(rounds))
        return hmac.compare_digest(actual, base64.b64decode(expected))
    except (ValueError, TypeError):
        return False
