import logging

from app.core.models import (
    Transaction,
    TransactionReport,
    TransactionReportRequest,
    User,
)

logger = logging.getLogger(__name__)


class InMemoryRepository:
    """
    Имплементация хранилища данных в оперативной памяти.

    Сохраняет данные только на время работы программы.
    Для хранения данных использует списки python.

    Attributes:
        transactions: list[Transactions] - созданные транзакции.
        transactions_count: int - счетчик сохраненных транзакций.
        reports: list[TransactionReport] - созданные отчеты.
        reports_count: int - счетчик сохраненных отчетов.
    """

    def __init__(self) -> None:
        """Функция инициализации."""
        self.transactions: list[Transaction] = []
        self.transactions_count: int = 0
        self.reports: list[TransactionReport] = []
        self.reports_count: int = 0
        self.users: list[User] = []
        self.users_count: int = 0

    async def create_transaction(self, transaction: Transaction) -> Transaction:
        """
        Создает запись о транзакции и возвращает ее.

        Создает индексированную запись о транзакции и записывает ее в
        список транзакций. Возвращает созданную индексированную запись
        о транзакции.

        :param transaction: Неиндексированный объект Transaction.
        :type transaction: Transaction
        :return: индексированная запись о транзакции.
        :rtype: Transaction
        """
        indexed_transaction = Transaction(
            username=transaction.username,
            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            timestamp=transaction.timestamp,
            transaction_id=self.transactions_count,
        )

        self.transactions.append(indexed_transaction)
        self.transactions_count += 1
        logger.info(f'created {transaction}')

        return indexed_transaction

    async def create_transaction_report(
        self, request: TransactionReportRequest,
    ) -> TransactionReport:
        """
        Создает отчет о транзакциях пользователя за период.

        Создает отчет о транзациях пользователя на основании
        ID пользователя, дат начала и конца периода. Сохраняет отчет
        в список, возвращает отчет.

        :param request: Запрос отчета
        :type request: TransactionReportRequest
        :return: отчет о транзакциях пользователя
        :rtype: TransactionReport
        """
        filtered_transactions = [
            in_transaction for in_transaction in self.transactions if (
                in_transaction.username == request.username and
                request.start_date.date() <=
                in_transaction.timestamp.date() <=
                request.end_date.date()
            )
        ]

        report = TransactionReport(
            report_id=self.reports_count,
            user_id=request.username,
            start_date=request.start_date,
            end_date=request.end_date,
            transanctions=filtered_transactions,
        )

        self.reports_count += 1
        self.reports.append(report)
        logger.info(f'created{report}')

        return report

    async def update_user(
        self, user: User,
    ) -> User | None:
        """
        Создает пользователя в базе данных.

        Создает, сохраняет в базе данных
        и возвращает индексированную запись о пользователе.

        :param user: Пользователь
        :type user: User
        :return: индексированная запись о пользователе.
        :rtype: User
        """
        user_in_db = await self.get_user(user.username)

        if user_in_db is None:
            user_in_db = await self.create_user(user)
            logger.info(f'Created user {user_in_db}')
            return user_in_db

        user_position = self.users.index(user_in_db)
        user.user_id = user_in_db.user_id
        self.users[user_position] = user
        logger.info(f'Updated {user}')
        return user

    async def create_user(self, user: User) -> User:
        """
        Создает пользователя в базе данных.

        Создает, сохраняет в базе данных
        и возвращает индексированную запись о пользователе.

        :param user: неидексированная запись о пользователе.
        :type user: User
        :return: индексированная запись о пользователе.
        :rtype: User
        """
        indexed_user = User(
            username=user.username,
            balance=user.balance,
            is_verified=user.is_verified,
            user_id=self.users_count,
        )
        self.users.append(indexed_user)
        self.users_count += 1
        logger.info(f'Created user {indexed_user}')
        return indexed_user

    async def get_user(self, username: str) -> User | None:
        """
        Получает пользователя из базы данных.

        Получает и возвращает запись о пользователе из базы данных.

        :param username: Имя пользователя
        :type username: str
        :return: индексированная запись о пользователе.
        :rtype: User
        """
        try:
            in_db_user = [
                member for member in self.users if (
                    member.username == username
                )
            ][0]
        except IndexError:
            logger.warning(f'{username} is not found')
            return None

        logger.info(f'got {in_db_user}')
        return in_db_user
