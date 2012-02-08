#!/usr/bin/env python
'''
Created on March 18, 2011

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, eventID) :
    return canolcbutils.makeframestring(0x1824F000+alias,eventID)
    
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
    print "-a --alias source alias (default 123)"
    print "-n --node eventID (default 01.02.03.04.05.06.EE.EE)"
    print "-v verbose"

import getopt, sys

def main():
    eventID = [1,2,3,4,5,6,0xEE,0xEE]
    alias = connection.thisNodeAlias;
    
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "h:p:n:a:v", ["alias=", "node=", "host=", "port="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            connection.network.verbose = True
        elif opt in ("-h", "--host"):
            connection.network.host = arg
        elif opt in ("-p", "--port"):
            connection.network.port = int(arg)
        elif opt in ("-a", "--alias"):
            alias = int(arg) # needs hex decode
        elif opt in ("-n", "--node"):
            eventID = canolcbutils.splitSequence(arg)
        else:
            assert False, "unhandled option"

    # now execute
    connection.network.send(makeframe(alias,eventID))
    while (True) :
        if (connection.network.receive() == None ) : break
    return

if __name__ == '__main__':
    main()
