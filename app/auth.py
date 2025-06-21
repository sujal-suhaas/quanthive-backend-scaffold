from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
import bcrypt

from .database import get_user
from .api_key_utils import generate_api_key

SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# In-memory API key store for demo
fake_api_keys = {"test-api-key": "testuser"}
router = APIRouter()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    username = verify_token(credentials.credentials)
    user = get_user(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_api_key_user(api_key: str = Depends(api_key_header)):
    if api_key and api_key in fake_api_keys:
        username = fake_api_keys[api_key]
        user = get_user(username)
        if user:
            return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
        headers={"WWW-Authenticate": "API-Key"},
    )


def verify_password(plain_password: str, hashed_password: str):
    # Simple comparison for demo - use proper hashing in production
    return plain_password + "_hashed" == hashed_password


@router.post("/auth/generate-api-key")
def create_api_key_for_user(username: str):
    raw_key, hashed_key = generate_api_key(username)
    # Store hashed_key in your persistent store, here we add to fake_api_keys for demo
    fake_api_keys[raw_key] = username
    return {"api_key": raw_key}
