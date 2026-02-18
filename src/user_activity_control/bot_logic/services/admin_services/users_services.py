from user_activity_control.bot_logic.schemas.user_schemas import UserSchema, UserUpdateSchema
from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.config import get_logger
from user_activity_control.infra.app_data.app_data import get_app_data, get_users


class UserService(Singleton):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.app_data = get_app_data()
        self.users = get_users()

    def get_users(self, offset: int, limit: int) -> list[UserSchema]:
        users_keys = sorted(self.users.keys())
        current_users_keys = (
            users_keys[offset:] if offset + limit - 1 > len(self.users) else users_keys[offset : offset + limit]
        )
        return [self.get_user(user_id=key) for key in current_users_keys]

    def get_user(self, user_id: str) -> UserSchema:
        return UserSchema(user_id=user_id, **self.users[user_id])

    def exists_user(self, user_id: str | None) -> bool:
        return user_id in self.users

    def create_user(self, user: UserSchema) -> None:
        self.app_data.save_user(user=user)

    def update_user(self, user_id: str, user_data: UserUpdateSchema) -> None:
        self.app_data.update_user(user_id=user_id, user_data=user_data)

    def remove_user(self, user_id: str) -> None:
        self.app_data.remove_user(user_id=user_id)

    def remove_users(self, user_ids: list[str]) -> None:
        self.app_data.remove_users(user_ids=user_ids)
