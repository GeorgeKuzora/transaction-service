import logging

from sqlalchemy import Engine, Sequence, create_engine, select
from sqlalchemy.orm import Session

from app.core import models as srv
from app.core.config import get_settings
from app.core.errors import NotFoundError, RepositoryError
from app.external.postgres import models as db

logger = logging.getLogger(__name__)


def create_pool() -> Engine:
    """Создет sqlalchemy engine с пулом соединений."""
    settings = get_settings()
    return create_engine(
        str(settings.postgres.pg_dns),
        pool_size=settings.postgres.pool_size,
        max_overflow=settings.postgres.max_overflow,
    )


def create_all_tables() -> None:
    """Создает таблицы в базе данных."""
    pool = create_pool()
    db.Base.metadata.create_all(pool)


class DBTransactionStorage():
    """База данных для работы с транзакциями."""

    def __init__(self) -> None:
        """Метод инициализации DBTransactionStorage."""
        self.pool = create_pool()

    async def create_transaction(
        self, transaction: srv.Transaction,
    ) -> srv.Transaction:
        """Метод создания транзакции."""
        with Session(self.pool) as session:
            user = self._get_db_user(transaction.username, session)
            if user is None:
                logger.error(f'{transaction.username} not found in db')
                raise NotFoundError(
                    detail=f'{transaction.username} not found',
                )
            db_transaction = db.Transaction(
                transaction_type=transaction.transaction_type.value,
                amount=transaction.amount,
                created_at=transaction.timestamp,
                is_deleted=False,
                user=user,
            )
            session.add(db_transaction)
            try:
                session.commit()
            except Exception as err:
                logger.error(
                    f"repository error can't create transaction for {transaction.username}",  # noqa: E501
                )
                raise RepositoryError(
                    detail=f"can't create transaction for {transaction.username}",  # noqa: E501
                ) from err
        return self._get_srv_transaction(db_transaction)

    def _get_db_user(self, username: str, session: Session) -> db.User | None:
        try:
            return session.scalars(
                select(db.User).where(db.User.username == username),
            ).first()
        except Exception as err:
            logger.error(f"repository error can't get {username}")
            raise RepositoryError(
                detail=f"can't get {username}",
            ) from err

    def _get_srv_transaction(
        self, transaction: db.Transaction,
    ) -> srv.Transaction:
        if transaction.transaction_type is False:
            transaction_type = srv.TransactionType.deposit
        else:
            transaction_type = srv.TransactionType.withdraw
        return srv.Transaction(
            username=transaction.user.username,
            transaction_type=transaction_type,
            amount=transaction.amount,
            timestamp=transaction.created_at,
            transaction_id=transaction.id,
        )


class DBUserStorage:
    """База данных."""

    def __init__(self) -> None:
        """Метод инициализации DBUserStorage."""
        self.pool = create_pool()

    async def get_user(self, username: str) -> srv.User | None:
        """
        Получает пользователя из базы данных.

        Получает и возвращает запись о пользователе из базы данных.

        :param username: Имя пользователя
        :type username: str
        :return: Пользователь в базе данных
        :rtype: sev.User | None
        """
        with Session(self.pool) as session:
            db_user = self._get_db_user(username, session)
            if db_user is not None:
                return self._get_srv_user(db_user)
            return None

    async def update_user(  # type: ignore  # deprecated
        self, user: srv.User,
    ) -> srv.User | None:
        """
        Создает пользователя в базе данных.

        Создает, сохраняет в базе данных
        и возвращает индексированную запись о пользователе.

        :param user: Пользователь
        :type user: User
        """
        logger.warning(
            'DEPRICATED: user should be updated in create_transaction',
        )

    def _get_db_user(self, username: str, session: Session) -> db.User | None:
        try:
            return session.scalars(
                select(db.User).where(db.User.username == username),
            ).first()
        except Exception as err:
            logger.error(f"repository error can't get {username}")
            raise RepositoryError(
                detail=f"can't get {username}",
            ) from err

    def _get_srv_user(self, db_user: db.User) -> srv.User:
        return srv.User(
            username=db_user.username,
            balance=db_user.balance,
            is_verified=db_user.is_verified,
            user_id=db_user.id,
        )


class DBReportStorage:
    """База данных DBReportStorage."""

    def __init__(self) -> None:
        """Метод инициализации."""
        self.pool = create_pool()

    async def create_transaction_report(
        self,
        request: srv.TransactionReportRequest,
    ) -> srv.TransactionReport:
        """Метод создания отчета."""
        with Session(self.pool) as session:
            user = self._get_db_user(request.username, session)
            transactions = self._get_transactions(request, session)
            report = db.Report(
                start_date=request.start_date,
                end_date=request.end_date,
                user=user,
                transactions=transactions,
            )
            session.add(report)
            try:
                session.commit()
            except Exception as err:
                logger.error(
                    f"repository error can't create report for {request.username}",  # noqa: E501
                )
                raise RepositoryError(
                    detail=f"can't create report for {request.username}",
                ) from err
            return self._get_srv_report(report)

    def _get_transactions(
        self, request: srv.TransactionReportRequest, session: Session,
    ) -> Sequence:
        stmt = select(db.Transaction).where(
            db.Transaction.user.username == request.username and
            request.start_date.date() <= db.Transaction.created_at.date() <= request.end_date.date(),  # noqa: E501
        )
        try:
            return session.scalars(stmt).all()  # type: ignore
        except Exception as err:
            logger.error("repository error can't get transactions")
            raise RepositoryError(
                detail="can't get transactions",
            ) from err

    def _get_db_user(self, username: str, session: Session) -> db.User | None:
        try:
            return session.scalars(
                select(db.User).where(db.User.username == username),
            ).first()
        except Exception as err:
            logger.error(f"repository error can't get {username}")
            raise RepositoryError(
                detail=f"can't get {username}",
            ) from err

    def _get_srv_transaction(
        self, transaction: db.Transaction,
    ) -> srv.Transaction:
        if transaction.transaction_type is False:
            transaction_type = srv.TransactionType.deposit
        else:
            transaction_type = srv.TransactionType.withdraw
        return srv.Transaction(
            username=transaction.user.username,
            transaction_type=transaction_type,
            amount=transaction.amount,
            timestamp=transaction.created_at,
            transaction_id=transaction.id,
        )

    def _get_srv_report(self, report: db.Report) -> srv.TransactionReport:
        transactions = [
            self._get_srv_transaction(trn) for trn in report.transactions
        ]
        return srv.TransactionReport(
            username=report.user.username,
            start_date=report.start_date,
            end_date=report.end_date,
            transactions=transactions,
            report_id=report.id,
        )


class DBStorage(DBTransactionStorage, DBUserStorage, DBReportStorage):
    """База данных."""

    def __init__(self) -> None:
        """Метод инициализации."""
        self.pool = create_pool()
