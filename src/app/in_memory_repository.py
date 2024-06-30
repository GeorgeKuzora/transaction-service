import logging

from app.service import Transaction, TransactionReport

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
