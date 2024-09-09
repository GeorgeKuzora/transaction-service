import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Self

import yaml
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings

from app.core.errors import ConfigError

logger = logging.getLogger(__name__)


class PostgresSettings(BaseSettings):
    """Конфигурация postgres."""

    pg_dns: PostgresDsn = Field(
        'postgresql+psycopg2://myuser:mysecretpassword@db:5432/mydatabase',
        validate_default=False,
    )
    pool_size: int = 10
    max_overflow: int = 20


class TracingSettings(BaseSettings):
    """Конфигурация трейсинга."""

    enabled: bool = False
    sampler_type: str = 'const'
    sampler_param: int = 1
    agent_host: str = 'jaeger'
    agent_port: int = 6831
    service_name: str = 'transaction-service'
    logging: bool = True
    validation: bool = True


class RedisSettings(BaseSettings):
    """Конфигурация redis."""

    host: str
    port: int = 6379
    decode_responses: bool = True
    db: int = 0


class Settings(BaseSettings):
    """Конфигурация приложения."""

    postgres: PostgresSettings
    tracing: TracingSettings
    redis: RedisSettings

    @classmethod
    def from_yaml(cls, config_path: str) -> Self:
        """
        Создает объект класса из файла yaml.

        :param config_path: Путь к файлу конфигурации.
        :type config_path: str
        :return: Объект с конфигурацией приложения.
        :rtype: Settings
        :raises ConfigError: При ошибке в ходе выполнения операции.
        """
        if not cls._is_valid_path(config_path):
            logger.critical(
                f'config file is missing on path {config_path}',
            )
            raise ConfigError(
                detail=f'config file is missing on path {config_path}',
            )
        settings = yaml.safe_load(Path(config_path).read_text())
        return cls(**settings)

    @classmethod
    def _is_valid_path(cls, path: str) -> bool:
        passlib_path = Path(path)
        return passlib_path.is_file()


@lru_cache
def get_settings() -> Settings:
    """
    Создает конфигурацию сервиса.

    :return: Объект с конфигурацией приложения.
    :rtype: Settings
    :raises ConfigError: При ошибке в ходе выполнения операции.
    """
    config_path_env_var = 'CONFIG_PATH'
    config_file = os.getenv(config_path_env_var)
    if config_file is None:
        logger.critical(f'env variable {config_path_env_var} not found')
        raise ConfigError(
            detail=f'env variable {config_path_env_var} not found',
        )
    return Settings.from_yaml(config_file)
