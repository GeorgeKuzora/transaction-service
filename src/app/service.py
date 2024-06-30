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

    def create_transaction(
        self, user_id: int, amount: int, transaction_type: TransactionType,
    ) -> Transaction:
        """
        Метод создание записи о проведенной транзакции.

        Создает запись о проведенной транзакции в хранилище данных.

        Args:
            user_id: int - ID пользователя выполневшего транзакцию.
            amount: int - сумма транзакции.
            transaction_type: TransactionType - тип транзакции.

        Return:
            Transaction: Объект транзакции.

        Raises:
            ValueError: В случае если входные значения некоректны.
            RepositoryError: При ошибке доступа к данным.
        """
        self._validate_user_id(user_id)
        self._validate_amount(amount)
        self._validate_transaction_type(transaction_type)

        timestamp = datetime.now()

        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            transacton_type=transaction_type,
            timestamp=timestamp,
        )

        try:
            return self.repository.create_transaction(transaction)
        except RepositoryError as err:
            logger.error(
                f"Can't create transaction {transaction} in data storage",
            )
            raise RepositoryError(
                f"Can't create transaction {transaction} in data storage",
            ) from err

    def _validate_user_id(self, user_id: int) -> None:
        if not isinstance(user_id, int):
            logger.error(f'userID {user_id} is not valid')
            raise ValueError(f'userID {user_id} is not valid')

    def _validate_amount(self, amount: int) -> None:
        if not isinstance(amount, int) and amount <= 0:
            logger.error(f'Transaction amount {amount} is not valid')
            raise ValueError(f'Transaction amount {amount} is not valid')

    def _validate_transaction_type(self, tran_type: TransactionType) -> None:
        if not isinstance(tran_type, TransactionType):
            logger.error(f'Transaction type {tran_type} is not valid')
            raise ValueError(f'Transaction type {tran_type} is not valid')

    def _validate_date(self, date: datetime) -> None:
        if not isinstance(date, datetime):
            logger.error(f'date {date} is not a valid date')
            raise ValueError(f'date {date} is not a valid date')

    def _validate_time_period(
        self, start_date: datetime, end_date: datetime,
    ) -> None:
        if start_date > end_date:
            logger.error(
                f"{start_date} can't be greater than {end_date}",
            )
            raise ValueError(
                f"{start_date} can't be greater than {end_date}",
            )
