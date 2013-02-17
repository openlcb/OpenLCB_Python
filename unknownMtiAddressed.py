#!/usr/bin/env python
'''
Check that unknown (unallocated) MTIs get a reject message

Tests that implementor has not grabbed MTIs for their own purposes

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, dest, mti) :
    return canolcbutils.makeframestring(0x19000000+alias+(mti<<12),[(dest>>8)&0xFF, dest&0xFF])
    
def usage() :
    print ""
    print "Called standalone, will send one CAN message with unknown MTI"
    print " and display response"
    print ""
    print "Expect a single error reply in return"
    print "e.g. [1Edddsss] 0C nn nn nn nn nn nn"
    print "containing dest alias and error info"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-n --node dest nodeID (default 01.02.03.04.05.06)"
    print "-t find destination alias automatically"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

knownMti = [0x488, 0x068, 0x0A8, 0x828, 0x628, 0x968, 0xDE8, 0xA08, 0xA28, 0xA48, 0xCC8, 0x868, 0x888, 0x8A8]

def main():
    # argument processing
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    identifynode = False
    verbose = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:vVt", ["alias=", "dest="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt == "-V":
            connection.network.verbose = True
            verbose = True
        elif opt in ("-a", "--alias"): # needs hex processing
            alias = int(arg)
        elif opt in ("-d", "--dest"): # needs hex processing
            dest = int(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)

    retval = test(alias, dest, connection, verbose)
    connection.network.close()
    exit(retval)
    
def test(alias, dest, connection, verbose) :
    for mti in range(0,4096) :
        if mti in knownMti : continue
        if (mti&0x08) == 0 : continue
        frame = makeframe(alias, dest, mti)
        connection.network.send(frame)
        reply = connection.network.receive()
        if reply == None : 
            print "No reply received for ", mti, "expected OIR"
            return 2
        if  (not reply.startswith(":X19068")) or reply[12:15] != frame[7:10] or reply[7:10] != frame[12:15] : 
            print "Wrong reply received for", mti, "was", reply
            return 4
    return 0

if __name__ == '__main__':
    main()
