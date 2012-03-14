#!/usr/bin/env python
'''
Read and check the Configuration Definition Information

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils
import datagram
    
def usage() :
    print ""
    print "Read and check the Configuration Definition Information"
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
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:vVt", ["dest=", "alias="])
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
    exit(retval)
    
def test(alias, dest, connection, verbose) :

    # instead of checking the length of the address space (not cleanly required anyway)
    # this assumes a null-terminated string and reads until it gets the null

    address = 0
    result = ""
    chunk = 16
    done = False
    
    while True :    
        # Read from CDI space
        retval = datagram.sendOneDatagram(alias, dest, [0x20,0x43,(address>>24)&0xFF,(address>>16)&0xFF,(address>>8)&0xFF,address&0xFF,chunk], connection, verbose)
        if retval != 0 :
            return retval
        # read data response
        retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
        if (type(retval) is int) : 
            # pass error code up
            return retval
        if retval[0:2] != [0x20,0x53] :
            print "Unexpected message instead of read reply datagram ", retval
            return 3
        for c in retval[6:] :
            result = result+chr(c)
            if c == 0 :
                done = True
                break;
        if done : break
        address = address + chunk
        
    if verbose : print "   Read CDI result was ", len(result), " bytes"
    if connection.network.verbose : print "  Read CDI result ++++++++++\n", result,"\n++++++++++++++++"
        
    executable = "xmllint --noout -schema ../xml/schema/cdi.xsd - "

    import subprocess
    process = subprocess.Popen(executable,1,None,subprocess.PIPE,subprocess.PIPE, 
                    subprocess.STDOUT, None, False, True)
    [stdout, stderr] = process.communicate(result) 
    
    if process.returncode != 0 :
        print "   CDI data did not validate:  ", stdout
    if process.returncode == 0 and verbose :
        print "   CDI result check:  ", stdout

    return process.returncode

if __name__ == '__main__':
    main()
