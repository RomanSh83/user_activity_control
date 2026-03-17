from pathlib import Path

from dynaconf import Dynaconf, Validator

from user_activity_control.infra.logger.project_logger_enums import ProjectLoggerLevelsEnum


class Config:
    base_dir = Path(__file__).resolve().parents[3]
    settings = Dynaconf(
        root_path=base_dir,
        environments=True,
        envvar_prefix="",
        settings_files=[(base_dir / "config" / "settings.yaml")],
        validators=[
            Validator("TELEGRAM_BOT_TOKEN", must_exist=True),
            Validator("ADMIN_IDS", must_exist=True, is_type_of=list),
            Validator("LANGUAGE", is_in=["ru", "en"], default="ru"),
            Validator("LOG_DIR", default="logs"),
            Validator("LOG_FILE", default="log.txt"),
            Validator("LOG_MAX_FILE_SIZE", is_type_of=int, default=10),
            Validator("LOG_BACKUP_COUNT", is_type_of=int, default=5),
            Validator("PRE_REGISTERED_LOGGERS", is_type_of=list, default=["aiogram"]),
            Validator("LOG_FILE", default="log.txt"),
            Validator("LOG_LEVEL", is_in=ProjectLoggerLevelsEnum, default=ProjectLoggerLevelsEnum.ERROR),
            Validator("PAGINATION_LIMIT", is_type_of=int, default=5),
            Validator("MAX_CATEGORY_NAME_LENGTH", is_type_of=int, default=25),
            Validator("MAX_YAML_FILESIZE", is_type_of=int, default=1),
        ],
    )
