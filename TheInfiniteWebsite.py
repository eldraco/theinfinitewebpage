#!/usr/bin/env python
'''
This code is almost exactly the same as the chunked_server_test.py from josiahcarlson (https://gist.github.com/josiahcarlson/3250376). I only putted the infinite part.

Copyright March 25, 2015
Released into the public domain

This implements an Infinite chunked server using Python threads and the built-in
BaseHTTPServer module. Enable gzip compression at your own peril - web
browsers seem to have issues, though wget, curl, Python's urllib2, my own
async_http library, and other command-line tools have no problems.

The infinite idea is of Sebastian Garcia: eldraco@gmail.com

Usage: Just execute it and then download the web page with wget or something.

'''

import BaseHTTPServer
import gzip
import SocketServer
import time
import curses
#from signal import signal, SIGPIPE, SIG_DFL, SIG_IGN
#signal(SIGPIPE,SIG_DFL) 

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


class ChunkingHTTPServer(SocketServer.ThreadingMixIn,
                        BaseHTTPServer.HTTPServer):
    '''
    This is just a proof of concept server that uses threads. You can make it
    fork, maybe hack up a worker thread model, or even use multiprocessing.
    That's your business. But as-is, it works reasonably well for streaming
    chunked data from a server.
    '''
    daemon_threads = True

class ListBuffer(object):
    '''
    This little bit of code is meant to act as a buffer between the optional
    gzip writer and the actual outgoing socket - letting us properly construct
    the chunked output. It also lets us quickly and easily determine whether
    we need to flush gzip in the case where a user has specified
    'ALWAYS_SEND_SOME'.
    
    This offers a minimal interface necessary to back a writing gzip stream.
    '''

    __slots__ = 'buffer',
    def __init__(self):
        self.buffer = []

    def __nonzero__(self):
        return len(self.buffer)

    def write(self, data):
        if data:
            self.buffer.append(data)

    def flush(self):
        pass

    def getvalue(self):
        data = ''.join(self.buffer)
        self.buffer = []
        return data

class ChunkingRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    global y_pos
    '''
    Nothing is terribly magical about this code, the only thing that you need
    to really do is tell the client that you're going to be using a chunked
    transfer encoding.

    Gzip compression works partially. See the module notes for more
    information.
    '''
    ALWAYS_SEND_SOME = False
    ALLOW_GZIP = False
    protocol_version = 'HTTP/1.1'
    #(y_max, x_max) = self.screen.getmaxyx()

    def do_GET(self):
        global y_pos
        # Store the new client with its address
        clients[self.client_address] = y_pos

        screen.addstr(clients[self.client_address],0,self.path+": "+self.client_address[0])
        y_pos += 1
        screen.refresh()

        #ae = self.headers.get('accept-encoding') or ''

        # send some headers
        self.send_response(200)
        self.send_header('Transfer-Encoding', 'chunked')
        self.send_header('Content-type', 'text/plain')


        self.end_headers()

        def write_chunk():
            tosend = '%X\r\n%s\r\n'%(len(chunk), chunk)
            self.wfile.write(tosend)

        # get some chunks
        for chunk in chunk_generator(self.client_address):
            if not chunk:
                continue

            write_chunk()

        # no more chunks!

        # send the chunked trailer
        self.wfile.write('0\r\n\r\n')

def chunk_generator(client):
    global clients
    import datetime
    # generate some chunks
    #for i in xrange(10):
    amount = 0
    while True:
        i = "<html>"
        i += "TheInfiniteWebsite" * 20000
        amount += len(i)
        time.sleep(.1)
        try:
            yield "%s\r\n"%i
            screen.addstr(clients[client],80,"Amount sent: "+str(amount/1024/1024)+" MB")
            screen.refresh()
        except:
            screen.addstr(clients[client],110,"Ended: "+str(datetime.datetime.now()))
            screen.refresh()

if __name__ == '__main__':
    server = ChunkingHTTPServer( ('0.0.0.0', 8080), ChunkingRequestHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
