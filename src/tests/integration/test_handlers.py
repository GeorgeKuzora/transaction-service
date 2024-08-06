from datetime import datetime, timedelta
from enum import StrEnum

import pytest
from fastapi import status

from app.core.models import TransactionRequest, User
from app.core.transactions import TransactionService


class Literals(StrEnum):
    """Часто используемые литералы."""

    george = 'george'
    username = 'username'
    amount = 'amount'
    transaction_type = 'transaction_type'
    peter = 'peter'
    start_date = 'start_date'
    end_date = 'end_date'


verified_user = User(
    user_id=1,
    username=Literals.george,
    balance=1,
    is_verified=True,
)
not_verified_user = User(
    user_id=1,
    username=Literals.george,
    balance=1,
    is_verified=False,
)
valid_transaction_request = {
    Literals.username: Literals.george,
    Literals.amount: 1,
    Literals.transaction_type: 1,
}
user_not_found_transaction_request = {
    Literals.username: Literals.peter,
    Literals.amount: 1,
    Literals.transaction_type: 1,
}
invalid_transaction_request = {
    'invalid': Literals.peter,
    Literals.amount: 1,
    Literals.transaction_type: 1,
}
big_widthdraw_transaction_request = {
    Literals.username: Literals.george,
    Literals.amount: 2,
    Literals.transaction_type: 1,
}
day_before_now = datetime.now() - timedelta(days=1)
day_after_now = datetime.now() + timedelta(days=1)
two_days_before_now = datetime.now() - timedelta(days=2)

all_transactions_report_request = {
    Literals.username: Literals.george,
    Literals.start_date: day_before_now.isoformat(),
    Literals.end_date: day_after_now.isoformat(),
}
none_transactions_report_request = {
    Literals.username: Literals.george,
    Literals.start_date: two_days_before_now.isoformat(),
    Literals.end_date: day_before_now.isoformat(),
}
invalid_key_transactions_report_request = {
    'user': Literals.george,
    Literals.start_date: day_before_now.isoformat(),
    Literals.end_date: day_after_now.isoformat(),
}
invalid_dates_transactions_report_request = {
    Literals.username: Literals.george,
    Literals.start_date: day_after_now.isoformat(),
    Literals.end_date: day_before_now.isoformat(),
}
invalid_user_transactions_report_request = {
    Literals.username: Literals.peter,
    Literals.start_date: day_before_now.isoformat(),
    Literals.end_date: day_after_now.isoformat(),
}


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
    ):
        """Тестирует хэндлер create_transaction."""
        service: TransactionService = await service_with_user_fixture(user)
        service_mocker(service)
        response = await client.post(
            self.url,
            json=transaction_request,
        )

        assert response.status_code == expected_status
        if response.status_code == status.HTTP_200_OK:
            assert len(service.repository.transactions) == 1  # type: ignore


class TestCreateReport:
    """Тестирует хэндлер /create_report."""

    url = '/create_report'

    @pytest.mark.asyncio
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        'report_request, expected_status, expected_qnt', (
            pytest.param(
                all_transactions_report_request,
                status.HTTP_200_OK,
                2,
                id='valid request, all transactions',
            ),
            pytest.param(
                none_transactions_report_request,
                status.HTTP_200_OK,
                0,
                id='valid request, none transactions',
            ),
            pytest.param(
                invalid_key_transactions_report_request,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                0,
                id='invalid request, invalid key',
            ),
            pytest.param(
                invalid_dates_transactions_report_request,
                status.HTTP_403_FORBIDDEN,
                0,
                id='invalid request, invalid dates',
            ),
        ),
    )
    async def test_create_report(
        self,
        report_request,
        expected_status,
        expected_qnt,
        client,
        service_with_transactions_fixture,
        service_mocker,
    ):
        """Тестирует create_report."""
        service: TransactionService = await service_with_transactions_fixture(
            verified_user,
            [
                TransactionRequest(**valid_transaction_request),
                TransactionRequest(**valid_transaction_request),
            ],
        )
        service_mocker(service)
        response = await client.post(
            self.url,
            json=report_request,
        )

        assert response.status_code == expected_status
        if response.status_code == status.HTTP_200_OK:
            assert len(response.json()['transactions']) == expected_qnt
