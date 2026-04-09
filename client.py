import socket
import threading

SERVER_HOST = "127.0.0.1"  # Укажи IP сервера, если клиент на другом компьютере
SERVER_PORT = 5000
STOP_MESSAGE = "[STOP]"


def receive_messages(sock: socket.socket) -> None:
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                print("\nСервер отключился.")
                break

            message = data.decode("utf-8").strip()
            print(f"\nСервер: {message}")

            if message == STOP_MESSAGE:
                print("Получена команда остановки. Соединение закрывается.")
                break
    except ConnectionResetError:
        print("\nСоединение было принудительно закрыто сервером.")
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        sock.close()


def send_messages(sock: socket.socket) -> None:
    try:
        while True:
            message = input("Вы: ").strip()
            sock.sendall(message.encode("utf-8"))

            if message == STOP_MESSAGE:
                print("Вы завершили соединение.")
                break
    except (BrokenPipeError, OSError):
        print("\nНе удалось отправить сообщение: соединение уже закрыто.")
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        sock.close()


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((SERVER_HOST, SERVER_PORT))
        print(f"Подключено к серверу {SERVER_HOST}:{SERVER_PORT}")

        receiver = threading.Thread(target=receive_messages, args=(client,), daemon=True)
        receiver.start()

        send_messages(client)


if __name__ == "__main__":
    main()