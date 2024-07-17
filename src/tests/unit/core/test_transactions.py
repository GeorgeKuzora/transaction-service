from datetime import datetime, timedelta

import pytest

from app.core.transactions import (
    RepositoryError,
    Transaction,
    TransactionReport,
    TransactionType,
)


class TestValidator:
    """Тестирует методы класса Validator."""

    int_number_zero = 0
    int_number_one = 1
    int_number_negative = -1
    float_number = 1.1
    str_number = '1'

    @pytest.mark.parametrize(
        'user_id', (
            pytest.param(int_number_zero, id='id 0'),
            pytest.param(int_number_one, id='id 1'),
            pytest.param(
                str_number,
                id='id string',
                marks=pytest.mark.xfail(raises=ValueError),
            ),
            pytest.param(
                float_number,
                id='id float',
                marks=pytest.mark.xfail(raises=ValueError),
            ),
        ),
    )
    def test_validate_user_id(self, user_id, validator):
        """Тест метода validate_user_id."""
        validator.validate_user_id(user_id)

    @pytest.mark.parametrize(
        'amount', (
            pytest.param(int_number_one, id='amount = 1'),
            pytest.param(
                int_number_zero,
                id='amount = 0',
                marks=pytest.mark.xfail(raises=ValueError),
            ),
            pytest.param(
                int_number_negative,
                id='amount = -1',
                marks=pytest.mark.xfail(raises=ValueError),
            ),
            pytest.param(
                str_number,
                id='amount string',
                marks=pytest.mark.xfail(raises=ValueError),
            ),
            pytest.param(
                float_number,
                id='amount float',
                marks=pytest.mark.xfail(raises=ValueError),
            ),
        ),
    )
    def test_validate_amount(self, amount, validator):
        """Тест метода _validate_amount."""
        validator.validate_amount(amount)

    @pytest.mark.parametrize(
        'transaction_type', (
            pytest.param(TransactionType.buy, id='type BUY'),
            pytest.param(TransactionType.sell, id='type SELL'),
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
    def test_validate_transaction_type(self, transaction_type, validator):
        """Тест метода _validate_transaction_type."""
        validator.validate_transaction_type(transaction_type)

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
    def test_validate_date(self, date, validator):
        """Тест метода _validate_date."""
        validator.validate_date(date)

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
    def test_validate_time_period(self, start_date, end_date, validator):
        """Тест метода _validate_time_period."""
        validator.validate_time_period(start_date, end_date)


@pytest.mark.parametrize(
    'user_id, amount, transaction_type', (
        pytest.param(
            1,
            1,
            TransactionType.buy,
            id='valid atributes BUY',
        ),
        pytest.param(
            1,
            1,
            TransactionType.sell,
            id='valid atributes SELL',
        ),
        pytest.param(
            '1',
            1,
            TransactionType.buy,
            id='invalid user ID',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            1,
            -1,
            TransactionType.buy,
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
        1, 1, TransactionType.buy, datetime.now(), 1,
    )
    service.repository.create_transaction.return_value = expected_transaction
    transaction = service.create_transaction(
        user_id, amount, transaction_type,
    )
    assert transaction == expected_transaction


def repository_error(*args):
    """
    Вызывает исключение.

    Служит для вызова в качестве side effect в моках.

    :param args: параметры передаваемые в функцию
    :type args: any
    :raises RepositoryError: исключение для вызова в моках
    """
    raise RepositoryError(args)


@pytest.mark.parametrize(
    'user_id, amount, transaction_type', (
        pytest.param(
            1,
            1,
            TransactionType.buy,
            id='valid atributes BUY',
        ),
        pytest.param(
            1,
            1,
            TransactionType.sell,
            id='valid atributes SELL',
        ),
    ),
)
def test_create_transaction_raises(
    user_id, amount, transaction_type, service,
):
    """Тест метода create_transaction в случае ошибки в репозитории."""
    service.repository.create_transaction = repository_error
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
        1, 1, TransactionType.buy, datetime.now(), 1,
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
    service.repository.create_transaction_report = repository_error
    with pytest.raises(RepositoryError):
        service.create_transaction_report(
            user_id, start_date, end_date,
        )
