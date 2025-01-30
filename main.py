from server.server import ChatServer
import logging
import threading

if __name__ == "__main__":
    server = ChatServer()

    # Heartbeat 스레드 시작
    heartbeat_thread = threading.Thread(target=server.send_heartbeat)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()

    try:
        server.start()
    except KeyboardInterrupt:
        logging.info("서버 종료 요청")
        server.stop()