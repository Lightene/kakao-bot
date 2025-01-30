from typing import Tuple

from .room_handler_manager import RoomHandlerManager
from .room import StaticReplyHandler
from .room import LLMReplyHandler

class ChatHandler:
    def __init__(self):
        self.handler_manager = RoomHandlerManager()
        self.handler_manager.register_handler("?e", StaticReplyHandler)
        self.handler_manager.register_handler("?q", LLMReplyHandler)

    def process_message(self, content: dict) -> str:
        message = content.get("content", "").strip()

        if not message:
            return None

        command, text = self._parse_command(message)
        handler = self.handler_manager.get_handler(command)

        if handler:
            return handler.handle(text)
        return None

    def _parse_command(self, message: str) -> Tuple[str, str]:
        parts = message.split(" ", 1)
        if len(parts) != 2:
            return "", ""

        command = parts[0].lower()
        content = parts[1].strip()

        return command, content

    def _handle_quick_reply(self, message: str) -> str:
        # 정적 답변 처리 로직 구현
        pass

    def _handle_llm_reply(self, message: str) -> str:
        # LLM 답변 처리 로직 구현
        pass
