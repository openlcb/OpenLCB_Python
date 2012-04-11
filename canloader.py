#!/usr/bin/env python
'''
Load firmware to OpenLCB device using FLIP CAN ISP protocol

@author: D.E. Goodman-Wilson
@author: Bob Jacobsen
'''

import connection as connection
from canbootloaderutils import *

CAN_ID_SELECT_NODE = 0x00
CAN_ID_PROG_START = 0x01
CAN_ID_PROG_DATA = 0x02
CAN_ID_DISPLAY_DATA = 0x03
CAN_ID_START_APPLICATION = 0x04
CAN_ID_SELECT_MEM_PAGE = 0x06
CAN_ID_ERROR = 0x06

def sendIDSelectNode(CRIS, NNB, connection, verbose) :
    frame = makeframestring(CRIS, CAN_ID_SELECT_NODE, [NNB])
    response = False
    while(not response):
      connection.network.send(frame)
      resp_frame = connection.network.receive()
      if(resp_frame != None):
	response = True

    
def usage() :
    print ""
    print "TODO Called standalone, will send one CAN datagram message"
    print " and display response."
    print ""
    print "Expect a single datagram reply in return"
    print "e.g. [1Esssddd] 4C"
    print "from destination alias to source alias"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-t find destination alias semi-automatically"
    print "-v verbose"
    print "-V Very verbose"


if __name__ == '__main__':
    import getopt, sys
    # argument processing
    dest = connection.testNodeAlias
   
    verbose = False
    identifynode = False 
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:vVt", ["dest=", "alias=", "content="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt == "-V" :
            connection.network.verbose = True
            verbose = True
        elif opt in ("-d", "--dest"):  # needs hex processing
            dest = int(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

#    if identifynode :
#        import getUnderTestAlias
#        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)

############ main code
    CRIS = dest>>4
    NNB = dest & 0x0F
    sendIDSelectNode(0x00, 0xFF, connection, verbose)
