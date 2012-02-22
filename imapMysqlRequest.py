#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
from twisted.enterprise import adbapi, util
from twisted.internet import defer
import sys, random
from email.mime.multipart import MIMEMultipart
from email.parser import Parser
from email.mime.text import MIMEText

def isBoxExists(con, avatarId):     
    def gotResult(results):
        if results:
            return True
        else:
            return False   
             
    param = util.quote(avatarId, "char")
    query = """
        SELECT name 
        FROM imap_mail_box 
        where name_mail_box = %r
        """ % avatarId
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
    nbTuple = nbTupleMail(con, name)
    print "nbTuple: %d" % nbTuple
    print "name: %s" % name
    if nbTuple == 1:
        query = """
            SELECT id_mail_message
            FROM imap_mail_message
            WHERE uid =(
                SELECT id_mail_message
                FROM imap_mail_message
                WHERE name_mail_box = %s
            )
            """ % name
    else:
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
    results = str(results[0])
    results = int(results)
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
    results = str(results[0])
    results = int(results)
    return results

def nbTupleMail(con, name):
    name = util.quote(name, "char")
    query = """
        SELECT count(*) 
        FROM imap_mail_message 
        WHERE name_mail_box = %s
        """ % name
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

        
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
    results = str(results[0])
    results = int(results)
    query = """
        UPDATE imap_mail_message
        SET deleted = 1
        WHERE id_mail_message = %d
        """ % results
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
    if results:
        uidValidity = int(str(results[0]))
        uidNext = int(str(results[1]))
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
        results2 = cursor.fetchall()
        namePar = name[1:-1]
        metadata["uids"][namePar] = []
        for uid in results2:
            uid = str(uid[0])
            uid = int(uid)
            metadata["uids"][namePar].append(uid)
            query = """
                SELECT name
                FROM imap_flags
                WHERE id_flag = (
                    SELECT id_flag
                    FROM imap_meta_flags
                    WHERE uid = %d
                )""" % uid
            cursor.execute(query)
            results3 = cursor.fetchall()
            metadata["flags"][uid] = []
            for flag in results3:
                flag = "".join(flag)
                metadata["flags"][uid].append(flag)

    return metadata

def getNameAllBoxes(con):
   listNameBoxes = []

   query = """
    SELECT name_mail_box
    FROM imap_mail_box
    """
   cursor = con.cursor()
   cursor.execute(query)
   results = cursor.fetchall()
   for name in results:
        name = "".join(name)
        listNameBoxes.append(name)

   return listNameBoxes


def getMessageAsMail(con, idMail):
    query = """
        SELECT *
        FROM imap_mail_message
        WHERE id_mail_message = %d
        """ % idMail

    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    #mail = MIMEMultipart('related')
    res = {}

    res["from"] = results[1]
    res["to"] = results[2]
    res["subject"] = results[3]
    res["date"] = results[4]
    res["contentType"] = results[5]
    res["content"] = results[6]

    mail = MIMEText(res["content"], "plain")

    mail["To"] = res["to"]
    mail["From"] = res["from"]
    mail["Subject"] = res["subject"]
    mail["Date"] = res["date"]

    #body = MIMEText(res["content"], 'plain')

    #mail.attach(body)
    return mail

def getUidWithId(con, idMail):
    query = """
        SELECT uid
        FROM imap_mail_message
        WHERE id_mail_message = %d
        """ % idMail
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

def getIdWithUid(con, name, uid):
    print "name: %r, uid: %r" % (name, uid)
    name = util.quote(name, "char")
    query = """
        SELECT uid
        FROM imap_mail_message
        WHERE uid IN(
            SELECT uid
            FROM imap_meta_uids
            WHERE uid_validity =(
                SELECT uid_validity
                FROM imap_mail_box
                WHERE name_mail_box = %s
                )
            )
        AND uid = %d
        """ % (name, uid)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    if results:
        results = str(results[0])
        results = int(results)
    return results

def getFlagsWithUid(con, name, uid):
    name = util.quote(name, "char")
    query = """
        SELECT name
        FROM imap_flags
        WHERE id_flag IN(
            SELECT id_flag
            FROM imap_meta_flags
            WHERE uid IN(
                SELECT uid
                FROM imap_meta_uids
                WHERE uid_validity=(
                    SELECT uid_validity
                    FROM imap_mail_box
                    WHERE name_mail_box = %s
                )
                AND uid = %d
            )
        )
        """ % (name, uid)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    retour = []
    for flag in results:
        flag = "".join(flag)
        retour.append(flag)
    return retour

def getUIDValidity(con, name):
    name = util.quote(name, "char")
    query = """
        SELECT uid_validity
        FROM imap_mail_box
        where name_mail_box = %s
        """ % name
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

def getUIDNext(con, name):
    name = util.quote(name, "char")
    query = """
        SELECT uid_next
        FROM imap_mail_box
        where name_mail_box = %s
        """ % name
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

def getUidValidityWithName(con, name):
    name = util.quote(name, "char")
    query = """
        SELECT uid_validity
        FROM imap_mail_box
        WHERE name_mail_box = %s
        """ % name
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

def getUIDlast(con, name):
    idMail = getLastTuple(con, name)
    uid = getUidWithId(con, idMail)
    uid = str(uid)
    uid = int(uid)
    return uid

def getUID(con, name, index):
    index -= 1
    if index == -1:
        return getUIDlast(con, name)
    else:
        name = util.quote(name, "char")
        query = """
            SELECT uid
            FROM imap_mail_message
            WHERE uid in(
                SELECT uid
                FROM imap_meta_uids
                WHERE uid_validity =(
                    SELECT uid_validity
                    FROM imap_mail_box
                    WHERE name_mail_box = %s
                )
            )
            LIMIT %d,1
            """ % (name, index)
        cursor = con.cursor()
        cursor.execute(query)
        results = cursor.fetchone()
        results = str(results[0])
        results = int(results)
        return results

def nbTupleFilter(con, name, flag=None):
    if flag == None:
        return 0
    else:
        #recup uidvalidity avec le nom, recup uid avec uidvalidity, 
        #recup idflag avec flag, compter nbTuple dans metaflags avec uid et idflag
        flag = util.quote(flag, "char")
        name = util.quote(name, "char")
        query = """
            SELECT count(*)
            FROM imap_meta_flags
            WHERE uid IN(
                SELECT uid
                FROM imap_meta_uids
                WHERE uid_validity =(
                    SELECT uid_validity
                    FROM imap_mail_box
                    WHERE name_mail_box = %s
                )
            )
            AND id_flag =(
                SELECT id_flag
                FROM imap_flags
                WHERE name = %s
            )
            """ % (name, flag)
        cursor = con.cursor()
        cursor.execute(query)
        results = cursor.fetchone()
        results = str(results[0])
        results = int(results)
        return results
             
def getPosWithId(con, idMail):
    return 1











