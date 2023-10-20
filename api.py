import json
import requests
from typing import Callable, Optional, Any, Dict, List, TYPE_CHECKING

from .config import (
    cmd_help_dict,
    config,
    config_file_path,
)
from .utils import (
    get_player_id,
    get_data_from_backend,
    get_server_name,
    get_server_chinese_name,
    get_server_id,
    get_server,
    match_player_id,
    match_servers,
    bind_player_id,
    remove_none_value,
    insert_value_and_remove_duplicates,
)

if TYPE_CHECKING:
    from .utils import UserDataStorage


# 以下函数的 `message` 参数须替换指令名为空并使用.strip()方法


def _help(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if not message:
        result = "\n>> ".join(cmd_help_dict.keys())  # 用换行连接不同键对应的值
        result = f"当前可用的 Tsugu 指令有：\n>> {result}\n发送 {message}+指令 查看帮助"
        return [
            {
                "type": "string",
                "string": result,
            }
        ]
    if message in cmd_help_dict.keys():
        return [
            {
                "type": "string",
                "string": ">> " + cmd_help_dict[message],
            }
        ]


def _swc(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if not message:
        return cmd_help_dict["swc"]

    args = message.split(maxsplit=1)
    status = args[0]  # on/off
    targets = args[1].split()

    if config.bot_name not in targets:
        return None

    if "ALL" not in config.admin and user_id not in config.admin:
        return [
            {
                "type": "string",
                "string": "权限不足",
            }
        ]

    if status == "on":
        config.ban_groups = [group for group in config.ban_groups if group != group_id]

        with open(config_file_path, "w", encoding="UTF-8") as file:
            json.dump(config.dict(), file, indent=4, ensure_ascii=False)

        return [
            {
                "type": "string",
                "string": config.status_on_echo,
            }
        ]

    elif status == "off":
        config.ban_groups.append(group_id)
        config.ban_groups = list(set(config.ban_groups))

        with open(config_file_path, "w", encoding="UTF-8") as file:
            json.dump(config.dict(), file, indent=4, ensure_ascii=False)

        return [
            {
                "type": "string",
                "string": config.status_off_echo,
            }
        ]


def _player_status(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    server_id = int(get_server(message, user_storage, user_id)[1])
    server = get_server_name(server_id)
    server_chinese_name = get_server_chinese_name(server_id)

    if server_id is None:
        return None

    if (player_id := get_player_id(user_id, server)).isdigit():
        return get_data_from_backend(
            "/searchPlayer",
            {
                "server": server_id,
                "useEasyBG": config.use_easy_bg,
                "playerId": player_id,
            },
        )
    elif isinstance(player_id, list):
        # 获取错误提示
        return player_id
    else:
        return [
            {
                "type": "string",
                "string": f"未在当前服务器: {server_chinese_name} 绑定过！\n{cmd_help_dict['绑定玩家']}",
            }
        ]


def _bind_player(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if not message:
        return [
            {
                "type": "string",
                "string": cmd_help_dict["绑定玩家"],
            }
        ]

    if (player_id := match_player_id(message)) is not None:
        server_id = get_server(message, user_storage, user_id)[1]
        return [
            {
                "type": "string",
                "string": bind_player_id(
                    user_id, player_id, get_server_name(int(server_id))
                ),
            }
        ]


def _bd_station_on_personal(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    user_storage.change_data(user_id, "car_send", True)
    return [
        {
            "type": "string",
            "string": "已开启个人车牌转发",
        }
    ]


def _bd_station_off_personal(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    user_storage.change_data(user_id, "car_send", False)
    return [
        {
            "type": "string",
            "string": "已关闭个人车牌转发",
        }
    ]


def _set_mode(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if (server_id := get_server_id(message)) is not None:
        user_storage.change_data(user_id, "present_server", server_id)
        p_servers = user_storage.get_data(user_id).servers
        user_storage.change_data(
            user_id, "servers", insert_value_and_remove_duplicates(p_servers, server_id)
        )
        return [
            {
                "type": "string",
                "string": f"默认服务器已改为 {get_server_chinese_name(int(server_id))}",
            }
        ]
    return None


def _main_server(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if servers := match_servers(message):
        user_storage.change_data(user_id, "servers", servers)
        return [
            {
                "type": "string",
                "string": f"默认服务器已改为 {', '.join([get_server_chinese_name(int(server)) for server in servers])}",
            }
        ]
    return [
        {
            "type": "string",
            "string": "错误: 未匹配到服务器",
        }
    ]


def __std__(
    api: str,
    message: Optional[str],
    user_id: int,
    user_storage: "UserDataStorage",
):
    return get_data_from_backend(
        api,
        {
            "default_servers": get_server(message, user_storage, user_id)[0],
            "text": message,
            "useEasyBG": config.use_easy_bg,
        },
    )


def _search_event(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if message != "":
        return __std__("/searchEvent", message, user_id, user_storage)
    return [{"type": "string", "string": cmd_help_dict["查活动"]}]


def _search_song(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if message != "":
        return __std__("/searchSong", message, user_id, user_storage)
    return [{"type": "string", "string": cmd_help_dict["查曲"]}]


def _search_card(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if message != "":
        return __std__("/searchCard", message, user_id, user_storage)
    return [{"type": "string", "string": cmd_help_dict["查卡"]}]


def _song_meta(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if get_server_id(message) is None and message != "":
        # 不能加上服务器以外的参数
        return None

    _, server = get_server(message, user_storage, user_id)
    return get_data_from_backend(
        "/songMeta",
        {
            "default_servers": [server],
            "useEasyBG": config.use_easy_bg,
            "server": server,
        },
    )


def _get_card_illustration(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if message != "" and message.isdigit():
        return get_data_from_backend("/getCardIllustration", {"cardId": message})
    return [{"type": "string", "string": cmd_help_dict["查卡面"]}]


def _search_character(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if message != "":
        return get_data_from_backend(
            "/searchCharacter",
            {
                "default_servers": get_server(message, user_storage, user_id)[0],
                "text": message,
            },
        )
    return [{"type": "string", "string": cmd_help_dict["查角色"]}]


def _search_gacha(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if message != "":
        return get_data_from_backend(
            "/searchGacha",
            {
                "default_servers": get_server(message, user_storage, user_id)[0],
                "useEasyBG": config.use_easy_bg,
                "gachaId": message,
            },
        )
    return [{"type": "string", "string": cmd_help_dict["查卡池"]}]


def _search_player(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if (player_id := match_player_id(message)) is not None:
        server_id = get_server(message, user_storage, user_id)[1]
        return get_data_from_backend(
            "/searchPlayer",
            {
                "server": int(server_id),
                "useEasyBG": config.use_easy_bg,
                "playerId": int(player_id),
            },
        )


# FEATURE: lsycx [tier] [event_id?] [server?]
def _lsycx(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    args = message.split()

    if len(args) == 0:
        return [
            {
                "type": "string",
                "string": f"格式错误: {cmd_help_dict['lsycx']}",
            }
        ]
    elif len(args) == 1:
        # tier
        tier, event_id = args[0], None
    else:
        # tier, event_id
        tier, event_id = args[0], int(args[1])

    return get_data_from_backend(
        "/lsycx",
        remove_none_value(
            {
                "server": get_server(message, user_storage, user_id)[1],
                "tier": int(tier),
                "eventId": event_id,
            }
        ),
    )


# FEATURE: ycxall [event_id?] [server?]
def _ycx_all(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    args = message.split()

    event_id = int(args[0]) if len(args) >= 1 else None

    return get_data_from_backend(
        "/ycxAll",
        remove_none_value(
            {
                "server": get_server(message, user_storage, user_id)[1],
                "eventId": event_id,
            },
        ),
    )


# FEATURE: ycx [tier] [event_id?] [server?]
def _ycx(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    args = message.split()

    if len(args) == 0:
        return [
            {
                "type": "string",
                "string": f"格式错误: {cmd_help_dict['ycx']}",
            }
        ]
    elif len(args) == 1:
        # tier
        tier, event_id = args[0], None
    else:
        # tier, event_id
        tier, event_id = args[0], int(args[1])

    return get_data_from_backend(
        "/ycx",
        remove_none_value(
            {
                "server": get_server(message, user_storage, user_id)[1],
                "tier": int(tier),
                "eventId": event_id,
            }
        ),
    )


def _song_chart(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if message == "":
        return [{"type": "string", "string": cmd_help_dict["查谱面"]}]

    args = message.split()

    if not args[0].isdigit():
        return [{"type": "string", "string": "不合规范的歌曲ID"}]

    return get_data_from_backend(
        "/songChart",
        {
            "default_servers": get_server(message, user_storage, user_id)[0],
            "songId": int(args[0]),
            "difficultyText": args[1] if len(args) >= 2 else "ex",
        },
    )


def _gacha_simulate(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if group_id in config.ban_gacha_simulate_groups:
        return [{"type": "string", "string": "本群的抽卡模拟功能已被Bot主禁用"}]

    args = message.split()
    server_id = get_server(message, user_storage, user_id)[1]

    return get_data_from_backend(
        "/gachaSimulate",
        remove_none_value(
            {
                "server_mode": server_id,
                "status": True,
                "times": int(args[0]) if message != "" and int(args[0]) < 10000 else 10,
                "gachaId": int(args[1]) if len(args) >= 2 else None,
            }
        )
        if message != ""
        else {"server_mode": server_id, "status": True, "times": 10},
    )


def _room_list(
    message: Optional[str] = None,
    user_id: Optional[int] = -1,
    group_id: Optional[int] = -1,
    user_storage: Optional["UserDataStorage"] = None,
):
    if message != "":
        # 无参数指令
        return None

    response = requests.get(
        "https://api.bandoristation.com/?function=query_room_number",
    )
    response.raise_for_status()
    response_json: dict = response.json()
    response_list: List[Dict[str, Any]] = response_json.get("response", [])

    room_dict = {}  # 用于存储最新时间的字典

    # 遍历原始列表，更新每个"number"对应的最新时间戳
    for item in response_list:
        number = int(item.get("number", 0))
        time = item["time"]
        if number not in room_dict or time > room_dict.get(number)["time"]:
            room_dict[number] = {
                "number": number,
                "rawMessage": item.get("raw_message", ""),
                "source": item.get("source_info", {}).get("name", ""),
                "userId": str(item.get("user_info", {}).get("user_id", "")),
                "time": time,
                "avanter": item.get("user_info", {}).get("avatar", None),
                "userName": item.get("user_info", {}).get("username", "Bob"),
            }
    room_list = list(room_dict.values())

    if room_list == []:
        return [{"type": "string", "string": "myc"}]

    return get_data_from_backend("/roomList", {"roomList": room_list})


HANDLERS: Dict[
    str, Callable[[str, int, int, "UserDataStorage"], List[Dict[str, str]]]
] = {
    "Help": _help,
    "Swc": _swc,
    "/searchSong": _search_song,
    "/searchEvent": _search_event,
    "/songChart": _song_chart,
    "/getCardIllustration": _get_card_illustration,
    "/searchCharacter": _search_character,
    "/searchGacha": _search_gacha,
    "/searchCard": _search_card,
    "/searchPlayer": _search_player,
    "PlayerStatus": _player_status,
    "BindPlayer": _bind_player,
    "/songMeta": _song_meta,
    "/roomList": _room_list,
    "/ycxAll": _ycx_all,
    "/ycx": _ycx,
    "/lsycx": _lsycx,
    "/gachaSimulate": _gacha_simulate,
    "BD_STATION_ON_PERSONAL": _bd_station_on_personal,
    "BD_STATION_OFF_PERSONAL": _bd_station_off_personal,
    "Main_server": _main_server,
    "SET_mode": _set_mode,
}
