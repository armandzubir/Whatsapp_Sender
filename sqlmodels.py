import sys
sys.path.insert(1, 'helper')
import sqldatabase as sql

##conn = sql.dbConnect(DBHOST,DBUSER,DBPASS,DBNAME)

def getOutbox():
    try:
        q = "SELECT top(1) * FROM tbl_outbox WHERE sendError IS NULL AND senderNumber is NULL AND sendAfter < GETDATE() ORDER BY priority,id ASC"
        c = sql.select(q)
        if len(c) < 1:
            return None
        data={}
        data['id']=c[0][0]
        data['dateInsert']=c[0][1]
        data['sendAfter']=c[0][2]
        data['destination']=c[0][3]
        data['isContact']=c[0][4]
        data['messageType']=c[0][5]
        data['messageText']=c[0][6]
        data['imagePath']=c[0][7]
        data['senderID']=c[0][8]
        data['sendError']=c[0][9]
        return data
    except Exception, e:
        print "Error getOutbox:", str(e)
        return None

def moveOutboxToSent(outboxId, sendStatus):
    try:
        q = "INSERT INTO tbl_sent([id],[dateInsertOutbox], [destination], [isContact], [messageType], [messageText], [imagePath], [senderId], [send_status], [priority], [senderNumber]) SELECT %s,dateInsert, destination, isContact, messageType, messageText, imagePath, senderId, '%s' as sStatus, [priority], senderNumber FROM tbl_outbox WHERE tbl_outbox.id=%s"
        sql.execute(q %(outboxId,sendStatus, outboxId))
        q = "DELETE FROM tbl_outbox WHERE id=%s"
        sql.execute(q %(outboxId))
        print "message:",outboxId,"send OK"
        return True,""
    except Exception, e:
        print 'error move to sent item:',str(e)
        return False, str(e)

def moveOutboxError(outboxId, sendError, errorPath='-'):
    try:
        q = "INSERT INTO tbl_outboxError([id],[dateInsertOutbox], [destination], [isContact], [messageType], [messageText], [imagePath], [senderId], [send_status], [priority],[senderNumber],[error_path]) SELECT %s,dateInsert, destination, isContact, messageType, messageText, imagePath, senderId, '%s' as sStatus, [priority],senderNumber, '%s' as error_path FROM tbl_outbox WHERE tbl_outbox.id=%s"
        sql.execute(q %(outboxId,sendError, errorPath, outboxId))
        q = "DELETE FROM tbl_outbox WHERE id=%s"
        sql.execute(q %(outboxId))
        print "message:",outboxId,"moved to outboxError"
        return True,""
    except Exception, e:
        print 'error move to outbox error:',str(e)
        return False, str(e)

def isNumberValid(destination, period=30):
    try:
        q = "select * from tbl_outboxError where send_status  in ('Invalid Number','Phone number is invalid format') and dateInsert >  dateadd(day,-%s,getdate()) and destination='%s'" %(period,destination)
        c = sql.select(q)
        if len(c) < 1:
            return True
        else:
            return False
    except Exception, e:
        print "Error getOutbox:", str(e)
        return False
