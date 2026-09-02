from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("API_BASE_URL", "http://localhost:8080").rstrip("/")
    user_1: str = os.getenv("API_USER_1", "test1")
    password_1: str = os.getenv("API_PASSWORD_1", "test123")
    user_2: str = os.getenv("API_USER_2", "test2")
    password_2: str = os.getenv("API_PASSWORD_2", "test456")
    timeout: float = float(os.getenv("API_TIMEOUT_SECONDS", "5"))
    load_requests: int = int(os.getenv("LOAD_REQUESTS", "1000"))
    load_workers: int = int(os.getenv("LOAD_WORKERS", "20"))
