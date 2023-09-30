import requests
from pydantic import BaseModel
from typing import List, Dict, Any


class Source(BaseModel):
    name: str
    type: str


class User(BaseModel):
    type: str
    user_id: int
    username: str
    avatar: str


class Room(BaseModel):
    number: str
    raw_message: str
    source_info: Source
    type: str
    time: int
    user_info: User


def _parse_rooms(room_list: List[Dict[str, Any]]) -> List[Room]:
    return [Room.parse_obj(room) for room in room_list]


def get_rooms():
    response = requests.get(
        "https://api.bandoristation.com/?function=query_room_number",
    )
    response.raise_for_status()
    room_list: List[Dict[str, Any]] = response.json().get("response", [])

    rooms = _parse_rooms(room_list)
    # TODO: 车牌缓存
