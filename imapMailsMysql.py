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
        #on regarde si le dossier existe:
        #"/home/greenlamp/Maildir/greenlamp"
        self.pathMailDirAvatar = os.path.join(self.pathMailDir, avatarId)
        if not os.path.exists(self.pathMailDirAvatar):
            #on crée le dossier si il existe pas.
            os.mkdir(self.pathMailDirAvatar)
        
    def getNamedBox(self, nameBox, create = False):
        if nameBox.lower() == "inbox":
			nameBox = "Inbox"
        
        if not self.mailBoxCache.has_key(NamedBox):
            createBox(self.con, nameBox)
            self.mailBoxCache[NamedBox] = self.specMessages.getMailBoxMessages(self.pathMailDirBox)
        return self.mailBoxCache[NamedBox]
        
    def allBoxes(self):
        for box in os.listdir(self.pathMailDirAvatar):
            print "box: %r" % box
            yield box
        
    def getMailBoxPlus(self, name):
        return MaildirMailboxPlus(self.con, name)
        
    def getMetadata(self, name):
		metadata = loadMetadata(self.con, name)
        return metadata
        
    def getNomMail(self, mailBox):
        for pathSelectedMail in mailBox:
            nomMail = os.path.basename(pathSelectedMail)
            yield nomMail
            
    def saveMetadata(self, metadata):
        pickle.dump(metadata, file(self.pathMetadataFile, "w+b"))
        
    def getNomMailByPosition(self, mailBox, position):
        nomMail = os.path.basename(mailBox[position-1])
        return nomMail
        
    def getNomMailForFilter(self, pathSelectedMail):
        nomMail = os.path.basename(pathSelectedMail)
        return nomMail
        
    def getNomLastMail(self, mailBox):
        nomMail = os.path.basename(mailBox[-1])
        return nomMail
    
    def delMessage(self, mailBox):
            mailbox.deleteMessage(pathSelectedMail)
        
        
        
        
        
class MaildirMailboxPlus(object):
    #add an iterator to the mailbox.
    def __init(self, con, name):
        self.con = con
        self.name = name
        self.i = 0
        
    def __iter__(self):
        return self.generator()
            
    def generator(self):
        value = getTupleMail(self.con, self.name, self.i)
        while value = getTupleMail(self.con, self.name, self.i):
            yield value
            self.i += 1
            value = getTupleMail(self.con, self.name, self.i)
        while(value)
        raise StopIteration
        
    def __len__(self):
        return nbTupleMail(self.con, self.name)
        
    def __getitem__(self, index):
        return getTupleMail(self.con, name, index)
        
    def deleteMessage(self, id_mail):
        delTupleMail(self.con, self.name, id_mail)
