from fastapi import HTTPException, status


class ServerError(HTTPException):
    """Ошибка при проблемах с сервисом."""

    def __init__(
        self,
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        detail: str = 'Неизвестная ошибка сервера',
    ):
        """
        Метод инициализации ServerError.

        :param status_code: Код ответа
        :type status_code: int
        :param detail: Сообщение
        :type detail: str
        """
        self.status_code = status_code
        self.detail = detail


class RepositoryError(ServerError):
    """
    Исключение возникающее при запросе в хранилище данных.

    Импортировать в имплементации репозитория данных,
    для вызова исключения при ошибке доступа к данным.
    """


class CacheError(ServerError):
    """Ошибка в кэше."""


class ValidationError(HTTPException):
    """Исключение при валидации данных."""

    def __init__(
        self,
        status_code: int = status.HTTP_403_FORBIDDEN,
        detail: str = 'Запрос имеет неверный формат',
    ):
        """
        Метод инициализации UnprocessableError.

        :param status_code: Код ответа
        :type status_code: int
        :param detail: Сообщение
        :type detail: str
        """
        self.status_code = status_code
        self.detail = detail


class NotFoundError(HTTPException):
    """Исключение возникающее когда запрошенная информация не найдена."""

    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        detail: str = 'Запрошенные данные не найдены',
    ):
        """
        Метод инициализации NotFoundError.

        :param status_code: Код ответа
        :type status_code: int
        :param detail: Сообщение
        :type detail: str
        """
        self.status_code = status_code
        self.detail = detail

