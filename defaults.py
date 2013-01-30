serial   = True
ethernet = False
windows  = False
local    = False


if ethernet and not local:
    import ethernetolcblink
    network = ethernetolcblink.EthernetToOlcbLink()
    network.host = "10.00.01.98"
    network.port = 23
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
    #network.port = "/dev/cu.usbmodemff1331"
    #network.port = "/dev/cu.usbserial-AE015IZE" # Ioduino
    network.port = "/dev/cu.usbserial-A500XBTQ" # TCH parallel
    network.speed = 125000
    network.parallel = True
    network.startdelay = 5
elif local :
    import pipeolcblink
    network = pipeolcblink.PipeOlcbLink()
    network.name = "pyOlcbBasicNode"
else :
    print "Please set one of the options to True"


thisNodeID = [1,2,3,4,5,6]
thisNodeAlias = 0xAAA
testNodeID = [2,3,4,5,6,1]
testNodeAlias = 0xDDD


testEventID = [0x05, 0x02, 0x01, 0x02, 0x02, 0x00, 0x00, 0x00]
