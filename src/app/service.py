import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """
    Исключение возникающее при запросе в хранилище данных.

    Импортировать в имплементации репозитория данных,
    для вызова исключения при ошибке доступа к данным.
    """


class TransactionType(Enum):
    """
    Тип транзакции.

    Может быть либо Продажа, либо Покупка.
    """

    SELL = 0
    BUY = 1


@dataclass
class Transaction:
    """
    Транзакция выполненная пользователем.

    Attributes:
        transaction_id: int | None - ID транзакции
        user_id: int - ID пользователя.
        amount: int - сумма транзакции.
        transaction_type: bool - тип транзации. True-продажа, False-покупка.
        timestamp: datetime - временная метка транзакции.
    """

    user_id: int
    amount: int
    transacton_type: TransactionType
    timestamp: datetime
    transaction_id: int | None = None
