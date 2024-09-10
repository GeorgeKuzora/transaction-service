import asyncio
import logging

from fastapi import APIRouter, HTTPException, status
from opentracing import global_tracer

from app.core.errors import ServerError, ValidationError
from app.core.models import (
    Transaction,
    TransactionReport,
    TransactionReportRequest,
    TransactionRequest,
)
from app.core.transactions import TransactionService
from app.external.postgres.storage import DBStorage
from app.external.redis import TransactionReportCache
from app.metrics.tracing import Tag

logger = logging.getLogger(__name__)

router = APIRouter()


def get_service() -> TransactionService:
    """
    Создает сервис.

    :return: Объект сервиса.
    :rtype: TransactionService
    """
    storage = DBStorage()
    cache = TransactionReportCache()
    return TransactionService(repository=storage, cache=cache)


service = get_service()


@router.post('/create_transaction', status_code=status.HTTP_200_OK)
async def create_transaction(
    transaction_request: TransactionRequest,
) -> Transaction:
    """
    Создает транзакцию.

    :param transaction_request: Данные для создания транзакции.
    :type transaction_request: TransactionRequest
    :return: Созданная транзакция.
    :rtype: Transaction
    :raises HTTPException: При ошибке в ходе выполнения.
    """
    with global_tracer().start_active_span('create_transaction') as scope:
        scope.span.set_tag(Tag.username, transaction_request.username)
        task = asyncio.create_task(
            service.create_transaction(transaction_request),
        )
        try:
            return await task
        except ValidationError as v_err:
            logger.info(f'транзакция {transaction_request} запрещена')
            scope.span.set_tag(Tag.warning, 'transaction validation failed')
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
            ) from v_err
        except ValueError as v_err:
            logger.info(f'транзакция {transaction_request} неверный формат')
            scope.span.set_tag(Tag.warning, 'transaction invalid format')
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
            ) from v_err
        except ServerError as err:
            logger.error('Неизвестная ошибка сервера')
            scope.span.set_tag(
                Tag.error, 'unexpected server error on create_transaction',
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ) from err


@router.post('/create_report', status_code=status.HTTP_200_OK)
async def create_report(
    report_request: TransactionReportRequest,
) -> TransactionReport:
    """
    Создает отчет.

    :param report_request: Данные для создания отчета.
    :type report_request: TransactionReportRequest
    :return: Отчет о транзакциях.
    :rtype: TransactionReport
    :raises HTTPException: При ошибке в ходе выполнения операции.
    """
    with global_tracer().start_active_span('create_report') as scope:
        scope.span.set_tag(Tag.username, report_request.username)
        task = asyncio.create_task(
            service.create_transaction_report(report_request),
        )
        try:
            return await task
        except ServerError as r_err:
            logger.error('Ошибка сервера')
            scope.span.set_tag(
                Tag.error, 'unexpected server error on create_report',
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ) from r_err
        except ValueError as r_err:
            logger.error(f'Переданное значение неверно {report_request}')
            scope.span.set_tag(Tag.warning, 'report request has invalid format')
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            ) from r_err
