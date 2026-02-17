from typing import Any

from user_activity_control.core.base.singleton import Singleton


class ActivityStorage(Singleton):
    def __init__(self) -> None:
        self.storage: dict[Any, Any] = {}

    def push_data(self, key: Any, value: Any) -> None:
        """Поместить ключ:значение в FSM Storage."""
        self.storage[key] = value

    def pull_data(self, key: Any) -> Any:
        """Получить значение (по ключу) из FSM Storage"""
        return self.storage.get(key)
