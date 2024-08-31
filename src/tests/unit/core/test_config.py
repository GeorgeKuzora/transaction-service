import os
from enum import StrEnum

import pytest
from pydantic import ValidationError

from app.core.config import PostgresSettings, Settings, get_settings
from app.core.errors import ConfigError


class Key(StrEnum):
    """Часто используемые строки."""

    host = 'host'
    port = 'port'
    file_encoding = 'file_encoding'
    file_compression_quality = 'file_compression_quality'
    storage_path = 'storage_path'
    topics = 'topics'
    kafka = 'kafka'
    postgres = 'postgres'
    pg_dns = 'pg_dns'
    pool_size = 'pool_size'
    max_overflow = 'max_overflow'
    tracing = 'tracing'


postgres_valid_input = {
    Key.pg_dns: 'postgresql+psycopg2://myuser:mysecretpassword@db:5432/mydatabase',  # noqa: E501
    Key.pool_size: 10,
    Key.max_overflow: 20,
}
postgres_invalid_input = {
    Key.pg_dns: 'invalid_dns',  # noqa: E501
    Key.pool_size: 10,
    Key.max_overflow: 20,
}
tracing_input = {
    'enabled': True,
    'sampler_type': 'const',
    'sampler_param': 1,
    'agent_host': 'jaeger',
    'agent_port': 6831,
    'service_name': 'auth-service',
    'logging': True,
    'validation': True,
}

valid_input = {
    Key.postgres: postgres_valid_input,
    Key.tracing: tracing_input,
}
invalid_input_postgres = {
    Key.postgres: postgres_invalid_input,
    Key.tracing: tracing_input,
}
valid_config_path = 'src/config/config-local.yml'
invalid_config_path = 'src/config/invalid_path.yml'


class TestPostgresSettings:
    """Тестирует класс PostgresSettings."""

    @pytest.mark.parametrize(
        'input_values', (
            pytest.param(
                postgres_valid_input,
                id='valid input parameters',
            ),
            pytest.param(
                postgres_invalid_input,
                id='invalid input parameters',
                marks=pytest.mark.xfail(raises=ValidationError),
            ),
        ),
    )
    def test_init(self, input_values: dict):
        """Тестирует инициализацию класса."""
        settings = PostgresSettings(**input_values)
        expected_pg_dns = input_values[Key.pg_dns]

        assert str(settings.pg_dns) == str(expected_pg_dns)


class TestSettings:
    """Тестирует класс Settings."""

    @pytest.mark.parametrize(
        'input_values', (
            pytest.param(
                valid_input,
                id='valid input parameters',
            ),
            pytest.param(
                invalid_input_postgres,
                id='invalid input parameters for postgres',
                marks=pytest.mark.xfail(raises=ValidationError),
            ),
        ),
    )
    def test_init(self, input_values: dict):
        """Тестирует инициализацию класса."""
        settings = Settings(**input_values)

        assert (
            str(settings.postgres.pg_dns) ==
            str(input_values[Key.postgres][Key.pg_dns])  # type: ignore
        )

    @pytest.mark.parametrize(
        'config_path', (
            pytest.param(
                valid_config_path,
                id='valid config path',
            ),
            pytest.param(
                invalid_config_path,
                id='invalid config path',
                marks=pytest.mark.xfail(raises=ConfigError),
            ),
        ),
    )
    def test_from_yml(self, config_path):
        """Тестирует метод from_yaml."""
        settings = Settings.from_yaml(config_path)

        assert (
            str(settings.postgres.pg_dns) ==
            str(valid_input[Key.postgres][Key.pg_dns])  # type: ignore
        )


@pytest.fixture
def valid_config_path_env():
    """Устанавливает валидный путь в переменной окружения."""
    os.environ['CONFIG_PATH'] = valid_config_path
    return valid_config_path


@pytest.mark.parametrize(
    'config_file_path', (
        pytest.param(
            'valid_config_path_env',
            id='valid config file path',
        ),
    ),
)
def test_get_settings(config_file_path, request):
    """Тестирует функцию get_settings."""
    request.getfixturevalue(config_file_path)

    settings = get_settings()

    assert (
        str(settings.postgres.pg_dns) ==
        str(valid_input[Key.postgres][Key.pg_dns])  # type: ignore
    )
