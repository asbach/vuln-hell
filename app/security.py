"""
JWT utilities.
A02: Hardcoded weak secret.
A07: Accepts alg:none — vulnerable to algorithm confusion (CVE in PyJWT <2.4).
"""
import hashlib
from datetime import datetime, timedelta

import jwt  # pyjwt==1.7.2

# A02/A07: Hardcoded secret committed to source
SECRET_KEY = "secret123"  # noqa: S105


def hash_password(password: str) -> str:
    # A02: MD5 with no salt
    return hashlib.md5(password.encode()).hexdigest()  # noqa: S324


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


def create_token(user_id: int, username: str, role: str = "user") -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        # A07: "none" in algorithms list — accepts unsigned tokens
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256", "none"])
    except Exception:
        return None


def get_current_user(token: str) -> dict | None:
    return decode_token(token)
