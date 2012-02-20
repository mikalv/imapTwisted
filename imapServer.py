#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
from twisted.internet import reactor, protocol
from twisted.mail import imap4
from twisted.cred import portal
from twisted.cred import error
from zope.interface import implements
from imapMailBoxes import getPortal


class imapServerProtocol(imap4.IMAP4Server):
    def lineReceived(self, line):
        imap4.IMAP4Server.lineReceived(self, line)
        print "reçu: %r" % line
    
    def sendLine(self, line):
        imap4.IMAP4Server.sendLine(self, line)
        print "envoyé: %r" % line

    def connectonLost(self, reason):
        pass
    
class imapServerFactory(protocol.Factory):
    protocol = imapServerProtocol
    portal = None
    
    def buildProtocol(self, addr):
        p = self.protocol()
        p.portal = self.portal
        p.factory = self
        return p

if __name__ == "__main__":
    myPortal = getPortal()
    
    factory = imapServerFactory()
    factory.portal = myPortal
    reactor.listenTCP(1234, factory)
    
    print "en attente"
    reactor.run()
