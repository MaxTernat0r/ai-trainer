from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler
from app.routers import auth, users, profiles, exercises, workouts, nutrition, chat, analytics, files


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
        allow_origins=settings.CORS_ORIGINS,
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

    return app


app = create_app()
