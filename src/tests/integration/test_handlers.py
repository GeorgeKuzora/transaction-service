import pytest
from fastapi import status
from app.core.models import User

valid_transaction_request = {
    'username': 'george', 'amount': 1.0, 'transaction_type': 1,
}
user_not_found_transaction_request = {
    'username': 'peter', 'amount': 1.0, 'transaction_type': 1,
}
invalid_transaction_request = {
    'invalid': 'peter', 'amount': 1.0, 'transaction_type': 1,
}
big_widthdraw_transaction_request = {
    'username': 'george', 'amount': 2.0, 'transaction_type': 1,
}
verified_user = User(
    user_id=1,
    username='george',
    balance=1.0,
    is_verified=True,
)
not_verified_user = User(
    user_id=1,
    username='george',
    balance=1.0,
    is_verified=False,
)


class TestCreateTransaction:
    """Тестирует хэндлер /create_transaction."""

    url = '/create_transaction'

    @pytest.mark.asyncio
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        'transaction_request, user, expected_status', (
            pytest.param(
                valid_transaction_request,
                verified_user,
                status.HTTP_200_OK,
                id='verified user, valid respose',
            ),
            pytest.param(
                valid_transaction_request,
                not_verified_user,
                status.HTTP_200_OK,
                id='not verified user, valid respose',
            ),
            pytest.param(
                user_not_found_transaction_request,
                verified_user,
                status.HTTP_404_NOT_FOUND,
                id='user not found, invalid respose',
            ),
            pytest.param(
                invalid_transaction_request,
                verified_user,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                id='invalid request, invalid respose',
            ),
            pytest.param(
                big_widthdraw_transaction_request,
                not_verified_user,
                status.HTTP_403_FORBIDDEN,
                id='not verified user forbidden transaction',
            ),
            pytest.param(
                big_widthdraw_transaction_request,
                verified_user,
                status.HTTP_200_OK,
                id='verified user accepted transaction',
            ),
        ),
    )
    async def test_create_transaction(
        self,
        transaction_request,
        user,
        expected_status,
        client,
        service_with_user_fixture,
        service_mocker,
        request,
    ):
        """Тестирует хэндлер create_transaction."""
        service = await service_with_user_fixture(user)
        service_mocker(service)
        response = await client.post(
            self.url,
            json=transaction_request,
        )

        assert response.status_code == expected_status

