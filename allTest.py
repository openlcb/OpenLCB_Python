#!/usr/bin/env python
##
# Run a series of tests with an attached node. Updated by Stuart Baker.
#
# @author: Bob Jacobsen
# @aurhor: Stuart Baker

import optionsParsing
import connection
#import canolcbutils
#import defaults

'''
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
'''

def main():
    (alias, nodeID, connection, verbose, complete, repeat) = \
        optionsParsing.parse("allTest", False)

    # now execute
    result = test(alias, nodeID, connection, verbose, complete, repeat)
    done(result)    

## Cleanup the test for exit
# @param status status result from running the test
def done(status) :
    connection.network.close()
    if (status == 0) :
        print "All tests passed!!!"
    exit(status)

## Run the tests
# @param alias destination alias (None if not a Grid Connect connection)
# @param nodeID destination Node ID
# @param connection OpenLCB connection
# @param verbose True to print verbose information
# @param complete True to run all the tests to completion, regardless of failure
# @param repeat True to repeate the tests continuously until failure
def test(alias, nodeID, connection, verbose, complete, repeat):
    result = 0;
    import verifyNodeGlobal
    import verifyNodeAddressed
    tests = [["verifyNodeGlobal",    verifyNodeGlobal],
             ["verifyNodeAddressed", verifyNodeAddressed]]


    while True :

        if (alias != None) :
            # we only perform this test for Grid Connect based nodes
            import aliasMapEnquiry
            if (verbose) :
                print "aliasMapEnquiry"
            retval = aliasMapEnquiry.test(connection.network.source_alias(),
                                          alias, nodeID, connection, verbose)
            if (retval != 0) :
                print "Error in aliasMapEnquiry"
                if (complete == False) :
                    done(retval)
                result |= retval
    
        #if verbose : print "verifyNodeGlobal w no NodeID"
        #retval = verifyNodeGlobal.test(alias, None, connection)
        #if retval != 0 :
        #    print "Error in verifyNodeGlobal w no NodeID"
        #    if not complete : done(retval)
        #    result |= retval

        for x in range(len(tests)) :
            if (verbose) :
                print tests[x][0]
            retval = tests[x][1].test(nodeID, connection)
            if (retval != 0) :
                print "Error in ", tests[x][0]
                if (complete == False) :
                    done(retval)
                result |= retval
    
        '''
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

        '''
        if (repeat != True) :
            break
        if (verbose == True) :
            print "End of pass, repeat\n"
            print "Note: Did not perform testStartup, which is manual"
            print "Note: Did not perform testForZeroAlias.py, which is slow"
            if (result != 0) :
                print "Encountered errors"
            else :
                print "Normal end"        

    return result

if __name__ == '__main__':
    main()
