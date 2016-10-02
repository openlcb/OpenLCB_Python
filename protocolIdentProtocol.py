#!/usr/bin/env python
'''
OpenLCB ProtocolIdentificationProtocol message

@author: Bob Jacobsen
@author: Stuart Baker - cleaned up and modernized
'''

import connection as connection
import canolcbutils

def makeframe(alias, dest) :
    body = [(dest>>8)&0xFF, dest&0xFF]
    return canolcbutils.makeframestring(0x19828000+alias,body)
    
from optparse import OptionParser

def main():
    # argument processing
    usage = "usage: %prog [options]\n\n" + \
            "Called standalone, will send one CAN " + \
            "ProtocolIdentProtocol (addressed) message.\n\n" + \
            "Expect a single ProtocolIdentProtocol reply in return\n" + \
            "  e.g. [180B7sss] nn nn nn nn nn nn\n" + \
            "containing protocols supported\n\n" + \
            "valid usages (default values):\n" + \
            "  ./protocolIdentProtocol.py\n" + \
            "  ./protocolIdentProtocol.py -a 0xAAA\n" + \
            "  ./protocolIdentProtocol.py -a 0xAAA -d 0x5F9\n\n" + \
            "Default connection detail taken from connection.py"

    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--alias", dest="alias", metavar="ALIAS",
                      default=connection.thisNodeAlias, type = int,
                      help="source alias")
    parser.add_option("-d", "--dest", dest="dest", metavar="ALIAS",
                      default=connection.testNodeAlias, type = int,
                      help="destination alias")
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

    '''
    @todo identifynode option not currently implemented
    '''
    #if identifynode :
    #    import getUnderTestAlias
    #    dest, otherNodeId = getUnderTestAlias.get(alias, None, verbose)

    retval = test(options.alias, options.dest, connection, options.verbose)
    connection.network.close()
    exit(retval)
    
def test(alias, dest, connection, verbose) :
    connection.network.send(makeframe(alias, dest))
    body = [(alias>>8)&0xFF, alias&0xFF]
    expect = canolcbutils.makeframestring(0x19668000 + dest, body)
    expect = expect[:-1]
    reply = connection.network.expect(startswith=expect)
    if (reply == None) :
        print "Expected reply to good request not received"
        return 2
    if (verbose) : 
        print "  Node supports:"
        value = canolcbutils.bodyArray(reply)
        if (value[2] & 0x80) != 0 : print "      Protocol Identification"
        if (value[2] & 0x40) != 0 : print "      Datagram Protocol"
        if (value[2] & 0x20) != 0 : print "      Stream Protocol"
        if (value[2] & 0x10) != 0 : print "      Memory Configuration Protocol"
        if (value[2] & 0x08) != 0 : print "      Reservation Protocol"
        if (value[2] & 0x04) != 0 : print "      Event Exchange (P/C) Protocol"
        if (value[2] & 0x02) != 0 : print "      Identification Protocol"
        if (value[2] & 0x01) != 0 : print "      Teaching/Learning Protocol"
        if (value[3] & 0x80) != 0 : print "      Remote Button Protocol"
        if (value[3] & 0x40) != 0 : print "      Abbreviated Default CDI Protocol"
        if (value[3] & 0x20) != 0 : print "      Display Protocol"
        if (value[3] & 0x10) != 0 : print "      Simple Node Information Protocol"
        if (value[3] & 0x08) != 0 : print "      Configuration Description Information"
        if (value[3] & 0x04) != 0 : print "      Traction Control Protocol"
        if (value[3] & 0x02) != 0 : print "      Function Description Information"
        if (value[3] & 0x01) != 0 : print "      DCC Command Station Protocol"
        if (value[4] & 0x80) != 0 : print "      SimpleTrain Node Information"
        if (value[4] & 0x40) != 0 : print "      Function Configuration"
        if (value[4] & 0x20) != 0 : print "      Firmware Upgrade Protocol"
        if (value[4] & 0x10) != 0 : print "      Firmware Upgrade Active"

    if (verbose) :
        print "  not addressed, expect no reply"
    connection.network.send(makeframe(alias, (~dest)&0xFFF))
    body = [(alias>>8)&0xFF, alias&0xFF]
    expect = canolcbutils.makeframestring(0x19668000 + dest, body)
    expect = expect[:-1]
    reply = connection.network.expect(startswith=expect)
    if (reply != None ) : 
        print "Unexpected reply received to request to different node ", reply
        return 1

    return 0

if __name__ == '__main__':
    main()
