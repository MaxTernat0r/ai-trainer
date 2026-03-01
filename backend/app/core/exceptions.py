from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(
        self, status_code: int, detail: str, error_code: str | None = None
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code


class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(404, f"{resource} not found", "NOT_FOUND")


class ForbiddenError(AppException):
    def __init__(self, detail: str = "Access denied") -> None:
        super().__init__(403, detail, "FORBIDDEN")


class BadRequestError(AppException):
    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(400, detail, "BAD_REQUEST")


class UnauthorizedError(AppException):
    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(401, detail, "UNAUTHORIZED")


class AIServiceError(AppException):
    def __init__(self, detail: str = "AI service temporarily unavailable") -> None:
        super().__init__(503, detail, "AI_SERVICE_ERROR")


class RateLimitError(AppException):
    def __init__(self) -> None:
        super().__init__(429, "Rate limit exceeded", "RATE_LIMIT")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.error_code, "message": exc.detail}},
    )
