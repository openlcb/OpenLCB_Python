'''
Created on March 18, 2011

Define implementation defaults for OpenLCB interface

@author: Bob Jacobsen
'''

import ethernetolcblink

global network
network = ethernetolcblink.EthernetToOlcbLink()
network.host = "10.00.01.98"
network.port = 23

global thisNodeID
thisNodeID = 0x000000000000

global thisNodeIDa
thisNodeIDa = 0x001

def main():
    usage()
    
    return  # done with example

def usage() :
    print ""
    print "Python module for defining the layout connection."
    print ""
    print "Invoked by other routines to know how to send, "
    print "not intended to be invoked standalone"
    print ""
    print "currently set to Ethernet connection via node "+network.host+" port "+network.port
    print ""
    return
    
if __name__ == '__main__':
    main()
