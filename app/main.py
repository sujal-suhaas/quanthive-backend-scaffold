from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
import uvicorn

from .auth import get_current_user, create_access_token, verify_password
from .models import User, UserCreate, UserLogin
from .database import fake_users_db, get_user

app = FastAPI(title="FastAPI Backend Scaffold", version="1.0.0")
security = HTTPBearer()

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
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": user.password + "_hashed",  # Simple fake hashing
        "is_active": True
    }
    
    return MessageResponse(message="User registered successfully")

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
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return User(
        username="username",
        email="email",
        is_active=current_user["hashed_password"]
    )

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}, this is a protected route!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
