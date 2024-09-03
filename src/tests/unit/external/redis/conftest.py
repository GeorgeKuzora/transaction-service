import logging

import pytest_asyncio

from app.external.redis import TransactionReportCache
from tests.unit.external.redis import test_data

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def redis():
    """Создает экземпляр объекта взаимодействия с redis."""
    try:
        redis = TransactionReportCache()
    except Exception as exc:
        logger.error("can't access Redis")
        raise exc
    await redis.flush_cache()
    try:
        yield redis
    except Exception:
        logger.debug('error during tests, cleaning')
    finally:
        await redis.flush_cache()


@pytest_asyncio.fixture
async def redis_with_report(
    redis: TransactionReportCache,
) -> TransactionReportCache:
    """Создает кэш с загруженным отчетом."""
    await redis.create_cache(test_data.report)
    return redis
