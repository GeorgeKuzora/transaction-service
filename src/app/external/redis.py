from app.core.models import TransactionReport, TransactionReportRequest


class TransactionReportCache:
    """Имплементация кэша для хранения отчетов."""

    def __init__(self) -> None:
        """Метод инициализации."""
        self.storage: dict[str, TransactionReport] = {}

    async def get_cache(
        self, cache_value: TransactionReportRequest,
    ) -> TransactionReport:
        """
        Получает значение из кэша.

        :param cache_value: Кэшированное значение
        :type cache_value: Token
        :return: Кэшированное значение
        :rtype: Token
        :raises KeyError: Значение не найдено в кэше
        """
        key = self._create_key(cache_value)
        token_value = self.storage.get(key)
        if token_value:
            return token_value
        raise KeyError(f'{cache_value} not found')

    async def create_cache(self, cache_value: TransactionReport) -> None:
        """
        Записывает значение в кэш.

        :param cache_value: Кэшируемое значение
        :type cache_value: Token
        """
        key = self._create_key(cache_value)
        self.storage[key] = cache_value

    def _create_key(
        self, cache_value: TransactionReport | TransactionReportRequest,
    ) -> str:
        date_format = '%d-%m-%Y'  # noqa: WPS323 date format
        return f'{cache_value.username}{cache_value.start_date.strftime(date_format)}{cache_value.end_date.strftime(date_format)}'  # noqa: E501, WPS237, WPS221 cant help
