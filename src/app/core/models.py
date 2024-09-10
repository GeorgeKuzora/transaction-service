import logging
from datetime import datetime
from enum import Enum
from typing import Self

from pydantic import BaseModel

from app.core.errors import ValidationError

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """
    Тип транзакции.

    Может быть либо Продажа, либо Покупка.
    """

    deposit = False
    withdraw = True

    def to_int(self) -> int:
        """
        Преобразует TransactionType в int.

        :return: Значение TransactionType в виде int.
        :rtype: int
        """
        tt_value = self.value
        match tt_value:
            case False:
                return 0
            case True:
                return 1

    @classmethod
    def from_int(cls, t_type: int | str) -> Self:
        """
        Преобразует int в TransactionType.

        :param t_type: Значение TransactionType в форме int.
        :type t_type: int, str
        :return: Объект TransactionType соответствующий входному int.
        :rtype: TransactionType
        :raises ValueError: Если в метод передано неверное значение.
        """
        t_type = int(t_type)
        match t_type:
            case 0:
                return cls.deposit  # type:ignore
            case 1:
                return cls.withdraw  # type:ignore
            case _:
                logger.error(
                    f"{t_type} can't be converted to TransactionType",
                )
                raise ValueError(
                    f"{t_type} can't be converted to TransactionType",
                )


class TransactionRequest(BaseModel):
    """Запрос создания транзакции."""

    username: str
    amount: int
    transaction_type: TransactionType


class Transaction(BaseModel):
    """
    Транзакция выполненная пользователем.

    Attributes:
        transaction_id: int | None - ID транзакции
        username: str - ID пользователя.
        amount: int - сумма транзакции.
        transaction_type: bool - тип транзакции. True-продажа, False-покупка.
        timestamp: datetime - временная метка транзакции.
    """

    username: str
    amount: int
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
    Отчет о транзакциях выполненных пользователем.

    Attributes:
        report_id: int - ID отчета о транзакциях
        username: int - ID пользователя.
        start_date: datetime - дата начала периода отчета
        end_date: datetime - дата конца периода отчета.
        transactions: list[Transaction] - список транзакций за период.
    """

    report_id: int | None
    username: str
    start_date: datetime
    end_date: datetime
    transactions: list[Transaction]


class User(BaseModel):
    """Пользователь."""

    user_id: int | None = None
    username: str
    balance: int
    is_verified: bool

    def validate_transaction(
        self, transaction_request: TransactionRequest,
    ) -> None:
        """
        Валидирует транзакцию и баланс.

        :param transaction_request: Запрос на создание транзакции.
        :type transaction_request: TransactionRequest
        :raises ValidationError: Если транзакция не прошла валидацию.
        """
        valid = True
        invalid = False
        validation_result = invalid
        if transaction_request.transaction_type == TransactionType.deposit:
            validation_result = valid
        elif self.balance - transaction_request.amount >= 0:
            validation_result = valid
        elif self.is_verified:
            validation_result = valid
        if not validation_result:
            logger.info(f'Баланс пользователя {transaction_request.username} не может быть отрицательным')  # noqa: E501
            raise ValidationError(detail=f'Баланс пользователя {transaction_request.username} не может быть отрицательным')  # noqa: E501

    def process_transaction(self, transaction: Transaction):
        """
        Производит изменение баланса пользователя.

        :param transaction: Транзакция для изменения баланса.
        :type transaction: Transaction
        """
        if transaction.transaction_type == TransactionType.deposit:
            self.balance += transaction.amount
        elif transaction.transaction_type == TransactionType.withdraw:
            self.balance -= transaction.amount
