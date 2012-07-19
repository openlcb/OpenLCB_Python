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
    network.port = "/dev/tty.usbserial-A6007MhL"
    network.speed = 230400
    network.startdelay = 4
elif local :
    import pipeolcblink
    network = pipeolcblink.PipeOlcbLink()


thisNodeID = [1,2,3,4,5,6]
thisNodeAlias = 0xAAA
testNodeID = [2,3,4,5,6,1]
testNodeAlias = 0xDDD

