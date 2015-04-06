#!/usr/bin/env python
from twisted.internet import reactor # drives the whole process, accepting TCP connections and moving bytes
from twisted.internet import defer
from twisted.web import http
from twisted.internet import protocol

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
y_pos = 0
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
new_screen.addstr(0,0, 'Live Log')
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
        clients[http.Request.getClientIP(self)] = newcli
        clients[http.Request.getClientIP(self)].y_pos = y_pos
        y_pos += 1

        useragent = http.Request.getAllHeaders(self)['user-agent']
        # Print
        screen.addstr(clients[http.Request.getClientIP(self)].y_pos,0, "Client "+http.Request.getClientIP(self)+'. '+str(clients[http.Request.getClientIP(self)].connectionTime)+'. User-Agent: '+useragent)
        screen.refresh()


        while not http.Request.finished:
                self.setHeader('Connection', 'Keep-Alive')
                s = "A"*1024
                newcli.amountTransfered += len(s)
                # For some reason the connection is not stopped and continues to try to send data
                screen.addstr(clients[http.Request.getClientIP(self)].y_pos,130, "Transfered "+str(clients[http.Request.getClientIP(self)].amountTransfered/1024/1024.0)+' MB')
                screen.refresh()
                try:
                    self.write(s)
                    yield wait(0)
                except:
                    return

    def connectionLost(self,reason):
        global clients
        disconnect_time = datetime.datetime.now()
        #screen.addstr(clients[http.Request.getClientIP(self)].y_pos,140, "Duration "+str(disconnect_time - clients[http.Request.getClientIP(self)].connectionTime)+'. Total: '+str(clients[http.Request.getClientIP(self)].amountTransfered/1024/1024.0)+' MB')
        screen.addstr(clients[http.Request.getClientIP(self)].y_pos,160, "Duration "+str(disconnect_time - clients[http.Request.getClientIP(self)].connectionTime))
        screen.refresh()
        http.Request.notifyFinish(self)
        http.Request.finish(self)


class StreamProtocol(http.HTTPChannel):
    requestFactory = StreamHandler

class StreamFactory(http.HTTPFactory):
    protocol = StreamProtocol

reactor.listenTCP(8800, StreamFactory())
reactor.run()
