#!/usr/bin/env python
'''
OpenLCB VerifyNodeAddressed message

@author: Bob Jacobsen
@author: Stuart Baker - cleaned up and modernized
'''

import connection
import mtiDefs
import optionsParsing

import time
import copy

#def makeframe(alias, dest, nodeID) :
#    body = [(dest>>8)&0xFF, dest&0xFF]
#    if nodeID != None : body = body+nodeID
#    return canolcbutils.makeframestring(0x19488000+alias,body)

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
def test(nodeID, connection) :
    # send correct address, node ID in the body
    connection.network.send(mtiDefs.OlcbMessage(mtiDefs.VERIFY_NODE_ID_ADDRESSED,
                                                dest = nodeID, payload = nodeID))
    if (connection.network.expect(mti = mtiDefs.VERIFY_NODE_ID_NUMBER,
                                  source = nodeID, payload = nodeID) == None) :
        print "Expected reply to correct alias & correct ID not received"
        return 2

    connection.network.send(mtiDefs.OlcbMessage(mtiDefs.VERIFY_NODE_ID_ADDRESSED,
                                                dest = nodeID))
    # send correct address, no node ID in body
    if (connection.network.expect(mti = mtiDefs.VERIFY_NODE_ID_NUMBER,
                                  source = nodeID, payload = nodeID) == None) :
        print "Expected reply to correct alias & no ID not received"
        return 2

    # send correct address, wrong node ID in body
    tnodeID = copy.copy(nodeID)
    tnodeID[0] = tnodeID[0]^1
    
    connection.network.send(mtiDefs.OlcbMessage(mtiDefs.VERIFY_NODE_ID_ADDRESSED,
                                                dest = nodeID, payload = tnodeID))
    if (connection.network.expect(mti = mtiDefs.VERIFY_NODE_ID_NUMBER,
                                  source = nodeID, payload = nodeID) == None) :
        print "Expected reply to correct alias & incorrect ID not received"
        return 2


    # repeate all three with invalid node ID, use our own ID
    invalidID = connection.network.get_node_id_self()
    connection.network.send(mtiDefs.OlcbMessage(mtiDefs.VERIFY_NODE_ID_ADDRESSED,
                                                dest = invalidID,
                                                payload = nodeID))
    reply = connection.network.expect(mti = mtiDefs.VERIFY_NODE_ID_NUMBER,
                                  source = nodeID, payload = nodeID)
    if (reply != None) :
        print "Unexpected reply received on incorrect Node ID, OK nodeID", reply
        return 1
    
    connection.network.send(mtiDefs.OlcbMessage(mtiDefs.VERIFY_NODE_ID_ADDRESSED,
                                                dest = invalidID))
    reply = connection.network.expect(mti = mtiDefs.VERIFY_NODE_ID_NUMBER,
                                      source = nodeID, payload = nodeID)
    if (reply != None) :
        print "Unexpected reply received on incorrect Node ID, no nodeID", reply
        return 1
    
    connection.network.send(mtiDefs.OlcbMessage(mtiDefs.VERIFY_NODE_ID_ADDRESSED,
                                                dest = invalidID,
                                                payload = tnodeID))
    reply = connection.network.expect(mti = mtiDefs.VERIFY_NODE_ID_NUMBER,
                                      source = nodeID, payload = nodeID)
    if (reply != None) :
        print "Unexpected reply received on incorrect Node ID, wrong nodeID", \
              reply
        return 1

    return 0

if __name__ == '__main__':
    main()
