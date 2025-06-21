import threading
from datetime import datetime

log_lock = threading.Lock()
LOG_FILE = "api_usage.log"

# Log only /auth/me and /protected accesses
MONITORED_PATHS = ["/auth/me", "/protected"]


def log_api_usage(username: str, path: str, api_key: str = None):
    if path not in MONITORED_PATHS:
        return
    log_entry = (
        f"{datetime.utcnow().isoformat()} | user: {username} | path: {path} | "
        f"api_key: {api_key or 'N/A'}\n"
    )
    with log_lock:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)


def get_api_usage(username: str = None, api_key: str = None):
    usage = []
    with log_lock:
        try:
            with open(LOG_FILE, "r") as f:
                for line in f:
                    if (username and f"user: {username}" not in line) and (
                        api_key and f"api_key: {api_key}" not in line
                    ):
                        continue
                    usage.append(line.strip())
        except FileNotFoundError:
            pass
    return usage
