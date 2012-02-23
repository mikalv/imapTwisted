#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from twisted.mail import maildir, imap4
import os, pickle, random, email
from imapMessages import imapMessages
from zope.interface import implements
from imapMysqlRequest import *
from cStringIO import StringIO

class imapMailsMysql(object):
    """Class for mail Boxes"""
    def __init__(self, con):
        self.con = con 
        self.mailBoxCache = {}
        self.specMessages = imapMessages(self)
        
    def initMaildir(self, avatarId):
        self.avatarId = avatarId
        
    def getNamedBox(self, nameBox, create = False):
        if nameBox.lower() == "inbox":
            nameBox = "Inbox"
        if not self.mailBoxCache.has_key(nameBox):
            if create:
                if not isAlreadyExists(self.con, nameBox, self.avatarId):
                    createBox(self.con,self.avatarId, nameBox)
                self.mailBoxCache[nameBox] = self.specMessages.getMailBoxMessages(
                                                nameBox)  
            else:
                return None
        return self.mailBoxCache[nameBox]
        
    def allBoxes(self):
        boxes = getNameAllBoxes(self.con, self.avatarId)
        return boxes

    def getMailBoxPlus(self, name):
        return MaildirMailboxPlus(self.con, name, self.avatarId)
        
                 
    def getMailMessage(self, idMail, flags):
        mail = getMessageAsMail(self.con, idMail)
        return MailMessage(mail, idMail, flags)
        
    def getUidWithId(self, idMail):
        uid = getUidWithId(self.con, idMail)
        return uid
    
    def getIdWithUid(self, name, uid):
        idMail = getIdWithUid(self.con, name, self.avatarId, uid)
        return idMail

    def getPosWithId(self, name, idMail):
        pos = getPosWithId(self.con, name, self.avatarId, idMail)
        return pos
 
    def getFlagsWithId(self, name, idMail):
        flags = getFlagsWithId(self.con, name, self.avatarId, idMail)
        return flags
    
    def getIdMailBox(self, name):
        return getIdMailBox(self.con, name, self.avatarId)

    def getUIDNext(self, name):
        return getUIDNext(self.con, name, self.avatarId)    
       
    def getUidWithPos(self, name, index):
        return getUID(self.con, name, self.avatarId, index)
    
    def getMessageCount(self, name):
        return nbTupleMail(self.con, name, self.avatarId)

    def getRecentCount(self, name):
        return nbTupleFilter(self.con, name, self.avatarId, r"\Recent")

    def getUnseenCount(self, name):
        nbTuple = nbTupleMail(self.con, name, self.avatarId)
        nbSeen = nbTupleFilter(self.con, name, self.avatarId, r"\Seen")
        unSeen = nbTuple - nbSeen
        return unSeen
        
    def getLastTuple(self, name):
        return getLastTuple(self.con, name, self.avatarId)
        
    def expunge(self, name):
        pass
    
    def deleteFlags(self, name, idMail):
        deleteFlags(self.con, name, self.avatarId, idMail)

    def deleteFlag(self, name, idMail, flag):
        deleteFlag(self.con, name, self.avatarId, idMail, flag)

    def addFlag(self, idMail, flags):
        print "imapMailsMysql"
        addFlag(self.con, idMail, flags)

    def getAllFlags(self):
        return getAllFlags(self.con)

    def getIdWithPosV(self, name, pos):
        return getIdWithPosV(self.con, name, self.avatarId, pos)

    def getPosWithIdV(self, name, idMail):
        return getPosWithIdV(self.con, name, self.avatarId, idMail)
        
    def getLastPos(self, name):
        return getLastPos(self.con, name, self.avatarId)
        
class MaildirMailboxPlus(object):
    #add an iterator to the mailbox.
    def __init__(self, con, name, avatarId):
        self.con = con
        self.name = name
        self.avatarId = avatarId
        self.i = 0
        
    def __iter__(self):
        return self.generator()
            
    def generator(self):
        nb = nbTupleMail(self.con, self.name, self.avatarId)
        while self.i <= nb :
            value = getTupleMail(self.con, self.name, self.avatarId, self.i)
            yield value
            self.i += 1
        raise StopIteration
        
    def __len__(self):
        return nbTupleMail(self.con, self.name, self.avatarId)
        
    def __getitem__(self, index):
        return getTupleMail(self.con, self.name, self.avatarId, index)
        
    def deleteMessage(self, id_mail):
        delTupleMail(self.con, self.name, self.avatarId, id_mail)

class MailMessagePart(object):
    implements(imap4.IMessagePart)
    
    def __init__(self, mimeMessage):
        self.mimeMessage = mimeMessage
        self.mail = str(self.mimeMessage)
    
    def getHeaders(self, negate, *names):
        headers = {}
        results = {}
        headers["DATE"] = self.mimeMessage.get("Date", "")
        headers["FROM"] = self.mimeMessage.get("From", "")
        headers["TO"] = self.mimeMessage.get("To", "")
        headers["SUBJECT"] = self.mimeMessage.get("Subject", "")
        #headers["CC"] = None
        #headers["BCC"] = None
        #headers["MESSAGE-ID"] = None
        #headers["PRIORITY"] = None
        #headers["X-PRIORITY"] = None
        #headers["REFERENCES"] = None
        #headers["NEWSGROUPS"] = None
        #headers["IN-REPLY-TO"] = None
        #headers["CONTENT-TYPE"] = None
        if not names:
            names = headers
        if negate:
            for key in headers:
                if key.upper() not in names:
                   results[key.lower()] = headers[key]
        else:
            for name in names:
                if headers.has_key(name):
                    results[name] = headers[name]

        return results 
        
    def getBodyFile(self):
        body = str(self.mimeMessage.get_payload())
        return StringIO(body)
    
    def getSize(self):
        return len(self.mail)
    
    def isMultipart(self):
        return self.mimeMessage.is_multipart()
    
    def getSubPart(self, part):
        return MailMessagePart(self.mimeMessage.get_payload()[0])
    
class MailMessage(MailMessagePart):
    implements(imap4.IMessage)
    
    def __init__(self, mail, idMail, flags):
        self.mail = str(mail)
        self.idMail = idMail
        self.flags = flags
        self.mimeMessage = mail
    
    def getUID(self):
        return self.idMail
    
    def getFlags(self):
        return self.flags
        
    def getInternalDate(self):
        return self.mimeMessage.get("Date", "")
