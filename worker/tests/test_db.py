from datetime import datetime

import pytest

from worker.db import list_service_statuses, save_service_status


@pytest.mark.asyncio
async def test_db_queries(db, mocked_now):
    services = await list_service_statuses()
    assert services == []

    await save_service_status("testURL", 200, 0.5)
    await save_service_status("testURL2", 404, 0.6)
    services = await list_service_statuses()
    assert services == [
        {
            "code": 200,
            "elapsed": 0.5,
            "date": datetime(2020, 7, 1, 10, 0, 0),
            "id": 1,
            "url": "testURL",
        },
        {
            "code": 404,
            "elapsed": 0.6,
            "date": datetime(2020, 7, 1, 10, 0, 0),
            "id": 2,
            "url": "testURL2",
        },
    ]
