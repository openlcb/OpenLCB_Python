#!/usr/bin/env python
'''
Tests a node's response to seeing messages with its alias

@author: Bob Jacobsen
'''

# Expects:
# :X17020573N;
# :X16304573N;
# :X15050573N;
# :X10700573N;
# :X10701573N020304050607;
# :X19087573N020304050607;

import connection as connection
import canolcbutils
import verifyNodeGlobal
import verifyNodeAddressed
import time

def usage() :
    print("")
    print("Called standalone, tests a node's response to")
    print("seeing messages with its alias")
    print("")
    print("Default connection detail taken from connection.py")
    print("")
    print("-a --alias source alias (default 123)")
    print("-d --dest dest alias (default 123)")
    print("-t find destination alias automatically")
    print("-v verbose")
    print("-V very verbose")

import getopt, sys

def main():
    alias = connection.thisNodeAlias;
    dest = connection.testNodeAlias;
    verbose = False
    identifynode = False

    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:vVt", ["alias=", "dest="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt == "-V":
            verbose = True
            connection.network.verbose = True
        elif opt in ("-a", "--alias"):
            alias = int(arg) # needs hex decode
        elif opt in ("-d", "--dest"):
            dest = int(arg) # needs hex decode
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, otherNodeId = getUnderTestAlias.get(alias, None, verbose)

    retval = test(alias, dest, connection, verbose)
    connection.network.close()
    return retval

def test(alias, dest, connection, verbose) :
    # Note: This test assumes that the response will be
    # to reacquire another alias after the conflicted one is
    # dropped.  This isn't required behavior by standard, but
    # is a necessary condition for the test to continue and
    # check another conflict condition.

    # Sending a global message (that normally doesn't get a response)
    # by sending verifyNodeGlobal with a nodeID that doesn't match any valid ID
    if verbose : print("  check no-response global message with alias conflict")
    connection.network.send(verifyNodeGlobal.makeframe(dest, [0,0,0,0,0,1]))
    reply = connection.network.receive()
    if reply == None :
        print("no response received to conflict frame")
        return 21
    if not reply.startswith(":X10703") :    # Expect AMR
        print("Expected first AMR")
        return 22
    if int(reply[7:10],16) != dest :        # with expected (existing) alias
        print("incorrect alias in AMR")
        return 23
    reply = connection.network.receive()
    if reply == None :
        print("no response received to conflict frame")
        return 21
    if not reply.startswith(":X17") :       # Then first CID
        print("Expected first CID")
        return 22
    if int(reply[7:10],16) == 0 :           # With a new, non-zero alias
        print("received alias == 0")
        return 23
    dest = int(reply[7:10],16)
    # pull & drop rest of sequence
    reply = connection.network.receive()  # CID 2
    reply = connection.network.receive()  # CID 3
    reply = connection.network.receive()  # CID 4
    timeout = connection.network.timeout
    connection.network.timeout = 1.0      # (expect delay here)
    reply = connection.network.receive()  # RID
    connection.network.timeout = timeout
    # dump everything until nothing heard - can include lots of e.g. event identification
    while (reply != None) :
        reply = connection.network.receive()

    # Sending a global message (that normally does get a response)
    # check to make sure that response is sent with new alias
    if verbose : print("  check response-inducing global message with alias conflict")
    connection.network.send(verifyNodeGlobal.makeframe(dest, None))
    reply = connection.network.receive()
    if reply == None :
        print("no response received to conflict frame")
        return 21
    if not reply.startswith(":X10703") :    # Expect AMR
        print("Expected second AMR")
        return 22
    if int(reply[7:10],16) != dest :        # with alias from previous collision recovery
        print("incorrect alias in AMR")
        return 23
    reply = connection.network.receive()
    if reply == None :
        print("no response received to conflict frame")
        return 31
    if not reply.startswith(":X17") :       # Expect 1st frame of 2nd CID sequence
        print("Expected second CID")
        return 32
    if int(reply[7:10],16) == 0 :           # with a new, non-zero alias
        print("received alias == 0")
        return 33
    dest = int(reply[7:10],16)
    # pull & drop rest of sequence
    reply = connection.network.receive()  # CID 2
    reply = connection.network.receive()  # CID 3
    reply = connection.network.receive()  # CID 4
    timeout = connection.network.timeout
    connection.network.timeout = 1.0
    reply = connection.network.receive()  # RID
    connection.network.timeout = timeout
    # dump everything until nothing heard - not yet checking for reply to VerifyNode
    while (reply != None) :
        reply = connection.network.receive()

    # Sending an addressed message to some other alias (note arguments backwards, on purpose)
    if verbose : print("  check addressed message with alias conflict")
    connection.network.send(verifyNodeAddressed.makeframe(dest, alias, None))
    reply = connection.network.receive()
    if reply == None :
        print("no response received to conflict frame")
        return 21
    if not reply.startswith(":X10703") :
        print("Expected third AMR")
        return 22
    if int(reply[7:10],16) != dest :
        print("incorrect alias in AMR")
        return 23
    reply = connection.network.receive()
    if reply == None :
        if verbose : print("no response received to conflict frame")
        return 41
    if not reply.startswith(":X17") :
        if verbose : print("Expected third CID")
        return 42
    if int(reply[7:10],16) == 0 :
        print("received alias == 0")
        return 43
    dest = int(reply[7:10],16)
    # pull & drop rest of sequence
    reply = connection.network.receive()  # CID 2
    reply = connection.network.receive()  # CID 3
    reply = connection.network.receive()  # CID 4
    timeout = connection.network.timeout
    connection.network.timeout = 1.0
    reply = connection.network.receive()  # RID
    connection.network.timeout = timeout
    # dump everything until nothing heard
    while (reply != None) :
        reply = connection.network.receive()

   # send a CheckID
    if verbose : print("  check CheckID with alias conflict")
    connection.network.send(canolcbutils.makeframestring(0x17020000+dest, None))
    reply = connection.network.receive()
    if reply == None :
        if verbose : print("no response received to CID")
        return 51
    if int(reply[7:10],16) != dest :
        if verbose : print("mismatched reply alias")
        return 52
    if not reply.startswith(":X10700") :
        if verbose : print("CID reply not correct, RID expected")
        return 53

    # send a ReserveID
    if verbose : print("  check ReserveID with alias conflict")
    connection.network.send(canolcbutils.makeframestring(0x10700000+dest, None))
    reply = connection.network.receive()
    if reply == None :
        print("no response received to conflict frame")
        return 21
    if not reply.startswith(":X10703") :    # Expect AMR
        print("Expected fourth AMR")
        return 22
    if int(reply[7:10],16) != dest :
        print("incorrect alias in AMR")
        return 23
    reply = connection.network.receive()
    if reply == None :
        if verbose : print("no response received to conflict frame")
        return 61
    if not reply.startswith(":X17") :
        if verbose : print("Expected fourth CID")
        return 62
    if int(reply[7:10],16) == 0 :
        print("received alias == 0")
        return 63
    dest = int(reply[7:10],16)
    # pull & drop rest of sequence
    reply = connection.network.receive()  # CID 2
    reply = connection.network.receive()  # CID 3
    reply = connection.network.receive()  # CID 4
    timeout = connection.network.timeout
    connection.network.timeout = 1.0
    reply = connection.network.receive()  # RID
    connection.network.timeout = timeout
    # dump everything until nothing heard
    while (reply != None) :
        reply = connection.network.receive()

    return 0

if __name__ == '__main__':
    main()
