import pytest

from app.core.transactions import TransactionService
from app.external.in_memory_repository import InMemoryRepository


@pytest.fixture
def service():
    """
    Фикстура для получения экземпляра сервиса.

    :return: экземпляр сервиса
    :rtype: TransactionService
    """
    repository = InMemoryRepository()
    return TransactionService(repository)
