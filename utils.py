import json
import re
import inspect
import requests
from typing import Any, Dict, Union, List, Tuple
from pathlib import Path
from pydantic import BaseModel

from .config import (
    car_config,
    cmd_dict,
    config,
    language_mapping,
    chinese_language_mapping,
)
from .room import RoomStorage
from .model import User


class JsonDataStorage:
    """基于 Pydantic 的 JSON 数据读写方法"""

    def __init__(
        self,
        model: Union[BaseModel, List[BaseModel]] = None,
        file_path: Union[str, Path] = "",
    ):
        """基于 Pydantic 的 JSON 数据读写方法

        参数:
        - model (Union[BaseModel, List[BaseModel]], optional): 父类为 BaseModel 的模型
        - file_path (Union[str, Path]): 要保存数据的文件路径
        """
        if not file_path:
            raise ValueError("File path is required.")
        self.model = model
        self.file_path = file_path

    def load(self) -> "JsonDataStorage.model":
        """
        从指定的文件路径加载 JSON 数据并将其转换为模型对象

        返回:
        - BaseModel: 解析后的模型对象
        """
        return self.model.parse_file(self.file_path)

    def load_as_list(self) -> List["JsonDataStorage.model"]:
        """
        从指定的文件路径加载 JSON 数据并将其转换为模型对象列表

        返回:
        - List[BaseModel]: 解析后的模型对象列表
        """
        with open(self.file_path, "r", encoding="UTF-8") as file:
            data: List[Dict[Any, Any]] = json.load(file)
        return [self.model.parse_obj(d) for d in data]

    def save(self, data: BaseModel) -> None:
        """
        将模型对象转换为 JSON 数据并保存到指定的文件路径

        参数:
        - data (BaseModel): 要保存的模型对象
        """
        with open(self.file_path, "w", encoding="UTF-8") as file:
            json.dump(data.dict(), file, indent=4)

    def save_as_list(self, data: List[BaseModel]) -> None:
        """
        将模型对象转换为列表 JSON 数据并保存到指定的文件路径

        参数:
        - data (List[BaseModel]): 要保存的模型对象列表
        """
        if type(data) != list:
            raise ValueError("Only list-like object is suitable for this method.")
        with open(self.file_path, "w", encoding="UTF-8") as file:
            json.dump([d.dict() for d in data], file, indent=4)


class UserDataStorage(JsonDataStorage):
    def __init__(self):
        super().__init__(User, Path.cwd() / "data" / "user.json")
        if not self.file_path.exists():
            if not self.file_path.parent.exists():
                self.file_path.parent.mkdir()
            with open(self.file_path, "w", encoding="UTF-8") as file:
                json.dump([], file, indent=4, ensure_ascii=False)
            self.data = []
        else:
            self.data: List[User] = self.load_as_list()

    def add_user(self, user_id: int) -> User:
        data = User(user_id=user_id)
        self.data.append(data)
        self.save_as_list(self.data)
        return data

    def change_data(self, user_id: int, key: str, value: Any) -> User:
        symbol = False
        for idx, data in enumerate(self.data):
            if data.user_id == user_id:
                setattr(self.data[idx], key, value)
                symbol = True
                break

        if not symbol:
            self.add_user(user_id)
            self.change_data(user_id, key, value)

        self.save_as_list(self.data)
        return self.get_data(user_id)

    def get_data(self, user_id: int) -> User:
        for data in self.data:
            if data.user_id == user_id:
                return data
        return self.add_user(user_id)


def is_car(message: str) -> bool:
    is_car = False

    # 检查car_config['car']中的关键字
    for keyword in car_config["car"]:
        if keyword in message:
            is_car = True
            break

    # 检查car_config['fake']中的关键字
    for keyword in car_config["fake"]:
        if keyword in message:
            is_car = False
            break

    pattern = r"^\d{5}(\D|$)|^\d{6}(\D|$)"
    if re.match(pattern, message):
        pass
    else:
        is_car = False

    return is_car


def is_support_cmd(message: str) -> bool:
    for key in cmd_dict.keys():
        if message.startswith(key):
            return True
    return False


def get_api(message: str) -> Tuple[str, str]:
    for key in cmd_dict.keys():
        if message.startswith(key):
            api = cmd_dict[key]
            if not message.endswith(("玩家状态", "模式")):
                return api, message.replace(key, "").strip()
            return api, message.replace("玩家状态", "").replace("模式", "").strip()
    return None


def extra_args_handler(func):
    def wrapper(*args, **kwargs):
        # 获取原始函数的参数信息
        func_argspec = inspect.getfullargspec(func)
        func_args = func_argspec.args

        # 提取原始函数的参数
        func_kwargs = {arg: kwargs[arg] for arg in func_args if arg in kwargs}

        result = func(**func_kwargs)  # 调用原始函数并传入原始参数
        return result

    return wrapper


def remove_none_value(data: dict) -> dict:
    return {k: v for k, v in data.items() if v is not None}


def insert_value_and_remove_duplicates(lst: list, value):
    lst.insert(0, value)

    result = []
    for x in lst:
        if x not in result:
            result.append(x)

    return result


def match_player_id(message: str) -> str:
    args = message.split()
    for arg in args:
        if arg.isdigit() and len(arg) > 5:
            return arg
    return None


def get_server_name(server_id: int) -> str:
    for k, v in language_mapping.items():
        if v == server_id:
            return k


def get_server_chinese_name(server_id: int) -> str:
    for k, v in chinese_language_mapping.items():
        if v == server_id:
            return k


def get_server_id(message: str) -> str:
    """注意: `server_id` 可能为 "0", 不能直接使用 `if server_id: ...` 进行判断！"""
    for k, v in language_mapping.items():
        if k in message:
            return str(v)

    for k, v in chinese_language_mapping.items():
        if k in message:
            return str(v)


def get_server(
    message: str, user_storage: UserDataStorage, user_id: int
) -> Tuple[List[str], str]:
    if (server_id := get_server_id(message)) is not None:
        return [server_id], server_id
    data = user_storage.get_data(user_id)
    return data.servers, data.present_server


def post_car(message: str, user_id: int, room_storage: RoomStorage) -> int:
    car_id = message[:6]

    if not car_id.isdigit() and car_id[:5].isdigit():
        car_id = car_id[:5]

    url = f"https://api.bandoristation.com/index.php?function=submit_room_number&number={car_id}&user_id={user_id}&raw_message={message}&source={config.token_name}&token={config.bandori_station_token}"
    room_storage.add_room(car_id, user_id, message, config.token_name)
    return requests.get(url).status_code


def get_player_id(user_id: Union[str, int], server: str) -> str:
    url = f"{config.bind_api_base}/api/data"
    params = {"mode": "get", "user_id": str(user_id), "server": server}
    try:
        with requests.Session() as session:
            headers = {"Content-Type": "application/json"}
            response = session.post(url, json=params, headers=headers)
            response.raise_for_status()
            return response.text
    except requests.exceptions.RequestException as e:
        return [{"type": "string", "string": f"获取玩家ID错误: {e}"}]


def bind_player_id(user_id: str, uid: str, server: str):
    url = f"{config.bind_api_base}/api/data"
    data = {"mode": "save", "user_id": str(user_id), "uid": str(uid), "server": server}
    try:
        with requests.Session() as session:
            headers = {"Content-Type": "application/json"}
            response = session.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.text
    except requests.exceptions.RequestException as e:
        return [{"type": "string", "string": f"绑定错误: {e}"}]


def match_servers(message: str) -> List[str]:
    str_servers = message.split()
    servers = []
    for str_server in str_servers:
        if (server_id := get_server_id(str_server)) is not None:
            servers.append(server_id)
    return servers


def get_data_from_backend(api, data) -> List[Dict[str, str]]:
    try:
        print(data)
        response = requests.post(f"{config.api_base}{api}", json=data)
        response.raise_for_status()  # 如果发生HTTP错误，将引发异常
        return response.json()
    except requests.exceptions.RequestException as e:
        return [{"type": "string", "string": f"后端服务器连接出错\n{e}\n{data}"}]
    except Exception as e:
        return [{"type": "string", "string": f"内部错误: {e}"}]
