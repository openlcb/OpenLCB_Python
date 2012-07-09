#!/usr/bin/env python
'''
Check that unknown (unallocated) MTIs get a reject message

Tests that implementor has not grabbed MTIs for their own purposes

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, dest, mti) :
    return canolcbutils.makeframestring(0x1E000000+alias+(dest<<12),[mti])
    
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

knownMti = [0x0A, 0x0C, 0x0D, 0x2B, 0x2E, 0x2F, 0x4C, 0x4D, 0x4E, 0x4F, 0x52, 0x53, 0x6A, 0x6B]

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
    for mti in range(0,256) :
        if mti in knownMti : continue
        frame = makeframe(alias, dest, mti)
        connection.network.send(frame)
        reply = connection.network.receive()
        if reply == None : 
            print "Expected reply not received for", mti
            return 2
        if  (not reply.startswith(":X1E")) or reply[11:13] != "0C" or reply[4:7] != frame[7:10] or reply[7:10] != frame[4:7] : 
            print "Wrong reply received for", mti, "was", reply
            return 4
    return 0

if __name__ == '__main__':
    main()
