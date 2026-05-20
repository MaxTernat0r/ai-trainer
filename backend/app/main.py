from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler
from app.routers import auth, users, profiles, exercises, workouts, nutrition, chat, analytics, files


def _cors_origins() -> list[str]:
    origins = [*settings.CORS_ORIGINS, settings.FRONTEND_URL.rstrip("/")]
    return list(dict.fromkeys(origin for origin in origins if origin))


def _local_dev_origin_regex() -> str | None:
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    if not frontend_url.startswith(("http://localhost", "http://127.0.0.1")):
        return None

    return (
        r"^http://("
        r"localhost|127\.0\.0\.1|0\.0\.0\.0|"
        r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
        r"192\.168\.\d{1,3}\.\d{1,3}|"
        r"172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}"
        r")(:\d+)?$"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_origin_regex=_local_dev_origin_regex(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppException, app_exception_handler)

    prefix = settings.API_V1_PREFIX
    app.include_router(auth.router, prefix=prefix)
    app.include_router(users.router, prefix=prefix)
    app.include_router(profiles.router, prefix=prefix)
    app.include_router(exercises.router, prefix=prefix)
    app.include_router(workouts.router, prefix=prefix)
    app.include_router(nutrition.router, prefix=prefix)
    app.include_router(chat.router, prefix=prefix)
    app.include_router(analytics.router, prefix=prefix)
    app.include_router(files.router, prefix=prefix)
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

    return app


app = create_app()
