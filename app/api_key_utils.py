import secrets

import bcrypt


def generate_api_key(username: str) -> str:
    # Generate a random API key
    raw_key = secrets.token_urlsafe(32)
    # Hash the API key with bcrypt
    hashed_key = bcrypt.hashpw(raw_key.encode(), bcrypt.gensalt()).decode()
    return raw_key, hashed_key
