#!/usr/bin/env python
'''
Extensive datagram testing using the Memory Config Protocol to generate return datagrams

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeonlyframe(alias, dest, content) :
    return canolcbutils.makeframestring(0x1A000000+alias+(dest<<12),content)

def makefirstframe(alias, dest, content) :
    return canolcbutils.makeframestring(0x1B000000+alias+(dest<<12),content)

def makemiddleframe(alias, dest, content) :
    return canolcbutils.makeframestring(0x1C000000+alias+(dest<<12),content)
    
def makefinalframe(alias, dest, content) :
    return canolcbutils.makeframestring(0x1D000000+alias+(dest<<12),content)

def makereply(alias, dest) :
    return canolcbutils.makeframestring(0x1E000000+alias+(dest<<12),[0x4C])

def isreply(frame) :
    return frame.startswith(":X1E") and frame[11:13] == "4C"

def isNAK(frame) :
    return frame.startswith(":X1E") and frame[11:13] == "4D"

def sendOneDatagram(alias, dest, content, connection, verbose) :
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

    retval = test(alias, dest, connection, verbose)
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
#    retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
    retval = receiveOneDatagram(alias, dest, connection, verbose)
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
   
def test(alias, dest, connection, verbose) :    
    # send a short read-request datagram in two segments
    if verbose : print "  test two segments"
    connection.network.send(makefirstframe(alias, dest, [0x20,0x41,0,0,0]))
    connection.network.send(makefinalframe(alias, dest, [0,8]))
    # check response to make sure it was received and interpreted OK
    retval = checkreply(alias, dest, connection, verbose)
    if type(retval) is int and retval != 0 :
        return retval+10
    
    # send a short read-request datagram in two segments with another to somebody else in between
    if verbose : print "  test two segments with extraneous one interposed" 
    connection.network.send(makefirstframe(alias, dest, [0x20,0x41,0,0,0]))
    connection.network.send(makeonlyframe(alias, (~dest)&0xFFF, [0x20,0x41,0,0,0]))
    connection.network.send(makefinalframe(alias, dest, [0,8]))
    # check response
    retval = checkreply(alias, dest, connection, verbose)
    if type(retval) is int and retval != 0 :
        return retval+20

    # send a final segment without a start segment
    if verbose : print "  test final segment without a start segment" 
    connection.network.send(makefinalframe(alias, dest, [0x20,0x41,0,0,0,0,8]))
    # check response, expect error
    frame = connection.network.receive()
    if not isNAK(frame) :
        print "Unexpected reply to final segment without a start segment", frame
        return 101

    # send a short read-request datagram in two segments with another from somebody else in between
    # interposed one could get rejected or processed; here we assume rejected
    if verbose : print "  test two segments with another datagram interposed" 
    connection.network.send(makefirstframe(alias, dest, [0x20,0x41,0,0,0]))
    newalias = (~alias)&0xFFF
    if newalias == dest:
	newalias = (newalias - 1)&0xFFF;
    connection.network.send(makeonlyframe(newalias, dest, [0x20,0x41,0,0,0,0,8]))
    # check for reject of this one
    frame = connection.network.receive()
    if frame == None or not (frame.startswith(":X1E") and frame[4:7] == hex(newalias)[2:].upper() and frame[11:13] == "4D") :
        print "interposed datagram was not rejected due to buffer full:", frame
        return 81
    # send final part of original datagram
    connection.network.send(makefinalframe(alias, dest, [0,8]))
    # check response
    retval = checkreply(alias, dest, connection, verbose)
    if type(retval) is int and retval != 0 :
        return retval+20

    # NAK the response datagram & check for retransmission
    if verbose : print "  send NAK to response"
    connection.network.send(makeonlyframe(alias, dest, [0x20,0x41,0,0,0,0,1]))
    frame = connection.network.receive()
    if frame == None : 
        print "Did not receive reply"
        return 31
    if not isreply(frame) :
        print "Unexpected message received instead of reply"
        return 32
    # read reply, should be a resend of same
    reply = connection.network.receive()
    if (reply == None ) : 
        print "No datagram segment received"
        return 34
    elif not reply.startswith(":X1A") :
        print "Unexpected message instead of datagram segment BOO", reply
        return 33
    # send NAK asking for retransmit retransmit and see if it's right this time
    connection.network.send(canolcbutils.makeframestring(0x1E000000+alias+(dest<<12),[0x4D,0x20,00]))
    #retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
    retval = receiveOneDatagram(alias, dest, connection, verbose)
    if type(retval) is int : 
        # pass error code up
        return retval
    if retval[0:3] != [0x20,0x51,0] :
        print "Unexpected message instead of read reply datagram ", retval
        return 37
        
    # Test recovery from failure during datagram send by sending a 1st segment, then AMR, 
    # then a complete datagram.  The reply will tell if the first part
    # was properly ignored.
    if verbose : print "  test recovery from AMR (node failure) after partial transmission of datagram" 
    # send 1st part (valid datagram part, garbage content)
    connection.network.send(makefirstframe(alias, dest, [0,0,0]))
    # send AMR for that node
    connection.network.send(canolcbutils.makeframestring(0x10703000+alias,None))
    # send correct datagram
    connection.network.send(makefinalframe(alias, dest, [0x20,0x41,0,0,0,0,8]))
    # check response
    retval = checkrejection(alias, dest, connection, verbose)
    if type(retval) is int and retval != 0 :
        return retval+20

    # Test recovery from failure during datagram send by sending a 1st segment, then AMD, 
    # then a complete datagram.  The reply will tell if the first part
    # was properly ignored.
    if verbose : print "  test recovery from AMD (node failure) after partial transmission of datagram" 
    # send 1st part (valid datagram part, garbage content)
    connection.network.send(makefirstframe(alias, dest, [0,0,0]))
    # send AMR for that node
    connection.network.send(canolcbutils.makeframestring(0x10701000+alias,None))
    # send correct datagram
    connection.network.send(makefinalframe(alias, dest, [0x20,0x41,0,0,0,0,8]))
    # check response
    retval = checkrejection(alias, dest, connection, verbose)
    if type(retval) is int and retval != 0 :
        return retval+20

    # Test that AMR and AMD from other nodes don't confuse datagram transmission
    if verbose : print "  test that AMR, AMD from other nodes doesnt interfere" 
    # send 1st part (valid datagram part)
    connection.network.send(makefirstframe(alias, dest, [0x20]))
    # send AMR,AMD for another node
    connection.network.send(canolcbutils.makeframestring(0x10703000+(alias^dest),None))
    connection.network.send(canolcbutils.makeframestring(0x10701000+(alias^dest),None))
    # send 2nd part datagram
    connection.network.send(makefinalframe(alias, dest, [0x41,0,0,0,0,8]))
    # check response
    retval = checkreply(alias, dest, connection, verbose)
    if type(retval) is int and retval != 0 :
        return retval+20

    return 0

if __name__ == '__main__':
    main()
