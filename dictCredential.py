#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
from zope.interface import implements
from twisted.cred import checkers, credentials, error
from twisted.internet import defer

class passwordCredentialChecker(object):
    implements(checkers.ICredentialsChecker)
    # credentials.IUsernamePassword => pseudo + mot de passe clair
    # credentials.IUsernameHashedPassword => pseudo clair, pass hashé
    credentialInterfaces = (credentials.IUsernamePassword,
        credentials.IUsernameHashedPassword)
        
    def __init__(self, listPassword):
        self.listPassword = listPassword
        
    def requestAvatarId(self, credentials):
        #Récupération du username reçu
        username = credentials.username
        
        #on regarde dans le dict si l'utilisateur existe
        #on travaille en asynchrone.
        if self.listPassword.has_key(username):
            # si le username est présent:
            
            #on récup le mot de passe
            password = self.listPassword[username]
            resultat = defer.maybeDeferred(
                credentials.checkPassword, password)
            resultat.addCallback(self._checkPassword, username)
            return resultat
        else:
            # si le username est pas présent:
            defer.fail(error.UnauthorizedLogin("Bad username"))
            
    def _checkPassword(self, resultat, username):
        if resultat:
            #si ça correspond:
            return username
        else:
            #si ça correspond pas:
            raise error.UnauthorizedLogin("Bad password")
