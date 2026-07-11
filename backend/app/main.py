from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.get("/")
def root():
    return {
        "message": "Welcome to CareerForge AI 🚀"
    }


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": str(e)
        }