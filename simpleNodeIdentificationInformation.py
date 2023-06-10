#!/usr/bin/env python
'''
OpenLCB SimpleNodeIdentificantInformation message

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, dest) :
    body = [(dest>>8)&0xFF, dest&0xFF]
    return canolcbutils.makeframestring(0x19DE8000+alias,body)

def usage() :
    print("")
    print("Called standalone, will send one CAN Simple Node Identificant Information (addressed) message")
    print(" and display response")
    print("")
    print("Default connection detail taken from connection.py")
    print("")
    print("-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")")
    print("-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")")
    print("-t find destination alias automatically")
    print("-v verbose")
    print("-V Very verbose")

import getopt, sys

def main():
    # argument processing
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    identifynode = False
    verbose = False

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
        dest, otherNodeId = getUnderTestAlias.get(alias, None, verbose)

    retval = test(alias, dest, connection, verbose)
    connection.network.close()
    exit(retval)

def test(alias, dest, connection, verbose) :
    if verbose : print("  check valid request")
    connection.network.send(makeframe(alias, dest))

    mfgName = ""
    mfgType = ""
    mfgHVers = ""
    mfgSVers = ""
    userName = ""
    userComment = ""
    fill = 0   # 0 is format byte, 1 is name, 2 is type, 3 is vers

    # assume always sends the same number of frames
    count = 0

    while (True) :
        reply = connection.network.receive()
        if reply == None :
            break
        if not (reply.startswith(":X19A08") and int(reply[7:10],16)==dest and int(reply[12:15],16)==alias) :
            print("Unexpected reply received ", reply)
            return 1
        # process content
        val = canolcbutils.bodyArray(reply)
        count = count + 1
        for c in val[2:] :
            if fill == 0 :
                fill = 1
                if c != 1 and c != 4:
                    print("First byte of first part should have been one or four, was ",c)
                    return 3
            elif fill == 1 :
                mfgName = mfgName+chr(c)
            elif fill == 2 :
                mfgType = mfgType+chr(c)
            elif fill == 3 :
                mfgHVers = mfgHVers+chr(c)
            elif fill == 4 :
                mfgSVers = mfgSVers+chr(c)
            elif fill == 5 :
                fill = 6
                if c != 1 and c != 2 :
                    print("First byte of second part should have been one or two, was ",c)
                    return 4
            elif fill == 6 :
                userName = userName+chr(c)
            elif fill == 7 :
                userComment = userComment+chr(c)
            else :
                print("Unexpected extra content", c)
                return 15
            if c == 0 :   # end of string
                fill = fill + 1
    if fill != 8 and fill != 5:
        print("Didn't receive all strings", fill)
        return fill+10
    if verbose :
        print("       Manufacturer: ", mfgName)
        print("               Type: ", mfgType)
        print("   Hardware Version: ", mfgHVers)
        print("   Software Version: ", mfgSVers)
        if fill == 8 :
            print("          User Name: ", userName)
            print("       User Comment: ", userComment)

    if verbose : print("  address other node, expect no reply")
    connection.network.send(makeframe(alias, (~dest)&0xFFF))
    reply = connection.network.receive()
    if reply != None :
        print("Unexpected reply received ", reply)

    if verbose : print("  check three simultaneous requests")
    alias2 = (alias+1)&0xFFF
    if alias2 == dest : alias2 = (alias2+1)&0xFFF
    alias3 = (alias+3)&0xFFF
    if alias3 == dest : alias3 = (alias3+10)&0xFFF

    connection.network.send(makeframe(alias, dest))
    connection.network.send(makeframe(alias2, dest))
    connection.network.send(makeframe(alias3, dest))

    count1 = 0
    count2 = 0
    count3 = 0
    while (True) :
        reply = connection.network.receive()
        if reply == None :
            break
        if (reply.startswith(":X19A08") and int(reply[7:10],16)==dest and int(reply[12:15],16)==alias) :
            count1 = count1+1
        if (reply.startswith(":X19068") and int(reply[7:10],16)==dest and int(reply[12:15],16)==alias) :
            count1 = count1-100
        if (reply.startswith(":X19A08") and int(reply[7:10],16)==dest and int(reply[12:15],16)==alias2) :
            count2 = count2+1
        if (reply.startswith(":X19068") and int(reply[7:10],16)==dest and int(reply[12:15],16)==alias2) :
            count2 = count2-100
        if (reply.startswith(":X19A08") and int(reply[7:10],16)==dest and int(reply[12:15],16)==alias3) :
            count3 = count3+1
        if (reply.startswith(":X19068") and int(reply[7:10],16)==dest and int(reply[12:15],16)==alias3) :
            count3 = count3-100
    if count != count1 and count1 != -100:
        print("got "+str(count1)+" frames for request 1 instead of "+str(count)+" in overlapping requests test")
        return 101
    if count != count2 and count2 != -100:
        print("got "+str(count2)+" frames for request 2 instead of "+str(count)+" in overlapping requests test")
        return 102
    if count != count3 and count3 != -100:
        print("got "+str(count3)+" frames for request 3 instead of "+str(count)+" in overlapping requests test")
        return 103

    return 0

if __name__ == '__main__':
    main()
