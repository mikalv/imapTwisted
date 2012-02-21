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
        for box in boxes:
            yield box

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

    def getFlagsWithUid(self, uid):
        flags = getFlagsWithUid(self.con, uid)
        return flags        
        
        
class MaildirMailboxPlus(object):
    #add an iterator to the mailbox.
    def __init__(self, con, name):
        self.con = con
        self.name = name
        self.i = 0
        
    def __iter__(self):
        return self.generator()
            
    def generator(self):
        nb = nbTupleMail(self.con, self.name)
        while self.i <= nb :
            value = getTupleMail(self.con, self.name, self.i)
            yield value
            self.i += 1
        raise StopIteration
        
    def __len__(self):
        return nbTupleMail(self.con, self.name)
        
    def __getitem__(self, index):
        return getTupleMail(self.con, self.name, index)
        
    def deleteMessage(self, id_mail):
        delTupleMail(self.con, self.name, id_mail)


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
