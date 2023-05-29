#!/usr/bin/env python
'''
Handle OpenLCB verifyNodeGlobal

@author: Bob Jacobsen
@author: Stuart Baker - cleaned up and modernized
'''

import connection as connection
import canolcbutils

'''
Make a Verify Node ID Global frame.

@param alias alias of self
@param nodeID node id to enquire about
@return string of CAN Grid Connect bytes to send
'''
def makeframe(alias, nodeID) :
    return canolcbutils.makeframestring(0x19490000+alias,nodeID)

import time
from optparse import OptionParser

def main():

    # argument processing
    usage = "usage: %prog [options]\n\n" + \
            "Called standalone, will send one CAN VerifyNode (Global) " + \
            "message.\n\n" + \
            "Expect a single VerifiedNode reply in return\n" + \
            "  e.g. [180B7sss] nn nn nn nn nn nn\n" + \
            "containing dest alias and NodeID\n\n" + \
            "valid usages (default values):\n" + \
            "  ./verifyNodeGlobal.py\n" + \
            "  ./verifyNodeGlobal.py -a 0xAAA\n" + \
            "  ./verifyNodeGlobal.py -a 0xAAA " + \
            "-n 0x2 0x1 0x99 0xff 0x00 0x1e\n\n" + \
            "Default connection detail taken from connection.py"

    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--alias", dest="alias", metavar="ALIAS",
                      default=connection.thisNodeAlias, type = int,
                      help="source alias")
    parser.add_option("-n", "--node", dest="nodeID",
                      metavar="0x1 0x2 0x3 0x4 0x5 0x6",
                      default=connection.testNodeID, type=int, nargs=6,
                      help="destination Node ID")
    parser.add_option("-t", "--auto", action="store_true", dest="identifynode",
                      default=False,
                      help="find destination NodeID automatically")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False,
                      help="print verbose debug information")
    parser.add_option("-V", "--veryverbose",
                      action="store_true", dest="veryverbose",
                      default=False,
                      help="print very verbose debug information")

    (options, args) = parser.parse_args()

    if options.veryverbose :
        connection.network.verbose = True

    if options.identifynode :
        import getUnderTestAlias
        options.dest, options.nodeID = getUnderTestAlias.get(options.alias, None, options.verbose or options.veryverbose)

    # now execute
    retval = test(options.alias, options.nodeID, connection)
    connection.network.close()
    exit(retval)

def test(alias, nodeID, connection):
    # first, send to this node
    connection.network.send(makeframe(alias, nodeID))
    if (connection.network.expect(startswith=":X19170", data=nodeID) == None) :
        print ("Global verify with matching node ID did not receive expected reply")
        return 2

    # send without node ID
    connection.network.send(makeframe(alias, None))
    if (connection.network.expect(startswith=":X19170", data=nodeID) == None) :
        print ("Global verify without node ID did not receive expected reply")
        return 12

    # allow time for the bus to settle
    time.sleep(3)
    while connection.network.receive() != None :
        continue

    # send with wrong node ID
    connection.network.send(makeframe(alias, [0,0,0,0,0,1]))
    reply = connection.network.expect(startswith=":X19170")
    if (reply == None) :
        return 0
    else :
        print ("Global verify with wrong node ID should not receive reply but did: ", reply)
        return 24

if __name__ == '__main__':
    main()
