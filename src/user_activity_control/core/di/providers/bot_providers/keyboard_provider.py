from dishka import Provider, Scope, provide
from dynaconf import Dynaconf

from user_activity_control.bot_logic.keyboards.common_menu_buttons import CommonMenuButtons
from user_activity_control.bot_logic.keyboards.keyboard_generator import KeyboardGenerator
from user_activity_control.infra.locale.types import LocaleFactory
from user_activity_control.infra.logger.types import LoggerFactory


class KeyboardProvider(Provider):
    @provide(scope=Scope.APP)
    def get_common_buttons(
        self, logger_factory: LoggerFactory, settings: Dynaconf, locale_factory: LocaleFactory
    ) -> CommonMenuButtons:
        return CommonMenuButtons(logger_factory=logger_factory, settings=settings, locale_factory=locale_factory)

    @provide(scope=Scope.APP)
    def get_keyboard_generator(
        self, logger_factory: LoggerFactory, common_buttons: CommonMenuButtons, locale_factory: LocaleFactory
    ) -> KeyboardGenerator:
        return KeyboardGenerator(
            logger_factory=logger_factory, common_buttons=common_buttons, locale_factory=locale_factory
        )
