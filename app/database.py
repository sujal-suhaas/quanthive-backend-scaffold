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
