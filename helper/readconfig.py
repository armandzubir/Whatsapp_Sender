import ConfigParser

configPath = 'sqlconfig.ini'
config = ConfigParser.SafeConfigParser()

def getVal(sect, option, config_path=configPath):   
    config.read(config_path)
    if config.has_section(sect):
        if config.has_option(sect, option):
            return (0,config.get(sect, option))
        else:
            print 'error: option ',option,' not found'
            return (1,'error: option not found')
    else:
        print 'error: section ',sect,' not found'
        return (2,'error: section not found')

