import sys
import time
from meep_example_app import MeepExampleApp, initialize

headers_to_environ = {
    'host' : 'HTTP_HOST',
    'connection' : 'HTTP_CONNECTION',
    'user-agent' : 'HTTP_USER_AGENT',
    'accept' : 'HTTP_ACCEPT',
    'referrer': 'HTTP_REFERRER',
    'accept-encoding': 'HTTP_ACCEPT_ENCODING',
    'accept-language': 'HTTP_ACCEPT_LANGUAGE',
    'accept-charset': 'HTTP_ACCEPT_CHARSET',
    'cookie': 'HTTP_COOKIE'
}
def process_request(request):
    environ = {}
    for line in request:
        line = line.strip()
        #print (line,)
        if line == '':
            continue
        if line.startswith('get') or line.startswith('post'):
            line = line.split()
            environ['REQUEST_METHOD'] = line[0]
            environ['PATH_INFO'] = line[1]
        else:
            line = line.split(':', 1)
            try:
                environ[headers_to_environ[line[0]]] = line[1].strip()
            except KeyError:
                pass

    return environ

def start_response(status, headers):
    response=[]

    response.append('HTTP/1.0 ' + status)
    response.extend([x+': '+y for x,y in headers])
    response.append('Date: ' + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))
    response.append('Server: WSGIServer/0.1 Python/2.7')
    response.append('\r\n')
    #response.extend(body)
    print ('\r\n'.join(response))

def main():
    initialize()
    app = MeepExampleApp()

    if len(sys.argv) >= 2:
        file_name = sys.argv[1]
    else:
        file_name = raw_input("Please enter the request file's name: ")
        print
    f = open(file_name)

    fileText = ''
    for line in f.readlines():
        fileText+=line
    f.close()

    environ = process_request(fileText.lower().split('\r\n'))

    data = app(environ, start_response)

if __name__ == "__main__":
    main()