from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from app.service import TransactionType  # noqa
from app.service import RepositoryError, Transaction, TransactionReport, TransactionService  # noqa


@pytest.fixture(scope='module')
def service():
    """
    Фикстура для получения экземпляра сервиса.

    Возвращает экземпляр сервиса с мок-объектом вместо
    атрибута repository.
    """
    repository = MagicMock()
    return TransactionService(repository)
