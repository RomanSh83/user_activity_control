from enum import Enum


class MenuActionEnum(str, Enum):
    LIST = "list"
    CHOICE_LIST = "choice_list"
    RELATED_LIST = "related_list"
    CREATE = "create"
    RETRIEVE = "retrieve"
    UPDATE = "update"
    REMOVE = "remove"
    CHOICE = "choice"


class NavigatorEntityEnum(str, Enum):
    CATEGORIES = "categories"
    USERS = "users"
