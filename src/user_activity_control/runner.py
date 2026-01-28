from user_activity_control.core.config import get_logger
from user_activity_control.core.run import run_app

logger = get_logger(__name__)


def run():
    logger.info("Application started.")
    run_app()
    logger.info("Application stopped.")
