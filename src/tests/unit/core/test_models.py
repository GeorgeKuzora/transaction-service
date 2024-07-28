from datetime import datetime
from decimal import Decimal

import pytest

from app.core.models import Transaction, TransactionType, User

username = 'george'

deposit_transaction = Transaction(
    amount=Decimal(10),
    username=username,
    transaction_type=TransactionType.deposit,
    timestamp=datetime.now(),
)
withdraw_transaction = Transaction(
    amount=Decimal(10),
    username=username,
    transaction_type=TransactionType.withdraw,
    timestamp=datetime.now(),
)
balance_after_deposit = Decimal(20)  # noqa: WPS432 no magic
balance_after_withdraw = Decimal(0)


@pytest.fixture
def test_user():
    """Ооздает пользователя."""
    return User(
        username=username,
        balance=Decimal(10),
        is_verified=True,
    )


@pytest.mark.parametrize(
    'transaction, expected_balance', (
        pytest.param(
            deposit_transaction,
            balance_after_deposit,
            id='deposit transaction',
        ),
        pytest.param(
            withdraw_transaction,
            balance_after_withdraw,
            id='withdraw transaction',
        ),
    ),
)
def test_user_process_transaction(test_user, transaction, expected_balance):
    """Тестирует метод process_transaction."""
    test_user.process_transacton(transaction)

    assert test_user.balance == expected_balance
