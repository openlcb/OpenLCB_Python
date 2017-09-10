#!/usr/bin/env python
'''
Send identifyEvents message

@author: Bob Jacobsen
@author: Stuart Baker - cleaned up and modernized
'''

import connection
import mtiDefs
import optionsParsing

## run this test only
def main():
    # argument processing
    (alias, nodeID, connection, verbose, complete, repeat) = \
        optionsParsing.parse("identifyEventsGobal")

    # now execute
    retval = test(nodeID, connection, verbose)
    connection.network.close()
    exit(retval)

## run test
# @param nodeID destination Node ID
# @param connection OpenLCB connection
# @param verbose True to print verbose information
def test(nodeID, connection, verbose) :
    network = connection.network

    network.send(mtiDefs.OlcbMessage(mtiDefs.IDENTIFY_EVENTS_GLOBAL))

    producerCount = 0
    consumerCount = 0
    producerRange = list()
    consumerRange = list()
    while (True) :
        reply = network.expect(source = nodeID)
        if (reply == None ) :
            break
        if (reply.get_mti() == mtiDefs.CONSUMER_IDENTIFIED_UNKNOWN or
            reply.get_mti() == mtiDefs.CONSUMER_IDENTIFIED_VALID or
            reply.get_mti() == mtiDefs.CONSUMER_IDENTIFIED_INVALID) :
            consumerCount = consumerCount + 1
        elif (reply.get_mti() == mtiDefs.PRODUCER_IDENTIFIED_UNKNOWN or
              reply.get_mti() == mtiDefs.PRODUCER_IDENTIFIED_VALID or
              reply.get_mti() == mtiDefs.PRODUCER_IDENTIFIED_INVALID) :
            producerCount = producerCount + 1
        elif (reply.get_mti() == CONSUMER_RANGE_IDENTIFIED) :
            consumerRange.append(reply.get_event_value())
        elif (reply.get_mti() == PRODUCER_RANGE_IDENTIFIED) :
            producerRange.append(reply.get_event_value())

    if (verbose) :
        # print what we found
        print "  Found", consumerCount,"consumer events"
        print "  Found", producerCount,"producer events"
        for a in consumerRange :
            i = 4
            if ((a % 2) == 0) :
                while (True) :
                    if ((a % i) != 0) :
                        break;
                    i = i * 2
            else :
                while (True) :
                    if ((a % i) == 0) :
                        break;
                    i = i * 2
            mask = (i / 2) - 1
            base = a & ~mask
            print "  Found consumer range", \
                  '{0:8x}'.format(base), "-", \
                  '{0:8x}'.format(base + mask)
        for a in producerRange :
            i = 4
            if ((a % 2) == 0) :
                while (True) :
                    if ((a % i) != 0) :
                        break;
                    i = i * 2
            else :
                while (True) :
                    if ((a % i) == 0) :
                        break;
                    i = i * 2
            mask = (i / 2) - 1
            base = a & ~mask
            print "  Found producer range", \
                  '{0:8x}'.format(base), "-", \
                  '{0:8x}'.format(base + mask)

    return 0

if __name__ == '__main__':
    main()
