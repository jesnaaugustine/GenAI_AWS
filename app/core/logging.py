import logging
import logging.config

from app.core.request_context import request_id_context


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord, ) -> bool:
        record.request_id = request_id_context.get()
        return True


def configure_logging(log_level: str = "INFO") -> None:

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,

        "filters": {
            "request_id": {
                "()": RequestIDFilter,
            },
        },

        "formatters": {
            "standard": {
                "format": (
                    "%(asctime)s | "
                    "%(levelname)s | "
                    "request_id=%(request_id)s | "
                    "%(name)s | "
                    "%(message)s"
                ),
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "filters": ["request_id"],
                "stream": "ext://sys.stdout",
            },
        },

        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }

    logging.config.dictConfig(logging_config)