from typing import Dict, List, Optional

from .api import HANDLERS
from .config import config
from .room import RoomStorage
from .utils import UserDataStorage, is_car, is_support_cmd, post_car, get_api


user_storage = UserDataStorage()
room_storage = RoomStorage()


def is_cmd(message: str) -> bool:
    """判断消息是否为 Tsugu 指令

    Args:
        message (str): 用户发送的消息

    Returns:
        bool: 是否为 Tsugu 指令
    """
    return is_car(message) or is_support_cmd(message)


def get_result(
    message: str, user_id: int, group_id: int = -1
) -> Optional[List[Dict[str, str]]]:
    """获取来自 Tsugu 的回应

    Args:
        message (str): 用户发送的消息
        user_id (int): 用户ID (QQ号)
        group_id (int, optional): 群聊ID (群号). Defaults to -1.

    Returns:
        Optional[List[Dict[str, str]]]: Tsugu 的回应
    """
    if is_car(message):
        if user_storage.get_data(user_id).car_send:
            post_car(message, user_id, room_storage)
            return None

    result = get_api(message)
    if not result:
        return None

    api, arg = result

    if group_id in config.ban_groups and api != "Swc":
        return None

    if api is not None:
        return HANDLERS[api](
            message=arg,
            user_id=user_id,
            group_id=group_id,
            user_storage=user_storage,
            room_storage=room_storage,
        )
