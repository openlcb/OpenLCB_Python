#!/usr/bin/env python
'''
Send and receive single datagrams

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
    body = [(dest>>8)&0xFF, dest&0xFF]
    return canolcbutils.makeframestring(0x19A28000+alias,body)

def isNakReply(frame) :
    return frame.startswith(":X19A48")

def isOkReply(frame) :
    return frame.startswith(":X19A28")

def sendOneDatagram(alias, dest, content, connection, verbose) :
    if len(content) > 8 :
        first = True
        while len(content) > 8 :
            if first :
                frame = makefirstframe(alias, dest, content[0:8])
                first = False
            else :
                frame = makemiddleframe(alias, dest, content[0:8])
            connection.network.send(frame)
            content = content[8:]
    
        frame = makefinalframe(alias, dest, content)
        connection.network.send(frame)
    else :
        frame = makeonlyframe(alias, dest, content)
        connection.network.send(frame)
        
    frame = connection.network.receive()
    if frame == None : 
        print("Did not receive reply")
        return 1
    if not isOkReply(frame) :
        print("Unexpected message received instead of Datagram Received OK")
        return 2
    if not int(frame[12:15],16) == alias:
        print("Improper dest alias in reply", frame)
        return 3
    if not int(frame[7:10],16) == dest:
        print("Improper source alias in reply", frame)
        return 3
    return 0

def receiveOneDatagram(alias, dest, conection, verbose) :
    retval = []
    while True :
        reply = connection.network.receive()
        if (reply == None ) : 
            print("No datagram segment received")
            return 4
        elif reply.startswith(":X1B") or reply.startswith(":X1C") :
            retval = retval + canolcbutils.bodyArray(reply)
            continue
        elif reply.startswith(":X1A") or reply.startswith(":X1D") :
            retval = retval + canolcbutils.bodyArray(reply)
            connection.network.send(makereply(alias, dest))
            return retval
        else :
            print("Unexpected message instead of datagram segment", reply)
            return 3

def sendOneDatagramNoWait(alias, dest, content, connection, verbose) :
    if len(content) > 8 :
        first = True
        while len(content) > 8 :
            if first :
                frame = makefirstframe(alias, dest, content[0:8])
                first = False
            else :
                frame = makemiddleframe(alias, dest, content[0:8])
            connection.network.send(frame)
            content = content[8:]
    
        frame = makefinalframe(alias, dest, content)
        connection.network.send(frame)
    else :
        frame = makeonlyframe(alias, dest, content)
        connection.network.send(frame)
        
def receiveDatagramReplyAndOneDatagram(alias, dest, conection, verbose) :
    # use after SendOneDatagramNoWait to get both the reply datagram and 
    # the response to the sent datagram, in either order.
    retval = []
    haveReply = False
    haveDatagram = False
    while True :
        reply = connection.network.receive()
        if (reply == None ) : 
            print("Missing response")
            return 4
        elif isOkReply(reply) : 
            haveReply = True
            if haveDatagram : 
                return retval
        elif reply.startswith(":X1B") or reply.startswith(":X1C") :
            retval = retval + canolcbutils.bodyArray(reply)
            continue
        elif reply.startswith(":X1A") or reply.startswith(":X1D") :
            retval = retval + canolcbutils.bodyArray(reply)
            connection.network.send(makereply(alias, dest))
            haveDatagram = True
            if haveReply :
                return retval
        else :
            print("Unexpected message", reply)
            return 3

    
def usage() :
    print("")
    print("Called standalone, will send one CAN datagram message")
    print(" and display response.")
    print("")
    print("Expect a single datagram reply in return")
    print("e.g. [1Esssddd] 4C")
    print("from destination alias to source alias")
    print("")
    print("Default connection detail taken from connection.py")
    print("")
    print("See also testDatagram.py")
    print("")
    print("-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")")
    print("-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")")
    print("-c --content message content (default 1.2.3.4)")
    print("-t find destination alias automatically")
    print("-v verbose")
    print("-V Very verbose")

import getopt, sys

def main():
    # argument processing
    content = [1,2,3,4]
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    identifynode = False
    verbose = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:c:vVt", ["dest=", "alias=", "content="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
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
        elif opt in ("-c", "--content"):
            content = canolcbutils.splitSequence(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)
    
    retval = test(alias, dest, content, connection, verbose)
    connection.network.close()
    exit(retval)
    
def test(alias, dest, content, connection, verbose) :    
    return sendOneDatagram(alias, dest, content, connection, verbose)

if __name__ == '__main__':
    main()
