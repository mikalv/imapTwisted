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
        self.getNamedBox(avatarId, create = True)
        
    def getNamedBox(self, nameBox, create = False):
        nameBox = "".join(nameBox)
        if nameBox.lower() == "inbox":
            nameBox = self.avatarId
        elif nameBox.lower() == "trash":
            nameBox = "%s_%s" % (self.avatarId, "Trash")
        if not self.mailBoxCache.has_key(nameBox):
            createBox(self.con, nameBox)
            self.mailBoxCache[nameBox] = self.specMessages.getMailBoxMessages(nameBox)
        return self.mailBoxCache[nameBox]
        
    def allBoxes(self):
        boxes = getNameAllBoxes(self.con)
        return boxes

    def getMailBoxPlus(self, name):
        return MaildirMailboxPlus(self.con, name)
        
    def getMetadata(self, name):
        metadata = loadMetadata(self.con, name)    
        return metadata
        
    def getNomMail(self, mailBox):
        for mails in mailBox:
            yield mails[0]
            
    def saveMetadata(self, metadata):
        #pickle.dump(metadata, file(self.pathMetadataFile, "w+b"))
        pass

    def getNomMailByPosition(self, mailBox, position):
        nomMail = mailBox[position-1]
        nomMail = nomMail[0]
        return nomMail
        
    def getNomMailForFilter(self, pathSelectedMail):
        nomMail = self.getNomMail(pathSelectedMail)
        return nomMail
        
    def getNomLastMail(self, mailBox):
        nomMail = mailBox[-1]
        nomMail = nomMail[0]
        return nomMail
    
    def delMessage(self, mailBox, id_mail):
        mailbox.deleteMessage(id_mail)
                 
    def getMailMessage(self, idMail, uidMail, flags):
        mail = getMessageAsMail(self.con, idMail)
        return MailMessage(mail, uidMail, flags)         
        
    def getUidWithId(self, idMail):
        uid = getUidWithId(self.con, idMail)
        return uid
    
    def getIdWithUid(self, name, uid):
        idMail = getIdWithUid(self.con, name, uid)
        return idMail

    def getPosWithId(self, name, idMail):
        pos = getPosWithId(self.con, name, idMail)
        return pos
 
    def getFlagsWithUid(self, name, uid):
        flags = getFlagsWithUid(self.con, name, uid)
        return flags        
    
    def getUIDValidity(self, name):
        return getUIDValidity(self.con, name)

    def getUIDNext(self, name):
        return getUIDNext(self.con, name)    
       
    def getUidWithPos(self, name, index):
        return getUID(self.con, name, index)
    
    def getMessageCount(self, name):
        return nbTupleMail(self.con, name)

    def getRecentCount(self, name):
        return nbTupleFilter(self.con, name, r"\Recent")

    def getUnseenCount(self, name):
        nbTuple = nbTupleMail(self.con, name)
        nbSeen = nbTupleFilter(self.con, name, r"\Seen")
        unSeen = nbTuple - nbSeen
        return unSeen


class MailMessagePart(object):
    implements(imap4.IMessagePart)
    
    def __init__(self, mimeMessage):
        self.mimeMessage = mimeMessage
        self.mail = str(self.mimeMessage)
    
    def getHeaders(self, negate, *names):
        headers = {}
        result = {}
        headers["Date"] = self.mimeMessage.get("Date", "")
        headers["From"] = self.mimeMessage.get("From", "")
        headers["To"] = self.mimeMessage.get("To", "")
        headers["Subject"] = self.mimeMessage.get("Subject", "")
        if not names:
            names = headers
        if negate:
            for key in headers:
                if key.lower() not in names:
                   results[key.lower()] = headers[key]
        else:
            for name in names:
                results[name] = headers[name]

        return results 
        
    def getBodyFile(self):
        body = str(self.mimeMessage.get_payload()[0])
        return StringIO(body)
    
    def getSize(self):
        return len(self.mail)
    
    def isMultipart(self):
        return self.mimeMessage.is_multipart()
    
    def getSubPart(self, part):
        return MailMessagePart(self.mimeMessage.get_payload()[0])
    
class MailMessage(MailMessagePart):
    implements(imap4.IMessage)
    
    def __init__(self, mail, uid, flags):
        self.mail = str(mail)
        self.uid = uid
        self.flags = flags
        self.mimeMessage = mail
    
    def getUID(self):
        return self.uid
    
    def getFlags(self):
        return self.flags
        
    def getInternalDate(self):
        return self.mimeMessage.get("Date", "")
