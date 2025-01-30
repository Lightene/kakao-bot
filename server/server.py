from logging.handlers import RotatingFileHandler

from handlers.chat_handler import ChatHandler
# from handlers.webhook_handler import WebhookHandler

import socket
import json
import threading
import logging
import sys
import time
from datetime import datetime


def setup_logger():
    logger = logging.getLogger("ServerLogger")
    logger.setLevel(logging.DEBUG)

    # 로그 포맷 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    info_handler = logging.FileHandler('logs/server.log')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # 에러 로그 파일 핸들러 (ERROR 이상)
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # 콘솔 핸들러 추가
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)

    # ERROR 및 CRITICAL 로그를 stderr로 보내는 핸들러
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    return logger


class ChatServer:
    def __init__(self, host='0.0.0.0', port=9905):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}
        self.running = True
        self.lock = threading.Lock()
        self.logger = setup_logger()
        self.chat_handler = ChatHandler()
        self.socket_config()

    def socket_config(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # TCP Keepalive 설정
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)

        self.server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)  # 60초 후 시작
        self.server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)  # 10초 간격
        self.server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)  # 5회 시도

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()

            self.logger.info(f"서버 시작: {self.host}:{self.port}")

            # 연결 모니터링 스레드 시작
            monitor_thread = threading.Thread(target=self.monitor_connections)
            monitor_thread.daemon = True
            monitor_thread.start()

            while self.running:
                client_socket, addr = self.server_socket.accept()
                self.logger.info(f"새 클라이언트 연결: {addr}")

                with self.lock:
                    self.clients[client_socket] = time.time()

                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()

        except Exception as e:
            self.logger.error(f"서버 시작 오류: {e}")
        finally:
            self.stop()

    def monitor_connections(self):
        """연결 상태 모니터링"""
        while self.running:
            try:
                current_time = time.time()
                with self.lock:
                    disconnected = []
                    for client, last_time in self.clients.items():
                        if current_time - last_time > 60:  # 60초 동안 응답 없으면 연결 해제
                            disconnected.append(client)

                    for client in disconnected:
                        self.logger.warning(f"연결 시간 초과: {client.getpeername()}")
                        self.remove_client(client)

                time.sleep(5)  # 10초마다 체크
            except Exception as e:
                self.logger.error(f"모니터링 오류: {e}")

    def handle_client(self, client_socket, addr):
        buffer = ""

        try:
            while self.running:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        raise ConnectionError("연결 종료됨")

                    buffer += data.decode('utf-8')

                    while '\n' in buffer:
                        message, buffer = buffer.split('\n', 1)
                        with self.lock:
                            self.clients[client_socket] = time.time()
                        self.process_message(client_socket, message)

                except socket.timeout:
                    continue
                except socket.error as e:
                    self.logger.error(f"소켓 오류 발생 {addr}: {e}")
                    break

        except Exception as e:
            self.logger.error(f"클라이언트 처리 오류 {addr}: {e}")
        finally:
            self.remove_client(client_socket)

    def process_message(self, client_socket, message):
        try:
            data = json.loads(message)
            event = data.get('event')
            content = data.get('data', {})

            if event == 'chat':
                self.handle_chat(client_socket, content)
            elif event == 'pong':
                with self.lock:
                    self.clients[client_socket] = time.time()

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류: {e}")
        except Exception as e:
            self.logger.error(f"메시지 처리 오류: {e}")

    def handle_chat(self, client_socket, content):
        try:
            response_msg = self.chat_handler.process_message(content)

            response = {
                'event': 'response',
                'data': {
                    'room': content.get('room'),
                    'rescon': response_msg
                }
            }

            self.send_message(client_socket, response)
            self.logger.info(f"채팅 처리 - {content}")

        except Exception as e:
            self.logger.error(f"채팅 처리 오류: {e}")

    def send_message(self, client_socket, message):
        try:
            message_str = json.dumps(message) + '\n'
            client_socket.send(message_str.encode('utf-8'))
        except Exception as e:
            self.logger.error(f"전송 오류: {e}")
            self.remove_client(client_socket)

    def remove_client(self, client_socket):
        try:
            with self.lock:
                if client_socket in self.clients:
                    try:
                        peer = client_socket.getpeername()  # 소켓이 유효한지 먼저 확인
                        del self.clients[client_socket]
                        client_socket.close()
                        self.logger.info(f"클라이언트 제거: {peer}")
                    except socket.error:
                        # 이미 닫힌 소켓인 경우
                        del self.clients[client_socket]
                        self.logger.info("이미 닫힌 클라이언트 제거")
        except Exception as e:
            self.logger.error(f"클라이언트 제거 오류: {e}")

    def send_heartbeat(self):
        while self.running:
            try:
                with self.lock:
                    for client in list(self.clients.keys()):
                        try:
                            ping_message = {
                                'event': 'ping',
                                'data': {}
                            }
                            self.send_message(client, ping_message)
                        except Exception as e:
                            self.logger.error(f"Heartbeat 전송 오류: {e}")
                            self.remove_client(client)

                time.sleep(30)  # 30초마다 heartbeat 전송
            except Exception as e:
                self.logger.error(f"Heartbeat 처리 오류: {e}")

    def stop(self):
        self.running = False
        try:
            with self.lock:
                for client in list(self.clients.keys()):
                    self.remove_client(client)

            if self.server_socket:
                self.server_socket.close()

            self.logger.info("서버 종료")
        except Exception as e:
            self.logger.error(f"서버 종료 오류: {e}")
