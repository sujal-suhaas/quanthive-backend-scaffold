# FastAPI Backend Scaffold

## Project Structure
```
fastapi-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py
│   ├── models.py
│   └── database.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## app/main.py
```python
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
        username=current_user["username"],
        email=current_user["email"],
        is_active=current_user["is_active"]
    )

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}, this is a protected route!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## app/auth.py
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .database import get_user

SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

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

def verify_password(plain_password: str, hashed_password: str):
    # Simple comparison for demo - use proper hashing in production
    return plain_password + "_hashed" == hashed_password
```

## app/models.py
```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str
```

## app/database.py
```python
# Simple in-memory database for demo purposes
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "testpass_hashed",
        "is_active": True,
    }
}

def get_user(username: str):
    if username in fake_users_db:
        return fake_users_db[username]
    return None
```

## app/__init__.py
```python
# This file makes Python treat the directory as a package
```

## requirements.txt
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
email-validator==2.1.0
pydantic[email]==2.5.0
```

## Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Makefile
```makefile
.PHONY: help install run test docker-build docker-run docker-stop clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  run          - Run the FastAPI server locally"
	@echo "  test         - Run basic endpoint tests"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker containers"
	@echo "  clean        - Clean up Docker resources"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "Testing basic endpoints..."
	@curl -s http://localhost:8000/ || echo "Server not running"
	@curl -s http://localhost:8000/health || echo "Health check failed"

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d
	@echo "API running at http://localhost:8000"
	@echo "Docs available at http://localhost:8000/docs"

docker-stop:
	docker-compose down

clean:
	docker-compose down -v
	docker system prune -f
```

## README.md
```markdown
# FastAPI Backend Scaffold

A simple FastAPI backend with JWT authentication, Docker containerization, and basic automation scripts.

## Features

- FastAPI web framework
- JWT-based authentication
- Docker containerization
- Makefile for automation
- Basic CRUD endpoints
- Health check endpoint
- Interactive API docs (Swagger UI)

## Quick Start

### Using Docker (Recommended)
```bash
make docker-build
make docker-run
```

### Local Development
```bash
make install
make run
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `GET /protected` - Protected endpoint example

## Testing the Authentication Flow

1. Register a user:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secret123"}'
```

2. Login to get token:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123"}'
```

3. Use token to access protected routes:
```bash
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

- The code uses a simple in-memory database for demo purposes
- JWT secret key should be changed in production
- Password hashing is simplified - use proper bcrypt in production
- Add proper logging, error handling, and validation for production use

## Commands

Run `make help` to see all available commands.
```

## Setup Instructions

1. Create a new directory: `mkdir fastapi-backend && cd fastapi-backend`
2. Create the project structure and copy all the files above
3. Run `make docker-build && make docker-run`
4. Visit http://localhost:8000/docs to see your API!

The scaffold includes:
- JWT authentication with login/register
- Protected routes
- Docker setup with hot reload
- Makefile for common tasks
- Basic error handling
- Interactive API documentation

You can test the auth flow using the example curl commands in the README!