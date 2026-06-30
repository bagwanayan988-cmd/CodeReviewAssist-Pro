import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    UPLOAD_FOLDER = "uploads"

    REPORT_FOLDER = "reports"