import logging
from copy import copy
from datetime import datetime

from app.core.errors import RepositoryError, ValidationError
from app.core.interfaces import Cache, Repository
from app.core.models import (
    Transaction,
    TransactionReport,
    TransactionReportRequest,
    TransactionRequest,
    TransactionType,
)

logger = logging.getLogger(__name__)


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
        self,
        repository: Repository,
        validator: Validator = default_validator,
        cache: Cache | None = None,
    ) -> None:
        """
        Функция инициализации.

        :param repository: хранилище данных.
        :type repository: Repository
        :param validator: валидатор входных данных.
        :type validator: Validator
        :param cache: Кэш сервиса
        :type cache: Cache
        """
        self.repository = repository
        self.validator = validator
        self.cache = cache

    async def create_transaction(
        self, transaction_request: TransactionRequest,
    ) -> Transaction:
        """
        Метод создание записи о проведенной транзакции.

        Создает запись о проведенной транзакции в хранилище данных.

        :param transaction_request: Запрос о транзакции
        :type transaction_request: TransactionRequest
        :return: объект транзакции
        :rtype: Transaction
        :raises RepositoryError: при ошибке доступа к данным
        :raises ValidationError: при ошибке валидации данных
        """
        user = await self.repository.get_user(transaction_request.username)
        if not user:
            logger.warning(
                f'Пользователь {transaction_request.username} не найден',
            )
            raise ValidationError(
                f'Пользователь {transaction_request.username} не найден',
            )
        user.validate_transaciton(transaction_request)

        timestamp = datetime.now()

        transaction = Transaction(
            username=transaction_request.username,
            amount=transaction_request.amount,
            transaction_type=transaction_request.transaciton_type,
            timestamp=timestamp,
        )

        user.process_transacton(transaction)

        try:
            await self.repository.update_user(user)
        except RepositoryError as user_err:
            logger.error(
                f"Can't update user {user}",
            )
            raise RepositoryError(
                f"Can't update user {user}",
            ) from user_err
        try:
            return await self.repository.create_transaction(transaction)
        except RepositoryError as transaction_err:
            logger.error(
                f"Can't create transaction {transaction}",
            )
            raise RepositoryError(
                f"Can't create transaction {transaction}",
            ) from transaction_err

    async def create_transaction_report(
        self,
        report_request: TransactionReportRequest,
    ) -> TransactionReport:
        """
        Метод создания отчета о транзакциях пользователя.

        Создает сохраняет в хранилище данных и возвращает отчет
        о транзакциях пользоватля за период.

        :param report_request: Запрос отчета
        :type report_request: TransactionReportRequest
        :return: объект отчет о транзакциях
        :rtype: TransactionReport
        """
        self.validator.validate_time_period(
            report_request.start_date, report_request.end_date,
        )

        if self.cache:
            report = await self._create_transaction_report_with_cache(
                report_request,
            )
        else:
            report = await self._create_transaction_report_without_cache(
                report_request,
            )
        return report

    async def _create_transaction_report_with_cache(
        self, request: TransactionReportRequest,
    ) -> TransactionReport:
        report = None
        if self.cache:
            try:
                report = await self.cache.get_cache(request)
            except KeyError:
                report = await self.repository.create_transaction_report(
                    request,
                )
                await self.cache.create_cache(report)
        if report:
            return report
        logger.error('ошибка хранилища данных')
        raise RepositoryError('ошибка хранилища данных')

    async def _create_transaction_report_without_cache(
        self, request: TransactionReportRequest,
    ) -> TransactionReport:
        return await self.repository.create_transaction_report(request)
