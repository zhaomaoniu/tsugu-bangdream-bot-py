from pydantic import BaseModel
from typing import List

class User(BaseModel):
    user_id : str
    car_send: bool = True
    servers: List[str] = ["3", "0"]
    present_server: str = "3"
