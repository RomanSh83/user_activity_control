import logging
from typing import Protocol


class LoggerFactory(Protocol):
    def __call__(self, name: str) -> logging.Logger:
        pass
