import asyncio

from worker import log  # noqa
from worker.consumer import Consumer
from worker.producer import Producer
from worker.settings import Settings, load_settings_from_env

queue: asyncio.Queue = asyncio.Queue()


async def _run_worker(s: Settings):
    producer = Producer(s, queue)
    consumers = [Consumer(s.timeout, queue, i) for i in range(s.workers)]
    consumer_futures = [asyncio.ensure_future(cons.run()) for cons in consumers]
    producer_future = asyncio.ensure_future(producer.run())
    await producer_future
    await asyncio.wait(consumer_futures)


def run_worker():
    s = load_settings_from_env()
    asyncio.get_event_loop().run_until_complete(_run_worker(s))


if __name__ == "__main__":
    run_worker()
