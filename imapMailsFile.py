#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from twisted.mail import maildir, imap4
import os, pickle, random
from imapMessages import imapMessages
from zope.interface import implements

class imapMailsFile(object):
    """Class for mail Boxes"""
    def __init__(self, pathMailDir):
        #"/home/greenlamp/Maildir"
        self.pathMailDir = pathMailDir
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
        split = nameBox.split(".")
        
        if split[0].lower() == "inbox":
            split[0] = "Inbox"
        NamedBox = ".".join(split)
        
        if not self.mailBoxCache.has_key(NamedBox):
            #"/home/greenlamp/Maildir/greenlamp/Inbox"
            self.pathMailDirBox = os.path.join(self.pathMailDirAvatar, NamedBox)
            if not os.path.exists(self.pathMailDirBox):
                if create == True:
                    maildir.initializeMaildir(self.pathMailDirBox)
                else:
                    raise KeyError("No such Box")
            self.mailBoxCache[NamedBox] = self.specMessages.getMailBoxMessages(self.pathMailDirBox)
        return self.mailBoxCache[NamedBox]
        
    def allBoxes(self):
        for box in os.listdir(self.pathMailDirAvatar):
            print "box: %r" % box
            yield box
        
    def getMailBoxPlus(self, fullPath):
        return MaildirMailboxPlus(fullPath)
        
    def getMetadata(self, fullPath):
        self.pathMetadataFile = os.path.join(fullPath, "imap_metadata.pickle")
        metadata = {}
        if os.path.exists(self.pathMetadataFile):
            metadata = pickle.load(file(self.pathMetadataFile, "r+b"))
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
        
    def getMailMessage(fileMail, uidMail, flags):
        return MailMessage(fileMail, uidMail, flags)         
        
        
        
class MaildirMailboxPlus(maildir.MaildirMailbox):
    #add an iterator to the mailbox.
    def __iter__(self):
        return iter(self.list)
        
    def __len__(self):
        return len(self.list)
        
    def __getitem__(self, i):
        return self.list[i]
        
    def deleteMessage(self, name):
        position = self.list.index(name)
        os.remove(name)
        del(self.list[position])


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
