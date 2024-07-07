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


@pytest.mark.parametrize(
    'user_id', (
        pytest.param(0, id='id 0'),
        pytest.param(1, id='id 1'),
        pytest.param(
            '1',
            id='id string',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            1.1,
            id='id float',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ),
)
def test_validate_user_id(user_id, service):
    """Тест метода _validate_user_id."""
    service._validate_user_id(user_id)
