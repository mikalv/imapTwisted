#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
from twisted.enterprise import util
from zope.interface import implements
from twisted.cred import checkers, credentials, error
from twisted.internet import defer

#aaa
class passwordCredentialChecker(object):
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword, 
        credentials.IUsernameHashedPassword)
    
    def __init__(self, con):
        self.con = con
    
    def requestAvatarId(self, credentials):
        param = util.quote(credentials.username, "char")
        query = "SELECT username, password from imap_users where username = %s" % param
        results = self.con.runQuery(query)
        results.addCallback(self._gotResult, credentials)
        return results
            
    def _gotResult(self, results, credentials):
        if results:
            username, password = results[0]
            defered = defer.maybeDeferred(
                credentials.checkPassword, password)
            defered.addCallback(self._checkPassword, username)
            return defered
        else:
            defer.fail(error.UnauthorizedLogin("Bad username"))
            
    def _checkPassword(self, resultat, username):
        if resultat:
            #si ça correspond:
            return username
        else:
            #si ça correspond pas:
            raise error.UnauthorizedLogin("Bad password")
            
