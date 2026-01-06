from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from src.config import Config
import uuid
import logging

password_context = CryptContext(
    schemes=["bcrypt"]
)

ACCESS_TOKEN_EXPIRY = 3600  # in seconds

def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)

def create_access_tokens(user_data:dict, expiry:timedelta= None,refesh:bool=False) -> str:
    payload= {}
    payload["user"] = user_data
    payload["exp"] = datetime.now() +  expiry if expiry else datetime.now() + timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refesh
    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )
    return token

def decode_access_token(token:str)->dict:
    try:
        token_data = jwt.decode(
            jwt = token,
            key = Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None