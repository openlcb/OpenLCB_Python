#!/usr/bin/env python
'''
Send identifyEvents message

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias) :
    return canolcbutils.makeframestring(0x19970000+alias, None)
    
def usage() :
    print ""
    print "Called standalone, will send one CAN IdentifyEvents global message"
    print " and display response"
    print ""
    print "Expect zero or more ConsumerIdentified replies in return"
    print "e.g. [194C4sss] nn nn nn nn nn nn"
    print "containing dest alias and EventID"
    print ""
    print "Expect zero or more ProducerIdentified replies in return"
    print "e.g. [19954sss] nn nn nn nn nn nn"
    print "containing dest alias and EventID"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

def main():
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    verbose = False
    
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:vV", ["alias=", "dest="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt == "-V":
            connection.network.verbose = True
            verbose = True
        elif opt in ("-a", "--alias"):
            alias = int(arg) # needs hex decode
        elif opt in ("-d", "--dest"):
            dest = int(arg) # needs hex processing
        else:
            assert False, "unhandled option"

    retval = test(alias, connection, verbose)
    connection.network.close()
    exit(retval)

def test(alias, connection, verbose) : 
    # now execute
    connection.network.send(makeframe(alias))
    count = 0
    while (True) :
        reply = connection.network.receive()
        if (reply == None ) : break
        if not (reply.startswith(':X194C7') or reply.startswith(':X194C4') or reply.startswith(':X194C5') or reply.startswith(':X19547') or reply.startswith(':X19544') or reply.startswith(':X19545')):
            print "Wrong reply received", reply
            return 4
        count = count + 1
    if verbose : print "  Found",count,"events"
    return 0

if __name__ == '__main__':
    main()
