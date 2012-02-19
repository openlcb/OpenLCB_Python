#!/usr/bin/env python
'''
Extensive datagram testing using the Memory Config Protocol to generate return datagrams

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makepartialframe(alias, dest, content) :
    return canolcbutils.makeframestring(0x1C000000+alias+(dest<<12),content)
    
def makefinalframe(alias, dest, content) :
    return canolcbutils.makeframestring(0x1D000000+alias+(dest<<12),content)

def makereply(alias, dest) :
    return canolcbutils.makeframestring(0x1E000000+alias+(dest<<12),[0x4C])

def isreply(frame) :
    return frame.startswith(":X1E") and frame[11:13] == "4C"

def sendOneDatagram(alias, dest, content, connection, verbose) :
    while len(content) > 8 :
        frame = makepartialframe(alias, dest, content[0:8])
        connection.network.send(frame)
        content = content[8:]

    frame = makefinalframe(alias, dest, content)
    connection.network.send(frame)
        
    frame = connection.network.receive()
    if frame == None : 
        print "Did not receive reply"
        return 1
    if not isreply(frame) :
        print "Unexpected message received instead of reply"
        return 2
    return 0

def receiveOneDatagram(alias, dest, conection, verbose) :
    retval = []
    while True :
        reply = connection.network.receive()
        if (reply == None ) : 
            print "No datagram segment received"
            return 4
        elif reply.startswith(":X1C") :
            retval = retval + canolcbutils.bodyArray(reply)
            continue
        elif reply.startswith(":X1D") :
            retval = retval + canolcbutils.bodyArray(reply)
            connection.network.send(makereply(alias, dest))
            return retval
        else :
            print "Unexpected message instead of datagram segment", reply
            return 3

    
def usage() :
    print ""
    print "Extensive datagram testing using the Memory Config Protocol"
    print "to generate return datagrams"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-t find destination alias automatically"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

def main():
    # argument processing
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    identifynode = False
    verbose = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:vVt", ["dest=", "alias=", "content="])
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
        elif opt in ("-a", "--alias"):  # needs hex processing
            alias = int(arg)
        elif opt in ("-d", "--dest"):  # needs hex processing
            dest = int(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)

    exit( test(alias, dest, connection, verbose) )

import datagram

def checkreply(alias, dest, connection, verbose) :
    frame = connection.network.receive()
    if frame == None : 
        print "Did not receive reply"
        return 1
    if not isreply(frame) :
        print "Unexpected message received instead of reply"
        return 2
    # read reply
    retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
    if type(retval) is int : 
        # pass error code up
        return retval
    if retval[0:3] != [0x20,0x52,0] :
        print "Unexpected message instead of read reply datagram ", retval
        return 3
   
def test(alias, dest, connection, verbose) :    
    # send a short datagram in two segments
    if verbose : print "test two segments"
    connection.network.send(makepartialframe(alias, dest, [0x20,0x42,0,0,0]))
    connection.network.send(makefinalframe(alias, dest, [0,8]))
    # check response
    retval = checkreply(alias, dest, connection, verbose)
    if type(retval) is int and retval != 0 :
        return retval+10
    
    # send a short datagram in two segments with another to somebody else in between
    if verbose : print "test two segments with another interposed" 
    connection.network.send(makepartialframe(alias, dest, [0x20,0x42,0,0,0]))
    connection.network.send(makepartialframe(alias, ~dest, [0x20,0x42,0,0,0]))
    connection.network.send(makefinalframe(alias, dest, [0,8]))
    # check response
    retval = checkreply(alias, dest, connection, verbose)
    if type(retval) is int and retval != 0 :
        return retval+10
    
    return 0

if __name__ == '__main__':
    main()
