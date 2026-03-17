from dishka import Provider, Scope, provide

from user_activity_control.infra.logger.project_logger import ProjectLogger
from user_activity_control.infra.logger.types import LoggerFactory


class LoggerProvider(Provider):
    def __init__(self, project_logger: ProjectLogger):
        super().__init__()
        self.project_logger = project_logger

    @provide(scope=Scope.APP)
    def get_logger(self) -> LoggerFactory:
        return self.project_logger.get_logger
