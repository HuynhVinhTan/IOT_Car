import logging.config
import os

from app.core.config import settings

os.makedirs("logs", exist_ok=True)


class ExactLevelFilter(logging.Filter):
    def __init__(self, level: int):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.level


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "info_only": {
            "()": ExactLevelFilter,
            "level": logging.INFO,
        },
        "warning_only": {
            "()": ExactLevelFilter,
            "level": logging.WARNING,
        },
        "error_only": {
            "()": ExactLevelFilter,
            "level": logging.ERROR,
        },
    },
    "formatters": {
        "standard": {
            "format": settings.logger_format,
        },
    },
    "handlers": {
        "default": {
            "level": settings.logger_level,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "app_file": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 5242880,
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "info_file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/info.log",
            "maxBytes": 5242880,
            "backupCount": 5,
            "encoding": "utf-8",
            "filters": ["info_only"],
        },
        "warning_file": {
            "level": "WARNING",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/warning.log",
            "maxBytes": 5242880,
            "backupCount": 5,
            "encoding": "utf-8",
            "filters": ["warning_only"],
        },
        "error_file": {
            "level": "ERROR",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/error.log",
            "maxBytes": 5242880,
            "backupCount": 5,
            "encoding": "utf-8",
            "filters": ["error_only"],
        },
        "sqlalchemy_file": {
            "level": settings.sqlalchemy_log_level,
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/sqlalchemy.log",
            "maxBytes": 5242880,
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "audit_file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/audit.log",
            "maxBytes": 5242880,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "": {
            "level": settings.logger_level,
            "handlers": [
                "default",
                "app_file",
                "info_file",
                "warning_file",
                "error_file",
            ],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": settings.logger_level,
            "handlers": ["default", "app_file", "error_file"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": settings.logger_level,
            "handlers": ["default", "app_file"],
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "level": settings.sqlalchemy_log_level,
            "handlers": ["default", "sqlalchemy_file"],
            "propagate": False,
        },
        "syswatch.audit": {
            "level": "INFO",
            "handlers": ["audit_file"],
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
