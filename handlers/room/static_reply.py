from .room_handler import RoomHandler

class StaticReplyHandler(RoomHandler):
    def handle(self, message: str) -> str:
        return "static_reply"