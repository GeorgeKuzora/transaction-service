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


class TestCreateTransactionReport:
    """Тесты метода create_transaction_report."""

    user_id = 1
    amount = 1
    base_date = datetime(year=2024, month=1, day=1)
    empty_report_lenght = 0
    transactions_in_db = [
        Transaction(
            user_id, amount, TransactionType.BUY, base_date, 1,
        ),
        Transaction(
            user_id,
            amount,
            TransactionType.BUY,
            base_date + timedelta(days=1),
            2,
        ),
    ]

    @pytest.fixture
    def service_with_transactions_in_db(self, service):
        """Фикстура для создания сервиса с транзакциями в базе данных."""
        service.repository.transactions = self.transactions_in_db
        return service

    @pytest.mark.parametrize(
        'user_id, start_date, end_date, expected_tran_qnt', (
            pytest.param(
                user_id,
                base_date - timedelta(days=2),
                datetime.now() + timedelta(days=2),
                len(transactions_in_db),
                id='transactions in period = 2',
            ),
            pytest.param(
                user_id,
                base_date + timedelta(days=2),
                datetime.now() + timedelta(days=4),
                empty_report_lenght,
                id='transactions in period = 0',
            ),
            pytest.param(
                1,
                datetime.now(),
                datetime.now() - timedelta(days=1),
                empty_report_lenght,
                id='invalid period',
                marks=pytest.mark.xfail(raises=ValueError),
            ),
            pytest.param(
                1,
                str(datetime.now()),
                datetime.now() + timedelta(days=1),
                empty_report_lenght,
                id='invalid start date',
                marks=pytest.mark.xfail(raises=ValueError),
            ),
            pytest.param(
                1,
                datetime.now(),
                str(datetime.now() + timedelta(days=1)),
                empty_report_lenght,
                id='invalid end date',
                marks=pytest.mark.xfail(raises=ValueError),
            ),
            pytest.param(
                '1',
                datetime.now(),
                datetime.now() + timedelta(days=1),
                empty_report_lenght,
                id='invalid user id',
                marks=pytest.mark.xfail(raises=ValueError),
            ),
        ),
    )
    def test_create_transaction_report(
        self,
        user_id,
        start_date,
        end_date,
        expected_tran_qnt,
        service_with_transactions_in_db,
    ):
        """Тест метода create_transaction_report."""
        report: TransactionReport = service_with_transactions_in_db.create_transaction_report(  # noqa
            user_id, start_date, end_date,
        )

        assert len(report.transanctions) == expected_tran_qnt
        assert report.start_date == start_date
        assert report.end_date == end_date
        assert report.user_id == user_id
