from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import uuid
import logging

password_context = CryptContext(
    schemes=["bcrypt"]
)

ACCESS_TOKEN_EXPIRY = 3600  # in seconds

def hash_password(password: str) -> str:
    return password_context.hash(password)



print(hash_password("test123"))