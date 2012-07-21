#!/usr/bin/env python
'''
Send identifyEvents message

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, dest) :
    body = [(dest>>8)&0xFF, dest&0xFF]
    return canolcbutils.makeframestring(0x19968000+alias,body)
    
def usage() :
    print ""
    print "Called standalone, will send one CAN IdentifyEvents message"
    print " and display response"
    print ""
    print "Expect zero or more ConsumerIdentified reply in return"
    print "e.g. [1926Bsss] nn nn nn nn nn nn"
    print "containing dest alias and EventID"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-t find destination alias automatically"
    print "-v verbose"
    print "-V very verbose"

import getopt, sys

def main():
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    identifynode = False
    verbose = False

    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:vVt", ["alias=", "dest="])
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
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)

    retval = test(alias, dest, connection, verbose)
    connection.network.close()
    exit(retval)
    
def test(alias, dest, connection, verbose) : 
    connection.network.send(makeframe(alias,dest))
    count = 0
    while (True) :
        if (connection.network.receive() == None ) : break
        count = count + 1
    if verbose : print "  Found",count,"events"
    
    # check that there's no reply to another node id
    if verbose : print "  checking for no reply to request to another node"
    connection.network.send(makeframe(alias,dest^alias))
    reply = connection.network.receive()
    if (reply == None ) : return 0
    print "unexpected reply: "+reply
    return 12

    return 0

if __name__ == '__main__':
    main()
