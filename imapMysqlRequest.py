#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
from twisted.enterprise import adbapi, util
from twisted.internet import defer
import sys, random, traceback
from email.mime.multipart import MIMEMultipart
from email.parser import Parser
from email.mime.text import MIMEText

def createBox(con, avatarId, name):
    if not isAlreadyExists(con, name, avatarId):
        avatarId = util.quote(avatarId, "char")
        name = util.quote(name, "char")
        query = """
            INSERT INTO imap_mail_box(
            username, name_mail_box)
            VALUES(%s, %s)""" % (avatarId, name)
        cursor = con.cursor()
        try:
            cursor.execute(query)
        except Exception:
            print traceback.print_exc(file=sys.stdout)
    else:
        print "box(%s) déja existante" % name
        
def isAlreadyExists(con, name, avatarId):
    avatarId = util.quote(avatarId, "char")
    name = util.quote(name, "char")
    query = """
        SELECT count(*)
        FROM imap_mail_box
        WHERE name_mail_box = %s
        AND username = %s
        """ % (name, avatarId)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = int(str(results[0]))
    if results == 0:
        return False
    else:
        return True
        
def getLastTuple(con, name, avatarId):
    nbTuple = nbTupleMail(con, name, avatarId)
    if nbTuple == 0:
        return None
    elif nbTuple == 1:
        return getTupleMail(con, name, avatarId, 1)
    else:
        name = util.quote(name, "char")
        avatarId = util.quote(avatarId, "char")
        query = """
            SELECT id_mail_message
            FROM imap_mail_message
            WHERE id_mail_message >= ALL(
                SELECT id_mail_message
                FROM imap_mail_message
                WHERE id_mail_message IN(
                    SELECT id_mail_message
                    FROM imap_box_message
                    WHERE id_mail_box =(
                        SELECT id_mail_box
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
        WHERE id_mail_message IN(
            SELECT id_mail_message
            FROM imap_box_message
            WHERE id_mail_box =(
                SELECT id_mail_box
                FROM imap_mail_box
                WHERE name_mail_box = %s
                AND username = %s
            )
        )
        LIMIT %d, 1
        """ % (name, avatarId, index)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    results = str(results[0])
    results = int(results)
    return results

def nbTupleMail(con, name, avatarId):
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    query = """
        SELECT count(*) 
        FROM imap_box_message 
        WHERE id_mail_box IN(
            SELECT id_mail_box
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
        WHERE id_mail_message IN(
            SELECT id_mail_message
            FROM imap_box_message
            WHERE id_mail_box =(
                SELECT id_mail_box
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
        SET active = 1
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

def getFlagsWithId(con, name, avatarId, idMail):
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    query = """
        SELECT name
        FROM imap_flags
        WHERE id_flag IN(
            SELECT id_flag
            FROM imap_message_flag
            WHERE id_mail_message IN(
                SELECT id_mail_message
                FROM imap_box_message
                WHERE id_mail_box =(
                    SELECT id_mail_box
                    FROM imap_mail_box
                    WHERE name_mail_box = %s
                    AND username = %s
                )
            )
            AND id_mail_message = %d
        )
        """ % (name, avatarId, idMail)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    retour = []
    for flag in results:
        flag = "".join(flag)
        retour.append(flag)
    return retour

def getIdMailBox(con, name, avatarId):
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    query = """
        SELECT id_mail_box
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

def getIdMailMessageLast(con, name, avatarId):
    idMail = getLastTuple(con, name, avatarId)
    return idMail

def getIdMailMessage(con, name, avatarId, index):
    index -= 1
    if index == -1:
        return getIdMailMessageLast(con, name, avatarId)
    else:
        name = util.quote(name, "char")
        avatarId = util.quote(avatarId, "char")
        query = """
            SELECT id_mail_message
            FROM imap_mail_message
            WHERE id_mail_message in(
                SELECT id_mail_message
                FROM imap_box_message
                WHERE id_mail_box =(
                    SELECT id_mail_box
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
        flag = util.quote(flag, "char")
        name = util.quote(name, "char")
        avatarId = util.quote(avatarId, "char")
        query = """
            SELECT id_mail_message
            FROM imap_message_flag
            WHERE id_flag =(
                SELECT id_flag
                FROM imap_flags
                WHERE name = %s
            )
            AND id_mail_message IN(
                SELECT id_mail_message
                FROM imap_box_message
                WHERE id_mail_box =(
                    SELECT id_mail_box
                    FROM imap_mail_box
                    WHERE name_mail_box = %s
                    AND username = %s
                )
            )
        """ % (flag, name, avatarId)
        cursor = con.cursor()
        cursor.execute(query)
        results = cursor.fetchone()
        if results:
            results = str(results[0])
            results = int(results)
        return results

def deleteFlags(con, name, avatarId, idMail):
    query = """
        DELETE
        FROM imap_message_flag
        WHERE id_mail_message IN(
            SELECT id_mail_message
            FROM imap_box_message
            WHERE id_mail_box =(
                SELECT id_mail_box
                FROM imap_mail_box
                WHERE name_mail_box = %s
                AND username = %s
            )
        )
        AND id_mail_message = %d
        """ % (name, avatarId, idMail)
    cursor = con.cursor()
    cursor.execute(query)

def deleteFlag(con, name, avatarId, idMail, flag):
    query = """
        DELETE
        FROM imap_message_flag
        WHERE id_mail_message IN(
            SELECT id_mail_message
            FROM imap_box_message
            WHERE id_mail_box =(
                SELECT id_mail_box
                FROM imap_mail_box
                WHERE name_mail_box = %s
                AND username = %s
            )
        )
        AND id_mail_message = %d
        AND id_flag =(
            SELECT id_flag
            FROM imap_flags
            WHERE name = %s
        )
        """ % (name, avatarId, idMail, flag)
    cursor = con.cursor()
    cursor.execute(query)
        
def addFlag(con, idMail, flag):
    query = """
        INSERT INTO imap_message_flag
        (id_mail_message, id_flag)
        VALUES(%d,(
            SELECT id_flag
            FROM imap_flags
            WHERE name = %s
        ))
        """ % (idMail, flag)
    cursor = con.cursor()
    try:
        cursor.execute(query)
    except:
        print "flag déja présent"

def getAllFlags(con):
    query = """
        SELECT name
        FROM imap_flags
        """
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    flags = []
    for flag in results:
        flag = "".join(flag)
        flags.append(flag)
    return flags

def getVirtualTab(con, name, avatarId):
    #DETAIL
    #virtual[1]:
    #{
    #####'username': 'greenlamp',
    #####'active': '0',
    #####'from': 'greenlamp@localhost',
    #####'name': 'Inbox',
    #####'content': 'ceci est un test de contenu',
    #####'to': 'greenlamp@localhost',
    #####'date': 'Mon, 13 Feb 2012 13:43:53 +0100 (CET)',
    #####'content-type': 'Content-Type: text/html; charset=iso-8859-1',
    #####'id': '10',
    #####'subject': 'Pour gabriel'
    #}

    virtual = {}
    pos = 1

    active = 0
    if name.lower() == "trash":
        active = 1
    name = util.quote(name, "char")
    avatarId = util.quote(avatarId, "char")
    query = """
    SELECT *
    FROM imap_mail_message
    WHERE id_mail_message IN(
        SELECT id_mail_message
        FROM imap_box_message
        WHERE id_mail_box =(
            SELECT id_mail_box
            FROM imap_mail_box
            WHERE name_mail_box = %s
            AND username = %s
        )
    )
    AND active = %d
    """ % (name, avatarId, active)
    cursor = con.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    for result in results:
        virtual[pos] = {}
        virtual[pos]["id"] = "%d" % result[0]
        virtual[pos]["from"] = "%s" % result[1]
        virtual[pos]["to"] = "%s" % result[2]
        virtual[pos]["subject"] = "%s" % result[3]
        virtual[pos]["date"] = "%s" % result[4]
        virtual[pos]["content-type"] = "%s" % result[5]
        virtual[pos]["content"] = "%s" % result[6]
        virtual[pos]["active"] = "%d" % result[7]
        virtual[pos]["name"] = name[1:-1]
        virtual[pos]["username"] = avatarId[1:-1]
        pos += 1

    return virtual

def getPosWithIdV(con, name, avatarId, idMail):
    virtual = getVirtualTab(con, name, avatarId)
    for i in range(len(virtual)):
        if idMail == int(str(virtual[i+1]["id"])):
            return i+1

def getIdWithPosV(con, name, avatarId, pos):
    virtual = getVirtualTab(con, name, avatarId)
    if virtual.has_key(pos):
        return virtual[pos]["id"]

def getLastPos(con, name, avatarId):
    return len(getVirtualTab(con, name, avatarId))









    