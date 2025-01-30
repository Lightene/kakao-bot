from .room_handler import RoomHandler
from llm.llm import LLM

class LLMReplyHandler(RoomHandler):
    def handle(self, message: str) -> str:
        ai = LLM()
        return ai.question(message)