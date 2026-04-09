import socket
import threading
import sys

HOST = "0.0.0.0"
PORT = 5000
STOP_MESSAGE = "[STOP]"

print_lock = threading.Lock()


def safe_print(text: str = "", end: str = "\n") -> None:
    with print_lock:
        print(text, end=end, flush=True)


def show_prompt() -> None:
    with print_lock:
        sys.stdout.write("Вы: ")
        sys.stdout.flush()


def receive_messages(conn: socket.socket, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        try:
            data = conn.recv(1024)

            if not data:
                safe_print("\nКлиент отключился.")
                stop_event.set()
                break

            message = data.decode("utf-8").strip()

            with print_lock:
                sys.stdout.write("\r" + " " * 120 + "\r")
                print(f"Клиент: {message}", flush=True)

                if not stop_event.is_set():
                    sys.stdout.write("Вы: ")
                    sys.stdout.flush()

            if message == STOP_MESSAGE:
                safe_print("\nКлиент завершил соединение.")
                stop_event.set()
                break

        except (ConnectionResetError, OSError):
            safe_print("\nСоединение было закрыто клиентом.")
            stop_event.set()
            break


def main() -> None:
    stop_event = threading.Event()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    safe_print(f"Сервер запущен на {HOST}:{PORT}")
    safe_print("Ожидание подключения клиента...")

    conn = None

    try:
        conn, addr = server.accept()
        safe_print(f"Подключён клиент: {addr}")

        receiver = threading.Thread(
            target=receive_messages,
            args=(conn, stop_event),
            daemon=True
        )
        receiver.start()

        while not stop_event.is_set():
            try:
                message = input("Вы: ").strip()
            except KeyboardInterrupt:
                safe_print("\nСервер остановлен вручную.")
                stop_event.set()
                break
            except EOFError:
                safe_print("\nВвод недоступен. Сервер завершает работу.")
                stop_event.set()
                break

            try:
                conn.sendall(message.encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError, OSError):
                safe_print("\nНе удалось отправить сообщение. Соединение закрыто.")
                stop_event.set()
                break

            if message == STOP_MESSAGE:
                safe_print("Вы завершили соединение.")
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
        safe_print("Сервер завершил работу.")


if __name__ == "__main__":
    main()