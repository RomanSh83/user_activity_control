from user_activity_control.core.config import Config
from user_activity_control.core.run import run_app
from user_activity_control.infra.logger.project_logger import ProjectLogger


def run():
    config = Config()
    project_logger = ProjectLogger(base_dir=config.base_dir, settings=config.settings)
    logger = project_logger.get_logger(__name__)
    logger.info("Initializing app...")
    try:
        import uvloop

        logger.info("Running with uvloop event loop...")
        uvloop.run(run_app(config=config, project_logger=project_logger))
    except (ImportError, AttributeError):
        import asyncio

        logger.info("Running with asyncio event loop...")
        asyncio.run(run_app(config=config, project_logger=project_logger))
