#!/usr/bin/env python
'''
OpenLCB ProtocolIdentificationProtocol message

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
        optionsParsing.parse("verifyNodeGobal")

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

    network.send(mtiDefs.OlcbMessage(mtiDefs.PROTOCOL_SUPPORT_INQUIRY,
                                     dest = nodeID))
    reply = network.expect(mti = mtiDefs.PROTOCOL_SUPPORT_REPLY,
                           source = nodeID)

    if (reply == None) :
        print "Expected reply to good request not received"
        return 2
    if (verbose) : 
        print "  Node supports:"
        value = reply.get_payload()
        if (value[0] & 0x80) != 0 :
            print "      Protocol Identification"
        if (value[0] & 0x40) != 0 :
            print "      Datagram Protocol"
        if (value[0] & 0x20) != 0 :
            print "      Stream Protocol"
        if (value[0] & 0x10) != 0 :
            print "      Memory Configuration Protocol"
        if (value[0] & 0x08) != 0 :
            print "      Reservation Protocol"
        if (value[0] & 0x04) != 0 :
            print "      Event Exchange (P/C) Protocol"
        if (value[0] & 0x02) != 0 :
            print "      Identification Protocol"
        if (value[0] & 0x01) != 0 :
            print "      Teaching/Learning Protocol"
        if (value[1] & 0x80) != 0 :
            print "      Remote Button Protocol"
        if (value[1] & 0x40) != 0 :
            print "      Abbreviated Default CDI Protocol"
        if (value[1] & 0x20) != 0 :
            print "      Display Protocol"
        if (value[1] & 0x10) != 0 :
            print "      Simple Node Information Protocol"
        if (value[1] & 0x08) != 0 :
            print "      Configuration Description Information"
        if (value[1] & 0x04) != 0 :
            print "      Traction Control Protocol"
        if (value[1] & 0x02) != 0 :
            print "      Function Description Information"
        if (value[1] & 0x01) != 0 :
            print "      DCC Command Station Protocol"
        if (value[2] & 0x80) != 0 :
            print "      SimpleTrain Node Information"
        if (value[2] & 0x40) != 0 :
            print "      Function Configuration"
        if (value[2] & 0x20) != 0 :
            print "      Firmware Upgrade Protocol"
        if (value[2] & 0x10) != 0 :
            print "      Firmware Upgrade Active"

    
    # repeate invalid node ID, use our own ID
    invalidID = connection.network.get_node_id_self()
    if (verbose) :
        print "  not addressed, expect no reply"

    network.send(mtiDefs.OlcbMessage(mtiDefs.PROTOCOL_SUPPORT_INQUIRY,
                                     dest = invalidID))
    reply = network.expect(mti = mtiDefs.PROTOCOL_SUPPORT_REPLY,
                           source = nodeID)

    if (reply != None ) : 
        print "Unexpected reply received to request to different node ", reply
        return 1

    return 0

if __name__ == '__main__':
    main()
