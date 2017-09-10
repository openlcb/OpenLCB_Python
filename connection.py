#!/usr/bin/env python
## Helper method for establishing a connection to an OpenLCB network
# 
# @author: Bob Jacobsen
# @author: Stuart Baker - extensively modified

network = None

def establish(nodeid, gchost=None, host=None, port=None, device=None,
              verbose=False, veryverbose=False) :
    if (gchost != None and port != None) :
        import generictogc
        import rawiotcp
        raw_io = rawiotcp.RawIoTCP(gchost, port)
        global network
        network = generictogc.GenericToGC(nodeid, raw_io, verbose, veryverbose)
    elif (host != None and port != None) :
        assert False, "Native TCP connections not [yet] supported."
    elif (device != None) :
        import generictogc
        import rawIoSerial
        raw_io = rawIoSerial.RawIoSerial(device)
        global network
        network = generictogc.GenericToGC(nodeid, raw_io, verbose, veryverbose)
    else :
        assert False, "Invalid connection parameters."
