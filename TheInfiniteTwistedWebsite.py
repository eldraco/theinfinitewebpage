#!/usr/bin/env python

from twisted.web.server import Site # An IProtocolFactory wich glues a listening server port to the HTTPChannel. A web site, manage log, resources and sessions
from twisted.internet import reactor # drives the whole process, accepting TCP connections and moving bytes
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import defer
from twisted.web import http
from twisted.internet import protocol

import datetime



class Infinite(Resource):
    def __init__(self):
        self.clients = {}

    class cli():
        def __init__(self):
            self.connectionTime = -1
            self.disconnectionTime = -1
            self.amountTransfered = -1

    isLeaf = True


    def _responseFailed(self, err, request):
        disconnect_time = datetime.datetime.now()
        print 'Client disconnected: {}. Duration: {}. Transfered: {} MB'.format(request.client, disconnect_time - self.clients[request.client].connectionTime, self.clients[request.client].amountTransfered/1024/1024.0)

    def render_GET(self, request):
        # Call back for when the client disconnects
        request.notifyFinish().addErrback(self._responseFailed, request)
        # New cli object
        newcli = self.cli()
        newcli.connectionTime = datetime.datetime.now()
        toTransfer = 'A'*1024
        newcli.amountTransfered = len(toTransfer)
        # Store the cli
        self.clients[request.client] = newcli
        print 'Client connected: {} on {}'.format(request.client, self.clients[request.client].connectionTime)
        # Write some data
        for i in range(0,1048576):
            request.write(toTransfer)
        return NOT_DONE_YET
    


#resource = Infinite()
#factory = Site(resource) # Bind them to the site
#reactor.listenTCP(8000, factory) # Listen in this port
#reactor.run()

clients = {}

class cli():
    def __init__(self):
        self.connectionTime = -1
        self.disconnectionTime = -1
        self.amountTransfered = 0

#####################
def wait(seconds, result=None):
    """Returns a deferred that will be fired later"""
    d = defer.Deferred()
    reactor.callLater(seconds, d.callback, result)
    return d

class StreamHandler(http.Request):

    @defer.inlineCallbacks
    def process(self):
        newcli = cli()
        newcli.connectionTime = datetime.datetime.now()
        clients[http.Request.getClientIP(self)] = newcli
        #print dir(http.Request)
        useragent = http.Request.getAllHeaders(self)['user-agent']
        print 'Client connected: {} on {}. User-Agent: {}'.format(http.Request.getClientIP(self), clients[http.Request.getClientIP(self)].connectionTime, useragent)
        while True:
            self.setHeader('Connection', 'Keep-Alive')
            self.setHeader('Content-Type', "multipart/x-mixed-replace")
            self.write("Content-Type: text/html\n")
            s = "A"*1024
            newcli.amountTransfered += len(s)
            self.write(s)
            yield wait(0)

    def connectionLost(self,reason):
        disconnect_time = datetime.datetime.now()
        print 'Client disconnected: {}. Duration: {}. Transfered: {:.2f} MB'.format(http.Request.getClientIP(self), disconnect_time - clients[http.Request.getClientIP(self)].connectionTime, clients[http.Request.getClientIP(self)].amountTransfered/1024/1024.0)


class StreamProtocol(http.HTTPChannel):
    requestFactory = StreamHandler

class StreamFactory(http.HTTPFactory):
    protocol = StreamProtocol

reactor.listenTCP(8800, StreamFactory())
reactor.run()


