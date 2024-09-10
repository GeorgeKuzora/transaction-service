from datetime import datetime, timedelta

import pytest

from app.core.errors import NotFoundError, ValidationError
from app.core.models import (
    Transaction,
    TransactionReportRequest,
    TransactionRequest,
    TransactionType,
    User,
)

user_positive_balance = User(
    username='george', balance=1, is_verified=False, user_id=1,
)
user_zero_balance = User(
    username='george', balance=0, is_verified=False, user_id=1,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'user, amount, transaction_type', (
        pytest.param(
            user_positive_balance,
            1,
            TransactionType.withdraw,
            id='valid attributes withdraw',
        ),
        pytest.param(
            user_positive_balance,
            1,
            TransactionType.deposit,
            id='valid attributes deposit',
        ),
        pytest.param(
            user_zero_balance,
            1,
            TransactionType.withdraw,
            id='invalid amount',
            marks=pytest.mark.xfail(raises=ValidationError),
        ),
        pytest.param(
            user_positive_balance,
            1,
            'BUY',
            id='invalid transaction type',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ),
)
async def test_create_transaction(
    user: User, amount, transaction_type, service,
):
    """Тест метода create_transaction."""
    await service.repository.create_user(user)

    expected_transaction = Transaction(
        username=user.username,
        amount=amount,
        transaction_type=transaction_type,
        timestamp=datetime.now(),
        transaction_id=1,
    )
    request = TransactionRequest(
        username=user.username,
        amount=amount,
        transaction_type=transaction_type,
    )
    transaction = await service.create_transaction(request)
    assert len(service.repository.transactions) == 1
    assert transaction.username == expected_transaction.username
    assert transaction.amount == expected_transaction.amount
    assert transaction.transaction_type == expected_transaction.transaction_type


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'user, amount, transaction_type', (
        pytest.param(
            user_positive_balance,
            1,
            TransactionType.withdraw,
            id='user not found',
        ),
    ),
)
async def test_create_transaction_raises(
    user: User, amount, transaction_type, service,
):
    """create_transaction поднимает ошибку если пользователь не найден."""
    request = TransactionRequest(
        username=user.username,
        amount=amount,
        transaction_type=transaction_type,
    )
    with pytest.raises(NotFoundError):
        await service.create_transaction(request)


class TestCreateTransactionReport:
    """Тесты метода create_transaction_report."""

    username = 'george'
    amount = 1
    date = {'year': 2024, 'month': 1, 'day': 1}
    base_date = datetime(
        year=date['year'], month=date['month'], day=date['day'],
    )
    empty_report_length = 0
    transactions_in_db = [
        Transaction(
            username=username,
            amount=amount,
            transaction_type=TransactionType.withdraw,
            timestamp=base_date,
            transaction_id=1,
        ),
        Transaction(
            username=username,
            amount=amount,
            transaction_type=TransactionType.withdraw,
            timestamp=base_date + timedelta(days=1),
            transaction_id=2,
        ),
    ]

    @pytest.fixture
    def service_with_transactions_without_cache(self, service):
        """Фикстура для создания сервиса без кэша."""
        service.repository.transactions = self.transactions_in_db
        return service

    @pytest.fixture
    def service_with_transactions_with_cache(self, service_with_cache):
        """Фикстура для создания сервиса без кэша."""
        service_with_cache.repository.transactions = self.transactions_in_db
        return service_with_cache

    @pytest.fixture(
        params=[
            'service_with_transactions_without_cache',
            'service_with_transactions_with_cache',
        ],
    )
    def service_with_transactions(self, request):
        """Фикстура для создания сервиса с транзакциями."""
        service = request.getfixturevalue(request.param)
        service.repository.transactions = self.transactions_in_db
        return service

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'report_request, expected_tran_qnt', (
            pytest.param(
                TransactionReportRequest(
                    username=username,
                    start_date=base_date - timedelta(days=2),
                    end_date=datetime.now() + timedelta(days=2),
                ),
                len(transactions_in_db),
                id='transactions in period = 2',
            ),
            pytest.param(
                TransactionReportRequest(
                    username=username,
                    start_date=base_date + timedelta(days=2),
                    end_date=datetime.now() + timedelta(days=4),
                ),
                empty_report_length,
                id='transactions in period = 0',
            ),
            pytest.param(
                TransactionReportRequest(
                    username=username,
                    start_date=datetime.now(),
                    end_date=datetime.now() - timedelta(days=1),
                ),
                empty_report_length,
                id='invalid period',
                marks=pytest.mark.xfail(raises=ValidationError),
            ),
        ),
    )
    async def test_create_transaction_report(
        self,
        report_request: TransactionReportRequest,
        expected_tran_qnt,
        service_with_transactions,
    ):
        """Тест метода create_transaction_report."""
        report = await service_with_transactions.create_transaction_report(
            report_request,
        )

        assert len(report.transactions) == expected_tran_qnt
        assert report.start_date == report_request.start_date
        assert report.end_date == report_request.end_date
        assert report.username == report_request.username
