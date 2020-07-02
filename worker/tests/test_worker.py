import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import InvalidURL

from worker.consumer import Consumer
from worker.db import list_service_statuses
from worker.producer import Producer
from worker.settings import Settings


@pytest.mark.asyncio
async def test_saving_url_status(db, mocked_now, httpx_client):
    queue = asyncio.Queue()
    settings = Settings(
        urls=["google.com", "ya.ru"],
        interval=1,
        timeout=1,
        log_level="DEBUG",
        workers=1,
    )
    consumer = Consumer(timeout=1, queue=queue, consumer_id="1")
    producer = Producer(settings, queue)

    httpx_client.get = AsyncMock(
        return_value=MagicMock(
            status_code=200, request=MagicMock(), elapsed=timedelta(seconds=0.5)
        )
    )

    producer_fut = asyncio.ensure_future(producer.run())
    consumer_fut = asyncio.ensure_future(consumer.run())

    await asyncio.sleep(0.1)
    producer.stop()
    consumer.stop()

    await producer_fut
    await consumer_fut

    statuses_in_db = await list_service_statuses()
    assert statuses_in_db == [
        {
            "code": 200,
            "elapsed": 0.5,
            "date": datetime(2020, 7, 1, 10, 0),
            "id": 1,
            "url": "google.com",
        },
        {
            "code": 200,
            "elapsed": 0.5,
            "date": datetime(2020, 7, 1, 10, 0),
            "id": 2,
            "url": "ya.ru",
        },
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "side_effect, expected_code, expected_elapsed",
    [(TimeoutError, 0, 1.0), (InvalidURL, 0, 0)],
)
async def test_fetching_errors(
    httpx_client, side_effect, expected_code, expected_elapsed
):
    httpx_client.get = AsyncMock(side_effect=[side_effect])
    consumer = Consumer(timeout=1.0, queue=asyncio.Queue(), consumer_id="1")
    code, elapsed = await consumer.check_url("http://dummy.url")
    assert code == expected_code
    assert elapsed == expected_elapsed
