#!/usr/bin/env python
'''

Provides a basic connection definition for the OpenLCB python test suite

Works with the (mutable) defaults.py file, which contains specific values

@author: Bob Jacobsen
'''

import defaults

network         = defaults.network
network.host    = defaults.network.host
network.port    = defaults.network.port
thisNodeID      = defaults.thisNodeID 
thisNodeAlias   = defaults.thisNodeAlias
testNodeID      = defaults.testNodeID 
testNodeAlias   = defaults.testNodeAlias


def main():
    usage()
    
    return  # done with example

# following is just start of a load/store system for defaults
# to replace the defaults.py file

def store(file) :
    pickle(network.host, file)
    pickle(network.port, file)
    pickle(thisNodeID, file)
    pickle(thisNodeAlias, file)
    pickle(testNodeID, file)
    pickle(testNodeAlias, file)
    return
    
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
    print "currently set to Ethernet connection via node "+network.host+" port "+str(network.port)
    print ""
    list()
    return
    
if __name__ == '__main__':
    main()
