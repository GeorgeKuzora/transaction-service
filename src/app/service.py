import logging

from fastapi import FastAPI

app = FastAPI()


def main() -> None:
    """Точка входа в программу."""
    logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    main()
