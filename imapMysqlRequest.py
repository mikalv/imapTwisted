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
    cursor = con.cursor()
    param = util.quote(avatarId, "char")
    uidValidity = random.randint(1000000, 9999999)
    query = """
        INSERT INTO imap_mail_box(
        name_mail_box, uid_validity, uid_next) 
        VALUES(%s, %d, 1)""" % (param, uidValidity)
    try:
        cursor.execute(query)
    except:
        print "box déja existante"



def getLastTuple(con, name):
    name = util.quote(name, "char")
    query = """
        SELECT id_mail_message
        FROM imap_mail_message
        WHERE uid >= ALL(
            SELECT id_mail_message
            FROM imap_mail_message
            WHERE name_mail_box = %s
        )""" % name
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    return results
    
def getTupleMail(con, name, index):
    index = index - 1
    name = util.quote(name, "char")
    if index == -1:
        return getLastTuple(con, name)
    query = """
        SELECT id_mail_message
        FROM imap_mail_message
        WHERE name_mail_box = %s
        LIMIT %d, 1""" % (name, index)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    return results

def nbTupleMail(con, name):
    name = util.quote(name, "char")
    query = """
        SELECT count(*) 
        FROM imap_mail_message 
        WHERE name_mail_box = %s
        """ % name
    print "query: %s" % query
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    return results[0]

        
def delTupleMail(con, name, id_mail):
    name = util.quote(name, "char")
    query = """
        SELECT id_mail_message
        FROM imap_mail_message
        WHERE name_mail_box = %s
        AND id_mail_message = %d
        """ % (name, id_mail)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    query = """
        UPDATE imap_mail_message
        SET deleted = 1
        WHERE id_mail_message = %d
        """ % results[0]
    cursor.execute(query)

def loadMetadata(con, name):
    name = util.quote(name, "char")
    query = """
        SELECT uid_validity, uid_next
        FROM imap_mail_box
        WHERE name_mail_box = %s
        """ % name

    metadata = {}   
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    uidValidity = results[0]
    uidNext = results[1]
    metadata["uid_validity"] = uidValidity
    metadata["uid_next"] = uidNext
    metadata["uids"] = {}
    metadata["flags"] = {}
    query = """
        SELECT uid
        FROM imap_mail_message
        WHERE name_mail_box = %s
        """ % name
    cursor.execute(query)
    results = cursor.fetchall()
    metadata["uids"][name] = []
    for uid in results:
        metadata["uids"][name].append(uid)
        query = """
            SELECT name
            FROM imap_flags
            WHERE id_flag = (
                SELECT id_flag
                FROM imap_meta_flags
                WHERE uid = %d
            )""" % uid
        cursor.execute(query)
        results2 = cursor.fetchall()
        metadata["flags"][uid] = []
        for flag in results2:
            metadata["flags"][uid].append(flag)

    return metadata

def getNameAllBoxes(con):
   listNameBoxes = []

   query = """
    SELECT name_mail_box
    FROM imap_mail_box
    """

   cursor.execute(query)
   results = cursos.fetchall()
   for name in results:
        listNameBoxes.append(name)

   return listNameBoxes










