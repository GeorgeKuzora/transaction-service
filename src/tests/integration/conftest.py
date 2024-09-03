import logging

import pytest
from httpx import AsyncClient

from app.core.models import TransactionRequest, User
from app.core.transactions import TransactionService
from app.external.in_memory_repository import InMemoryRepository
from app.external.redis import TransactionReportCache
from app.service import app

logger = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def client() -> AsyncClient:
    """Создает тестовый клиент."""
    return AsyncClient(app=app, base_url='http://test')


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


@pytest.fixture
def service_with_user_fixture(service_with_cache: TransactionService):
    """
    Возвращает функцию для создания сервиса.

    Возвращаемая функция примает user,
    создает запись о пользователе в базе данных

    :param service_with_cache: экземпляр сервиса
    :type service_with_cache: TransactionSerivce
    :return: функция создания сервиса
    :rtype: callable
    """
    async def _service_with_cache_fixture(user):  # noqa: WPS430, E501 need for service state parametrization
        if service_with_cache.cache is not None:
            await service_with_cache.cache.flush_cache()
        user = await service_with_cache.repository.create_user(user)
        return service_with_cache
    return _service_with_cache_fixture


@pytest.fixture
def service_with_transactions_fixture(
    service_with_user_fixture,
):
    """
    Возвращает функцию для создания сервиса.

    Возвращаемая функция примает user,
    создает запись о пользователе в базе данных

    :param service_with_user_fixture: функция создания сервиса c пользователем
    :type service_with_user_fixture: Callable
    :return: функция создания сервиса
    :rtype: callable
    """
    async def _service_with_transactions_fixture(  # noqa: WPS430, E501 need for service state parametrization
        user: User, transactions: list[TransactionRequest],
    ):
        service: TransactionService = await service_with_user_fixture(user)
        if service.cache is not None:
            await service.cache.flush_cache()
        for transaction in transactions:
            await service.create_transaction(transaction)
        return service
    return _service_with_transactions_fixture


@pytest.fixture
def service_mocker(monkeypatch):
    """
    Мокирует app.api.handlers.service, возращает функцию мокирования.

    Функция мокирования принимает объект сервиса и подменяет им
    объект сервиса в модуле хэндлеров.

    :param monkeypatch: Фикстура для патча объектов
    :return: Функция мокирования
    :rtype: Callable
    """
    def _service_mocker(service: TransactionService):  # noqa: WPS430, E501 need for params
        monkeypatch.setattr(
            'app.api.handlers.service',
            service,
        )
    return _service_mocker
