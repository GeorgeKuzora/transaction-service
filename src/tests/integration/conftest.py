import pytest

from app.core.transactions import TransactionService
from app.external.in_memory_repository import InMemoryRepository
from app.external.redis import TransactionReportCache


@pytest.fixture
def service():
    """
    Фикстура для получения экземпляра сервиса.

    :return: экземпляр сервиса
    :rtype: TransactionService
    """
    repository = InMemoryRepository()
    return TransactionService(repository)


@pytest.fixture
def service_with_cache():
    """
    Фикстура для получения экземпляра сервиса с кэшем.

    :return: экземпляр сервиса
    :rtype: TransactionService
    """
    repository = InMemoryRepository()
    cache = TransactionReportCache()
    return TransactionService(repository, cache=cache)
