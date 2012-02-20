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
        self._assignUids()
            
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
        self.coreMail.assignUids(self.mailBox, self.metadata)
        self.saveMetadata(self.metadata, self.nomBoiteMail)
        
    def saveMetadata(self):
        self.coreMail.saveMetadata(self.metadata)
        
    def getUIDValidity(self):
        return self.metadata["uidvalidity"]
        
    def getUIDNext(self):
        return self.metadata["next"]
        
    def getUID(self, num):
        nomMail = self.coreMail.getNomMailByPosition(self.mailBox, num)
        return self.metadata["uids"].get(nomMail)
        
    def getMessageCount(self):
        #on a surcharger MaildirMailbox
        return len(self.mailBox)
        
    def getRecentCount(self):
        def recent(criteria):
            nomMail = self.coreMail.getNomMailForFilter(criteria)
            uid = self.metadata["uids"].get(nomMail)
            flags = self.metadata["flags"].get(uid, [])
            
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
        return self.mailBox.appendMessage(message).addCallback(self._addSuccess, flags)
     
    def _addSuccess(self, _, flags):
        self._assignUids()
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
        for pathSelectedMail in self.mailBox:
            nomMail = os.path.basename(pathSelectedMail)
            uid = self.metadata["uids"][nomMail]
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
            seq[pos] = self.mailBox[pos-1]
        return seq
        
    def fetch(self, messages, uid):
        if uid:
            sequence = self.getSeqWithUids(messages)
        else:
            sequence = self.getSeqsWithPos(messages)
          
        for pos, nomMail in sequence.items():
            uidMail = self.getUID(pos)
            flags = self.metadata["flags"].get(uidMail, [])
            yield pos, MailMessage(file(nomMail).read(), uidMail, flags)
        
        
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
        self.saveMetadata()
        return seqFlag
        
    def getFlags(self):
        return [
            r"\seen", r"\Answered", r"\Flagged", r"\Deleted", r"\Draft", r"\Recent"]
    def getHierarchicalDelimiter(self):
        return "."
    

class MailMessagePart(object):
    implements(imap4.IMessagePart)
    
    def __init__(self, mimeMessage):
        self.mimeMessage = mimeMessage
        self.mail = str(self.mimeMessage)
    
    def getHeaders(self, negate, *names):
        headers = {}
        
        #si pas de names, on met tout le header dans names
        if not names:
            names = self.mimeMessage.keys()
        if negate:
            for header in self.mimeMessage.keys():
                if header.upper() not in names:
                    headers[header.lower()] = self.mimeMessage.get(header, "")
        else:
            for name in names:
                headers[name] = self.mimeMessage.get(name, "")
                
        return headers
        
    def getBodyFile(self):
        body = str(self.mimeMessage.get_payload())
        return StringIO(body)
    
    def getSize(self):
        return len(self.mail)
    
    def isMultipart(self):
        return self.mimeMessage.is_multipart()
    
    def getSubPart(self, part):
        return MailMessagePart(self.mimeMessage.get_payload())
    
class MailMessage(MailMessagePart):
    implements(imap4.IMessage)
    
    def __init__(self, mail, uid, flags):
        self.mail = mail
        self.uid = uid
        self.flags = flags
        self.mimeMessage = email.message_from_string(self.mail)
    
    def getUID(self):
        return self.uid
    
    def getFlags(self):
        return self.flags
        
    def getInternalDate(self):
        return self.mimeMessage.get("Date", "")
       
