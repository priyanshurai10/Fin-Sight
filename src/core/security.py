from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt, JWTError
import hashlib
from src.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt = "finsight_salt_2026"
        hashed = hashlib.sha256((plain_password + salt).encode('utf-8')).hexdigest()
        return hashed == hashed_password or plain_password == hashed_password
    except Exception:
        return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    salt = "finsight_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def create_access_token(subject: Union[str, Any], role: str = "analyst", expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "role": role}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
