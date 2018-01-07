serial   = False
tcp      = True
ethernet = False
windows  = False
local    = False

thisNodeID = [1,2,3,4,5,6]
thisNodeAlias = 0xAAA
testNodeID = [0x2,0x1,0x99,0xff,0x00,0x1e]
testNodeAlias = 0x5F9


if tcp and not local:
    #import tcpolcblink
    #network = tcpolcblink.TcpToOlcbLink()
    #network = generictogc
    #network.host = "172.168.1.10"
    #network.host = "localhost"
    #network.host = "propername.local."
    #network.port = 12021
    import generictogc
    import rawiotcp
    raw_io = rawiotcp.RawIoTCP("localhost", 12021)
    network = generictogc.GenericToGC(testNodeID, raw_io, True)

elif ethernet and not local:
    import ethernetolcblink
    network = ethernetolcblink.EthernetToOlcbLink()
    network.host = "174.18.137.234"
    #network.host = "propername.local."
    network.port = 12021
elif windows and not local :
    import serialolcblink
    network = serialolcblink.SerialOlcbLink()
    network.port = "COM9"
    network.speed = 500000
    network.startdelay = 0
elif serial and not local :
    import serialolcblink
    network = serialolcblink.SerialOlcbLink()
    #network.port = "/dev/cu.usbserial-A900fLVC"
    #network.port = "/dev/cu.usbmodem401331"
    #network.port = "/dev/cu.usbserial-AE015IZE" # Ioduino
    network.port = "/dev/cu.usbserial-A5VRG6OF" # TCH parallel
    network.speed = 230400
    network.parallel = True
    network.startdelay = 2
elif local :
    import pipeolcblink
    network = pipeolcblink.PipeOlcbLink()
    network.name = "pyOlcbBasicNode"
else :
    print "Please set one of the options to True"



testEventID = [0x05, 0x02, 0x01, 0x02, 0x02, 0x00, 0x00, 0x00]
