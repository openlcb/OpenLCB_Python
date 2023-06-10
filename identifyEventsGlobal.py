#!/usr/bin/env python
'''
Send identifyEvents message

@author: Bob Jacobsen
@author: Stuart Baker - cleaned up and modernized
'''

import connection as connection
import canolcbutils

def makeframe(alias) :
    return canolcbutils.makeframestring(0x19970000+alias, None)

from optparse import OptionParser

'''
Program entry point.
'''
def main():
    # argument processing
    usage = "usage: %prog [options]\n\n" + \
            "Called standalone, will send one CAN IdentifyEvents (global) \n" + \
            "message and display response\n\n" + \
            "Expect zero or more ConsumerIdenfified replies in return\n" + \
            "  e.g. [194C4sss] nn nn nn nn nn nn\n" + \
            "containing dest alias and EventID\n\n" + \
            "Expect zero or more ProducerIdenfified replies in return\n" + \
            "  e.g. [19544sss] nn nn nn nn nn nn\n" + \
            "containing dest alias and EventID\n\n" + \
            "valid usages (default values):\n" + \
            "  ./identifyEventsGlobal.py\n" + \
            "  ./identifyEventsGlobal.py -a 0xAAA\n" + \
            "  ./identifyEventsGlobal.py -a 0xAAA -d 0x5F9\n\n" + \
            "Default connection detail taken from connection.py"

    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--alias", dest="alias", metavar="ALIAS",
                      default=connection.thisNodeAlias, type = int,
                      help="source alias")
    parser.add_option("-d", "--dest", dest="dest", metavar="ALIAS",
                      default=connection.testNodeAlias, type = int,
                      help="destination alias")
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

    retval = test(options.alias, options.dest, connection, options.verbose)
    connection.network.close()
    exit(retval)

def test(alias, dest, connection, verbose) :
    # now execute
    connection.network.send(makeframe(alias))
    producerCount = 0
    consumerCount = 0
    producerRange = list()
    consumerRange = list()
    while (True) :
        reply = connection.network.expect(startswith=':X19')
        if (reply == None ) :
            break
        if (int(reply[7:10],16) != dest) :
            continue
        if (reply.startswith(':X194C7') or reply.startswith(':X194C4') or
            reply.startswith(':X194C5')) :
            consumerCount = consumerCount + 1
        if (reply.startswith(':X19547') or reply.startswith(':X19544') or
            reply.startswith(':X19545')) :
            producerCount = producerCount + 1
        if (reply.startswith(':X194A4')) :
            consumerRange.append(int(reply[11:27],16))
        if (reply.startswith(':X19524')) :
            producerRange.append(int(reply[11:27],16))
    if (verbose) :
        print("  Found", consumerCount,"consumer events")
        print("  Found", producerCount,"producer events")
        for a in consumerRange :
            i = 4
            if ((a % 2) == 0) :
                while (True) :
                    if ((a % i) != 0) :
                        break;
                    i = i * 2
            else :
                while (True) :
                    if ((a % i) != i-1) :
                        break;
                    i = i * 2
            mask = int(i / 2) - 1
            base = a & ~mask
            print("  Found consumer range", \
                  '{0:8x}'.format(base), "-", \
                  '{0:8x}'.format(base + mask))
        for a in producerRange :
            i = 4
            if ((a % 2) == 0) :
                while (True) :
                    if ((a % i) != 0) :
                        break;
                    i = i * 2
            else :
                while (True) :
                    if ((a % i) != i-1) :
                        break;
                    i = i * 2
            mask = int(i / 2) - 1
            base = a & ~mask
            print("  Found producer range", \
                  '{0:8x}'.format(base), "-", \
                  '{0:8x}'.format(base + mask))

    return 0

if __name__ == '__main__':
    main()
