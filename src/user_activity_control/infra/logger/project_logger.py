import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dynaconf import Dynaconf

from user_activity_control.core.base.singleton import Singleton
from user_activity_control.infra.logger.project_logger_enums import ProjectLoggerLevelsEnum


class ProjectLogger(Singleton):
    def __init__(self, base_dir: Path, settings: Dynaconf) -> None:
        self.log_dir = base_dir / settings.LOG_DIR
        self.log_file = settings.LOG_FILE
        self.log_max_file_size = settings.LOG_MAX_FILE_SIZE * 1024 * 1024
        self.log_backup_count = settings.LOG_BACKUP_COUNT
        self.pre_registered_loggers = settings.PRE_REGISTERED_LOGGERS
        self.logging_level = self._get_logging_level(settings=settings)

        self._make_log_dir(log_dir=self.log_dir)

        for logger in self.pre_registered_loggers:
            self.get_logger(logger)

    @staticmethod
    def _make_log_dir(log_dir: Path) -> None:
        log_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _get_logging_level(settings: Dynaconf):
        return (
            settings.LOG_LEVEL.upper()
            if hasattr(settings, "LOG_LEVEL") and settings.LOG_LEVEL in ProjectLoggerLevelsEnum
            else ProjectLoggerLevelsEnum.ERROR
        )

    def _get_formatter(self) -> logging.Formatter:
        return logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(filename)-45s | %(funcName)-25s  | %(lineno)-5d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def _get_console_handler(self) -> logging.Handler:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.logging_level)
        handler.setFormatter(self._get_formatter())
        return handler

    def _get_file_handler(self) -> logging.Handler:
        handler = RotatingFileHandler(
            filename=(self.log_dir / self.log_file),
            encoding="utf-8",
            maxBytes=self.log_max_file_size,
            backupCount=self.log_backup_count,
        )
        handler.setLevel(self.logging_level)
        handler.setFormatter(self._get_formatter())
        return handler

    def get_logger(self, name: str | None) -> logging.Logger:
        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            logger.setLevel(self.logging_level)
            logger.addHandler(self._get_console_handler())
            logger.addHandler(self._get_file_handler())
        return logger
