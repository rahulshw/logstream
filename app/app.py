import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.ioloop import IOLoop
import tornado.web
import tornado.gen
import tornado.log
import os
import uuid
import re
from helpers import seek2 as seek

LOGDIR = os.environ.get('LOGDIR', '/var/log')  # directory of logfile
LOGBUFFER = int(os.environ.get('LOGBUFFER', 5))  # application will wait these many seconds let the new accumulate before sending it forward
PINGINTERVAL = int(os.environ.get('PINGINTERVAL', 5))  # websocket ping interval in second
PINGTIMEOUT = int(os.environ.get('PINGTIMEOUT', 10))  # websocket timeout duration in second
PORT = int(os.environ.get('PORT', 8888))  # webserver port


@tornado.gen.coroutine
def read_and_send_file(request, filepath, nlines):
    """
    emulates tail -f sending the content through websockets.
    :param request: WebsocketHandler object
    :param filename: name of file to be opened
    :param nlines: number of lines to be read from the end
    """
    try:
        f = open(filepath, encoding='utf-8')
    except FileNotFoundError as e:
        request.logger.error('Error occurred while opening file for connection:%s, reason:%s' % (request.id, e))
        request.close(code=400, reason='File not found')
    else:
        # initially seek to nth last line
        f = seek(f, nlines)
        while True:
            try:
                content = f.read()
                if content:
                    request.write_message(content)
            except tornado.websocket.WebSocketClosedError as e:
                request.logger.error('Error occurred while sending data for connection:%s, reason: %s'
                                     % (request.id, e))
                request.close(code=400, reason='Websocket closed')
                f.close()
                raise Exception('Discarding thread because websocket is closed for connection:%s' % request.id)
            # return the execution to event loop
            yield tornado.gen.sleep(LOGBUFFER)


class WSHandler(tornado.websocket.WebSocketHandler):
    """ Handler for websocket connection """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = tornado.log.app_log
        self.logger.setLevel('INFO')
        self.id = uuid.uuid4()  # handler object identifier
        self.nlines = 0
        self.filepath = ''
        self.already_sending = False

    def open(self):
        self.logger.info('new connection: %s, from: %s, at %s' % (self.id, self.request.remote_ip, self.request.uri))
        try:
            self.nlines = int(self.get_query_argument('l'))
            filename = self.get_query_argument('f')
            self.filepath = os.path.join(LOGDIR, filename)
        except ValueError:
            tornado.log.app_log.error('Invalid query arguments for connection: %s' % self.id)
            self.close(400, reason='Invalid query arguments')

    def on_message(self, message):
        if message == 'start_sending':
            if not self.already_sending:
                self.already_sending = True
                read_and_send_file(self, self.filepath, self.nlines)
            else:
                self.logger.warn('received message:%s, while file was being served already for connection: %s'
                                 % (message, self.id))
        else:
            self.logger.info('received invalid message: %s from connection:%s' % (message, self.id))

    def on_close(self):
        self.logger.info('connection:%s closed' % self.id)

    def check_origin(self, origin):
        return True


class TailHandler(tornado.web.RequestHandler):
    """ Handler for HTTP connection """

    def get(self):
        """ Serves base HTML page with javascript code for websocket """
        try:
            nlines = int(self.get_query_argument('l'))
            filename = self.get_query_argument('f')
        except ValueError:
            tornado.log.app_log.error('Invalid query arguments.')
            self.send_error(400)
        else:
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
    http_server.start(num_processes=1, max_restarts=3)
    print('server started at port: %s' % PORT)
    IOLoop.current().start()

