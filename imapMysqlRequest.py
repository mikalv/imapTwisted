#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
from twisted.enterprise import adbapi, util
from twisted.internet import defer
import sys, random

def isBoxExists(con, avatarId):     
    def gotResult(results):
        if results:
            return True
        else:
            return False   
             
    param = util.quote(avatarId, "char")
    query = "SELECT name from imap_mail_box where name_mail_box = %r" % avatarId
    results = self.con.runQuery(query)
    results.addCallback(gotResult)
    return results
        
def createBox(con, avatarId):
    def gotResult(results):
        if results:
            return results
        
    param = util.quote(avatarId, "char")
    query = "INSERT INTO imap_mail_box(name) VALUES(%s)" % (param)
    results = con.runOperation(query)
    results.addCallback(gotResult)
    
def getLastTuple(con, name):
    def gotResult(results):
        if results:
            return results
            
    query = """
        SELECT id_mail_message
        FROM imap_mail_message
        WHERE uid >= ALL(
            SELECT id_mail_message
            FROM imap_mail_message
            WHERE name_mail_box = %s
        )""" % name
    results = self.con.runQuery(query)
    results.addCallback(gotResult)
    return results
    
    
def getTupleMail(con, name, index):
    def gotResult(results):
        if results:
            return results
            
    index = index - 1
    namedBox = util.quote(con, name, "char")
    if index == -1:
        return getLastTuple(name)
    query = """
        SELECT id_mail_message
        FROM imap_mail_message
        WHERE name_mail_box = %s
        LIMIT %d, 1""" % (name, index)
    results = self.con.runQuery(query)
    results.addCallback(gotResult)
    return results
    
def nbTupleMail(con, name):
    def gotResult(results):
        return results
        
    namedBox = util.quote(namedBox, "char")
    query = """
        SELECT count(*) 
        FROM imap_mail_message 
        WHERE name_mail_box = %s
        """ % name
    results = self.con.runQuery(query)
    results.addCallback(gotResult)
    return results
    
def delTupleMail(con, name, id_mail):
    def gotDeleted(results):
        if results:
            return results
            
    def gotResultSelect(results):
        if results:
            query = """
                UPDATE imap_mail_message
                SET deleted = 1
                WHERE id = %d
                """ % results
        results = self.con.runQuery(query)
        results.addCallback(gotDeleted, namedBox)
        return results
        
    namedBox = util.quote(namedBox, "char")
    query = """
        SELECT id_mail_message
        FROM imap_mail_message
        WHERE name_mail_box = %s
        AND id_mail_message = %d
        """ % (namedBox, id_mail)
    results = self.con.runQuery(query)
    results.addCallback(gotResultSelect)
    return results

def loadMetadata(con, name):
	def gotResults3(results, name, metadata, uid):
		if results:
			metadata["flags"][uid] = []
			flags = results[0]
			for flag in flags:
				metadata["flags"][uid].append(name)
			return metadata
		else:
		    return metadata

	def gotResults2(results, name, metadata):
		if results:
			metadata["uids"][name] = []
			uids = results[0]
			for uid in uids:
				metadata["uids"][name].append(uid)
				query = """
					SELECT name
					FROM imap_flags
					WHERE id_flag = (
						SELECT id_flag
						FROM imap_meta_flags
						WHERE uid = %d
					)""" % uid

				results = con.runQuery(query)
				results.addCallback(gotResults3, name, metadata, uid)
				return results

	def gotResults1(results, name):
		if results:
			uidValidity, uidNext = results[0]
			print "uidValidity: %s" % (uidValidity)
			metadata = {}
			metadata["uid_validity"] = uidValidity
			metadata["uid_next"] = uidNext
			metadata["uids"] = {}
			metadata["flags"] = {}
			query = """
				SELECT uid
				FROM imap_mail_message
				WHERE name_mail_box = %s
				""" % name

			results = self.con.runQuery(query)
			results.addCallback(gotResult2, name, metadata)
			return results

	name = util.quote(name, "char")
	query = """
		SELECT uid_validity, uid_next
		FROM imap_mail_box
		WHERE name_mail_box = %s
		""" % name

	results = con.runQuery(query)
	results.addCallback(gotResults1, name)
	return results











