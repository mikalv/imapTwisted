#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from twisted.mail import maildir, imap4
import os, pickle, random, email
from zope.interface import implements
from cStringIO import StringIO
from twisted.internet import defer

class imapMessages(object):
    """Class for messages in mailBoxes"""
    def __init__(self, coreMail):
        self.coreMail = coreMail
        
    def getMailBoxMessages(self, name):
        return IMAPMailbox(name, self.coreMail)

       
class IMAPMailbox(object):
    implements(imap4.IMailbox)
    
    def __init__(self, name, coreMail):
        self.name = name
        self.coreMail = coreMail
        self.listeners = []
    
    def getUIDValidity(self):
        return self.coreMail.getIdMailBox(self.name)
        
    def getUIDNext(self):
        pass
        
    def getUID(self, index):
        return self.coreMail.getIdMailMessage(self.name, index)
        
    def getMessageCount(self):
        return self.coreMail.getMessageCount(self.name)
        
    def getRecentCount(self):
        return self.coreMail.getRecentCount(self.name)       
 
    def getUnseenCount(self):
        return self.coreMail.getUnseenCount(self.name)
 
    def isWriteable(self):
        return True
        
    def destroy(self):
        pass
        
    def requestStatus(self, names):
        return imap4.statusRequestHelper(self, names)
        
    def addListener(self, listener):
        self.listeners.append(listener)
        
    def removeListener(self, listener):
        self.listeners.remove(listener)
        
    def addMessage(self, message, flags=None, date=None):
        pass
        
    def expunge(self):
        return self.coreMail.expunge(self.name)

    def getSequenceWithUids(self, messageSet):
        if not messageSet.last:
            messageSet.last = self.coreMail.getLastTuple(self.name) + 1
            print "messageLastID : "
            print messageSet.last

        sequence = {}
        for idMail in messageSet:
            idMail = int(str(idMail))
            pos = self.coreMail.getPosWithIdV(self.name, idMail)
            if pos:
                sequence[pos] = idMail
        return sequence
    
    def getSequenceWithPos(self, messageSet):
        if not messageSet.last:
            messageSet.last = self.coreMail.getLastPos(self.name) + 1
            print "messageLast POS: ;"
            print messageSet.last

        sequence = {}
        for pos in messageSet:
            pos = int(str(pos))
            idMail = self.coreMail.getIdWithPosV(self.name, pos)
            if idMail:
                sequence[pos] = idMail

        return sequence

        
    def fetch(self, messages, uid):
        if uid:
            sequence = self.getSequenceWithUids(messages)
        else:
            sequence = self.getSequenceWithPos(messages)
            
        for pos, idMail in sequence.items():
            pos = int(str(pos))
            idMail = int(str(idMail))
            flags = self.coreMail.getFlagsWithId(self.name, idMail)
            mailMessage = self.coreMail.getMailMessage(idMail, flags)
            yield pos, mailMessage
        
    def store(self, messages, flags, mode, uid):
        print "messages:"
        print messages
        print "flags:"
        print flags
        print "mode:"
        print mode
        print "uid:"
        print uid
        sequence = {}
        if uid:
            sequence = self.getSequenceWithUids(messages)
        else:
            sequence = self.getSequenceWithPos(messages)
        for pos, idMail in sequence.items():
            pos = int(str(pos))
            idMail = int(str(idMail))
            if mode == 0:
                self.coreMail.deleteFlags(self.name, self.idMail)
                for flag in flags:
                    self.coreMail.addFlag(self.idMail, flag)
            else:
                if mode == 1:
                    for flag in flags:
                        self.coreMail.addFlag(self.name, self.idMail, flag)
                elif mode == -1:
                    for flag in flags:
                        self.coreMail.deleteFlag(self.name, self.idMail, flag)
            seq[idMail] = []
            seq[idMail] = self.coreMail.getFlagsWithId(self.name, idMail)
        return seq
        
    def getFlags(self):
        return self.coreMail.getAllFlags()
        
    def getHierarchicalDelimiter(self):
        return "."
    

