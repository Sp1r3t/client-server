import socket
import threading

HOST = "0.0.0.0"
PORT = 5000
STOP_MESSAGE = "[STOP]"


def receive_messages(conn: socket.socket, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        try:
            data = conn.recv(1024)

            if not data:
                print("\nКлиент отключился.")
                stop_event.set()
                break

            message = data.decode("utf-8")
            print(f"\nКлиент: {message}")

            if message.strip() == STOP_MESSAGE:
                print("Клиент завершил соединение.")
                stop_event.set()
                break

        except (ConnectionResetError, OSError):
            print("\nСоединение было закрыто клиентом.")
            stop_event.set()
            break


def main() -> None:
    stop_event = threading.Event()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"Сервер запущен на {HOST}:{PORT}")
    print("Ожидание подключения клиента...")

    conn = None

    try:
        conn, addr = server.accept()
        print(f"Подключён клиент: {addr}")

        receiver = threading.Thread(
            target=receive_messages,
            args=(conn, stop_event),
            daemon=True
        )
        receiver.start()

        while not stop_event.is_set():
            try:
                message = input("Вы: ")
            except KeyboardInterrupt:
                print("\nСервер остановлен вручную.")
                stop_event.set()
                break
            except EOFError:
                print("\nВвод недоступен. Сервер завершает работу.")
                stop_event.set()
                break

            try:
                conn.sendall(message.encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError, OSError):
                print("\nНе удалось отправить сообщение. Соединение закрыто.")
                stop_event.set()
                break

            if message.strip() == STOP_MESSAGE:
                print("Вы завершили соединение.")
                stop_event.set()
                break

    finally:
        stop_event.set()

        if conn is not None:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            conn.close()

        server.close()
        print("Сервер завершил работу.")


if __name__ == "__main__":
    main()