from user_activity_control.core.exceptions.core_exceptions import CoreException


class LocaleKeyException(CoreException):
    """Ключ для перевода не найден в словаре строк."""

    def __init__(self) -> None:
        """Инициализировать исключение с сообщением по умолчанию."""

        super().__init__("Locale key not found.")


class LocaleFormatArgumentsException(CoreException):
    """Ключ для перевода не найден в словаре строк."""

    def __init__(self) -> None:
        """Инициализировать исключение с сообщением по умолчанию."""

        super().__init__(
            "Invalid formatting arguments: required kwargs are missing or unexpected kwargs were provided."
        )
