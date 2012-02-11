#!/usr/bin/env python
'''
Tests a node's startup processing:
 * Alias allocation
 * State changes and notification
 * P/C event notification

Requires that the user reset the node (or otherwise force a startup)
after the script is started.

@author: Bob Jacobsen
'''

# Expects:
# :X17020573N;
# :X16304573N;
# :X15050573N;
# :X10700573N;
# :X19087573N020304050607;
# :X192AB573N0203040506070001;
# :X192AB573N0203040506070004;
# :X1926B573N0203040506070005;
# :X1926B573N0203040506070008;

import connection as connection
import canolcbutils

import time
    
def usage() :
    print ""
    print "Called standalone, tests a nodes startup processing."
    print "Reset the node (or force startup) after the script starts"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 123)"
    print "-d --dest dest alias (default 123)"
    print "-t find destination alias automatically"
    print "-v verbose"
    print "-V very verbose"

import getopt, sys

def main():
    alias = connection.thisNodeAlias;
    dest = connection.testNodeAlias;
    verbose = False
    identifynode = False
    
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
            verbose = True
            connection.network.verbose = True
        elif opt in ("-a", "--alias"):
            alias = int(arg) # needs hex decode
        elif opt in ("-d", "--dest"):
            dest = int(arg) # needs hex decode
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    retval = test(alias, dest, connection, identifynode, verbose)
    return retval
    
def test(alias, dest, connection, identifynode, verbose) :
    # wait for reset
    if verbose : print "Restart node now"
    
    # expect RIF sequence (check timing)
    connection.network.connect()
    timeout = connection.network.timeout
    connection.network.timeout = 25
    reply = connection.network.receive()
    connection.network.timeout = timeout
    if reply == None :
        if verbose : print "1st reply not received, did you reset node?"
        return 1
    if not reply.startswith(":X17") :
        if verbose : print "1st reply not correct"
        return 31
    testAlias = reply[7:10]
    id = reply[4:7]
    start = time.time()
    
    reply = connection.network.receive()
    if reply == None :
        if verbose : print "2nd reply not received"
        return 2
    if reply[7:10] != testAlias :
        if verbose : print "mismatched 2nd source alias"
        return 12
    if not reply.startswith(":X16") :
        if verbose : print "2nd reply not correct"
        return 32
    id = id+reply[4:7]

    reply = connection.network.receive()
    if reply == None :
        if verbose : print "3rd reply not received"
        return 3
    if reply[7:10] != testAlias :
        if verbose : print "mismatched 3rd source alias"
        return 13
    if not reply.startswith(":X15") :
        if verbose : print "3rd reply not correct"
        return 33
    id = id+reply[4:7]

    reply = connection.network.receive()
    if reply == None :
        if verbose : print "4th reply not received"
        return 4
    if reply[7:10] != testAlias :
        if verbose : print "mismatched 4th source alias"
        return 14
    if not reply.startswith(":X14") :
        if verbose : print "4th reply not correct"
        return 34
    id = id+reply[4:7]
    
    # expect CIF (check timing)
    reply = connection.network.receive()
    end = time.time()
    if reply == None :
        if verbose : print "5th reply not received"
        return 5
    if not reply.startswith(":X10700") :
        if verbose : print "5th reply not correct"
        return 35
    if reply[7:10] != testAlias :
        if verbose : print "mismatched 5th source alias"
        return 15
    if end-start < 0.15 :
        if verbose : print "did not wait long enough ", end-start
        return 22
    
    if end-start > 0.550 :
        if verbose : print "waited too long ", end-start
        return 23

    # expect NodeInit
    reply = connection.network.receive()
    if reply == None :
        if verbose : print "6th reply not received"
        return 6
    if not reply.startswith(":X19087") :
        if verbose : print "6th reply not correct"
        return 35
    if reply[7:10] != testAlias :
        if verbose : print "mismatched 6th source alias"
        return 16
    if id != reply[11:23] :
        if verbose : print "node ID did not match",id, reply[11:23]
        return 21
    
    # expect one or more Produced/Consumed messages

    consumed = []
    produced = []
    while (True) :
        reply = connection.network.receive()
        if (reply == None ) : break
        if (reply.startswith(":X1926B")) :
            event = canolcbutils.bodyArray(reply)
            if verbose : print "consumes ", event
            consumed = consumed+[event]
        elif (reply.startswith(":X192AB")) :
            event = canolcbutils.bodyArray(reply)
            if verbose : print "produces ", event
            produced = produced+[event]
        else :
            if verbose : print "Unexpected message"
            return 50
    return 0

if __name__ == '__main__':
    main()
