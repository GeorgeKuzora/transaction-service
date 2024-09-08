from enum import StrEnum
from typing import Any

import pytest

from app.core.models import TransactionReport
from app.external.redis import (
    ReportCacheMixin,
    TransactionReportCache,
    TransactionsListCacheMixin,
)
from tests.unit.external.redis import test_data


class Key(StrEnum):
    """Часто встречающиеся ключи."""

    username = 'username'
    transactions = 'transactions'


class TestWithEmptyCache:
    """Тестирует пустой redis."""

    @pytest.mark.asyncio
    async def test_create_cache(self, redis: TransactionReportCache):
        """Тестирует метод create_cache."""
        await redis.create_cache(test_data.report)

        stored_data = self._get_stored_data(test_data.report)

        assert (
            stored_data[Key.username] ==
            test_data.report.username
        )
        assert (
            len(stored_data[Key.transactions]) ==
            len(test_data.report.transactions)
        )

    @pytest.mark.asyncio
    async def test_get_cache_raises(self, redis: TransactionReportCache):
        """Тестирует метод get_cache."""
        with pytest.raises(KeyError):
            await redis.get_cache(test_data.report_request)

    def _get_stored_data(
        self, external_data: TransactionReport,
    ) -> dict[str, Any]:
        report_storage = ReportCacheMixin()
        transaction_list_storage = TransactionsListCacheMixin()
        key = report_storage._get_key(external_data)
        report: dict = report_storage.storage.hgetall(key)
        transactions = transaction_list_storage._get_transactions_list_cache(
            transaction_list_storage._get_transactions_key(external_data),
        )
        report[Key.transactions] = transactions
        return report


class TestWithNotEmptyCache:
    """Тестирует redis с загруженным отчетом."""

    @pytest.mark.asyncio
    async def test_get_cache(self, redis_with_report: TransactionReportCache):
        """Тестирует метод create_cache."""
        stored_report = await redis_with_report.get_cache(
            test_data.report_request,
        )

        assert (
            stored_report.username ==
            test_data.report.username
        )
        assert (
            len(stored_report.transactions) ==
            len(test_data.report.transactions)
        )

    def _get_stored_data(
        self, external_data: TransactionReport,
    ) -> dict[str, Any]:
        report_storage = ReportCacheMixin()
        transaction_list_storage = TransactionsListCacheMixin()
        key = report_storage._get_key(external_data)
        report: dict = report_storage.storage.hgetall(key)
        transactions = transaction_list_storage._get_transactions_list_cache(
            transaction_list_storage._get_transactions_key(external_data),
        )
        report[Key.transactions] = transactions
        return report
