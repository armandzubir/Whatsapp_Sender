import sys
sys.path.insert(1, 'helper')
sys.path.insert(1, 'modules')
import sqlmodels as db
import whatsapp3 as wa
import readconfig as cfg
import time


DRIVERPATH = "chromedriver.exe"
wa.openwa()
sendkode, sendingtime = cfg.getVal('general', 'sendingTime')
    
def openwa():
    if not wa.openwa():
        print "wa not open"
        pass
    
def run_wajob():
    ob = db.getOutbox()
    if ob is None:
        print "ob is none"
        return
    print "ob:",ob
    res, msg = wa.sendwa(ob)
    print "res:",res,msg
    if not res:
        db.moveOutboxError(ob['id'], str(msg).replace("'",""))
        return
    db.moveOutboxToSent(ob['id'], 'send OK')
        
if __name__ == '__main__':
    while True:
        run_wajob()
        time.sleep(sendkode == 0 and float(sendingtime) or 5)
