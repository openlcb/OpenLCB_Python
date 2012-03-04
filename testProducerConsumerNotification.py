#!/usr/bin/env python
'''
Tests a node's response to request for information
about it's producers and consumers.

Note that this doesn't test the the messages that
happen as part of reset.

1) Use IdentifyEvents to get list of event IDs
2) Use IdentifyConsumer/IdentifyProducer to make sure each is available


@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils
import identifyEventsAddressed
import identifyConsumers
import identifyProducers

    
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

    if identifynode :
        import getUnderTestAlias
        dest,nodeID = getUnderTestAlias.get(alias, None, verbose)

    retval = test(alias, dest, connection, verbose)
    return retval
    
def test(alias, dest, connection, verbose) :
    # now execute
    connection.network.send(identifyEventsAddressed.makeframe(alias, dest))
    consumed = []
    produced = []
    while (True) :
        reply = connection.network.receive()
        if (reply == None ) : break
        if (reply.startswith(":X1926B")) :
            event = canolcbutils.bodyArray(reply)
            if verbose : print "  consumes ", event
            consumed = consumed+[event]
        elif (reply.startswith(":X192AB")) :
            event = canolcbutils.bodyArray(reply)
            if verbose : print "  produces ", event
            produced = produced+[event]
    # now check consumers and producers individually
    timeout = connection.network.timeout
    connection.network.timeout = 0.25
    if connection.network.verbose : print "Start individual checks"
    for c in consumed :
        connection.network.send(identifyConsumers.makeframe(alias, c))
        reply = connection.network.receive()
        if (reply == None ) : 
            print "no reply for consumer ", c
        elif ( not reply.startswith(":X1926B") ) :
            print "Unexpected reply "+reply
        # here is OK, go around to next
        while True :
            reply = connection.network.receive()
            if (reply == None ) : break
            elif ( not reply.startswith(":X1926B") ) :
                print "Unexpected reply "+reply
    for p in produced :
        connection.network.send(identifyProducers.makeframe(alias, p))
        reply = connection.network.receive()
        if (reply == None ) : 
            print "no reply for producer ", p
        elif ( not reply.startswith(":X192AB")) :
            print "Unexpected reply "+reply
        # here is OK, go around to next
        while True :
            reply = connection.network.receive()
            if (reply == None ) : break
            elif ( not reply.startswith(":X192AB") ) :
                print "Unexpected reply "+reply
    connection.network.timeout = timeout
    return 0

if __name__ == '__main__':
    main()
