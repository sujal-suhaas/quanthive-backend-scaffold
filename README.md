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