import logging

from fastapi import FastAPI

from app.api.handlers import router
from app.api.healthz.handlers import healthz_router

app = FastAPI()
app.include_router(router)
app.include_router(healthz_router)


def main() -> None:
    """Точка входа в программу."""
    logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    main()
