from optparse import OptionParser

import connection
import canolcbutils

def parse(command, simple=True):
    usage =  "usage: %prog [options]\n\n" + \
             "Will sequence through a set of tests " + \
             "and display the response.\n\n" + \
             "valid usage examples:\n" + \
             "  ./" + command + " -d /dev/ttyACM0 -n 2.1.99.ff.0.1e\n" + \
             "  ./" + command + " -i 192.168.1.101 -n 2.1.99.ff.0.1e\n" + \
             "  ./" + command + " -g 192.168.1.101 -n 2.1.99.ff.0.1e\n" + \
             "  ./" + command + " -p 3002 -g localhost" + \
                                " -n 2.1.99.ff.0.1e\n" + \
             "  ./" + command + " -d /dev/ttyACM0 -n 2.1.99.ff.0.1e -v\n" + \
             "  ./" + command + " -d /dev/ttyACM0 -n 2.1.99.ff.0.1e -V\n"

    if (not simple) :
        usage += \
             "  ./" + command + " -d /dev/ttyACM0 -n 2.1.99.ff.0.1e -c\n" + \
             "  ./" + command + " -d /dev/ttyACM0 -n 2.1.99.ff.0.1e -c -v\n" + \
             "  ./" + command + " -d /dev/ttyACM0 -n 2.1.99.ff.0.1e -c -V\n" + \
             "  ./" + command + " -d /dev/ttyACM0 -n 2.1.99.ff.0.1e -r\n" + \
             "  ./" + command + " -d /dev/ttyACM0 -n 2.1.99.ff.0.1e -r -v\n" + \
             "  ./" + command + " -d /dev/ttyACM0 -n 2.1.99.ff.0.1e -r -V\n"

    usage += "\nDefault connection detail taken from connection.py"

    parser = OptionParser(usage=usage)
    parser.add_option("-p", "--port", dest="port", metavar="12021",
                      default=12021,
                      help="port number for TCP connection")
    parser.add_option("-i", "--ip", dest="host", metavar="127.0.0.1",
                      default=None,
                      help="hostname or IP to make native TCP connection with")
    parser.add_option("-g", "--gridconnect", dest="gchost", metavar="127.0.0.1",
                      default=None,
                      help="hostname or IP to make Grid Connect TCP " +
                           "connection with")
    parser.add_option("-d", "--device", dest="device", metavar="/dev/ttyACM0",
                      default=None,
                      help="TTY device make a Grid Connect connection with")
    parser.add_option("-n", "--node", dest="nodeid", metavar="2.1.99.ff.0.1e",
                      default="1.2.3.4.5.6",
                      help="destination Node ID")
    parser.add_option("-a", "--alias", dest="alias", metavar="0x123",
                      default=None,
                      help="destination alias, by default, auto-discover")
    if (not simple) :
        parser.add_option("-c", "--complete", action="store_true",
                          dest="complete", default=False,
                          help="continue after error, run to completion")
        parser.add_option("-r", "--repeat", action="store_true", dest="repeat",
                          default=False,
                          help="run until error, repeat until failure")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False,
                      help="print verbose debug information")
    parser.add_option("-V", "--veryverbose", action="store_true",
                      dest="veryverbose", default=False,
                      help="print very verbose debug information")

    (options, args) = parser.parse_args()

    if (simple) :
        options.repeat = False
        options.complete = False


    if ((options.repeat == True and options.complete == True) or
        (options.device != None and options.gchost != None) or
        (options.device != None and options.host != None) or
        (options.gchost != None and options.host != None) or
        (options.alias != None and options.gchost == None and
         options.device == None)):
        parser.error('Invalid option combination')

    if (options.alias != None) :
        if (options.alias == 0 or options.alias == 0xFFF) :
            parser.error('Invalid alias specified')

    if (options.veryverbose) :
        options.verbose = True

    nodeID = canolcbutils.splitSequence(options.nodeid)
    alias = options.alias
    repeat = options.repeat
    complete = options.complete
    verbose = options.verbose

    connection.establish([1, 2, 3, 4, 5, 6], options.gchost, options.host,
                         options.port,
                         options.device, options.verbose, options.veryverbose)

    if ((options.gchost != None or options.device != None) and alias == None) :
        # auto-discover the destination node alias
        alias = connection.network.dest_alias(nodeID)
        alias_string = "Destination Alias: 0x" + \
                       ("000" + (hex(alias).upper()[2:]))[-3:]
        print alias_string

    # argument processing
    return (alias, nodeID, connection, verbose, complete, repeat)

