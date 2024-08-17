import logging
from enum import StrEnum

import pytest

from app.core.errors import NotFoundError
from app.core.models import Transaction, TransactionReport, User
from app.external.postgres import models as db
from app.external.postgres.storage import DBStorage
from tests.unit.external.postgres.conftest import (
    count_storage,
    test_report_request,
    test_transactions,
    valid_user,
)

logger = logging.getLogger(__name__)


class Fixtures(StrEnum):
    """Часто используемые названия фикстур."""

    storage_with_user = 'storage_with_user'
    storage_without_user = 'storage_without_user'


class TestGetUser:
    """Тестирует метод get_user."""

    @pytest.mark.asyncio
    @pytest.mark.database
    @pytest.mark.parametrize(
        'storage_fixture, user, expected', (
            pytest.param(
                Fixtures.storage_with_user,
                valid_user,
                valid_user,
                id='valid user',
            ),
            pytest.param(
                Fixtures.storage_without_user,
                valid_user,
                None,
                id='invalid user',
            ),
        ),
    )
    async def test_get_user(
        self, storage_fixture, user: User, expected: User, request,
    ):
        """Тестирует что метод возвращает правильный объект."""
        storage, _ = request.getfixturevalue(storage_fixture)

        db_user: User | None = await storage.get_user(user.username)

        if db_user is None:
            assert db_user is expected
        else:
            assert db_user.username == expected.username
            assert db_user.balance == expected.balance
            assert db_user.is_verified == expected.is_verified


class TestUpdateUser:
    """Тестирует метод upgrage_user."""

    @pytest.mark.asyncio
    async def test_update_user(self, caplog, storage):
        """Проверяет что метод выполняется без ошибок."""
        caplog.set_level(logging.DEBUG)
        await storage.update_user(valid_user)
        assert 'DEPRICATED' in caplog.text


class TestCreateTransaction:
    """Тестирует метод create_transaction."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'transaction, expected, storage_fixture', (
            pytest.param(
                test_transactions[0],
                test_transactions[0],
                Fixtures.storage_with_user,
                id='transaction for valid user',
            ),
            pytest.param(
                test_transactions[0],
                test_transactions[0],
                Fixtures.storage_without_user,
                id='transaction for not valid user',
                marks=pytest.mark.xfail(raises=NotFoundError),
            ),
        ),
    )
    async def test_create_transaction_return_value(
        self, transaction: Transaction, expected, storage_fixture, request,
    ):
        """Проверяет что метод выполняется верно."""
        storage, _ = request.getfixturevalue(storage_fixture)

        db_transaction: Transaction = await storage.create_transaction(
            transaction,
        )

        assert db_transaction.username == transaction.username
        assert db_transaction.amount == transaction.amount
        assert db_transaction.timestamp == transaction.timestamp
        assert db_transaction.transaction_type == transaction.transaction_type

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'transactions, expected_qnt, storage_fixture', (
            pytest.param(
                test_transactions,
                2,
                Fixtures.storage_with_user,
                id='2 transactions',
            ),
            pytest.param(
                [test_transactions[0]],
                1,
                Fixtures.storage_with_user,
                id='1 transaction',
            ),
            pytest.param(
                [],
                0,
                Fixtures.storage_with_user,
                id='0 transaction',
            ),
        ),
    )
    async def test_create_transaction_storage_state(
        self,
        transactions: list[Transaction],
        expected_qnt,
        storage_fixture,
        request,
    ):
        """Проверяет состояние хранилища данных."""
        storage, _ = request.getfixturevalue(storage_fixture)

        for transaction in transactions:
            await storage.create_transaction(
                transaction,
            )

        assert count_storage(storage, db.Transaction) == expected_qnt


class TestCreateReport:
    """Тестирует метод create_transaciton_report."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'report_request, expected_qnt, storage_fixture', (
            pytest.param(
                test_report_request,
                2,
                'storage_with_transactions',
                id='valid user with transactions',
            ),
            pytest.param(
                test_report_request,
                0,
                'storage_without_transactions',
                id='valid user without transactions',
            ),
            pytest.param(
                test_report_request,
                0,
                Fixtures.storage_without_user,
                id='invalid user',
                marks=pytest.mark.xfail(raises=NotFoundError),
            ),
        ),
    )
    async def test_create_report_return_values(
        self, report_request, expected_qnt, storage_fixture, request,
    ):
        """Проверяет что метод создания отчета возвращает верные значения."""
        storage, _ = request.getfixturevalue(storage_fixture)

        report: TransactionReport = await storage.create_transaction_report(
            report_request,
        )

        assert report.username == report_request.username
        assert report.start_date == report_request.start_date
        assert report.end_date == report_request.end_date
        assert len(report.transactions) == expected_qnt

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'report_request, expected_qnt, storage_fixture', (
            pytest.param(
                test_report_request,
                1,
                'storage_with_transactions',
                id='valid user with transactions',
            ),
            pytest.param(
                test_report_request,
                1,
                'storage_without_transactions',
                id='valid user without transactions',
            ),
        ),
    )
    async def test_create_report_storage_state(
        self, report_request, expected_qnt, storage_fixture, request,
    ):
        """Проверяет состояие хранилища данных после выполнения метода."""
        storage, _ = request.getfixturevalue(storage_fixture)

        report: TransactionReport = await storage.create_transaction_report(
            report_request,
        )

        assert count_storage(storage, db.Report) == expected_qnt
        assert (
            count_storage(storage, db.Transaction) == len(report.transactions)
        )


def test_init():
    """Тестирует инициализацию DBStorage."""
    storage = DBStorage()
    assert storage
