from serve2 import handle_connection
import threading
import socket

def main():
    HOST = ''
    PORT = 8000

    app_socket = socket.socket()
    app_socket.bind((HOST, PORT))
    app_socket.listen(5)

    while 1:
        conn, addr = app_socket.accept()
        print 'Connected by', addr
        t = threading.Thread(target=handle_connection, args=(conn,))

        print 'starting thread'
        t.start()

if __name__ == "__main__":
    main()
