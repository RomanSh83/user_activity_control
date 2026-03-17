from typing import Any, Protocol


class LocaleFactory(Protocol):
    def __call__(self, key: str, **kwargs: Any) -> str:
        pass
