import logging
from datetime import datetime

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

    def create_transaction(self, transaction: Transaction) -> Transaction:
        """
        Создает запись о транзакции и возвращает ее.

        Создает индексированную запись о транзакции и записывает ее в
        список транзакций. Возвращает созданную индексированную запись
        о транзакции.

        Args:
            transaction: Неиндексированный объект Transaction.

        Returns:
            Transaction: Индексированная запись о транзакции.
        """
        indexed_transaction = Transaction(
            user_id=transaction.user_id,
            amount=transaction.amount,
            transacton_type=transaction.transacton_type,
            timestamp=transaction.timestamp,
            transaction_id=self.transactions_count,
        )

        self.transactions_count += 1
        self.transactions.append(indexed_transaction)
        logger.info(f'Добавил транзакцию {transaction} в хранилище')

        return indexed_transaction
