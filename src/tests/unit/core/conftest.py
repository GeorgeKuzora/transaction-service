from unittest.mock import MagicMock

import pytest

from app.core.transactions import TransactionService, Validator


@pytest.fixture(scope='module')
def service():
    """
    Фикстура для получения экземпляра сервиса.

    Возвращает экземпляр сервиса с мок-объектом вместо
    атрибута repository.

    :return: экземпляр сервиса
    :rtype: TransactionService
    """
    repository = MagicMock()
    return TransactionService(repository)


@pytest.fixture(scope='module')
def validator():
    """
    Фикстура для получения экземпляра валидатора.

    Возвращает экземпляр валидатора.

    :return: экземпляр валидатора
    :rtype: Validator
    """
    return Validator()
