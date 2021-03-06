#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
from zope.interface import implements
from twisted.cred import portal
import dictCredential
import mysqlCredential
from twisted.mail import imap4, maildir
from twisted.internet import defer
from twisted.enterprise import adbapi, util
import os, pickle, random, email
from cStringIO import StringIO
from imapMailsMysql import imapMailsMysql
import MySQLdb
 
class account(object):
    implements(imap4.IAccount)
    
    def __init__(self, coreMail):
        self.coreMail = coreMail
        Inbox = self.coreMail.getNamedBox("Inbox", create = True)

    def addMailbox(self, name, mbox=None):
        self.coreMail.getNamedBox(name, create = True)
        
    def create(self, name):
        return self.coreMail.getNamedBox(name, create = True)
        
    def select(self, name, rw=True):
        return self.coreMail.getNamedBox(name)
        
    def delete(self, name):
        pass
        
    def rename(self, oldname, newname):
        pass
        
    def isSubscribed(self, name):
        #raise NotImplementedError
        pass
        
    def subscribe(self, name):
        pass

    def unsubscribe(self, name):
        pass

    def listMailboxes(self, ref, wildcard):
        boxes = self.coreMail.allBoxes()
        for box in boxes:
            yield box, self.coreMail.getNamedBox(box, create=True)

class mailRealm(object):
    implements(portal.IRealm)
    avatarInterfaces = {
        imap4.IAccount: account
    }
    
    def __init__(self, coreMail):
        self.coreMail = coreMail
        
    #avatarId = le username du credentials
    def requestAvatar(self, avatarId, mind, *interfaces):
        if avatarId == None:
            raise KeyError("avatar id is None")
            
        for interface in interfaces:
            #si une des interfaces passée en parametre est dans la
            #liste des interfaces implémentatant Iaccount
            if self.avatarInterfaces.has_key(interface):
                self.coreMail.initMaildir(avatarId)
                
            #on récupere la classe implémentant l'interface
            execInterface = self.avatarInterfaces[interface]
            #on instancie la classe, avatar est: Inbox
            avatar = execInterface(self.coreMail)
            
            #on doit retourner un tuple:
            #(interface, avatarAspect, logout) donc:
            return defer.succeed((interface, avatar, lambda: None))
        #on arrive ici si aucunes classe n'implémente l'interface:
        raise KeyError("No classes implements the interface")

DRIVER = "MySQLdb"
PARAM = {
    'db': 'imap_db',
    'user': 'root',
    'passwd': 'password',
    }
def getPortal():
    con = MySQLdb.connect("localhost", "root", "password", "imap_db")
    coreMail = imapMailsMysql(con)

    realm = mailRealm(coreMail)
    myPortal = portal.Portal(realm)
       
    ###Mysql Credential Checking
    con = adbapi.ConnectionPool(DRIVER, **PARAM)
    checker = mysqlCredential.passwordCredentialChecker(con)
    
    myPortal.registerChecker(checker)
    return myPortal
