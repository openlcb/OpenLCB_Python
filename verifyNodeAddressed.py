#!/usr/bin/env python
'''
OpenLCB VerifyNodeAddressed message

@author: Bob Jacobsen
@author: Stuart Baker - cleaned up and modernized
'''

import connection as connection
import canolcbutils
import copy

def makeframe(alias, dest, nodeID) :
    body = [(dest>>8)&0xFF, dest&0xFF]
    if nodeID != None : body = body+nodeID
    return canolcbutils.makeframestring(0x19488000+alias,body)

from optparse import OptionParser

def main():
    nodeID = connection.testNodeID
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias

    # argument processing
    usage = "usage: %prog [options]\n\n" + \
            "Called standalone, will send one CAN VerifyNode (addressed) " + \
            "message.\n\n" + \
            "Expect a single VerifiedNode reply in return\n" + \
            "  e.g. [180B7sss] nn nn nn nn nn nn\n" + \
            "containing dest alias and NodeID\n\n" + \
            "valid usages (default values):\n" + \
            "  ./verifyNodeAddressed.py\n" + \
            "  ./verifyNodeAddressed.py -a 0xAAA\n" + \
            "  ./verifyNodeAddressed.py -a 0xAAA -d 0x5F9\n" + \
            "  ./verifyNodeAddressed.py -a 0xAAA -d 0x5F9 " + \
            "-n 0x2 0x1 0x99 0xff 0x00 0x1e\n\n" + \
            "Default connection detail taken from connection.py"

    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--alias", dest="alias", metavar="ALIAS",
                      default=connection.thisNodeAlias, type = int,
                      help="source alias")
    parser.add_option("-d", "--dest", dest="dest", metavar="ALIAS",
                      default=connection.testNodeAlias, type = int,
                      help="destination alias")
    parser.add_option("-n", "--node", dest="nodeid",
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
        dest, nodeID = getUnderTestAlias.get(alias, None, options.verbose or options.veryverbose)

    retval = test(alias, dest, nodeID, connection,
                  options.verbose)
    connection.network.close()
    exit(retval)

def test(alias, dest, nodeID, connection, verbose) :
    # send correct address, correct node ID in body
    connection.network.send(makeframe(alias, dest, nodeID))
    expect = canolcbutils.makeframestring(0x19170000 + dest, nodeID)
    if (connection.network.expect(startswith=expect) == None) :
        print ("Expected reply "+expect+" to correct alias & correct ID not received")
        return 2

    # send correct address, no node ID in body
    connection.network.send(makeframe(alias, dest, None))
    if (connection.network.expect(startswith=":X19170", data=nodeID) == None) :
        print ("Expected reply to correct alias & no ID not received")
        return 2

    # send correct address, wrong node ID in body
    tnodeID = copy.copy(nodeID)
    tnodeID[0] = tnodeID[0]^1

    connection.network.send(makeframe(alias, dest, tnodeID))
    if (connection.network.expect(startswith=":X19170", data=nodeID) == None) :
        print ("Expected reply to correct alias & incorrect ID not received")
        return 2

    # repeat all three with invalid alias
    connection.network.send(makeframe(alias, (~dest)&0xFFF, nodeID))
    expect = canolcbutils.makeframestring(0x19170000 + dest, nodeID)
    reply = connection.network.expect(startswith=expect)
    if (reply != None) :
        print ("Unexpected reply received on incorrect alias, OK nodeID", reply)
        return 1

    connection.network.send(makeframe(alias, (~dest)&0xFFF, None))
    reply = connection.network.expect(startswith=":X19170", data=nodeID)
    if (reply != None) :
        print ("Unexpected reply received on incorrect alias, no nodeID", reply)
        return 1

    connection.network.send(makeframe(alias, (~dest)&0xFFF, tnodeID))
    reply = connection.network.expect(startswith=":X19170", data=nodeID)
    if (reply != None) :
        print ("Unexpected reply received on incorrect alias, wrong nodeID", reply)
        return 1

    return 0

if __name__ == '__main__':
    main()
