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
        return self.coreMail.getUIDValidity(self.name)
        
    def getUIDNext(self):
        return self.coreMail.getUIDNext(self.name)
        
    def getUID(self, index):
        return self.coreMail.getUID(self.name, index)
        
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
            idMail = self.coreMail.getLastTuple(self.name)
            messageSet.last = self.coreMail.getUidWithId(idMail)
        sequence = {}
        print "messageSet:"
        print messageSet
        for uid in messageSet:
            uid = str(uid)
            uid = int(uid)
            idMail = self.coreMail.getIdWithUid(self.name, uid)
            if idMail:
                sequence[idMail] = uid
        return sequence

    def getSequenceWithPos(self, messageSet):
        if not messageSet.last:
            messageSet.last = self.coreMail.getMessageCount(self.name)
        sequence = {}
        for pos in messageSet:
            pos = str(pos)
            pos = int(pos)
            uid = self.coreMail.getUidWithPos(self.name, pos)
            if uid:
                idMail = self.coreMail.getIdWithUid(self.name, uid)
                sequence[idMail] = uid
        return sequence

    def fetch(self, messages, uid):
        if uid:
            sequence = self.getSequenceWithUids(messages)
        else:
            sequence = self.getSequenceWithPos(messages)
        print "Sequence:"
        print sequence
        for idMail, uid in sequence.items():
            flags = self.coreMail.getFlagsWithUid(self.name, uid)
            mailMessage = self.coreMail.getMailMessage(idMail, uid, flags)
            yield idMail, mailMessage
        
        
    def store(self, messages, flags, mode, uid):
        if uid:
            sequence = self.getSeqWithUids(messages)
        else:
            sequence = self.getSeqsWithPos(messages)
            
        seqFlag = {}
        for pos, nomMail in sequence.items():
            uidMail = self.getUID(pos)
            if(mode == 0):
                flagPresent = self.metadata["flags"][uidMail] = flags
            else:
                #Recupere le tableau de flag, et si il existe pas, le 
                # préparer à en recevoir un
                flagPresent = self.metadata["flags"].setdefault(uidMail, [])
                for flag in flags:
                    if mode == 1 and not flagPresent.count(flag):
                        #flagPresent a la meme adresse que:
                        # self.metadata["flags"][uidMail]
                        flagPresent.append(flag)
                    elif mode == -1 and flagPresent.count(flag):
                        flagPresent.remove(flag)
            seqFlag[pos] = flagPresent
        #self.saveMetadata()
        return seqFlag
        
    def getFlags(self):
        return [
            r"\seen", 
            r"\Answered", 
            r"\Flagged", 
            r"\Deleted", 
            r"\Draft", 
            r"\Recent"]
    def getHierarchicalDelimiter(self):
        return "."
    

