import os
from dataclasses import dataclass
from typing import Any, List, Type

MIN_INTERVAL = 2  # sec
MAX_WORKERS = 100


def get_from_env(key: str, convert_to: Type = str, log=True):

    value: Any = os.environ.get(key)
    if value is None:
        raise ValueError(f"Param {key} is missing in the environment")
    if convert_to == bool:
        value = bool(int(value))  # '1' -> True, '0' -> False, for simplicity
    elif convert_to == list:
        value = value.split(",")
    else:
        value = convert_to(value)
    if log:
        from worker.log import logger

        logger.info("Load from env", key=key, value=value)
    return value


@dataclass
class Settings:
    interval: float
    log_level: str
    timeout: float
    urls: List[str]
    workers: int


def load_settings_from_env(silent: bool = False) -> Settings:
    log = not silent
    interval = get_from_env("INTERVAL", convert_to=float, log=log)
    timeout = get_from_env("TIMEOUT", convert_to=float, log=log)
    workers = get_from_env("WORKERS", convert_to=int, log=log)
    urls = get_from_env("URLS", convert_to=list, log=log)

    if timeout > interval:
        raise ValueError("Timeout must not be bigger than polling interval")

    if interval < MIN_INTERVAL:
        raise ValueError(f"Interval is too small. Min value is {MIN_INTERVAL} sec")

    if workers > MAX_WORKERS:
        raise ValueError(f"Workers count can not exceed {MAX_WORKERS}")

    # minimum workers needed to process all URLs in worst case
    min_workers = int(len(urls) * timeout)
    if workers * timeout < min_workers:
        raise ValueError(
            f"{workers} workers is not enough for processing {len(urls)} urls. "
            f"Minimum {min_workers} is required, or tweak the timeout"
        )

    return Settings(
        interval=interval,
        log_level=get_from_env("LOG_LEVEL", log=log),
        timeout=timeout,
        urls=urls,
        workers=workers,
    )
