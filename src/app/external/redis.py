import logging
from datetime import datetime
from enum import StrEnum
from typing import Any

import redis

from app.core.config import get_settings
from app.core.errors import ServerError
from app.core.models import (
    Transaction,
    TransactionReport,
    TransactionReportRequest,
    TransactionType,
)

logger = logging.getLogger(__name__)


class Key(StrEnum):
    """Часто используемые ключи словарей."""

    username = 'username'


class ReportCacheMixin:
    """Миксин для кэширования отчетов."""

    def __init__(self) -> None:
        """Метод инициализации класса ReportCacheMixin."""
        settings = get_settings()
        self.storage = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            decode_responses=settings.redis.decode_responses,
            db=settings.redis.db,
        )

    def create_report_cache(
        self,
        report_request: TransactionReportRequest | TransactionReport,
        transactions_key: str,
    ) -> None:
        """Создает кэш отчета."""
        key = self._get_key(report_request)
        mapping = self._get_mapping(report_request, transactions_key)
        try:
            self.storage.hset(key, mapping=mapping)
        except Exception as exc:
            logger.error(
                'unexpected cache error on create report cache', exc_info=exc,
            )
            raise ServerError() from exc

    def get_report_cache(
        self, report_request: TransactionReportRequest,
    ) -> dict[str, Any]:
        """Получает кэш отчета."""
        key = self._get_key(report_request)
        try:
            value_from_cache: dict[str, Any] = self.storage.hgetall(key)  # type:ignore # noqa: E501
        except Exception as exc:
            logger.error('error during cache access', exc_info=exc)
            raise ServerError() from exc
        if value_from_cache:
            logger.debug(f'got value from cache {value_from_cache}')
            return value_from_cache
        logger.debug(f'report not found: {report_request}')
        raise KeyError(f'{report_request} not found')

    def _get_key(
        self, cache_value: TransactionReport | TransactionReportRequest,
    ) -> str:
        date_format = '%d-%m-%Y'  # noqa: WPS323 date format
        return f'report:{cache_value.username}{cache_value.start_date.strftime(date_format)}{cache_value.end_date.strftime(date_format)}'  # noqa: E501, WPS237, WPS221 cant help

    def _get_mapping(
        self,
        report_request: TransactionReportRequest | TransactionReport,
        transactions_key: str,
    ) -> dict[str, Any]:
        return {
            Key.username: report_request.username,
            'start_date': report_request.start_date.isoformat(),
            'end_date': report_request.end_date.isoformat(),
            'transactions': transactions_key,
        }


class TransactionCacheMixin:
    """Миксин для кэширования транзакций."""

    def __init__(self) -> None:
        """Метод инициализации класса TransactionCacheMixin."""
        settings = get_settings()
        self.storage = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            decode_responses=settings.redis.decode_responses,
            db=settings.redis.db,
        )

    def create_transactions_cache(
        self, transactions: list[Transaction],
    ) -> list[str]:
        """Создает кэш транзакций."""
        transactions_keys = []
        for transaction in transactions:
            key = self._get_transaction_key(transaction)
            try:
                self.storage.hset(
                    key, mapping=self._get_transaction_mapping(transaction),
                )
            except Exception as exc:
                logger.error(
                    'cache error during create transaction', exc_info=exc,
                )
                raise ServerError() from exc
            transactions_keys.append(key)
        return transactions_keys

    def get_transactions_from_cache(
        self, keys: list[str],
    ) -> list[Transaction]:
        """Получает транзакции из кэша."""
        transactions = []
        for key in keys:
            try:
                transaction = self.storage.hgetall(key)
            except Exception as exc:
                logger.error(
                    'cache error during get transaction', exc_info=exc,
                )
                raise ServerError() from exc
            if transaction:
                transactions.append(self._get_transaction(transaction))  # type:ignore # noqa:E501
        return transactions

    def _get_transaction(self, mapping: dict[str, Any]) -> Transaction:
        transaction_type = TransactionType.from_int(
            mapping['transaction_type'],
        )
        timestamp = datetime.fromisoformat(mapping['timestamp'])
        return Transaction(
            username=mapping[Key.username],
            amount=mapping['amount'],
            transaction_type=transaction_type,
            timestamp=timestamp,
        )

    def _get_transaction_key(self, cache_value: Transaction) -> str:
        date_format = '%d-%m-%Y-%H-%M-%S'  # noqa: WPS323 date format
        return f'transaction:{cache_value.username}{cache_value.timestamp.strftime(date_format)}'  # noqa: E501, WPS237, WPS221 cant help

    def _get_transaction_mapping(
        self,
        transaction: Transaction,
    ) -> dict[str, Any]:
        return {
            Key.username: transaction.username,
            'amount': transaction.amount,
            'transaction_type': transaction.transaction_type.to_int(),
            'timestamp': transaction.timestamp.isoformat(),
        }


class TransactionsListCacheMixin:
    """Миксин для кэширования транзакций."""

    def __init__(self) -> None:
        """Метод инициализации класса TransactionsListCacheMixin."""
        settings = get_settings()
        self.storage = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            decode_responses=settings.redis.decode_responses,
            db=settings.redis.db,
        )

    def _get_transactions_key(
        self, cache_value: TransactionReport | TransactionReportRequest,
    ) -> str:
        date_format = '%d-%m-%Y'  # noqa: WPS323 date format
        return f'transactions:{cache_value.username}{cache_value.start_date.strftime(date_format)}{cache_value.end_date.strftime(date_format)}'  # noqa: E501, WPS237, WPS221 cant help

    def _create_transactions_list_cache(
        self, key: str, transactions_list: list[str],
    ) -> None:
        if transactions_list:
            try:
                self.storage.rpush(key, *transactions_list)
            except Exception as exc:
                logger.error(
                    'cache error during create transactions list', exc_info=exc,
                )
                raise ServerError() from exc

    def _get_transactions_list_cache(self, key: str) -> list[str]:
        try:
            return self.storage.lrange(key, 0, -1)  # type:ignore # noqa:E501
        except Exception as exc:
            logger.error(
                'cache error during get transactions list', exc_info=exc,
            )
            raise ServerError() from exc


class TransactionReportCache(
    ReportCacheMixin, TransactionCacheMixin, TransactionsListCacheMixin,
):
    """Имплементация кэша для хранения отчетов."""

    def __init__(self) -> None:
        """Метод инициализации класса TransactionReportCache."""
        settings = get_settings()
        self.storage = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            decode_responses=settings.redis.decode_responses,
        )

    async def get_cache(
        self, cache_value: TransactionReportRequest,
    ) -> TransactionReport:
        """
        Получает значение из кэша.

        :param cache_value: Кэшированное значение
        :type cache_value: Token
        :return: Кэшированное значение
        """
        report = self.get_report_cache(cache_value)
        key = report.get('transactions', '')
        transaction_keys = self._get_transactions_list_cache(key)
        if not transaction_keys:
            transaction_keys = []
        transactions = self.get_transactions_from_cache(transaction_keys)
        return self._get_report(report, transactions)

    async def create_cache(self, cache_value: TransactionReport) -> None:
        """
        Записывает значение в кэш.

        :param cache_value: Кэшируемое значение
        :type cache_value: Token
        """
        transactions_key = self._get_transactions_key(cache_value)
        transactions = self.create_transactions_cache(cache_value.transactions)
        self._create_transactions_list_cache(transactions_key, transactions)
        self.create_report_cache(cache_value, transactions_key)

    async def flush_cache(self) -> None:
        """Удаляет все ключи."""
        self.storage.flushall()

    def _get_report(
        self, report_map: dict[str, Any], transactions: list[Transaction],
    ) -> TransactionReport:
        return TransactionReport(
            username=report_map[Key.username],
            start_date=datetime.fromisoformat(report_map['start_date']),
            end_date=datetime.fromisoformat(report_map['end_date']),
            transactions=transactions,
            report_id=None,
        )
