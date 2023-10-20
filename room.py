import time
import requests
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from .config import config


class Source(BaseModel):
    name: str = ""
    type: Optional[str]


class User(BaseModel):
    type: Optional[str]
    user_id: int = 0
    username: str = "Unknown"
    avatar: Optional[str]


class Room(BaseModel):
    number: str
    raw_message: str = ""
    source_info: Source
    type: Optional[str]
    time: int
    user_info: User


class RoomStorage:
    def __init__(self):
        self.room_list = []

    def _parse_rooms(self, room_list: List[Dict[str, Any]]) -> List[Room]:
        return [Room.parse_obj(room) for room in room_list]

    def _merge_rooms(self, rooms: List[Room], present_rooms: List[Room]) -> List[Room]:
        room_dict = {room.number: room for room in rooms}

        # 新房间替换旧房间
        for present_room in present_rooms:
            room_dict[present_room.number] = present_room

        # 删除 120s 前的房间
        current_time_ms = time.time()
        rooms = [
            room
            for room in room_dict.values()
            if current_time_ms - room.time / 1000 <= 120
        ]

        return rooms

    def add_room(self, number: str, user_id: int, raw_message: str, source: str):
        room = Room(
            number=number,
            raw_message=raw_message,
            source_info=Source(name=config.token_name, type=source),
            type="other",
            time=int(time.time() * 1000),
            user_info=User(
                user_id=user_id, username=f"{source.upper()}用户", type=source
            ),
        )
        self.room_list.append(room)

    def get_raw_rooms(self):
        response = requests.get(
            "https://api.bandoristation.com/?function=query_room_number",
        )
        response.raise_for_status()
        present_room_list: List[Dict[str, Any]] = response.json().get("response", [])

        present_rooms = self._parse_rooms(present_room_list)

        self.room_list = self._merge_rooms(self.room_list, present_rooms)

        return self.room_list

    def export(self):
        rooms = self.get_raw_rooms()
        return [
            {
                "number": int(room.number),
                "rawMessage": room.raw_message,
                "source": room.source_info.name,
                "userId": str(room.user_info.user_id),
                "time": room.time,
                "avanter": room.user_info.avatar,
                "userName": room.user_info.username,
            }
            for room in rooms
        ]
