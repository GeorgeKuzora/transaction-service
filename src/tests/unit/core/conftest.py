from unittest.mock import AsyncMock

import pytest

from app.core.errors import NotFoundError, RepositoryError
from app.core.transactions import TransactionService, Validator


@pytest.fixture
def service():
    """
    Фикстура для получения экземпляра сервиса.

    Возвращает экземпляр сервиса с мок-объектом вместо
    атрибута repository.

    :return: экземпляр сервиса
    :rtype: TransactionService
    """
    repository = AsyncMock()
    return TransactionService(repository)


@pytest.fixture
def service_error_on_get_user(service: TransactionService):
    """
    Фикстура для получения сервиса с моком репозитория.

    Метод репозитория get_user вызывает ошибку.

    :param service: экземпляр сервиса
    :type service: TransactionService
    :return: экземпляр сервиса
    :rtype: TransactionService
    """
    service.repository.get_user.side_effect = NotFoundError
    return service


@pytest.fixture
def service_error_on_update_user(service: TransactionService):
    """
    Фикстура для получения сервиса с моком репозитория.

    Метод репозитория get_user вызывает ошибку.

    :param service: экземпляр сервиса
    :type service: TransactionService
    :return: экземпляр сервиса
    :rtype: TransactionService
    """
    service.repository.update_user.side_effect = RepositoryError
    return service


@pytest.fixture(scope='module')
def validator():
    """
    Фикстура для получения экземпляра валидатора.

    Возвращает экземпляр валидатора.

    :return: экземпляр валидатора
    :rtype: Validator
    """
    return Validator()
