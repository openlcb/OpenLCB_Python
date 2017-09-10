#!/usr/bin/env python
##
# Handle OpenLCB verifyNodeGlobal
#
# @author: Bob Jacobsen
# @author: Stuart Baker - cleaned up and modernized

import connection
import mtiDefs

import time
import optionsParsing

## run this test only
def main():
    # argument processing
    (alias, nodeID, connection, verbose, complete, repeat) = \
        optionsParsing.parse("verifyNodeGobal")

    # now execute
    retval = test(nodeID, connection)
    connection.network.close()
    exit(retval)    

## run test
# @param nodeID destination Node ID
# @param connection OpenLCB connection
def test(nodeID, connection):
    # first, send to this node
    connection.network.send(mtiDefs.OlcbMessage(mtiDefs.VERIFY_NODE_ID_GLOBAL,
                                                payload = nodeID))
    if (connection.network.expect(mti = mtiDefs.VERIFY_NODE_ID_NUMBER,
                                  source = nodeID, payload = nodeID) == None) :
        print "Global verify with matching node ID did not receive expected reply"
        return 2

    # send without node ID
    connection.network.send(mtiDefs.OlcbMessage(mtiDefs.VERIFY_NODE_ID_GLOBAL))
    if (connection.network.expect(mti = mtiDefs.VERIFY_NODE_ID_NUMBER,
                                  source = nodeID, payload = nodeID) == None) :
        print "Global verify without node ID did not receive expected reply"
        return 12


    # allow time for the bus to settle, and then flush input buffer
    time.sleep(3)
    while (connection.network.recv() != None) :
        continue

    # send with wrong node ID
    connection.network.send(mtiDefs.OlcbMessage(mtiDefs.VERIFY_NODE_ID_GLOBAL,
                                                payload = [0, 0, 0, 0, 0, 1]))
    reply = connection.network.expect(mti = mtiDefs.VERIFY_NODE_ID_NUMBER,
                                      source = nodeID, payload = nodeID)
    if (reply != None) :
        print "Global verify with wrong node ID received unexpected reply: ", \
              mtiDefs.olcb_message_to_string(reply)
        return 24

    return 0

if __name__ == '__main__':
    main()
