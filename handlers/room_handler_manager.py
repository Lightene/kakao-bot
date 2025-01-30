from typing import Dict, Type
from .room import RoomHandler


class RoomHandlerManager:
    def __init__(self):
        self._handlers: Dict[str, RoomHandler] = {}

    def register_handler(self, command: str, handler: Type[RoomHandler]):
        """새로운 핸들러 등록"""
        self._handlers[command] = handler()

    def get_handler(self, command: str) -> RoomHandler:
        """명령어에 해당하는 핸들러 반환"""
        return self._handlers.get(command)
