from dishka import Provider, Scope, provide

from user_activity_control.infra.storage.in_memory_storage import ActivityStorage


class ActivityStorageProvider(Provider):
    @provide(scope=Scope.APP)
    def get_activity_storage(self) -> ActivityStorage:
        return ActivityStorage()
