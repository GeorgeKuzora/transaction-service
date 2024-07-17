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

    sell = 0
    buy = 1


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
        ...  # noqa: WPS428 valid protocol syntax

    def create_transaction_report(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> TransactionReport:
        """Абстрактный метод создания отчета."""
        ...  # noqa: WPS428 valid protocol syntax


class Validator:
    """Валидатор для определения логики валидации поступающих данных."""

    def validate_user_id(self, user_id: int) -> None:
        """
        Метод валидации id пользователя.

        :param user_id: ID пользователя
        :type user_id: int
        :raises ValueError: если валидация не пройдена
        """
        if not isinstance(user_id, int) or user_id < 0:  # type: ignore
            logger.error(f'not valid userID {user_id}')
            raise ValueError(f'not valid userID {user_id}')

    def validate_amount(self, amount: int) -> None:
        """
        Метод валидации величины транзакции.

        :param amount: Величина транзакции
        :type amount: int
        :raises ValueError: если валидация не пройдена
        """
        if not isinstance(amount, int) or amount <= 0:  # type: ignore
            logger.error(f'not valid transaction amount {amount}')
            raise ValueError(f'not valid transaction amount {amount}')

    def validate_transaction_type(self, tran_type: TransactionType) -> None:
        """
        Метод валидации типа транзакции.

        :param tran_type: тип транзакции
        :type tran_type: TransactionType
        :raises ValueError: если валидация не пройдена
        """
        if not isinstance(tran_type, TransactionType):
            logger.error(  # type: ignore
                f'Not valid transaction type {tran_type}',
            )
            raise ValueError(
                f'Not valid transaction type {tran_type}',
            )

    def validate_date(self, date: datetime) -> None:
        """
        Метод валидации даты.

        :param date: дата
        :type date: datetime
        :raises ValueError: если валидация не пройдена
        """
        if not isinstance(date, datetime):
            logger.error(f'date {date} is not a valid date')  # type: ignore
            raise ValueError(f'date {date} is not a valid date')

    def validate_time_period(
        self, start_date: datetime, end_date: datetime,
    ) -> None:
        """
        Метод валидации периода времени.

        :param start_date: начальная дата периода
        :type start_date: datetime
        :param end_date: конечная дата периода
        :type end_date: datetime
        :raises ValueError: если валидация не пройдена
        """
        if start_date > end_date:
            logger.error(
                f"{start_date} can't be greater than {end_date}",
            )
            raise ValueError(
                f"{start_date} can't be greater than {end_date}",
            )


default_validator = Validator()


class TransactionService:
    """
    Сервис обработки транзакций пользователя.

    Позволяет:
       Создать транзацию и записать ее в хранилище.
       Получть список транзаций за указанный период.

    Attributes:
        repository: Repository - хранилище данных.
    """

    def __init__(
        self, repository: Repository, validator: Validator = default_validator,
    ) -> None:
        """
        Функция инициализации.

        :param repository: хранилище данных.
        :type repository: Repository
        :param validator: валидатор входных данных.
        :type validator: Validator
        """
        self.repository = repository
        self.validator = validator

    def create_transaction(
        self, user_id: int, amount: int, transaction_type: TransactionType,
    ) -> Transaction:
        """
        Метод создание записи о проведенной транзакции.

        Создает запись о проведенной транзакции в хранилище данных.

        :param user_id: ID пользователя выполневшего транзакцию.
        :type user_id: int
        :param amount: сумма транзакции.
        :type amount: int
        :param transaction_type: тип транзакции
        :type transaction_type: TransactionType
        :return: объект транзакции
        :rtype: Transaction
        :raises RepositoryError: при ошибке доступа к данным
        """
        self.validator.validate_user_id(user_id)
        self.validator.validate_amount(amount)
        self.validator.validate_transaction_type(transaction_type)

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
                f"Can't create transaction {transaction}",
            )
            raise RepositoryError(
                f"Can't create transaction {transaction}",
            ) from err

    def create_transaction_report(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> TransactionReport:
        """
        Метод создания отчета о транзакциях пользователя.

        Создает сохраняет в хранилище данных и возвращает отчет
        о транзакциях пользоватля за период.

        :param user_id: ID пользователя выполневшего транзакцию
        :type user_id: int
        :param start_date: дата начала периода
        :type start_date: datetime
        :param end_date: дата конца периода
        :type end_date: datetime
        :return: объект отчет о транзакциях
        :rtype: TransactionReport
        :raises RepositoryError: при ошибке доступа к данным
        """
        self.validator.validate_user_id(user_id)
        self.validator.validate_date(start_date)
        self.validator.validate_date(end_date)
        self.validator.validate_time_period(start_date, end_date)

        try:
            return self.repository.create_transaction_report(
                user_id, start_date, end_date,
            )
        except RepositoryError as err:
            logger.error(
                f"Can't create report for user {user_id}",
            )
            raise RepositoryError(
                f"Can't create report for user {user_id}",
            ) from err
