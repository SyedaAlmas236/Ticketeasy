# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"  # adjust route name if different

# helpers for password hashing (optional convenience wrappers)
def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(hash: str, password: str) -> bool:
    return check_password_hash(hash, password)
