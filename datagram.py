#!/usr/bin/env python
'''
Send one generic datagram

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, dest, content) :
    return canolcbutils.makeframestring(0x1D000000+alias+(dest<<12),content)
    
def makereply(alias, dest) :
    return canolcbutils.makeframestring(0x1E000000+alias+(dest<<12),[0x04])
    
def usage() :
    print ""
    print "Called standalone, will send one CAN datagram message"
    print " and display response"
    print ""
    print "Expect a single datagram reply in return"
    print "e.g. [1Esssddd] 4C"
    print "from destination alias to source alias"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-c --content message content (default 1,2,3,4)"
    print "-t find destination alias automatically"
    print "-v verbose"

import getopt, sys

def main():
    # argument processing
    content = [1,2,3,4]
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    identifynode = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:c:vt", ["dest=", "alias=", "content="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            connection.network.verbose = True
        elif opt in ("-a", "--alias"):  # needs hex processing
            alias = int(arg)
        elif opt in ("-d", "--dest"):  # needs hex processing
            dest = int(arg)
        elif opt in ("-c", "--content"):
            content = canolcbutils.splitSequence(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, nodeID = getUnderTestAlias.get(alias, None)

    # now execute
    connection.network.send(makeframe(alias, dest, content))
    while (True) :
        if (connection.network.receive() == None ) : break
    return

if __name__ == '__main__':
    main()
