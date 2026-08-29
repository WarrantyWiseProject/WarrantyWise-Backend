from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.db.mongodb import get_database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": user_id, "exp": expires}, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.jwt_secret_key.get_secret_value(), algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise error
    except JWTError as exc:
        raise error from exc
    user = await get_database().users.find_one({"id": user_id})
    if not user:
        raise error
    return user

def new_id() -> str:
    return str(uuid4())
