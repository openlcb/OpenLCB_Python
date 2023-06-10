#!/usr/bin/env python
'''
Tests a node's startup processing:
 * Alias allocation
 * State changes and notification
 * P/C event notification

Requires that the user reset the node (or otherwise force a startup)
after the script is started.

@author: Bob Jacobsen
'''

# Expects something like:
# :X17020573N;
# :X16304573N;
# :X15050573N;
# :X10700573N;
# :X19100573N020304050607;
# :X192AB573N0203040506070001;
# :X192AB573N0203040506070004;
# :X1926B573N0203040506070005;
# :X1926B573N0203040506070008;

import connection as connection
import canolcbutils

import time
import sys

def usage() :
    print ("")
    print ("Called standalone, tests a nodes startup processing.")
    print ("Reset the node (or force startup) when prompted")
    print ("")
    print ("Default connection detail taken from connection.py")
    print ("")
    print ("-a --alias source alias")
    print ("-d --dest destination (target node) starting alias")
    print ("-v verbose")
    print ("-V very verbose")

import getopt, sys

def main():
    alias = connection.thisNodeAlias;
    dest = connection.testNodeAlias;
    verbose = False

    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:vV", ["alias=", "dest="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print (str(err)) # will print something like "option -a not recognized"
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
        else:
            assert False, "unhandled option"

    retval = test(alias, dest, connection, verbose)
    connection.network.close()
    sys.exit(retval)

# skip (return False) frames that are not from our desired under-test source alias
# and return ones that are
def getDutMessage(dest) :
    reply = connection.network.receive()
    while (reply != None and (int(reply[7:10],16))!= dest) :
        print ("    skipping "+reply);
        reply = connection.network.receive()
    return reply

def test(alias, dest, connection, verbose) :
    # wait for reset

    # expect RIF sequence after reset, check timing
    timeout = connection.network.timeout
    connection.network.timeout = 25
    connection.network.connect()

    print ("Restart node now")

    reply = connection.network.receive()
    if verbose : print ("Start checking node output")
    while (True) :
        if reply == None :
            print ("1st CIM reply not received, did you reset node?")
            return 1
        elif reply.startswith(":X17") :
            break
        elif reply.startswith(":X") :
            if verbose: print ("ignoring unexpected frame", reply)
        else :
            if verbose: print ("ignoring misc characters not a frame: ", reply)
        reply = connection.network.receive()

    # this overrides pre-configuration, is that OK?
    dest = int(reply[7:10],16)

    connection.network.timeout = timeout
    testAlias = reply[7:10]
    if testAlias == "000" :
        print ("node using alias == 0")
        return 331

    id = reply[4:7]
    start = time.time()

    reply = getDutMessage(dest)
    if reply == None :
        print ("2nd CIM reply not received")
        return 2
    if reply[7:10] != testAlias :
        print ("mismatched 2nd CIM source alias")
        return 12
    if not reply.startswith(":X16") :
        print ("2nd CIM reply not correct")
        return 32
    id = id+reply[4:7]

    reply = getDutMessage(dest)
    if reply == None :
        print ("3rd CIM reply not received")
        return 3
    if reply[7:10] != testAlias :
        print ("mismatched 3rd CIM source alias")
        return 13
    if not reply.startswith(":X15") :
        print ("3rd CIM reply not correct")
        return 33
    id = id+reply[4:7]

    reply = getDutMessage(dest)
    if reply == None :
        print ("4th CIM reply not received")
        return (4)
    if reply[7:10] != testAlias :
        print ("mismatched 4th CIM source alias")
        return (14)
    if not reply.startswith(":X14") :
        print ("4th CIM reply not correct")
        return (34)
    id = id+reply[4:7]

    # expect RIM (check timing)
    connection.network.timeout = 1
    reply = getDutMessage(dest)
    end = time.time()
    connection.network.timeout = timeout
    if reply == None :
        print ("RIM reply not received")
        return (5)
    if not reply.startswith(":X10700") :
        print ("RIM reply not correct")
        return (35)
    if reply[7:10] != testAlias :
        print ("mismatched RIM source alias")
        return (15)

    if verbose : print ("   delay was ", end-start)

    if end-start < 0.15 :
        # some tolerance on check...
        print ("did not wait long enough ", end-start)
        return (22)
    if end-start > .55 :
        # some tolerance on check...
        print ("waited too long ", end-start)
        return (22)

    # expect AMD
    reply = getDutMessage(dest)
    if reply == None :
        print ("AMD reply not received")
        return (6)
    if not reply.startswith(":X10701") :
        print ("AMD reply not correct")
        return (35)
    if reply[7:10] != testAlias :
        print ("mismatched AMD source alias")
        return (16)
    if id != reply[11:23] :
        print ("AMD node ID ",reply[11:23],") did not match one in CID frames ",id)
        return (21)

    # expect NodeInit
    reply = getDutMessage(dest)
    if reply == None :
        print ("NodeInit reply not received")
        return 7
    if not reply.startswith(":X19100") :
        print ("NodeInit reply not correct")
        return 37
    if reply[7:10] != testAlias :
        print ("mismatched NodeInit source alias")
        return 17
    if id != reply[11:23] :
        print ("NodeInit node ID did not match",id, reply[11:23])
        return (27)

    # expect zero or more Produced/Consumed messages

    consumed = []
    produced = []
    start = time.time()
    while (time.time() - start < 5.0) :
        reply = getDutMessage(dest)
        if (reply == None ) : break
        if (reply.startswith(":X194C")) :
            event = canolcbutils.bodyArray(reply)
            if verbose : print ("consumes ", event)
            consumed = consumed+[event]
        elif (reply.startswith(":X19524")) :
            if verbose : print ("Producer Range Identified")
            # we don't post-process these
        elif (reply.startswith(":X194A4")) :
            if verbose : print ("Consumer Range Identified")
            # we don't post-process these
        elif (reply.startswith(":X1954")) :
            event = canolcbutils.bodyArray(reply)
            if verbose : print ("produces ", event)
            produced = produced+[event]
        elif (reply.startswith(":X195B4")) :
            event = canolcbutils.bodyArray(reply)
            if verbose : print ("event produced", event)
        elif (reply.startswith(":X198F4")) :
            event = canolcbutils.bodyArray(reply)
            if verbose : print ("Identify Consumer request ", event)
        elif (reply.startswith(":X19914")) :
            event = canolcbutils.bodyArray(reply)
            if verbose : print ("Identify Producer request ", event)
        else :
            print ("Unexpected message ", reply)
            return (50)
    return 0

if __name__ == '__main__':
    main()
