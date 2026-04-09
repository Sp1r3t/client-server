import socket
import threading
import sys

SERVER_HOST = "127.0.0.1"   # если используешь port forwarding в VirtualBox
SERVER_PORT = 5000
STOP_MESSAGE = "[STOP]"

print_lock = threading.Lock()


def safe_print(text: str = "", end: str = "\n") -> None:
    with print_lock:
        print(text, end=end, flush=True)


def show_prompt() -> None:
    with print_lock:
        sys.stdout.write("Вы: ")
        sys.stdout.flush()


def receive_messages(sock: socket.socket, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        try:
            data = sock.recv(1024)

            if not data:
                safe_print("\nСервер отключился.")
                stop_event.set()
                break

            message = data.decode("utf-8").strip()

            with print_lock:
                sys.stdout.write("\r" + " " * 120 + "\r")
                print(f"Сервер: {message}", flush=True)

                if not stop_event.is_set():
                    sys.stdout.write("Вы: ")
                    sys.stdout.flush()

            if message == STOP_MESSAGE:
                safe_print("\nСервер завершил соединение.")
                stop_event.set()
                break

        except (ConnectionResetError, OSError):
            safe_print("\nСоединение было принудительно закрыто сервером.")
            stop_event.set()
            break


def main() -> None:
    stop_event = threading.Event()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        safe_print(f"Подключено к серверу {SERVER_HOST}:{SERVER_PORT}")

        receiver = threading.Thread(
            target=receive_messages,
            args=(client, stop_event),
            daemon=True
        )
        receiver.start()

        while not stop_event.is_set():
            try:
                message = input("Вы: ").strip()
            except KeyboardInterrupt:
                safe_print("\nКлиент остановлен вручную.")
                stop_event.set()
                break
            except EOFError:
                safe_print("\nВвод недоступен. Клиент завершает работу.")
                stop_event.set()
                break

            try:
                client.sendall(message.encode("utf-8"))
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

        try:
            client.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        client.close()
        safe_print("Клиент завершил работу.")


if __name__ == "__main__":
    main()