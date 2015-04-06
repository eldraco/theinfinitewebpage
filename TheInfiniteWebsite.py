#!/usr/bin/env python
from twisted.internet import reactor # drives the whole process, accepting TCP connections and moving bytes
from twisted.internet import defer
from twisted.web import http
from twisted.internet import protocol
from twisted.web.server import NOT_DONE_YET

import datetime
import curses

clients = {}

class cli():
    def __init__(self):
        self.connectionTime = -1
        self.disconnectionTime = -1
        self.amountTransfered = 0
        self.y_pos = -1

# Global pos
y_pos = 1
clients = {}

# Initialize the curses       
stdscr = curses.initscr()
curses.start_color()
curses.use_default_colors()
new_screen = stdscr
curses.init_pair(1, curses.COLOR_GREEN, -1)
curses.init_pair(2, curses.COLOR_RED, -1)
curses.init_pair(3, curses.COLOR_CYAN, -1)
curses.init_pair(4, curses.COLOR_WHITE, -1)
stdscr.bkgd(' ')
curses.noecho()
curses.cbreak()
new_screen.keypad(1)
curses.curs_set(0)
new_screen.addstr(0,0, 'The Infinite Web Page. Live Log of captured clients.')
new_screen.refresh()
screen = new_screen


#####################
def wait(seconds, result=None):
    """Returns a deferred that will be fired later"""
    d = defer.Deferred()
    reactor.callLater(seconds, d.callback, result)
    return d

class StreamHandler(http.Request):
    global y_pos
    global clients

    @defer.inlineCallbacks
    def process(self):
        global y_pos
        global clients
        newcli = cli()
        newcli.connectionTime = datetime.datetime.now()
        clients[self.client] = newcli
        clients[self.client].y_pos = y_pos
        y_pos += 1

        useragent = http.Request.getAllHeaders(self)['user-agent']
        # Print
        screen.addstr(clients[self.client].y_pos,0, "Client "+str(self.client.host)+':'+str(self.client.port)+'. '+str(clients[self.client].connectionTime)+' '+str(self.method)+' '+str(self.uri)+' UA: '+useragent)
        #screen.addstr(10,0,http.Request.uri)
        #screen.addstr(11,0,str(http.Request.path))
        #screen.addstr(12,0,str(http.Request.getAllHeaders(self)))
        #self.method
        #['__doc__', '__implemented__', '__init__', '__module__', '__providedBy__', '__provides__', '__repr__', '__setattr__', '_authorize', '_cleanup', '_disconnected', '_forceSSL', '_warnHeaders', 'a ddCookie', 'args', 'channel', 'chunked', 'client', 'clientproto', 'code', 'code_message', 'connectionLost', 'content', 'cookies', 'etag', 'finish', 'finished', 'getAllHeaders', 'getClient', 'g etClientIP', 'getCookie', 'getHeader', 'getHost', 'getPassword', 'getRequestHostname', 'getUser', 'gotLength', 'handleContentChunk', 'headers', 'host', 'isSecure', 'lastModified', 'method', 'n oLongerQueued', 'notifications', 'notifyFinish', 'parseCookies', 'path', 'process', 'producer', 'queued', 'received_cookies', 'received_headers', 'redirect', 'registerProducer', 'requestHeader s', 'requestReceived', 'responseHeaders', 'sentLength', 'setETag', 'setHeader', 'setHost', 'setLastModified', 'setResponseCode', 'startedWriting', 'transport', 'unregisterProducer', 'uri', 'wr ite']

        #screen.addstr(13,0,str(self.uri))
        screen.refresh()


        # For GET and POST it works fine
        if 'GET' in self.method or 'POST' in self.method:
            while not http.Request.finished:
                    self.setHeader('Connection', 'Keep-Alive')
                    s = "A"*1024
                    newcli.amountTransfered += len(s)
                    # For some reason the connection is not stopped and continues to try to send data
                    screen.addstr(clients[self.client].y_pos,180, "Data {:>5.3f} MB".format(clients[self.client].amountTransfered/1024/1024.0))
                    screen.refresh()
                    try:
                        self.write(s)
                        yield wait(0)
                    except:
                        return
        # For HEAD we should do something different because they don't wait for any data.
        elif 'HEAD' in self.method:
            self.setHeader('Connection', 'Keep-Alive')


    def connectionLost(self,reason):
        global clients
        disconnect_time = datetime.datetime.now()
        #screen.addstr(clients[http.Request.getClientIP(self)].y_pos,140, "Duration "+str(disconnect_time - clients[http.Request.getClientIP(self)].connectionTime)+'. Total: '+str(clients[http.Request.getClientIP(self)].amountTransfered/1024/1024.0)+' MB')
        try:
            screen.addstr(clients[self.client].y_pos,195, "Duration "+str(disconnect_time - clients[self.client].connectionTime))
            screen.refresh()
        except:
            print
            print 'The screen is to narrow!! Try decreasing the font size.'
        http.Request.notifyFinish(self)
        http.Request.finish(self)


class StreamProtocol(http.HTTPChannel):
    requestFactory = StreamHandler

class StreamFactory(http.HTTPFactory):
    protocol = StreamProtocol

reactor.listenTCP(8800, StreamFactory())
reactor.run()
