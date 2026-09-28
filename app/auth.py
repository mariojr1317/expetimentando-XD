import base64
import hashlib
import hmac
import os
import time

PASSWORD = os.getenv("RUNNER_PASSWORD", "")
TOKEN_SECRET = os.getenv("TOKEN_SECRET", "")

def configured() -> bool:
    return bool(PASSWORD and TOKEN_SECRET)

def check_password(password: str) -> bool:
    if not configured():
        return False
    return hmac.compare_digest(password, PASSWORD)

def create_token() -> str:
    payload = str(int(time.time())).encode()
    signature = hmac.new(TOKEN_SECRET.encode(), payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(payload + b"." + signature).decode()

def valid_token(token: str, max_age: int = 86400) -> bool:
    if not configured():
        return False
    try:
        raw = base64.urlsafe_b64decode(token.encode())
        payload, signature = raw.split(b".", 1)
        expected = hmac.new(TOKEN_SECRET.encode(), payload, hashlib.sha256).digest()
        timestamp = int(payload.decode())
        return hmac.compare_digest(signature, expected) and time.time() - timestamp < max_age
    except (ValueError, TypeError, UnicodeDecodeError):
        return False
