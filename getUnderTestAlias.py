#!/usr/bin/env python
'''
Assuming one under-test node present, get its alias

@author: Bob Jacobsen
'''

import connection as connection
import verifyNodeGlobal
import canolcbutils

'''
Returns list of alias, nodeID

It obtains these by sending a globally-visible "verify nodes" message,
so it expects to have only one node on the network so that replies are unique.

'''
def get(alias, nodeID, verbose) :
    if verbose : print ("   get alias of node under test")
    connection.network.send(verifyNodeGlobal.makeframe(alias, nodeID))
    loop = 1
    while (loop < 20) :
        loop = loop+1
        reply = connection.network.receive()
        if (reply == None ) : continue
        if (reply.startswith(":X19170")) :
            alias,nodeID = int(reply[7:10],16),canolcbutils.bodyArray(reply)
            if verbose : print ("   Found alias "+str(alias)+" ("+hex(alias)+") for node ID "+str(nodeID))
            return alias,nodeID
    print ("Could not obtain alias, no reply from unit under test")
    exit(1)

def usage() :
    print ("")
    print (" Assumoing one under-test node present, uses ")
    print (" one CAN VerifyNode (Global) message")
    print (" to get that node's alias ")
    print ("")
    print ("Default connection detail taken from connection.py")
    print ("")
    print ("-a --alias source alias (default 123)")
    print ("-n --node dest nodeID (default None)")
    print ("-v verbose")

import getopt, sys

def main():
    # argument processing
    nodeID = None
    alias = connection.thisNodeAlias
    verbose = False
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "h:p:n:a:vV", ["alias=", "node=", "host=", "port="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print (str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v" or opt == "-V":
            connection.network.verbose = True
            verbose = True
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
    alias,nodeID = get(alias, nodeID, verbose)
    connection.network.close()

if __name__ == '__main__':
    main()
