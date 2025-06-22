import sublime
import sublime_plugin
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import _thread
import threading

def MakeHandlerClass():
    class HandleRequests(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf8'))
                print("[Hook] Received JSON:")
                print(json.dumps(data, indent=2))
            except Exception as e:
                print("[Hook] Error parsing request:", e)

    return HandleRequests

class CompetitiveCompanionServer:
    def startServer():
        host = 'localhost'
        port = 12345
        HandlerClass = MakeHandlerClass()
        try:
            httpd = HTTPServer((host, port), HandlerClass)
            print("[Hook] Listening on {}:{} ...".format(host, port))
            httpd.serve_forever()
        except OSError as e:
            print("[Hook] Port {} in use or failed: {}".format(port, e))

def plugin_loaded():
    try:
        _thread.start_new_thread(
            CompetitiveCompanionServer.startServer,
            ()
        )
        print("[Hook] Auto-listening for Competitive Companion...")
    except Exception as e:
        print("[Hook] Auto-startup error:", e)
