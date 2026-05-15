import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///jobtrackr.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-change-in-prod-use-32-chars")
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
