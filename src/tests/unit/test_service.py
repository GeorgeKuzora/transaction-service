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


@pytest.mark.parametrize(
    'amount', (
        pytest.param(1, id='amount = 1'),
        pytest.param(
            0,
            id='amount = 0',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            -1,
            id='amount = -1',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            '1',
            id='amount string',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            1.1,
            id='amount float',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ),
)
def test_validate_amount(amount, service):
    """Тест метода _validate_amount."""
    service._validate_amount(amount)


@pytest.mark.parametrize(
    'transaction_type', (
        pytest.param(TransactionType.BUY, id='type BUY'),
        pytest.param(TransactionType.SELL, id='type SELL'),
        pytest.param(
            'BUY',
            id='type string BUY',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            'SELL',
            id='type string SELL',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ),
)
def test_validate_transaction_type(transaction_type, service):
    """Тест метода _validate_transaction_type."""
    service._validate_transaction_type(transaction_type)
