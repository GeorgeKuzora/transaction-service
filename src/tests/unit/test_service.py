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


@pytest.mark.parametrize(
    'date', (
        pytest.param(datetime.now(), id='valid date'),
        pytest.param(
            '12.12.2024',
            id='date as string',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ),
)
def test_validate_date(date, service):
    """Тест метода _validate_date."""
    service._validate_date(date)


@pytest.mark.parametrize(
    'start_date, end_date', (
        pytest.param(
            datetime.now(),
            datetime.now() + timedelta(days=1),
            id='valid time period',
        ),
        pytest.param(
            datetime.now(),
            datetime.now() - timedelta(days=1),
            id='invalid time period end date less than start date',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ),
)
def test_validate_time_period(start_date, end_date, service):
    """Тест метода _validate_time_period."""
    service._validate_time_period(start_date, end_date)


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
    expected_transaction = Transaction(
        1, 1, TransactionType.BUY, datetime.now(), 1,
    )
    service.repository.create_transaction.return_value = expected_transaction
    transaction = service.create_transaction(
        user_id, amount, transaction_type,
    )
    assert transaction == expected_transaction


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
    ),
)
def test_create_transaction_raises(
    user_id, amount, transaction_type, service,
):
    """Тест метода create_transaction в случае ошибки в репозитории."""

    def side_effect(*args):
        raise RepositoryError(args)

    service.repository.create_transaction = side_effect
    with pytest.raises(RepositoryError):
        service.create_transaction(
            user_id, amount, transaction_type,
        )


@pytest.mark.parametrize(
    'user_id, start_date, end_date', (
        pytest.param(
            1,
            datetime.now(),
            datetime.now() + timedelta(days=1),
            id='valid atributes',
        ),
        pytest.param(
            '1',
            datetime.now(),
            datetime.now() + timedelta(days=1),
            id='invalid user ID',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            1,
            datetime.now(),
            datetime.now() - timedelta(days=1),
            id='invalid period',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            1,
            str(datetime.now()),
            datetime.now() + timedelta(days=1),
            id='invalid start date',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            1,
            datetime.now(),
            str(datetime.now() + timedelta(days=1)),
            id='invalid end date',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ),
)
def test_create_transaction_report(
    user_id, start_date, end_date, service,
):
    """Тест метода create_transaction_report."""
    expected_transaction = Transaction(
        1, 1, TransactionType.BUY, datetime.now(), 1,
    )

    expected_report = TransactionReport(
        1,
        1,
        datetime.now(),
        datetime.now() + timedelta(days=1),
        [expected_transaction],
    )

    service.repository.create_transaction_report.return_value = expected_report
    report = service.create_transaction_report(
        user_id, start_date, end_date,
    )
    assert report == expected_report


@pytest.mark.parametrize(
    'user_id, start_date, end_date', (
        pytest.param(
            1,
            datetime.now(),
            datetime.now() + timedelta(days=1),
            id='valid atributes',
        ),
    ),
)
def test_create_transaction_report_raises(
    user_id, start_date, end_date, service,
):
    """Тест метода create_transaction_report в случае ошибки репозитория."""

    def side_effect(*args):
        raise RepositoryError(args)

    service.repository.create_transaction_report = side_effect
    with pytest.raises(RepositoryError):
        service.create_transaction_report(
            user_id, start_date, end_date,
        )
