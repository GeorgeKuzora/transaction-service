import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.handlers import router
from app.api.healthz.handlers import healthz_router
from app.metrics.tracing import get_tracer, tracing_middleware


@asynccontextmanager
async def lifetime(app: FastAPI):
    """Функция жизненного цикла сервиса."""
    tracer = get_tracer()
    yield {'tracer': tracer}

app = FastAPI()
app.include_router(router)
app.include_router(healthz_router)
app.add_middleware(BaseHTTPMiddleware, dispatch=tracing_middleware)


def main() -> None:
    """Точка входа в программу."""
    logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    main()
