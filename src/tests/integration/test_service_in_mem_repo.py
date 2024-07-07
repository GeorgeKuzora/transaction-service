from datetime import datetime, timedelta

import pytest

from app.in_memory_repository import InMemoryRepository
from app.service import Transaction, TransactionReport, TransactionService, TransactionType  # noqa


@pytest.fixture
def service():
    """Фикстура для получения экземпляра сервиса."""
    repository = InMemoryRepository()
    return TransactionService(repository)


@pytest.mark.parametrize(
    'user_id, amount, transaction_type', (
        pytest.param(
            1,
            1,
            TransactionType.BUY,
            id='valid atributes BUY',
        ),
        pytest.param(
            1,
            1,
            TransactionType.SELL,
            id='valid atributes SELL',
        ),
        pytest.param(
            '1',
            1,
            TransactionType.BUY,
            id='invalid user ID',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            1,
            -1,
            TransactionType.BUY,
            id='invalid amount',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            1,
            1,
            'BUY',
            id='invalid transaction type',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ),
)
def test_create_transaction(user_id, amount, transaction_type, service):
    """Тест метода create_transaction."""
    transaction = service.create_transaction(
        user_id, amount, transaction_type,
    )
    assert len(service.repository.transactions) == 1
    assert transaction.user_id == 1
    assert transaction.amount == 1
    assert transaction.transacton_type in {
        TransactionType.BUY,
        TransactionType.SELL,
    }
