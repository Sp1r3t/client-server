import socket
import threading

SERVER_HOST = "10.0.2.15"  # замени на IP сервера
SERVER_PORT = 5000
STOP_MESSAGE = "[STOP]"


def receive_messages(sock: socket.socket, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        try:
            data = sock.recv(1024)

            if not data:
                print("\nСервер отключился.")
                stop_event.set()
                break

            message = data.decode("utf-8")
            print(f"\nСервер: {message}")

            if message.strip() == STOP_MESSAGE:
                print("Сервер завершил соединение.")
                stop_event.set()
                break

        except (ConnectionResetError, OSError):
            print("\nСоединение было принудительно закрыто сервером.")
            stop_event.set()
            break


def main() -> None:
    stop_event = threading.Event()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        print(f"Подключено к серверу {SERVER_HOST}:{SERVER_PORT}")

        receiver = threading.Thread(
            target=receive_messages,
            args=(client, stop_event),
            daemon=True
        )
        receiver.start()

        while not stop_event.is_set():
            try:
                message = input("Вы: ")
            except KeyboardInterrupt:
                print("\nКлиент остановлен вручную.")
                stop_event.set()
                break
            except EOFError:
                print("\nВвод недоступен. Клиент завершает работу.")
                stop_event.set()
                break

            try:
                client.sendall(message.encode("utf-8"))
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

        try:
            client.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        client.close()
        print("Клиент завершил работу.")


if __name__ == "__main__":
    main()