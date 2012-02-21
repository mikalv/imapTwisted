#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from twisted.mail import maildir, imap4
import os, pickle, random, email
from zope.interface import implements
from cStringIO import StringIO

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
        self.mailBox = self.coreMail.getMailBoxPlus(self.name)
        self.metadata = self.coreMail.getMetadata(self.name)
        self.listeners = []
        self.initMetadata()
        #self._assignUids()
            
    def initMetadata(self):
        #permet d'identifier de maniere unique un mail
        if not self.metadata.has_key("uids"):
            #une liste d'uid car il y a plusieurs mail dans la boite
            self.metadata["uids"] = {}
            
        #permet d'identifier de maniere unique la boite mail
        if not self.metadata.has_key("uidvalidity"):
            #génération de l'identifiant
            self.metadata["uidvalidity"] = random.randint(1000000, 9999999)
            
        #permet de disposer de plusieurs flag, comme a supprimé, non lu etc
        if not self.metadata.has_key("flags"):
            #un dict de flags
            self.metadata["flags"] = {}
        
        #permet de connaitre l'uid du prochain message pour l'incrémentation
        if not self.metadata.has_key("next"):
            self.metadata["next"] = 1

    def _assignUids(self):
        #self.coreMail.assignUids(self.mailBox, self.metadata)
        #self.saveMetadata(self.metadata, self.nomBoiteMail)
        pass

    def saveMetadata(self):
        self.coreMail.saveMetadata(self.metadata)
        
    def getUIDValidity(self):
        return self.metadata["uidvalidity"]
        
    def getUIDNext(self):
        return self.metadata["next"]
        
    def getUID(self, num):
        return self.metadata["uids"].get(self.name)[num]
        
    def getMessageCount(self):
        #on a surcharger MaildirMailbox
        return len(self.mailBox)
        
    def getRecentCount(self):
        def recent(criteria):
            uid = self.coreMail.getUidWithId(criteria)
            flags = self.coreMail.getFlagsWithUid(uid)
            
            if r"\Recent" in flags:
                return True
        return len(filter(recent, self.mailBox))
        
    def getUnseenCount(self):
        def unseen(where):
            nomMail = self.coreMail.getNomMailForFilter(where)
            uid = self.metadata["uids"].get(nomMail)
            flags = self.metadata["flags"].get(uid, [])
            if not r"\seen" in flags:
                return True
        return len(filter(unseen, self.mailBox))
        
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
        if flags == None:
            flags = []
        #return self.mailBox.appendMessage(message).addCallback(self._addSuccess, flags)
     
    def _addSuccess(self, _, flags):
        #self._assignUids()
        nomMail = self.coreMail.getNomLastMail(self.mailBox)
        uids = self.metadata["uids"][nomMail]
        self.metadata["flags"][uids] = flags
        self.saveMetadata()
        
    def expunge(self):
        def toDelete(where):
            nomMail = self.coreMail.getNomMailForFilter(where)
            uid = self.metadata["uids"].get(nomMail)
            flags = self.metadata["flags"].get(uid, [])
            if r"\Deleted" in flags:
                return where, uid
        if not self.isWriteable():
            raise imap4.ReadOnlyMailbox()
        else:
            deletedMessage = []
            for where, uid in filter(toDelete, self.mailBox):
                self.coreMail.delMessage(self.mailBox, where)
                deletedMessage.append(uid)
            return deletedMessage
        
    def getSeqWithUids(self, messageSet):
        if not messageSet.last:
            messageSet.last = len(self.mailBox)
        allUids = []
        for i in range(len(self.mailBox)):
            uid = self.metadata["uids"][self.name][i]
            allUids.append(uid)
        seq = {}
        for uid in messageSet:
            if uid in allUids:
                pos = allUids.index(uid)+1
                seq[pos] = self.mailBox[pos-1]
        return seq
        
    def getSeqsWithPos(self, messageSet):
        if not messageSet.last:
            messageSet.last = self.metadata['next']
        seq = {}
        for pos in messageSet:
            pos = str(pos)
            pos = int(pos)
            seq[pos] = self.mailBox[pos-1]
        return seq
        
    def fetch(self, messages, uid):
        if uid:
            sequence = self.getSeqWithUids(messages)
        else:
            sequence = self.getSeqsWithPos(messages)
        for idM, pos in sequence.items():
            pos = str(pos)
            pos = int(pos)
            uidMail = self.getUID(pos)
            flags = self.metadata["flags"].get(uidMail, [])
            mailMessage = self.coreMail.getMailMessage(idM, uidMail, flags)
            yield pos, mailMessage
        
        
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
                #Recupere le tableau de flag, et si il existe pas, le préparer a
                # en recevoir un
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
            r"\seen", r"\Answered", r"\Flagged", r"\Deleted", r"\Draft", r"\Recent"]
    def getHierarchicalDelimiter(self):
        return "."
    

