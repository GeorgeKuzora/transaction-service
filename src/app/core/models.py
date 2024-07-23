import logging
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel

from app.core.errors import ValidationError

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """
    Тип транзакции.

    Может быть либо Продажа, либо Покупка.
    """

    deposit = 0
    withdraw = 1


class TransactionRequest(BaseModel):
    """Запрос создания транзакции."""

    username: str
    amount: Decimal
    transaciton_type: TransactionType


class Transaction(BaseModel):
    """
    Транзакция выполненная пользователем.

    Attributes:
        transaction_id: int | None - ID транзакции
        user_id: int - ID пользователя.
        amount: int - сумма транзакции.
        transaction_type: bool - тип транзации. True-продажа, False-покупка.
        timestamp: datetime - временная метка транзакции.
    """

    username: str
    amount: Decimal
    transaction_type: TransactionType
    timestamp: datetime
    transaction_id: int | None = None


class TransactionReportRequest(BaseModel):
    """Запрос о транзакциях выполненных пользователем."""

    username: str
    start_date: datetime
    end_date: datetime


class TransactionReport(BaseModel):
    """
    Отчет о транзаkциях выполненных пользователем.

    Attributes:
        report_id: int - ID отчета о транзакциях
        user_id: int - ID пользователя.
        start_date: datetime - дата начала периода отчета
        end_date: datetime - дата конца периода отчета.
        transactions: list[Transaction] - список транзакций за период.
    """

    report_id: int
    user_id: str
    start_date: datetime
    end_date: datetime
    transanctions: list[Transaction]


class User(BaseModel):
    """Пользователь."""

    user_id: int | None = None
    username: str
    balance: Decimal
    is_verified: bool

    def validate_transaciton(
        self, transaction_request: TransactionRequest,
    ) -> None:
        """Валидирует транзакцию и баланс."""
        valid = True
        invalid = False
        validation_result = invalid
        if transaction_request.transaciton_type == TransactionType.deposit:
            validation_result = valid
        elif self.balance - transaction_request.amount >= 0:
            validation_result = valid
        elif self.is_verified:
            validation_result = valid
        if not validation_result:
            logger.info(f'Баланс пользователя {transaction_request.username} не может быть отрицательным')  # noqa: E501
            raise ValidationError(f'Баланс пользователя {transaction_request.username} не может быть отрицательным')  # noqa: E501

    def process_transacton(self, transaction: Transaction):
        """Производит изменение баланса пользователя."""
        if transaction.transaction_type == TransactionType.deposit:
            self.balance += transaction.amount
        elif transaction.transaction_type == TransactionType.withdraw:
            self.balance -= transaction.amount
