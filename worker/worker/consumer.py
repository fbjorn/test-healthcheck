import asyncio
from typing import Tuple, Union

import httpx
import structlog
from httpcore import TimeoutException

from worker.db import save_service_status


class Consumer:
    def __init__(
        self, timeout: float, queue: asyncio.Queue, consumer_id: Union[str, int]
    ):
        self.timeout = timeout
        self.queue = queue
        self._id = f"c{consumer_id}"
        self.log = structlog.get_logger().bind(id=self._id)
        self._stop_event = asyncio.Event()

    async def check_url(self, url: str) -> Tuple[int, float]:
        """
        Fetch URL. Returns status code and elapsed time.
        If request failed by timeout, then the code is 0.
        If request failed by another reason, then the code and elapsed time is 0.
        :param url: URL to check
        """
        code = 0
        elapsed = 0.0
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, timeout=self.timeout)
            except (TimeoutError, TimeoutException):
                self.log.debug("Timeout", timeout=self.timeout, url=url)
                return code, self.timeout
            except httpx.HTTPError:
                self.log.exception("Failed to fetch URL", url=url)
            else:
                code = resp.status_code
                elapsed = resp.elapsed.total_seconds()

            return code, elapsed

    async def process_url(self, url: str):
        """
        Fetch URL and save request information to the database
        :param url: URL to process
        """
        try:
            code, elapsed = await self.check_url(url)
            self.log.debug("Saved", url=url, code=code, elapsed=elapsed)
            await save_service_status(url, code, elapsed)
        except Exception:
            self.log.exception("Failed to process url", url=url)

    async def run(self):
        """
        Waits for an item in the queue, then start URL processing.
        Interrupts when stop even it set.
        """
        self.log.info("Consumer started")
        wait_stopped_fut = self._stop_event.wait()
        while True:
            done, pending = await asyncio.wait(
                [self.queue.get(), wait_stopped_fut],
                return_when=asyncio.FIRST_COMPLETED,
            )
            if not self._stop_event.is_set():
                url = done.pop().result()
                await self.process_url(url)
            else:
                for pending_task in pending:
                    pending_task.cancel()
                self.log.info("Consumer stopped")
                return

    def stop(self):
        self._stop_event.set()
