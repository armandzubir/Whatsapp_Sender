import phonenumbers
from selenium import webdriver
import selenium.common.exceptions as serror
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import readconfig as cfg
import os.path
import sqlmodels as db
import datetime

WAWEB    = "https://web.whatsapp.com/"
WAPI     = "https://web.whatsapp.com/send?phone=%s"

kd,CPROFILE = cfg.getVal('whatsapp', 'CPROFILE')
kd,SSDir = cfg.getVal('whatsapp', 'SSDir')
kd,xMsgButton    = cfg.getVal('whatsapp', 'xMsgButton')
kd,xUseWAButton  = cfg.getVal('whatsapp', 'xUseWAButton')
kd,xWAReady      = cfg.getVal('whatsapp', 'xWAReady')
kd,xContactField = cfg.getVal('whatsapp', 'xContactField')
kd,xIsContact    = cfg.getVal('whatsapp', 'xIsContact')
kd,xHeaderDest   = cfg.getVal('whatsapp', 'xHeaderDest')
kd,xMsgField     = cfg.getVal('whatsapp', 'xMsgField')
kd,xInvalid     = cfg.getVal('whatsapp', 'xInvalidNumber')
kd,xInvalidButton     = cfg.getVal('whatsapp', 'xInvalidButton')
kd,xAttachButton     = cfg.getVal('whatsapp', 'xAttachButton')
kd,xFileAttach     = cfg.getVal('whatsapp', 'xFileAttach')
kd,xSendAttachButton     = cfg.getVal('whatsapp', 'xSendAttachButton')
kd,xAttachMessage     = cfg.getVal('whatsapp', 'xAttachMessage')
kd,xMessageRead = cfg.getVal('whatsapp', 'xMessageRead')
kd,xMessageSent = cfg.getVal('whatsapp', 'xMessageSent')
kd,xSendButton = cfg.getVal('whatsapp', 'xSendButton')

driver = None

def phoneNumber(destination):
    try:
        print 'checking phone number format'
        x = phonenumbers.parse(destination,'ID')
        return True,phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except Exception,e:
        print "Error phoneNumber:",str(e)
        return False,destination

def clickElm(xpath):
    elm = driver.find_element_by_xpath(xpath)
    elm.click()

def clearElm(xpath):
    elm = driver.find_element_by_xpath(xpath)
    elm.clear()

def fillElm(xpath,keys):
    elm = driver.find_element_by_xpath(xpath)
    elm.send_keys(keys)

def openwa(driverpath="chromedriver.exe"):
    try:
        global driver
        if driver is None:
            options = webdriver.ChromeOptions()
            options.add_argument(CPROFILE)
            driver = webdriver.Chrome(executable_path=driverpath, options=options)
        print 'opening whatsapp'
        driver.get(WAWEB)
        isWaReady()
        return True
    except Exception, e:
        print "Error open wa:",str(e)
        return False

def isMessageSent():
    c = 0
    print 'waiting message sent'
    while c<10:
        if isElementExists(xMessageRead):
            print 'message read..'
            return True
        if isElementExists(xMessageSent):
            print 'message sent..'
            return True
        c += 1
        time.sleep(1)
    print 'message not sent'
    return False

def isWaReady():
    print "waiting for readiness..."
    while not isElementExists(xContactField):
        time.sleep(0.5)
    print "WA Ready..."
    time.sleep(1)

def isElementExists(xpath):
    try:
        if driver is None:
            return False
        driver.find_element_by_xpath(xpath)
        return True
    except serror.NoSuchElementException:
        return False

def openwapi(destination):
    try:
        if driver is None:
            return False,"Driver is Null"
        destination = destination.replace("+","").replace(' ','')
        print "open {}".format(WAPI %(destination))
        time.sleep(2)
        driver.get(WAPI %(destination))
        print "waiting for readiness..."
        while not isElementExists(xMsgField):
            print 'checking...'
            if isElementExists(xInvalid):
                print 'found invalid'
                time.sleep(0.2)
                clickElm(xInvalidButton)
                return False,'Invalid Number'
            time.sleep(1)
        while not isElementExists(xWAReady):
            time.sleep(0.5)
        print "WA Ready..."
        return True,"WA Ready"
    except Exception, e:
        driver.save_screenshot('%s/%s_%s.png' %(SSDir,datetime.datetime.now().strftime('%Y%m%d_%H%m%S'),destination))
        return False,"Error open wapi:"+str(e)
    
def checkDestination(destination):
    try:
        print 'checking number'
        if not isElementExists(xContactField):
            print 'contact field not found'
            return False,"contact field not found"
        clickElm(xContactField)
        clearElm(xContactField)
        isPhoneNumber, number = phoneNumber(destination)
        fillElm(xContactField,number)
        time.sleep(1.5) ##wait for search
        if not isElementExists(xIsContact):
            if not isPhoneNumber:
                print 'phone number is invalid'
                return False, "Phone number is invalid format"
            if db.isNumberValid(destination):
                return openwapi(number.replace('-','')) ##not inside chat / contact
            else:
                return False,'Invalid Number'
        else:
            clickElm(xContactField)
            fillElm(xContactField,Keys.ENTER)
            return True,""
    except Exception, e:
        return False,("error search contact:",str(e))
    
def sendText(ob):
    try:
        isPhoneNumber, destHead = phoneNumber(ob['destination'])
        if not isElementExists(xHeaderDest %(destHead)):##check if destination is right
            print "destination header not found!"
            pass
        
        
        clearElm(xMsgField)
        print 'sending:',ob['messageText']
        for msg in ob['messageText'].split('\r\n'):
            fillElm(xMsgField,msg)
            fillElm(xMsgField,(Keys.SHIFT, Keys.ENTER))
        fillElm(xMsgField,Keys.ENTER)
        time.sleep(1)
        
        if isMessageSent():
##            driver.save_screenshot('D:/WASender/Apps/media/screenshot/tes.png')
            return True,""
        else:
            raise ValueError('send timed out')
    except Exception, e:
        print "Error sendText:", str(e)
        return False,str(e).replace("'","")
    
def sendImage(ob, text=False):
    try:
        sendText = False
        isPhoneNumber, destHead = phoneNumber(ob['destination'])
        if not isElementExists(xHeaderDest %(destHead)):##check if destination is right
            print "destination header not found!"
            raise ValueError('(1)destination header not found!')

        clearElm(xMsgField)

        print 'checking file...'
        if not os.path.isfile(ob['imagePath']):
            raise ValueError('(2)Attached File not found')

        print 'checking attach button...'
        if not isElementExists(xAttachButton):
            raise ValueError('(3)Attach Button not found!')
        clickElm(xAttachButton)
        time.sleep(1)

        print 'checking file attach...'
        if not isElementExists(xFileAttach):
            raise ValueError('(4)Attach Button not found!')
        fillElm(xFileAttach,ob['imagePath'])
        time.sleep(1)

        if text:
            print 'message with text'
            if isElementExists(xAttachMessage):
                'there is text box'
                clearElm(xAttachMessage)
                for msg in ob['messageText'].split('\r\n'):
                    fillElm(xAttachMessage,msg)
                    fillElm(xAttachMessage,(Keys.SHIFT, Keys.ENTER))
                    sendText = True
                time.sleep(0.5)
            else:
                print 'message box not found'

        c=0
        while c < 5:
            if not isElementExists(xSendAttachButton):
                print 'waiting button'
            else:
                print 'button found!'
                pass
            time.sleep(0.5)
            c+=1
        if not isElementExists(xSendAttachButton):
            raise ValueError('(5)timed out, Send Button not found!')
        clickElm(xSendAttachButton)
        time.sleep(1)
        if isElementExists(xSendButton):
            clickElm(xSendButton)
            
        if isMessageSent():
            return True,""
        else:
            raise ValueError('send timed out')
    except Exception, e:
        print "Error send Image:", str(e)
        return False,str(e).replace("'","")
    
def sendBoth():
    return False, "send both"
def sendwa(ob):
    kode,msg = checkDestination(ob['destination'])
    if kode:
        msgType = int(ob['messageType'])
        if   msgType == 0: ##send text
            return sendText(ob)
        elif msgType == 1: ##send image
            return sendImage(ob)
        else: ##send both
            return sendImage(ob, text=True)
    else:
        return False, msg
