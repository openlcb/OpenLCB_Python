#!/usr/bin/env python
'''
Rapidly cycle requests to a single node to measure response time

@author: Bob Jacobsen
'''

import connection as connection
import verifyNodeGlobal
import canolcbutils
import time

'''
Returns list of alias, nodeID
'''
def get(alias, nodeID) :
    connection.network.send(verifyNodeGlobal.makeframe(alias, nodeID))
    while (True) :
        reply = connection.network.receive()
        if (reply == None ) : return None,None
        if (reply.startswith(":X180B7")) :
            return int(reply[7:10],16),canolcbutils.bodyArray(reply)

def usage() :
    print ""
    print " Assumoing one under-test node present, uses "
    print " one CAN VerifyNode (Global) message"
    print " to get that node's alias "
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 123)"
    print "-n --num number of cycles (default 100, 0 means forever)"
    print "-p number of requests to send in parallel (default 1)"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

def main():
    # argument processing
    n = 100
    alias = connection.thisNodeAlias
    verbose = False
    parallel = 1
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "h:p:n:a:vVp", ["alias=", "num=", "host=", "port="])
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
        elif opt == "-p":
            parallel = int(arg)
        elif opt in ("-a", "--alias"):
            alias = int(arg)
        elif opt in ("-n", "--num"):
            n = int(arg)
        else:
            assert False, "unhandled option"

    # now execute
    retval = test(alias, n, connection, verbose, parallel)
    exit(retval)

def once(alias, n, connection, verbose, parallel) :
    for j in range(parallel) :
        connection.network.send(verifyNodeGlobal.makeframe(alias, None))
    for j in range(parallel) :
        reply = connection.network.receive()
        while reply != None and reply.startswith("!") :
            # skip
            reply = connection.network.receive()
        if reply == None : 
            print "No reply received"
            return 1
        if not reply.startswith(":X180B7") :
            print "Incorrect reply received"
            return 2
    return 0
    
def test(alias, n, connection, verbose, parallel) :
    if n == 0 :
        while once(alias, n, connection, verbose, parallel) == 0 : pass
    else :
        start = time.time()
        for i in range(n) :
            retval = once(alias, n, connection, verbose, parallel)
            if retval != 0 : return retval
        end = time.time()
        if verbose :
            print end-start
    
    return 0
        
        
if __name__ == '__main__':
    main()
