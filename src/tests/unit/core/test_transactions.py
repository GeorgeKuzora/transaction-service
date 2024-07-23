from datetime import datetime, timedelta
from decimal import Decimal

import pydantic
import pytest

from app.core.errors import ValidationError
from app.core.models import (
    Transaction,
    TransactionReport,
    TransactionReportRequest,
    TransactionRequest,
    TransactionType,
    User,
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
            pytest.param(TransactionType.withdraw, id='type BUY'),
            pytest.param(TransactionType.deposit, id='type SELL'),
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


user_positive_balance = User(
    username='george', user_id=1, balance=Decimal(1), is_verified=False,
)
user_zero_balance = User(
    username='george', user_id=1, balance=Decimal(0), is_verified=False,
)
amount = Decimal(1)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'user, amount, transaction_type', (
        pytest.param(
            user_positive_balance,
            amount,
            TransactionType.withdraw,
            id='valid atributes BUY',
        ),
        pytest.param(
            user_positive_balance,
            amount,
            TransactionType.deposit,
            id='valid atributes SELL',
        ),
        pytest.param(
            user_zero_balance,
            amount,
            TransactionType.withdraw,
            id='invalid amount',
            marks=pytest.mark.xfail(raises=ValidationError),
        ),
        pytest.param(
            user_positive_balance,
            amount,
            'withdraw',
            id='invalid transaction type',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ),
)
async def test_create_transaction(user, amount, transaction_type, service):
    """Тест метода create_transaction."""
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
        transaciton_type=transaction_type,
    )
    service.repository.get_user.return_value = user
    service.repository.create_transaction.return_value = expected_transaction
    transaction = await service.create_transaction(request)
    assert transaction == expected_transaction


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'user, start_date, end_date', (
        pytest.param(
            user_positive_balance,
            datetime.now(),
            datetime.now() + timedelta(days=1),
            id='valid atributes',
        ),
        pytest.param(
            user_positive_balance,
            datetime.now(),
            datetime.now() - timedelta(days=1),
            id='invalid period',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            user_positive_balance,
            'invalid',
            datetime.now() + timedelta(days=1),
            id='invalid start date',
            marks=pytest.mark.xfail(raises=pydantic.ValidationError),
        ),
        pytest.param(
            user_positive_balance,
            datetime.now(),
            'invalid',
            id='invalid end date',
            marks=pytest.mark.xfail(raises=pydantic.ValidationError),
        ),
    ),
)
async def test_create_transaction_report_without_cache(
    user: User, start_date, end_date, service,
):
    """Тест метода create_transaction_report."""
    request = TransactionReportRequest(
        username=user.username,
        start_date=start_date,
        end_date=end_date,
    )
    expected_transaction = Transaction(
        username=user.username,
        amount=amount,
        transaction_type=TransactionType.deposit,
        timestamp=datetime.now() + timedelta(hours=1),
        transaction_id=1,
    )

    expected_report = TransactionReport(
        report_id=0,
        user_id=user.username,
        start_date=start_date,
        end_date=end_date,
        transanctions=[expected_transaction],
    )

    service.repository.create_transaction_report.return_value = expected_report
    report = await service.create_transaction_report(
        request,
    )
    assert report == expected_report
