from pathlib import Path
import secrets


base = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = str(secrets.token_hex(16))
