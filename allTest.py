#!/usr/bin/env python
'''
Run a series of tests with an attached node

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils
import defaults
    
def usage() :
    print ""
    print "Called standalone, will sequence through a set of tests"
    print ""
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 123)"
    print "-d --dest dest alias (default 123)"
    print "-b number of datagram buffers to test (sends b+1 requests) default 1"
    print "-c continue after error; (attempts to) run to completion even if error encountered"
    print "-e --event eventID as 1.2.3.4.5.6.7.8 form"
    print "-n --node dest nodeID (-t option sets automatically, format is 01.02.03.04.05.06)"
    print "-r run until error; repeats until failure"
    print "-t find destination alias automatically"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

def main():
    # argument processing
    nodeID = connection.testNodeID
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    event = defaults.testEventID
    verbose = False
    identifynode = False
    complete = False
    repeat = False
    bufnum = 1
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "e:n:b:a:d:vVtcr", ["event=", "alias=", "node=", "dest="])
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
        elif opt in ("-b"):
            bufnum = int(arg)
        elif opt == "-c":
            complete = True
        elif opt in ("-d", "--dest"):
            dest = int(arg, 0)
        elif opt in ("-e", "--event"):
            event = canolcbutils.splitSequence(arg)
        elif opt in ("-n", "--node"):
            nodeID = canolcbutils.splitSequence(arg)
        elif opt == "-r":
            repeat = True
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    # now execute
    retval = test(alias, dest, nodeID, event, connection, verbose, complete, repeat, identifynode, bufnum)
    done(retval)    

def done(retval) :
    connection.network.close()
    exit(retval)
    
def test(alias, dest, nodeID, event, connection, verbose, complete, repeat, identifynode, bufnum):

    result = 0;
    
    while True :

        if identifynode :
            import getUnderTestAlias
            dest, nodeID = getUnderTestAlias.get(alias, None, verbose)

        import aliasMapEnquiry
        if verbose : print "aliasMapEnquiry"
        retval = aliasMapEnquiry.test(alias, dest, nodeID, connection, verbose)
        if retval != 0 :
            print "Error in aliasMapEnquiry"
            if not complete : done(retval)
            result |= retval
    
        import verifyNodeGlobal
        #if verbose : print "verifyNodeGlobal w no NodeID"
        #retval = verifyNodeGlobal.test(alias, None, connection)
        #if retval != 0 :
        #    print "Error in verifyNodeGlobal w no NodeID"
        #    if not complete : done(retval)
        #    result |= retval
        if verbose : print "verifyNodeGlobal"
        retval = verifyNodeGlobal.test(alias, nodeID, connection)
        if retval != 0 :
            print "Error in verifyNodeGlobal"
            if not complete : done(retval)
            result |= retval
    
        import verifyNodeAddressed
        if verbose : print "verifyNodeAddressed"
        retval = verifyNodeAddressed.test(alias, dest, nodeID, connection, verbose)
        if retval != 0 :
            print "Error in verifyNodeAddressed"
            if not complete : done(retval)
            result |= retval
    
        import protocolIdentProtocol
        if verbose : print "protocolIdentProtocol"
        retval = protocolIdentProtocol.test(alias, dest, connection, verbose)
        if retval != 0 :
            print "Error in protocolIdentProtocol"
            if not complete : done(retval)
            result |= retval
    
        import identifyEventsGlobal
        if verbose : print "identifyEventsGlobal"
        retval = identifyEventsGlobal.test(alias, dest, connection, verbose)
        if retval != 0 :
            print "Error in identifyEventsGlobal"
            if not complete : done(retval)
            result |= retval
    
        import identifyEventsAddressed
        if verbose : print "identifyEventsAddressed"
        retval = identifyEventsAddressed.test(alias, dest, connection, verbose)
        if retval != 0 :
            print "Error in identifyEventsAddressed"
            if not complete : done(retval)
            result |= retval
    
        import identifyConsumers
        if verbose : print "identifyConsumers"
        retval = identifyConsumers.test(alias, event, connection, verbose)
        if retval != 0 :
            print "Error in identifyConsumers"
            if not complete : done(retval)
            result |= retval
    
        import identifyProducers
        if verbose : print "identifyProducers"
        retval = identifyProducers.test(alias, event, connection, verbose)
        if retval != 0 :
            print "Error in identifyProducers"
            if not complete : done(retval)
            result |= retval
    
        import testProducerConsumerNotification
        if verbose : print "testProducerConsumerNotification"
        retval = testProducerConsumerNotification.test(alias, dest, connection, verbose)
        if retval != 0 :
            print "Error in testProducerConsumerNotification"
            if not complete : done(retval)
            result |= retval
    
        import testConfigurationProtocol
        if verbose : print "testConfigurationProtocol"
        retval = testConfigurationProtocol.test(alias, dest, connection, verbose)
        if retval != 0 :
            print "Error in testConfigurationProtocol", retval
            if not complete : done(retval)
            result |= retval
    
        import testDatagram
        if verbose : print "testDatagram"
        retval = testDatagram.test(alias, dest, connection, bufnum, verbose)
        if retval != 0 :
            print "Error in testDatagram", retval
            if not complete : done(retval)
            result |= retval
        
        import testOverlappingDatagrams
        if verbose : print "testOverlappingDatagrams"
        retval = testOverlappingDatagrams.test(alias, dest, bufnum, connection, verbose)
        if retval != 0 :
            print "Error in testOverlappingDatagrams", retval
            if not complete : done(retval)
            result |= retval

        import simpleNodeIdentificationInformation
        if verbose : print "simpleNodeIdentificationInformation"
        retval = simpleNodeIdentificationInformation.test(alias, dest, connection, verbose)
        if retval != 0 :
            print "Error in simpleNodeIdentificationInformation"
            if not complete : done(retval)
            result |= retval
        
        import testCDI
        if verbose : print "testCDI"
        retval = testCDI.test(alias, dest, connection, verbose)
        if retval != 0 :
            print "Error in testCDI"
            if not complete : done(retval)
            result |= retval
        
        import testReservedBits
        if verbose : print "testReservedBits"
        retval = testReservedBits.test(alias, nodeID, dest, connection, verbose)
        if retval != 0 :
            print "Error in testReservedBits"
            if not complete : done(retval)
            result |= retval        
        
        import unknownDatagramType
        if verbose : print "unknownDatagramType"
        retval = unknownDatagramType.test(alias, dest, connection, verbose)
        if retval != 0 :
            print "Error in unknownDatagramType"
            if not complete : done(retval)
            result |= retval
        
        import unknownMtiAddressed
        if verbose : print "unknownMtiAddressed"
        retval = unknownMtiAddressed.test(alias, dest, connection, verbose)
        if retval != 0 :
            print "Error in unknownMtiAddressed"
            if not complete : done(retval)
            result |= retval
        
        import testStandardFrame
        import time
        if verbose : print "testStandardFrame"
        retval = testStandardFrame.test(connection, verbose)
        if retval != 0 :
            print "Error in testStandardFrame"
            if not complete : done(retval)
            result |= retval
        time.sleep(3)
 
        # done last, as changes alias in use
        import testAliasConflict
        if verbose : print "testAliasConflict"
        retval = testAliasConflict.test(alias, dest, connection, verbose)
        if retval != 0 :
            print "Error in testAliasConflict"
            if not complete : done(retval)
            result |= retval

        if not repeat : break
        if verbose : print "End of pass, repeat"
        if verbose : print ""
        
    if verbose : print "Note: Did not perform testStartup, which is manual"
    if verbose : print "Note: Did not perform testForZeroAlias.py, which is slow"
    if verbose :
        if result != 0 : print "Encountered errors"
        else : print "Normal end"

    return

if __name__ == '__main__':
    main()
