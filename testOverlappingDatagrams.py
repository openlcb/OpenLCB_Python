#!/usr/bin/env python
'''
Test of the specific case of overlapping datagrams,
created as part of the study of the missing start bit.

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils


# the following are cut&pasted from testDatagram, and should be properly imported instead

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
    print "Test of the specific case of overlapping datagrams,"
    print "created as part of the study of the missing start bit."
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-t find destination alias automatically"
    print "-n number of buffers to test (sends n+1 requests) default 1"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

def main():
    # argument processing
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    identifynode = False
    num = 1
    verbose = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:n:vVt", ["dest=", "alias=", "content="])
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
        elif opt in ("-n"):
            num = int(arg)
        elif opt in ("-d", "--dest"):  # needs hex processing
            dest = int(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)

    exit( test(alias, dest, num, connection, verbose) )

import datagram

# Check for a reply datagram to a request, and check if it's basically OK
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
   
def test(alias, dest, num, connection, verbose) :    

    # going to send a [0x20,0x42,0,0,0,0,8] read datagram in three parts:
    #     [0x20]   [0x42,0,0]   [0,0,8]

    if verbose : print "testing datagram parsing with ",num," buffer(s)"

    if connection.network.verbose : print "send initial frame from first source, plus",num,"more that should be ignored"
    tempalias = alias
    for n in range(0,num+1) :
        connection.network.send(makepartialframe(tempalias, dest, [0x20]))
        tempalias = (tempalias + 1 ) & 0xFFF
        if tempalias == dest : 
            tempalias = (tempalias + 1 ) & 0xFFF
        
    # do not expect reply at this point
    frame = connection.network.receive()
    if frame != None :
        print "unexpected reply to initial segments", frame
        return 81
    
    
    if connection.network.verbose : print "finish 1st datagram frames & check reply"
    connection.network.send(makepartialframe(alias, dest, [0x42,0,0]))
    connection.network.send(makefinalframe(alias, dest, [0,0,8]))
    # check response
    retval = checkreply(alias, dest, connection, verbose)
    if type(retval) is int and retval != 0 :
        return retval+20

    if connection.network.verbose : print "send intermediate frame of remaining",num,"datagram(s), expect no answers"
    tempalias = alias
    for n in range(1,num+1) :
        tempalias = (tempalias + 1 ) & 0xFFF
        if tempalias == dest : 
            tempalias = (tempalias + 1 ) & 0xFFF
        connection.network.send(makepartialframe(tempalias, dest, [0x42,0,0]))
    # do not expect reply at this point
    frame = connection.network.receive()
    if frame != None :
        print "unexpected reply to middle segments", frame
        return 82
    
    if connection.network.verbose : print "send final of other datagrams"
    tempalias = alias
    for n in range(1,num+1) :
        tempalias = (tempalias + 1 ) & 0xFFF
        if tempalias == dest : 
            tempalias = (tempalias + 1 ) & 0xFFF
        connection.network.send(makefinalframe(tempalias, dest, [0,0,8]))
        if n == num :
            # last should be rejected, no buffer
            frame = connection.network.receive()
            if frame == None :
                print "missing reply to final segment"
                return 83
            if  not (frame.startswith(":X1E") and frame[4:7] == hex(tempalias)[2:].upper() and frame[11:17] == "4D2000") :
                if frame.startswith(":X1E") and frame[4:7] == hex(tempalias)[2:].upper() and frame[11:17] == "4D1040" :
                    print "expected NAK-buffer-unavailable reply to final frame of final datagram but received NAK-invalid-format, corrupted datagram generated?", frame
                    return 84
                else :
                    print "expected NAK-buffer-unavailable reply to final frame of final datagram but received", frame
                    return 85
        else :
            # expect it's OK before last
            retval = checkreply(tempalias, dest, connection, verbose)
            if type(retval) is int and retval != 0 :
                return retval+30
        
    return 0

if __name__ == '__main__':
    main()
