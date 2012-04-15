#!/usr/bin/env python
'''
Check that standard CAN frames don't cause problems

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(header) :
    retval = ":S"
    retval += hex(header).upper()[2:]
    retval += "N"
    retval += ";"
    return retval
    
def usage() :
    print ""
    print "Sends standard-form CAN frames, checking for no reply"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

def main():
    # argument processing
    verbose = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "vV", [])
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
        else:
            assert False, "unhandled option"

    retval = test(connection, verbose)
    exit(retval)
    
def test(connection, verbose) :
    for header in range(0,2047) :
        connection.network.send(makeframe(header))
        
    # see if any replies
    reply = connection.network.receive()
    if reply == None : 
        return 0
    print "Unexpected reply recieved to standard frame", reply
    return 4

if __name__ == '__main__':
    main()
