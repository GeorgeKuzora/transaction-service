from typing import Any, Protocol

from app.core.models import (
    Transaction,
    TransactionReport,
    TransactionReportRequest,
    User,
)


class Repository(Protocol):
    """
    Интерфейс для работы с хранилищами данных.

    Repository - это слой абстракции для работы с хранилищами данных.
    Служит для уменьшения связности компонентов сервиса.
    """

    async def create_transaction(self, transaction: Transaction) -> Transaction:
        """Абстрактный метод создания транзакции."""
        ...  # noqa: WPS428 valid protocol syntax

    async def create_transaction_report(
        self,
        request: TransactionReportRequest,
    ) -> TransactionReport:
        """Абстрактный метод создания отчета."""
        ...  # noqa: WPS428 valid protocol syntax

    async def get_user(self, username: str) -> User | None:
        """
        Получает пользователя из базы данных.

        Получает и возвращает запись о пользователе из базы данных.

        :param username: Имя пользователя
        :type username: str
        """
        ...  # noqa: WPS428 valid protocol syntax

    async def create_user(self, user: User) -> User:
        """
        Создает пользователя в базе данных.

        Создает, сохраняет в базе данных
        и возвращает индексированную запись о пользователе.

        :param user: неидексированная запись о пользователе.
        :type user: User
        """
        ...  # noqa: WPS428 valid protocol syntax

    async def update_user(
        self, user: User,
    ) -> User | None:
        """
        Создает пользователя в базе данных.

        Создает, сохраняет в базе данных
        и возвращает индексированную запись о пользователе.

        :param user: Пользователь
        :type user: User
        """


class Cache(Protocol):
    """Интерфейс кэша сервиса."""

    async def get_cache(self, cached_value: Any) -> TransactionReport | None:
        """
        Получает значение из кэша.

        :param cached_value: Кэшированное значение
        :type cached_value: Any
        """
        ...  # noqa: WPS428 valid protocol syntax

    async def create_cache(self, cached_value: Any) -> None:
        """
        Записывает значение в кэш.

        :param cached_value: Кэшируемое значение
        :type cached_value: Any
        """
        ...  # noqa: WPS428 valid protocol syntax
