#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from twisted.mail import maildir, imap4
import os, pickle, random
from imapMessages import imapMessages
from zope.interface import implements
from imapMysqlRequest import *

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
        self.nameBox = nameBox
        if nameBox.lower() == "inbox":
            nameBox = "Inbox"
        
        if not self.mailBoxCache.has_key(nameBox):
            createBox(self.con, nameBox)
            self.mailBoxCache[nameBox] = self.specMessages.getMailBoxMessages(self.nameBox)
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
        
        
        
        
        
class MaildirMailboxPlus(object):
    #add an iterator to the mailbox.
    def __init__(self, con, name):
        self.con = con
        self.name = name
        self.i = 0
        
    def __iter__(self):
        return self.generator()
            
    def generator(self):
        value = getTupleMail(self.con, self.name, self.i)
        while value:
            yield value
            self.i += 1
            value = getTupleMail(self.con, self.name, self.i)
        raise StopIteration
        
    def __len__(self):
        return nbTupleMail(self.con, self.name)
        
    def __getitem__(self, index):
        return getTupleMail(self.con, name, index)
        
    def deleteMessage(self, id_mail):
        delTupleMail(self.con, self.name, id_mail)
