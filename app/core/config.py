import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DB_PATH = os.getenv("DB_PATH", "./rag_jdr_db")
    MODEL = os.getenv("MODEL", "gemini-2.5-flash-preview-09-2025")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8642"))

settings = Settings()