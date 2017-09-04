#!/usr/bin/env python
'''
OpenLCB AliasMapEquiry frame

@author: Bob Jacobsen
@author: Stuart Baker - cleaned up and modernized
'''

import connection as connection
import canolcbutils

'''
Make an Alias Map Enquery (AME) frame.

@param alias alias of self
@param nodeID node id to enquire about
@return string of CAN Grid Connect bytes to send
'''
def makeframe(alias, nodeID) :
    return canolcbutils.makeframestring(0x10702000+alias,nodeID)

from optparse import OptionParser

'''
Program entry point.
'''
def main():
    # argument processing
    usage = "usage: %prog [options]\n\n" + \
            "Called standalone, will send one CAN AliasMapEquiry frame \n" + \
            "and display response\n\n" + \
            "Expect a single frame in return\n" + \
            "  e.g. [180B7sss] nn nn nn nn nn nn\n" + \
            "containing dest alias and NodeID\n\n" + \
            "valid usages (default values):\n" + \
            "  ./aliasMapEnquiry.py\n" + \
            "  ./aliasMapEnquiry.py -a 0xAAA\n" + \
            "  ./aliasMapEnquiry.py -a 0xAAA -d 0x5F9\n" + \
            "  ./aliasMapEnquiry.py -a 0xAAA -d 0x5F9 " + \
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
                      help="find destination alias and NodeID automatically")
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

    '''
    @todo identifynode option not currently implemented
    '''
    #if options.identifynode :
    #    import getUnderTestAlias
    #    options.dest, otherNodeId = getUnderTestAlias.get(options.alias,
    #                                                      None,
    #                                                      options.verbose)
    #    if options.nodeid == None :
    #        options.nodeid = otherNodeId

    retval = test(options.alias, options.dest, options.nodeid, connection,
                  options.verbose)
    #connection.network.close()
    exit(retval)
    
def test(alias, dest, nodeID, connection, verbose) :
    # check with node id in frame
    connection.network.raw_send(makeframe(alias, nodeID))
    expect = canolcbutils.makeframestring(0x10701000 + dest, nodeID)
    if (connection.network.raw_expect(exact=expect) == None) :
        print "Expected reply when node ID matches not received"
        return 2

    # check without node id in frame 
    connection.network.raw_send(makeframe(alias, None))
    expect = canolcbutils.makeframestring(0x10701000 + dest, nodeID)
    if (connection.network.raw_expect(exact=expect) == None) :
        print "Expected reply when node ID matches not received"
        return 2

    # test non-matching NodeID using a reserved one
    connection.network.raw_send(makeframe(alias, [0,0,0,0,0,1]))
    expect = canolcbutils.makeframestring(0x10701000 + dest, nodeID)
    reply = connection.network.raw_expect(startswith=expect)
    if (reply != None) :
        print "Unexpected reply received when node ID didnt match ", reply
        return 2
        
    return 0

if __name__ == '__main__':
    main()
