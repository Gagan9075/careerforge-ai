from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.auth.router import router as auth_router

from app.profile.router import router as profile_router

from app.resume.router import router as resume_router

from app.ai.router import router as ai_router

from app.resume.upload import router as resume_upload_router
from app.ats.router import router as ats_router
from app.dashboard.router import router as dashboard_router
from app.jobs.router import router as jobs_router
from app.jobs.application_router import router as application_router
from app.notifications.router import router as notification_router

from contextlib import asynccontextmanager

from app.notifications.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()

    try:
        yield
    finally:
        stop_scheduler()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


# Authentication routes
app.include_router(
    auth_router,
    prefix="",
)

app.include_router(
    profile_router,
    prefix="",
)

app.include_router(resume_router)
app.include_router(resume_upload_router)
app.include_router(ai_router)
app.include_router(ats_router)
app.include_router(dashboard_router)
app.include_router(jobs_router)
app.include_router(application_router)
app.include_router(notification_router)

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