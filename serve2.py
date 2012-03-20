import socket
import time
import traceback
from miniapp import process_request
from meep_example_app import MeepExampleApp, initialize

class serve2_util():
    def __init__(self, con, addr):
        self.con = con
        self.addr = addr

    def start_response(self, status, headers):
        self.status = status
        self.headers = headers

    def respond(self, body):
        response=[]

        response.append('HTTP/1.0 '+self.status)
        response.extend([x+': '+y for x,y in self.headers])
        response.append('Date: ' + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))
        response.append('Server: WSGIServer/0.1 Python/2.7')
        response.append('\r\n')
        response.extend(body)

        self.con.send('\r\n'.join(response))

def main():
    HOST = ''
    PORT = 8000

    endString = '\r\n\r\n'

    initialize()
    app = MeepExampleApp()


    app_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    app_socket.bind((HOST, PORT))
    app_socket.listen(1)

    data = ''
    conn, addr = app_socket.accept()
    print 'Connected by', addr

    while 1:
        incomingData = conn.recv(1)
        data += incomingData
        if endString in data:
            break

    try:
        print(data,)
        environ = process_request(data.lower().split('\r\n'))
        responder = serve2_util(conn, addr)
        responder.respond(app(environ, responder.start_response))
    except socket.error:
        print 'socket error'
        tb = traceback.format_exc()
        print tb
    finally:
        conn.close()

if __name__ == "__main__":
    main()