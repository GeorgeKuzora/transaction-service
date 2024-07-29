import asyncio
import logging

from fastapi import APIRouter, HTTPException, status

from app.core.errors import RepositoryError, ValidationError
from app.core.models import (
    Transaction,
    TransactionReport,
    TransactionReportRequest,
    TransactionRequest,
)
from app.core.transactions import TransactionService
from app.external.in_memory_repository import InMemoryRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/create_transaction', status_code=status.HTTP_200_OK)
async def create_transaction(
    transaction_request: TransactionRequest,
) -> Transaction:
    """Созадет транзакцию."""
    storage = InMemoryRepository()
    service = TransactionService(storage)
    task = asyncio.create_task(service.create_transaction(transaction_request))
    try:
        return await task
    except ValidationError as v_err:
        logger.info(f'транзакция {transaction_request} запрещена')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from v_err
    except RepositoryError as r_err:
        logger.error('Ошибка хранилища данных')
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from r_err
    except Exception as err:
        logger.error('Неизвестная ошибка сервера')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from err


@router.post('/create_report', status_code=status.HTTP_200_OK)
async def create_report(
    report_request: TransactionReportRequest,
) -> TransactionReport:
    """Создает отчет."""
    storage = InMemoryRepository()
    service = TransactionService(storage)
    task = asyncio.create_task(
        service.create_transaction_report(report_request),
    )
    try:
        return await task
    except RepositoryError as r_err:
        logger.error('Ошибка хранилища данных')
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from r_err
    except Exception as err:
        logger.error('Неизвестная ошибка сервера')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from err
