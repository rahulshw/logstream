import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.ioloop import IOLoop
import tornado.web
import tornado.gen
import tornado.log
import socket
import os
import uuid
from helpers import seek2

LOGDIR = os.environ.get('LOGDIR', '/var/log')  # directory of logfile
LOGBUFFER = int(os.environ.get('LOGBUFFER', 5))  # application will wait these many seconds let the new accumulate before sending it forward
PINGINTERVAL = int(os.environ.get('PINGINTERVAL', 5))  # websocket ping interval in second
PINGTIMEOUT = int(os.environ.get('PINGTIMEOUT', 10))  # websocket timeout duration in second
PORT = int(os.environ.get('PORT', 8888))  # webserver port


def read_and_send_file(request, filename, nlines):
    """
    emulates tail -f sending the content through websockets.
    :param request: WebsocketHandler object
    :param filename: name of file to be opened
    :param nlines: number of lines to be read from the end
    """
    try:
        f = open(os.path.join(LOGDIR, filename), encoding='utf-8')
    except FileNotFoundError as e:
        request.logger.error('Error occurred while opening file for connection:%s, reason:%s' % (request.id, e))
        request.close(code=400, reason=str(e))
    else:
        f = seek2(f, nlines)
        while True:
            try:
                content = f.read()
                if content:
                    request.write_message(content)
            except tornado.websocket.WebSocketClosedError as e:
                request.logger.error('Error occurred while sending data for connection:%s, reason: %s' % (request.id, e))
                request.close(code=400, reason=str(e))
                f.close()
            except ValueError as e:
                request.logger.error('Error occurred while reading file for connection:%s, reason: %s' %(request.id, e))
                raise e
            tornado.gen.sleep(LOGBUFFER)


class WSHandler(tornado.websocket.WebSocketHandler):
    """ Handler for websocket connection """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = tornado.log.app_log
        self.logger.setLevel('INFO')
        self.id = uuid.uuid4()
        self.nlines = 0
        self.filename = ''

    def open(self):
        self.nlines = int(self.get_query_argument('l'))
        self.filename = self.get_query_argument('f')
        self.logger.info('new connection: %s, from: %s' % (self.id, self.request.remote_ip))
        #read_and_send_file(self, self.filename, self.nlines)

    def on_message(self, message):
        print('message: %s'%message)
        if message == 'start_sending':
            read_and_send_file(self, self.filename, self.nlines)

    def on_close(self):
        self.logger.info('connection:%s closed' % self.id)

    def check_origin(self, origin):
        return True


class TailHandler(tornado.web.RequestHandler):
    """ Handler for HTTP connection """

    def get(self):
        """ Serves base HTML page with javascript code for websocket """
        nlines = int(self.get_query_argument('l'))
        filename = self.get_query_argument('f')
        self.render('tail.html', filename=filename, nlines=nlines)


application = tornado.web.Application(
    [
        (r'/ws', WSHandler),
        (r'/tail', TailHandler)
    ],
    static_path=os.path.join(os.path.dirname(__file__), 'static'),
    template_path=os.path.join(os.path.dirname(__file__), 'static'),
    websocket_ping_interval=PINGINTERVAL,
    websocket_ping_timeout=PINGTIMEOUT
)

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT)
    http_server.start(num_processes=1, max_restarts=1)
    print('server started')
    IOLoop.current().start()

