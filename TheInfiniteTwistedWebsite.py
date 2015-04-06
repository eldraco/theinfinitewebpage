#!/usr/bin/env python

from twisted.web.server import Site # An IProtocolFactory wich glues a listening server port to the HTTPChannel. A web site, manage log, resources and sessions
from twisted.internet import reactor # drives the whole process, accepting TCP connections and moving bytes
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
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
        toTransfer = 'A'*1024*1024*1024
        newcli.amountTransfered = len(toTransfer)
        # Store the cli
        self.clients[request.client] = newcli
        print 'Client connected: {} on {}'.format(request.client, self.clients[request.client].connectionTime)
        # Write some data
        request.write(toTransfer)
        return NOT_DONE_YET
    


resource = Infinite()
factory = Site(resource) # Bind them to the site
reactor.listenTCP(8000, factory) # Listen in this port
reactor.run()

