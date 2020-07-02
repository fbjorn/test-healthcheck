import dataclasses
import logging
import os
from typing import Any, List, Type


def get_from_env(key: str, convert_to: Type = str, log=False):
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
        logging.info("Load from env", key=key, value=value)
    return value


@dataclasses.dataclass
class Settings:
    debug: bool
    reload: bool
    databases: List[str]


def load_settings_from_env() -> Settings:
    return Settings(
        debug=get_from_env("DEBUG", convert_to=bool, log=True),
        reload=get_from_env("RELOAD", convert_to=bool, log=True),
        databases=get_from_env("DATABASES", convert_to=list, log=True),
    )
