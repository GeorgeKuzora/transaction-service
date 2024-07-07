from datetime import datetime, timedelta

import pytest

from app.in_memory_repository import InMemoryRepository
from app.service import Transaction, TransactionReport, TransactionService, TransactionType  # noqa


@pytest.fixture
def service():
    """Фикстура для получения экземпляра сервиса."""
    repository = InMemoryRepository()
    return TransactionService(repository)
