import sys
from meep_example_app import MeepExampleApp, initialize
from wsgiref.simple_server import make_server

initialize()
app = MeepExampleApp()

PORT = 8000
if len(sys.argv) >= 2:
    PORT = int(sys.argv[2])

httpd = make_server('', PORT, app)
print "Serving HTTP on port %d..." % PORT

# Respond to requests until process is killed
httpd.serve_forever()

# Alternative: serve one request, then exit
httpd.handle_request()
