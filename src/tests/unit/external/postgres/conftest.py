import logging
from collections import namedtuple
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import models as srv
from app.external.postgres import models as db
from app.external.postgres.storage import DBStorage

logger = logging.getLogger(__name__)

user = namedtuple(
    'TestUser',
    'username, hashed_password, balance, is_verified, is_deleted',
)
test_user = user(  # noqa: S106
    username='george',
    hashed_password='3sfd235',
    balance=10,
    is_verified=True,
    is_deleted=False,
)
valid_user = srv.User(
    username=test_user.username,
    balance=test_user.balance,
    is_verified=test_user.is_verified,
)
test_transactions = [
    srv.Transaction(
        username=test_user.username,
        amount=2,
        transaction_type=srv.TransactionType.withdraw,
        timestamp=datetime(year=2024, month=1, day=1),  # noqa: WPS432
    ),
    srv.Transaction(
        username=test_user.username,
        amount=4,
        transaction_type=srv.TransactionType.deposit,
        timestamp=datetime(year=2024, month=1, day=15),  # noqa: WPS432
    ),
]
test_report_request = srv.TransactionReportRequest(
    username=test_user.username,
    start_date=datetime(year=2024, month=1, day=1),  # noqa: WPS432
    end_date=datetime(year=2024, month=1, day=15),  # noqa: WPS432
)


@pytest.fixture
def storage() -> DBStorage:
    """Создает объект DBStorage."""
    return DBStorage()


@pytest.fixture
def storage_with_user(storage: DBStorage):
    """Создает объект DBStorage с добавленным пользователем."""
    with Session(storage.pool) as session:
        user = db.User(
            username=test_user.username,
            hashed_password=test_user.hashed_password,
            balance=test_user.balance,
            is_verified=test_user.is_verified,
            is_deleted=test_user.is_deleted,
        )
        session.add(user)
        session.commit()
        try:
            yield storage, user
        except Exception:
            logger.debug('exception in tests with storage_with_user')
        finally:
            clean_storage(session, db.Report)
            clean_storage(session, db.Transaction)
            session.delete(user)
            session.commit()


@pytest.fixture
def storage_without_user(storage: DBStorage):
    """Создает объект DBStorage без пользователей."""
    try:
        yield storage, None
    except Exception:
        logger.debug('exception in tests with storage_without_user')


@pytest.fixture
def storage_with_transactions(storage_with_user):
    """Создает объект DBStorage с добавленными транзакциями."""
    storage, user = storage_with_user
    with Session(storage.pool) as session:
        db_user = session.scalars(
            select(db.User).where(db.User.username == user.username),
        ).first()
        transactions = [
            _create_db_transaction(trn, db_user) for trn in test_transactions  # type: ignore  # noqa: E501
        ]
        session.add_all(transactions)
        session.commit()
        try:
            yield storage, None
        except Exception:
            logger.debug('exception in tests with storage_with_user')
        finally:
            clean_storage(session, db.Report)
            clean_storage(session, db.Transaction)


@pytest.fixture
def storage_without_transactions(storage_with_user):
    """Создает объект DBStorage с добавленными транзакциями."""
    storage, _ = storage_with_user
    with Session(storage.pool) as session:
        try:
            yield storage, None
        except Exception:
            logger.debug('exception in tests with storage_with_user')
        finally:
            clean_storage(session, db.Report)
            clean_storage(session, db.Transaction)


def _create_db_transaction(
    transaction: srv.Transaction, user: db.User,
) -> db.Transaction:
    return db.Transaction(
        transaction_type=transaction.transaction_type.value,
        amount=transaction.amount,
        created_at=transaction.timestamp,
        is_deleted=False,
        user=user,
    )


def clean_storage(session: Session, orm_model):
    """Очищает транзакции после теста."""
    stmt = select(orm_model).where()
    for model_object in session.scalars(stmt):
        session.delete(model_object)
        session.flush()
    session.commit()


def count_storage(storage, orm_model) -> int:
    """Считает количество транзакций в базе."""
    with Session(storage.pool) as session:
        stmt = select(orm_model).where()
        transactions = session.scalars(stmt).all()
        return len(transactions)
