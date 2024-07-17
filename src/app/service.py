import logging
from datetime import datetime, timedelta

from app.core.transactions import TransactionService, TransactionType
from app.external.in_memory_repository import InMemoryRepository


def main() -> None:
    """Точка входа в программу."""
    logger = logging.getLogger(__name__)
    repository = InMemoryRepository()
    service = TransactionService(repository)

    transaction = service.create_transaction(
        user_id=1,
        amount=10,
        transaction_type=TransactionType.sell,
    )

    transaction = service.create_transaction(
        user_id=2,
        amount=10,
        transaction_type=TransactionType.sell,
    )

    transaction = service.create_transaction(
        user_id=1,
        amount=4,
        transaction_type=TransactionType.buy,
    )

    report = service.create_transaction_report(
        user_id=1,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=1),
    )

    logger.info(f'created {transaction}')
    logger.info(f'created {report}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
