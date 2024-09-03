from datetime import datetime
from enum import Enum

from app.core.models import (
    Transaction,
    TransactionReport,
    TransactionReportRequest,
    TransactionType,
)

year = 2024


class TestValues(Enum):
    """Тестовые значения."""

    username = 'george'
    amount = 10
    timestamp_one = datetime(year=year, month=2, day=2)
    timestamp_two = datetime(year=year, month=3, day=3)
    start_date = datetime(year=year, month=1, day=1)
    end_date = datetime(year=year, month=4, day=4)
    deposit = TransactionType.deposit
    withdraw = TransactionType.withdraw


transaction_one = Transaction(
    username=TestValues.username.value,
    amount=TestValues.amount.value,
    transaction_type=TestValues.deposit.value,
    timestamp=TestValues.timestamp_one.value,
)
transaction_two = Transaction(
    username=TestValues.username.value,
    amount=TestValues.amount.value,
    transaction_type=TestValues.withdraw.value,
    timestamp=TestValues.timestamp_one.value,
)
transactions = [transaction_one, transaction_two]
report = TransactionReport(
    username=TestValues.username.value,
    start_date=TestValues.start_date.value,
    end_date=TestValues.end_date.value,
    transactions=transactions,
    report_id=0,
)
report_request = TransactionReportRequest(
    username=TestValues.username.value,
    start_date=TestValues.start_date.value,
    end_date=TestValues.end_date.value,
)
