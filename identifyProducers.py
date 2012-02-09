#!/usr/bin/env python
'''
Send identifyProducers message

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, eventID) :
    return canolcbutils.makeframestring(0x1828F000+alias,eventID)
    
def usage() :
    print ""
    print "Called standalone, will send one CAN IdentifyProducer message"
    print " and display response"
    print ""
    print "Expect zero or more ProducerIdentified reply in return"
    print "e.g. [1926Bsss] nn nn nn nn nn nn"
    print "containing dest alias and EventID"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-e --event eventID as 1.2.3.4.5.6.7.8 form"
    print "-v verbose"

import getopt, sys

def main():
    alias = connection.thisNodeAlias
    event = [1,2,3,4,5,6,7,8]
    
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "e:a:vt", ["alias=", "event="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            connection.network.verbose = True
        elif opt in ("-a", "--alias"):
            alias = int(arg) # needs hex decode
        elif opt in ("-e", "--event"):
            event = canolcbutils.splitSequence(arg)
        else:
            assert False, "unhandled option"

    # now execute
    connection.network.send(makeframe(alias,event))
    while (True) :
        if (connection.network.receive() == None ) : break
    return

if __name__ == '__main__':
    main()
