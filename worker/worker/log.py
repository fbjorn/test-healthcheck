import logging.config

import structlog

from worker.settings import load_settings_from_env

LOG_LEVEL = load_settings_from_env(silent=True).log_level

logging_pre_chain = [
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
]

processors = [
    structlog.threadlocal.merge_threadlocal_context,
    structlog.processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
    structlog.processors.format_exc_info,
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_log_level,
    structlog.processors.UnicodeDecoder(),
    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
]

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False),  # or JSON
                "foreign_pre_chain": logging_pre_chain,
                "keep_exc_info": True,
                "keep_stack_info": True,
            },
        },
        "handlers": {
            "console": {
                "level": LOG_LEVEL,
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
        },
        "loggers": {
            "": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": True},
            "httpx": {"level": "WARN"},
            "asyncpg": {"level": "WARN"},
        },
    }
)

structlog.configure(
    processors=processors,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=False,
)
logger = structlog.get_logger()
