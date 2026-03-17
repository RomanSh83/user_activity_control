from user_activity_control.bot_logic.schemas.user_schemas import UserParamsUpdateSchema, UserSchema, UsersSchema
from user_activity_control.infra.app_data.app_data import AppData
from user_activity_control.infra.logger.types import LoggerFactory


class UserService:
    def __init__(self, app_data: AppData, users: UsersSchema, logger_factory: LoggerFactory):
        self.logger = logger_factory(__name__)
        self.app_data = app_data
        self.users = users

    def get_users(self, offset: int, limit: int, user_ids: list[str] | None = None) -> list[UserSchema]:
        if user_ids is None:
            user_ids = list(self.users.root.keys())
        return [self.get_user(user_id=key) for key in user_ids[offset : offset + limit]]

    def get_category_user_ids(self, category_id: str | None) -> list[str]:
        return [user_id for user_id in self.users.root if self.users.root[user_id].category == category_id]

    def get_user(self, user_id: str) -> UserSchema:
        return UserSchema(user_id=user_id, **self.users.root[user_id].model_dump())

    def exists_user(self, user_id: str | None) -> bool:
        return user_id in self.users.root

    def create_user(self, user: UserSchema) -> None:
        self.app_data.save_user(user=user)

    def update_user(self, user_id: str, user_data: UserParamsUpdateSchema) -> None:
        self.app_data.update_user(user_id=user_id, user_data=user_data)

    def remove_user(self, user_id: str) -> None:
        self.app_data.remove_user(user_id=user_id)

    def remove_users(self, user_ids: list[str]) -> None:
        self.app_data.remove_users(user_ids=user_ids)
