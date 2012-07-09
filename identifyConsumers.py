#!/usr/bin/env python
'''
Send identifyConsumers message

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, eventID) :
    return canolcbutils.makeframestring(0x18A4F000+alias,eventID)
    
def usage() :
    print ""
    print "Called standalone, will send one CAN IdentifyConsumers message"
    print " and display response"
    print ""
    print "Expect zero or more ConsumerIdentified reply in return"
    print "e.g. [1926Bsss] nn nn nn nn nn nn"
    print "containing dest alias and EventID"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-e --event eventID as 1.2.3.4.5.6.7.8 form"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

def main():
    alias = connection.thisNodeAlias
    event = [1,2,3,4,5,6,7,8]
    verbose = False
    
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "e:a:vV", ["alias=", "event="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt == "-V":
            verbose = True
            connection.network.verbose = True
        elif opt in ("-a", "--alias"):
            alias = int(arg) # needs hex decode
        elif opt in ("-e", "--event"):
            event = canolcbutils.splitSequence(arg)
        else:
            assert False, "unhandled option"
    
    retval = test(alias,event,connection,verbose)
    connection.network.close()
    exit(retval)

def test(alias,event,connection,verbose) :
    connection.network.send(makeframe(alias,event))
    count = 0
    while (True) :
        if (connection.network.receive() == None ) : break
        count = count + 1
    if verbose : print "  Found",count,"nodes"
    return 0

if __name__ == '__main__':
    main()
