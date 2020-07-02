import asyncio

import structlog

from worker.settings import Settings

logger = structlog.get_logger()


class Producer:
    def __init__(self, s: Settings, queue: asyncio.Queue):
        self.urls = s.urls
        self.interval = s.interval
        self.timeout = s.timeout
        self.queue = queue
        self._stop_event = asyncio.Event()

    async def _run(self):
        logger.debug("Queue size", size=self.queue.qsize())
        logger.info("Pushing to the queue", urls=len(self.urls))
        for url in self.urls:
            self.queue.put_nowait(url)
        logger.debug("Sleeping", sec=self.interval)

    async def run(self):
        """
        Start pushing URLs from config to the queue until stop event is set.
        """
        logger.info("Producer started")
        while True:
            await self._run()
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.interval)
                break
            except asyncio.exceptions.TimeoutError:
                pass
        logger.info("Producer stopped")

    def stop(self):
        self._stop_event.set()
