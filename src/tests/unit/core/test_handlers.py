import pytest
from fastapi import status
from httpx import AsyncClient

from app.api.handlers import app


class TestCreateTransaction:
    """Тестирует хэндлер create_transaction."""

    @pytest.mark.asyncio
    @pytest.mark.anyio
    async def test_create_transaction(self):
        """Тестирует хэндлер create_transaction."""
        transaction_request_body = {
            'username': 'george',
            'amount': 1,
            'transaciton_type': 1,
        }
        async with AsyncClient(app=app, base_url='http://test') as ac:
            response = await ac.post(
                '/create_transaction', json=transaction_request_body,
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
