from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

import asyncpg

CONNECTION_STRING = "postgresql://root:root@db/healthcheck"


def now():
    return datetime.utcnow()  # for easier mocking in tests


@asynccontextmanager
async def connection(connection_string: str):
    conn = await asyncpg.connect(connection_string)
    yield conn
    await conn.close()


async def save_service_status(url: str, code: int, elapsed: float):
    query = (
        "INSERT INTO service_status(url, code, elapsed, date) VALUES($1, $2, $3, $4)"
    )
    async with connection(CONNECTION_STRING) as conn:
        await conn.execute(query, url, code, elapsed, now())


async def list_service_statuses() -> List[dict]:
    query = "SELECT * FROM service_status"
    async with connection(CONNECTION_STRING) as conn:
        records = await conn.fetch(query)
        return [dict(rec) for rec in records]
