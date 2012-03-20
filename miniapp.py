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

class ResponseFunctionHolder(object):
    def __call__(self, status, headers):
        self.status = status
        self.headers = headers

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

    initialize()
    app = MeepExampleApp()
    response_fn_callable = ResponseFunctionHolder()
    appResponse = app(environ, response_fn_callable)
    response = []
    response.append('HTTP/1.0 ' + response_fn_callable.status)
    response.extend([x+': '+y for x,y in response_fn_callable.headers])
    response.append('Date: ' + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))
    response.append('Server: WSGIServer/0.1 Python/2.7')
    response.append('\r\n')
    response.extend(a for a in appResponse)

    return '\r\n'.join(response)

def main():

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

    response = process_request(fileText.lower().split('\r\n'))
    print response

if __name__ == "__main__":
    main()