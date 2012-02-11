#!/usr/bin/env python
'''
Run a series of tests with an attached node

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils
    
def usage() :
    print ""
    print "Called standalone, will sequence through a set of tests"
    print ""
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 123)"
    print "-d --dest dest alias (default 123)"
    print "-t find destination alias automatically"
    print "-n --node dest nodeID (default 01.02.03.04.05.06)"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

def main():
    # argument processing
    nodeID = connection.testNodeID
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    verbose = False
    identifynode = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "n:a:d:vVt", ["alias=", "node=", "dest="])
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
            alias = int(arg)
        elif opt in ("-d", "--dest"):
            dest = int(arg) # needs hex decode
        elif opt == "-t":
            identifynode = True
        elif opt in ("-n", "--node"):
            nodeID = canolcbutils.splitSequence(arg)
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, nodeID = getUnderTestAlias.get(alias, None)

    # now execute
    retval = test(alias, dest, nodeID, connection, verbose)
    exit(retval)    
    
def test(alias, dest, nodeID, connection, verbose):

    import verifyNodeGlobal
    if verbose : print "verifyNodeGlobal w no NodeID"
    retval = verifyNodeGlobal.test(alias, None, connection)
    if retval != 0 :
        print "Error in verifyNodeGlobal w no NodeID"
        exit(retval)
    if verbose : print "verifyNodeGlobal with NodeID"
    retval = verifyNodeGlobal.test(alias, nodeID, connection)
    if retval != 0 :
        print "Error in verifyNodeGlobal w NodeID"
        exit(retval)

    import identifyEventsGlobal
    if verbose : print "identifyEventsGlobal"
    retval = identifyEventsGlobal.test(alias, connection, verbose)
    if retval != 0 :
        print "Error in identifyEventsGlobal"
        exit(retval)

    import identifyEventsAddressed
    if verbose : print "identifyEventsAddressed"
    retval = identifyEventsAddressed.test(alias, dest, connection, verbose)
    if retval != 0 :
        print "Error in identifyEventsAddressed"
        exit(retval)

    import identifyConsumers
    if verbose : print "identifyConsumers"
    retval = identifyConsumers.test(alias, [1,2,3,4,5,6,7,8], connection, verbose)
    if retval != 0 :
        print "Error in identifyConsumers"
        exit(retval)

    import identifyProducers
    if verbose : print "identifyProducers"
    retval = identifyProducers.test(alias, [1,2,3,4,5,6,7,8], connection, verbose)
    if retval != 0 :
        print "Error in identifyProducers"
        exit(retval)

    import datagram
    if verbose : print "datagram"
    retval = datagram.test(alias, dest, [1,2,3,4], connection, verbose)
    if retval != 0 :
        print "Error in datagram"
        exit(retval)
    
    import testProducerConsumerNotification
    if verbose : print "testProducerConsumerNotification"
    retval = testProducerConsumerNotification.test(alias, dest, connection, verbose)
    if retval != 0 :
        print "Error in verifyNodeGlobal"
        exit(retval)

    import testConfigurationRead
    if verbose : print "testConfigurationRead"
    retval = testConfigurationRead.test(alias, dest, connection, verbose)
    if retval != 0 :
        print "Error in testConfigurationRead", retval
        exit(retval)

    import testResponseTime
    n = 100
    if verbose : print "testResponseTime",n
    retval = testResponseTime.test(alias, n, connection, verbose, 1)
    
    import unknownMtiAddressed
    n = 100
    if verbose : print "unknownMtiAddressed",n
    retval = unknownMtiAddressed.test(alias, dest, connection, verbose)
    
    return

if __name__ == '__main__':
    main()
