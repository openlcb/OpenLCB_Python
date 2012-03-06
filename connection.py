#!/usr/bin/env python
'''

Provides a basic connection definition for the OpenLCB python test suite

Works with the (mutable) defaults.py file, which contains specific values

@author: Bob Jacobsen
'''

import defaults

network         = defaults.network

thisNodeID      = defaults.thisNodeID 
thisNodeAlias   = defaults.thisNodeAlias
testNodeID      = defaults.testNodeID 
testNodeAlias   = defaults.testNodeAlias


def main():
    usage()
    
    return  # done with example
    
def list() :
    print "network.host = "+network.host
    print "network.port = "+str(network.port)
    print "thisNodeID = ",thisNodeID
    print "thisNodeAlias = "+hex(thisNodeAlias)
    print "testNodeID = ",testNodeID
    print "testNodeAlias = "+hex(testNodeAlias)
    return

def usage() :
    print ""
    print "Python module for defining the layout connection."
    print ""
    print "Invoked by other routines to know how to send, "
    print "not intended to be invoked standalone"
    print ""
    list()
    return
    
if __name__ == '__main__':
    main()
