from functools import lru_cache
from argon2 import PasswordHasher

@lru_cache
def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()