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
        
def createBox(con, avatarId, name):
    cursor = con.cursor()
    avatarId = util.quote(avatarId, "char")
    name = util.quote(name, "char")
    uidValidity = random.randint(1000000, 9999999)
    query = """
        INSERT INTO imap_mail_box(
        username, name_mail_box, uid_validity, uid_next) 
        VALUES(%s, %s, %d, 1)""" % (avatarId, name, uidValidity)
    try:
        cursor.execute(query)
    except:
        print "box déja existante"



def getLastTuple(con, name, avatarId):
    nbTuple = nbTupleMail(con, name, avatarId)
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    if nbTuple == 1:
        query = """
            SELECT id_mail_message
            FROM imap_mail_message
            WHERE uid =(
                SELECT id_mail_message
                FROM imap_mail_message
                WHERE uid IN(
                    SELECT uid
                    FROM imap_meta_uids
                    WHERE uid_validity =(
                        SELECT uid_validity 
                        FROM imap_mail_box
                        WHERE name_mail_box = %s
                        AND username = %s
                    )
               )
            )
            """ % (name, avatarId)
    else:
        query = """
            SELECT id_mail_message
            FROM imap_mail_message
            WHERE uid >= ALL(
                SELECT id_mail_message
                FROM imap_mail_message
                WHERE uid IN(
                    SELECT uid
                    FROM imap_meta_uids
                    WHERE uid_validity =(
                        SELECT uid_validity
                        FROM imap_mail_box
                        WHERE name_mail_box = %s
                        AND username = %s
                    )
               )
            )
            """ % (name, avatarId)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    if results:
        results = str(results[0])
        results = int(results)
    return results
    
def getTupleMail(con, name, avatarId, index):
    index = index - 1
    if index == -1:
        return getLastTuple(con, name, avatarId)
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    query = """
        SELECT id_mail_message
        FROM imap_mail_message
        WHERE uid IN(
            SELECT uid
            FROM imap_meta_uids
            WHERE uid_validity =(
                SELECT uid_validity
                FROM imap_mail_box
                WHERE name_mail_box = %s
                AND username = %s
            )
        )
        LIMIT %d, 1""" % (name, avatarId, index)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

def nbTupleMail(con, name, avatarId):
    print "nbTupleMail"
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    print "name: %s, avatarId: %s" % (name, avatarId)
    query = """
        SELECT count(uid)
        FROM imap_meta_uids
        WHERE uid_validity =(
            SELECT uid_validity
            FROM imap_mail_box
            WHERE name_mail_box = %s
            AND username = %s
        )
        """ % (name, avatarId)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

        
def delTupleMail(con, name, avatarId, id_mail):
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    query = """
        SELECT id_mail_message
        FROM imap_mail_message
        WHERE uid IN(
            SELECT uid
            FROM imap_meta_uids
            WHERE uid_validity =(
                SELECT uid_validity
                FROM imap_mail_box
                WHERE name_mail_box = %s
                AND username = %s
            )
        )
        AND id_mail_message = %d
        """ % (name, avatarId, id_mail)
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

def getNameAllBoxes(con, avatarId):
    listNameBoxes = []
    avatarId = util.quote(avatarId, "char")
    query = """
        SELECT name_mail_box
        FROM imap_mail_box
        WHERE username = %s
        """ % avatarId
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

def getIdWithUid(con, name, avatarId, uid):
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    print "uid: %r, name: %r, avatarId: %r" % (uid, name, avatarId)
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
                AND username = %s
                )
            )
        AND uid = %d
        """ % (name, avatarId, uid)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

def getFlagsWithUid(con, name, avatarId, uid):
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
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
                    AND username = %s
                )
                AND uid = %d
            )
        )
        """ % (name, avatarId, uid)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    retour = []
    for flag in results:
        flag = "".join(flag)
        retour.append(flag)
    return retour

def getUIDValidity(con, name, avatarId):
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    query = """
        SELECT uid_validity
        FROM imap_mail_box
        WHERE name_mail_box = %s
        AND username = %s
        """ % (name, avatarId)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

def getUIDNext(con, name, avatarId):
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    query = """
        SELECT uid_next
        FROM imap_mail_box
        where uid IN(
            SELECT uid
            FROM imap_meta_uids
            WHERE uid_validity =(
                SELECT uid_validity
                FROM imap_mail_box
                WHERE name_mail_box = %s
                AND username = %s
            )
        )
        """ % (name, avatarId)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

def getUidValidityWithName(con, name, avatarId):
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    query = """
        SELECT uid_validity
        FROM imap_mail_box
        WHERE uid IN(
            SELECT uid
            FROM imap_meta_uids
            WHERE uid_validity =(
                SELECT uid_validity
                FROM imap_mail_box
                WHERE imap_mail_box = %s
                AND username = %s
            )
        )
        """ % (name, avatarId)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

def getUIDlast(con, name, avatarId):
    idMail = getLastTuple(con, name, avatarId)
    uid = getUidWithId(con, idMail)
    uid = str(uid)
    uid = int(uid)
    return uid

def getUID(con, name, avatarId, index):
    index -= 1
    if index == -1:
        return getUIDlast(con, name, avatarId)
    else:
        name = util.quote(name, "char")
        avatarId = util.quote(avatarId, "char")
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
                    AND username = %s
                )
            )
            LIMIT %d,1
            """ % (name, avatarId, index)
        cursor = con.cursor()
        cursor.execute(query)
        results = cursor.fetchone()
        results = str(results[0])
        results = int(results)
        return results

def nbTupleFilter(con, name, avatarId, flag=None):
    if flag == None:
        return 0
    else:
        #recup uidvalidity avec le nom, recup uid avec uidvalidity, 
        #recup idflag avec flag, compter nbTuple dans metaflags avec uid et 
        # idflag
        flag = util.quote(flag, "char")
        name = util.quote(name, "char")
        avatarId = util.quote(avatarId, "char")
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
                    AND username = %s
                )
            )
            AND id_flag =(
                SELECT id_flag
                FROM imap_flags
                WHERE name = %s
            )
            """ % (name, avatarId, flag)
        cursor = con.cursor()
        cursor.execute(query)
        results = cursor.fetchone()
        results = str(results[0])
        results = int(results)
        return results
             










