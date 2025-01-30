from abc import ABC, abstractmethod

class RoomHandler(ABC):
    @abstractmethod
    def handle(self, message: str) -> str:
        """메시지 처리를 위한 추상 메서드"""
        pass
