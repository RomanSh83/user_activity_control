from enum import Enum


class StateKeysEnum(str, Enum):
    PREVIOUS_MSG_ID = "previous_msg_id"
    CALLBACK_STACK = "callback_stack"
