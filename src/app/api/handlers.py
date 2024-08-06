import asyncio
import logging

from fastapi import APIRouter, HTTPException, status

from app.core.errors import RepositoryError, ValidationError, ServerError
from app.core.models import (
    Transaction,
    TransactionReport,
    TransactionReportRequest,
    TransactionRequest,
)
from app.core.transactions import TransactionService
from app.external.in_memory_repository import InMemoryRepository
from app.external.redis import TransactionReportCache

logger = logging.getLogger(__name__)

router = APIRouter()


def get_service() -> TransactionService:
    """Инициализирует сервис."""
    storage = InMemoryRepository()
    cache = TransactionReportCache()
    return TransactionService(repository=storage, cache=cache)


service = get_service()


@router.post('/create_transaction', status_code=status.HTTP_200_OK)
async def create_transaction(
    transaction_request: TransactionRequest,
) -> Transaction:
    """Созадет транзакцию."""
    task = asyncio.create_task(service.create_transaction(transaction_request))
    try:
        return await task
    except ValidationError as v_err:
        logger.info(f'транзакция {transaction_request} запрещена')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        ) from v_err
    except ValueError as v_err:
        logger.info(f'транзакция {transaction_request} неверный формат')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        ) from v_err
    except ServerError as err:
        logger.error('Неизвестная ошибка сервера')
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from err


@router.post('/create_report', status_code=status.HTTP_200_OK)
async def create_report(
    report_request: TransactionReportRequest,
) -> TransactionReport:
    """Создает отчет."""
    task = asyncio.create_task(
        service.create_transaction_report(report_request),
    )
    try:
        return await task
    except ServerError as r_err:
        logger.error('Ошибка сервера')
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from r_err
    except ValueError as r_err:
        logger.error(f'Переданное значение неверно {report_request}')
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ) from r_err
