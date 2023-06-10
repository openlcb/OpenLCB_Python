# select the connection type (only one)
serial   = True
windows  = False
serialPort = "/dev/cu.usbmodemCC570001B1"

tcp      = False
ethernet = False
networkHost = "192.168.16.212"

local    = False

# thisNode is the node doing the testing
thisNodeID = [1,2,3,4,5,6]
thisNodeAlias = 0xAAA

# testNode is the node under test
# usually the -t option is used to gather this info from the single attached node
testNodeID = [2,3,4,5,6,1]
testNodeAlias = 0xDDD
# an event produced and consumed by the device under test or None
testEventID = [0x05, 0x02, 0x01, 0x02, 0x02, 0x00, 0x00, 0x00]


if tcp :
    import tcpolcblink
    network = tcpolcblink.TcpToOlcbLink()
    network.host = networkHost
    network.port = 12021
elif ethernet :
    import ethernetolcblink
    network = ethernetolcblink.EthernetToOlcbLink()
    network.host = networkHost
    network.port = 12021
elif windows :
    import serialolcblink
    network = serialolcblink.SerialOlcbLink()
    network.port = serialPort
    network.speed = 500000
    network.startdelay = 0
elif serial :
    import serialolcblink
    network = serialolcblink.SerialOlcbLink()
    network.port = serialPort
    network.speed = 57600 #115200 #230400
    network.parallel = False
    network.startdelay = 1 # time to wait at start for adapter to come up, in seconds
elif local :
    import pipeolcblink
    network = pipeolcblink.PipeOlcbLink()
    network.name = "pyOlcbBasicNode"
else :
    print ("Please set one of the options to True")


testNodeID = [2,3,4,5,6,1]
testNodeAlias = 0xDDD
testEventID = [0x05, 0x02, 0x01, 0x02, 0x02, 0x00, 0x00, 0x00]
