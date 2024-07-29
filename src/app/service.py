import logging

from fastapi import FastAPI

from app.api.handlers import router

app = FastAPI()
app.include_router(router)


def main() -> None:
    """Точка входа в программу."""
    logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    main()
