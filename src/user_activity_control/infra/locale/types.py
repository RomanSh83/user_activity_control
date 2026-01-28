from typing import Any, Protocol


class Locale(Protocol):
    def __call__(self, key: str, **kwargs: Any) -> str:
        pass
