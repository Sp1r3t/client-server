import socket
import threading

HOST = "0.0.0.0"
PORT = 5000
STOP_MESSAGE = "[STOP]"


def receive_messages(conn: socket.socket) -> None:
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                print("\nКлиент отключился.")
                break

            message = data.decode("utf-8").strip()
            print(f"\nКлиент: {message}")

            if message == STOP_MESSAGE:
                print("Получена команда остановки. Соединение закрывается.")
                break
    except ConnectionResetError:
        print("\nСоединение было принудительно закрыто клиентом.")
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        conn.close()


def send_messages(conn: socket.socket) -> None:
    try:
        while True:
            message = input("Вы: ").strip()
            conn.sendall(message.encode("utf-8"))

            if message == STOP_MESSAGE:
                print("Вы завершили соединение.")
                break
    except (BrokenPipeError, OSError):
        print("\nНе удалось отправить сообщение: соединение уже закрыто.")
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        conn.close()


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)

        print(f"Сервер запущен на {HOST}:{PORT}")
        print("Ожидание подключения клиента...")

        conn, addr = server.accept()
        print(f"Подключён клиент: {addr}")

        receiver = threading.Thread(target=receive_messages, args=(conn,), daemon=True)
        receiver.start()

        send_messages(conn)


if __name__ == "__main__":
    main()