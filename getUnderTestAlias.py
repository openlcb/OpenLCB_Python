#!/usr/bin/env python
'''
Assuming one under-test node present, get its alias

@author: Bob Jacobsen
'''

import connection as connection
import verifyNodeGlobal
import canolcbutils

def get(alias, nodeID) :
    connection.network.send(verifyNodeGlobal.makeframe(alias, nodeID))
    while (True) :
        reply = connection.network.receive()
        if (reply == None ) : return None
        if (reply.startswith(":X190B7")) :
            return int(reply[7:10],16)

def usage() :
    print ""
    print " Assumoing one under-test node present, uses "
    print " one CAN VerifyNode (Global) message"
    print " to get that node's alias "
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 123)"
    print "-n --node dest nodeID (default None)"
    print "-v verbose"

import getopt, sys

def main():
    # argument processing
    nodeID = None
    alias = connection.thisNodeAlias
    
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
            alias = int(arg)
        elif opt in ("-n", "--node"):
            nodeID = canolcbutils.splitSequence(arg)
        else:
            assert False, "unhandled option"

    # now execute
    alias = get(alias, nodeID)
    print "Found "+str(alias)+" ("+hex(alias)+")"

if __name__ == '__main__':
    main()
