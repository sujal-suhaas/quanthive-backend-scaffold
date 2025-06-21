from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
import uvicorn

from .auth import (
    get_current_user,
    create_access_token,
    verify_password,
    get_api_key_user,
    router as auth_router,
)
from .models import User, UserCreate, UserLogin
from .database import fake_users_db, get_user
from .metering import log_api_usage
from .api_key_utils import generate_api_key

app = FastAPI(title="FastAPI Backend Scaffold", version="1.0.0")
security = HTTPBearer()
app.include_router(auth_router)


class MessageResponse(BaseModel):
    message: str


@app.get("/")
async def root():
    return {"message": "FastAPI Backend is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fastapi-backend"}


@app.post("/auth/register", response_model=MessageResponse)
async def register(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")

    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": user.password + "_hashed",  # Simple fake hashing
        "is_active": True,
    }

    # Generate API key for the new user
    raw_key, hashed_key = generate_api_key(user.username)
    from .auth import fake_api_keys

    fake_api_keys[raw_key] = user.username

    return MessageResponse(message=f"User registered successfully. API Key: {raw_key}")


@app.post("/auth/login")
async def login(user: UserLogin):
    db_user = get_user(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=User)
async def read_users_me(
    request: Request,
    current_user: dict = Depends(get_current_user),
    api_key_user: dict = Depends(get_api_key_user),
):
    log_api_usage(
        current_user["username"], request.url.path, request.headers.get("x-api-key")
    )
    return User(
        username=current_user["username"],
        email=current_user["email"],
        is_active=current_user["is_active"],
    )


@app.get("/protected")
async def protected_route(
    request: Request,
    current_user: dict = Depends(get_current_user),
    api_key_user: dict = Depends(get_api_key_user),
):
    log_api_usage(
        current_user["username"], request.url.path, request.headers.get("x-api-key")
    )
    return {"message": f"Hello {current_user['username']}, this is a protected route!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
