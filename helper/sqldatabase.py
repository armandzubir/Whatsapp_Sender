import pyodbc
import readconfig as cfg

hostKey, hostVal = cfg.getVal('database', 'DBHOST')
userKey, userVal = cfg.getVal('database', 'DBUSER')
passKey, passVal = cfg.getVal('database', 'DBPASS')
dbKey, dbVal = cfg.getVal('database', 'DBNAME')

DBHOST = hostKey == 0 and hostVal or ''
DBUSER = userKey == 0 and userVal or ''
DBPASS = passKey == 0 and passVal or ''
DBNAME = dbKey == 0 and dbVal or ''

def dbConnect():
    try:
        conn = pyodbc.connect('Driver={SQL Server};Server=%s;Database=%s;UID=%s;PWD=%s' %(DBHOST,DBNAME,DBUSER,DBPASS))
        return conn
    except Exception, e:
        return None

def select(query):
    try:
        conn = dbConnect()
        csr = conn.cursor()
        csr.execute(query)
        return csr.fetchall()
    except Exception, e:
        print "error select:", str(e)
        return None
    finally:
        csr.close()
        conn.close()

def execute(query):
    try:
        print query
        conn = dbConnect()
        csr = conn.cursor()
        csr.execute(query)
        conn.commit()
        return True
    except Exception, e:
        print "error Execute:", str(e)
        return False
    finally:
        csr.close()
        conn.close()
