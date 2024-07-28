class RepositoryError(Exception):
    """
    Исключение возникающее при запросе в хранилище данных.

    Импортировать в имплементации репозитория данных,
    для вызова исключения при ошибке доступа к данным.
    """


class ValidationError(Exception):
    """Исключение при валидации данных."""


class NotFoundError(Exception):
    """Исключение если данные не найдены."""


class CacheError(Exception):
    """Ошибка в кэше."""
