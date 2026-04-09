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
        except ConnectionResetError:
            print("\nСоединение было закрыто клиентом.")
            stop_event.set()
            break
        except OSError:
            stop_event.set()
            break


def main() -> None:
    stop_event = threading.Event()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)

        print(f"Сервер запущен на {HOST}:{PORT}")
        print("Ожидание подключения клиента...")

        conn, addr = server.accept()
        print(f"Подключён клиент: {addr}")

        with conn:
            receiver = threading.Thread(
                target=receive_messages,
                args=(conn, stop_event),
                daemon=True
            )
            receiver.start()

            while not stop_event.is_set():
                try:
                    message = input("Вы: ")
                    conn.sendall(message.encode("utf-8"))

                    if message.strip() == STOP_MESSAGE:
                        print("Вы завершили соединение.")
                        stop_event.set()
                        break
                except (BrokenPipeError, ConnectionResetError, OSError):
                    print("\nНе удалось отправить сообщение. Соединение закрыто.")
                    stop_event.set()
                    break

        print("Сервер завершил работу с клиентом.")


if __name__ == "__main__":
    main()