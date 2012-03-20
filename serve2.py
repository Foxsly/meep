import socket
import traceback
from miniapp import process_request

def handle_connection(connection):
    endString = '\r\n\r\n'
    data = ''
    while 1:
        incomingData = connection.recv(1)
        data += incomingData
        if endString in data:
            break

    try:
        print(data,)
        response = process_request(data.lower().split('\r\n'))
        connection.sendall(response)
    except socket.error:
        print 'socket error'
        tb = traceback.format_exc()
        print tb
    finally:
        connection.close()

def main():
    HOST = ''
    PORT = 8000

    app_socket = socket.socket()
    app_socket.bind((HOST, PORT))
    app_socket.listen(5)

    while 1:
        conn, addr = app_socket.accept()
        print 'Connected by', addr
        handle_connection(conn)

if __name__ == "__main__":
    main()