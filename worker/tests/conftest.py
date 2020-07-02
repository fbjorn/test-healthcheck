from datetime import datetime
from unittest.mock import MagicMock

import pytest

from worker.db import connection

test_connection_string = "postgresql://root:root@db/healthcheck_test"


@pytest.fixture()
async def db(monkeypatch):
    monkeypatch.setattr("worker.db.CONNECTION_STRING", test_connection_string)
    async with connection(test_connection_string) as conn:
        await conn.execute("TRUNCATE TABLE service_status")
        await conn.execute("ALTER SEQUENCE service_status_id_seq RESTART WITH 1")


@pytest.fixture()
def mocked_now(monkeypatch):
    now = datetime(2020, 7, 1, 10, 0, 0)
    monkeypatch.setattr("worker.db.now", MagicMock(return_value=now))


@pytest.fixture()
def httpx_client(monkeypatch):
    mocked_cm = MagicMock()
    mocked_async_client = MagicMock()
    mocked_async_client.return_value.__aenter__.return_value = mocked_cm
    monkeypatch.setattr("worker.consumer.httpx.AsyncClient", mocked_async_client)
    return mocked_cm
