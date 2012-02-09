#!/usr/bin/env python
'''
Send identifyEvents message

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias) :
    return canolcbutils.makeframestring(0x182B7000+alias, None)
    
def usage() :
    print ""
    print "Called standalone, will send one CAN IdentifyEvents global message"
    print " and display response"
    print ""
    print "Expect zero or more ConsumerIdentified reply in return"
    print "e.g. [1926Bsss] nn nn nn nn nn nn"
    print "containing dest alias and EventID"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-v verbose"

import getopt, sys

def main():
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:v", ["alias=", "dest="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            connection.network.verbose = True
        elif opt in ("-a", "--alias"):
            alias = int(arg) # needs hex decode
        elif opt in ("-d", "--dest"):
            dest = int(arg) # needs hex processing
        else:
            assert False, "unhandled option"

    # now execute
    connection.network.send(makeframe(alias))
    while (True) :
        if (connection.network.receive() == None ) : break
    return

if __name__ == '__main__':
    main()
