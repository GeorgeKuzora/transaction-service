import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

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


@dataclass
class TransactionReport:
    """
    Отчет о транзациях выполненных пользователем.

    Attributes:
        report_id: int - ID отчета о транзакциях
        user_id: int - ID пользователя.
        start_date: datetime - дата начала периода отчета
        end_date: datetime - дата конца периода отчета.
        transactions: list[Transaction] - список транзакций за период.
    """

    report_id: int
    user_id: int
    start_date: datetime
    end_date: datetime
    transanctions: list[Transaction]


class Repository(Protocol):
    """
    Интерфейс для работы с хранилищами данных.

    Repository - это слой абстракции для работы с хранилищами данных.
    Служит для уменьшения связности компонентов сервиса.
    """

    def create_transaction(self, transaction: Transaction) -> Transaction:
        """Абстрактный метод создания транзакции."""
        ...

    def create_transaction_report(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> TransactionReport:
        """Абстрактный метод создания отчета."""
        ...


class TransactionService:
    """
    Сервис обработки транзакций пользователя.

    Позволяет:
       Создать транзацию и записать ее в хранилище.
       Получть список транзаций за указанный период.

    Attributes:
        repository: Repository - хранилище данных.
    """

    def __init__(self, repository: Repository) -> None:
        """
        Функция инициализации.

        Args:
            repository: Repository - хранилище данных.
        """
        self.repository: Repository = repository

    def _validate_user_id(self, user_id: int) -> None:
        if not isinstance(user_id, int):
            logger.error(f'userID {user_id} is not valid')
            raise ValueError(f'userID {user_id} is not valid')
