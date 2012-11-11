#!/usr/bin/env python
'''
Test of the specific case of overlapping datagrams,
created as part of the study of the missing start bit.

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils


# the following are cut&pasted from testDatagram, and should be properly imported instead

def makeonlyframe(alias, dest, content) :
    return canolcbutils.makeframestring(0x1A000000+alias+(dest<<12),content)

def makefirstframe(alias, dest, content) :
    return canolcbutils.makeframestring(0x1B000000+alias+(dest<<12),content)

def makemiddleframe(alias, dest, content) :
    return canolcbutils.makeframestring(0x1C000000+alias+(dest<<12),content)
    
def makefinalframe(alias, dest, content) :
    return canolcbutils.makeframestring(0x1D000000+alias+(dest<<12),content)

def makereply(alias, dest) :
    body = [(dest>>8)&0xFF, dest&0xFF]
    return canolcbutils.makeframestring(0x19A28000+alias,body)

def isreply(frame) :
    return frame.startswith(":X19A28") or frame.startswith(":X19A48")

def isNAK(frame) :
    return frame.startswith(":X19A48")

    if(len(content) <= 8):
        frame = makeonlyframe(alias, dest, content)
        connection.network.send(frame)
        return

    frame = makefirstframe(alias, dest, content[0:8])
    connection.network.send(frame)
    content = content[8:]

    while len(content) > 8 :
        frame = makemiddleframe(alias, dest, content[0:8])
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
    reply = connection.network.receive()

    if reply == None :
        return None
    if reply.startswith(":X1A"):
      retval = retval + canolcbutils.bodyArray(reply)
      connection.network.send(makereply(alias, dest))
      return retval

    if reply.startswith(":X1B"):
      retval = retval + canolcbutils.bodyArray(reply)
    else:
      print "Unexpected message instead of first datagram segment", reply
      return 3
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
    print "Sends enough datagrams to force a buffer-full reject message,"
    print "then checks processing of that."
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-b number of buffers to test (sends b+1 requests) default 1, -1 if node has variable number"
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
    num = 1
    verbose = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:b:vVt", ["dest=", "alias=", "content="])
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
        elif opt in ("-b"):
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

    retval = test(alias, dest, num, connection, verbose)
    connection.network.close()
    exit(retval)
    
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
    retval = receiveOneDatagram(alias, dest, connection, verbose)
    if retval == None :
        return 13
    if type(retval) is int : 
        # pass error code up
        return retval
    if retval[0:3] != [0x20,0x51,0] :
        print "Unexpected message instead of read reply datagram ", retval
        return 3

# Check for a NAK datagram to a request, and check if it's basically OK
def checkrejection(alias, dest, connection, verbose) :
    frame = connection.network.receive()
    if frame == None :
        print "Did not receive reply"
        return 1
    if not isNAK(frame) :
        print "Unexpected message received instead of NAK"
        return 2
    return 0


def test(alias, dest, num, connection, verbose) :    

    # num < 0 encodes "variable number of buffers, skip"
    if num < 0 : 
        if verbose : print "  skipping datagram parsing test"
        return

    # going to send a [0x20,0x41,0,0,0,0,8] read datagram in three parts:
    #     [0x20]   [0x41,0,0]   [0,0,8]

    if verbose : print "  testing datagram parsing with ",num," buffer(s)"
    
    if connection.network.verbose : print "  send initial frame from first source, plus",num,"more that should be ignored"
    tempalias = alias
    for n in range(0,num+1) :
        connection.network.send(makefirstframe(tempalias, dest, [0x20]))
        tempalias = (tempalias + 1 ) & 0xFFF
        if tempalias == dest : 
            tempalias = (tempalias + 1 ) & 0xFFF
        
    # reply at this point should only be error to 2nd_or_later message, check for that
    frame = connection.network.receive()
    gotNAK = False  # Assumes we only send one past the number of buffers
    if frame != None :
        if  not (isNAK(frame) and (frame[15:17] == "20" or frame[15:17] == "60") ) :
              print "expected NAK-buffer-unavailable reply to final frame of final datagram but received", frame
              return 81
        # OK NAK, remember
        gotNAK = True
    
    
    if connection.network.verbose : print "  finish 1st datagram frames & check reply"
    connection.network.send(makemiddleframe(alias, dest, [0x41,0,0]))
    connection.network.send(makefinalframe(alias, dest, [0,0,8]))
    # check response
    retval = checkreply(alias, dest, connection, verbose)
    if type(retval) is int and retval != 0 :
        return retval+20

    if connection.network.verbose : print "  send intermediate frame of remaining",num,"datagram(s), expect no answers"
    tempalias = alias
    for n in range(1,num+1) :
        tempalias = (tempalias + 1 ) & 0xFFF
        if tempalias == dest : 
            tempalias = (tempalias + 1 ) & 0xFFF
        connection.network.send(makemiddleframe(tempalias, dest, [0x41,0,0]))
    # do not expect reply at this point
    frame = connection.network.receive()
    if frame != None :
        print "unexpected reply to middle segments", frame
        return 82
    
    if connection.network.verbose : print "  send final of other datagrams"
    tempalias = alias
    for n in range(1,num+1) :
        tempalias = (tempalias + 1 ) & 0xFFF
        if tempalias == dest : 
            tempalias = (tempalias + 1 ) & 0xFFF
        connection.network.send(makefinalframe(tempalias, dest, [0,0,8]))
        if n == num :
            # last should be rejected, no buffer
            if gotNAK : continue
            frame = connection.network.receive()
            if frame == None :
                print "missing reply to final segment"
                return 83
            if  not (isNAK(frame) and (frame[15:17] == "20" or frame[15:17] == "60") ) :
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
