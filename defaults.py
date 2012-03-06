
serial   = True
ethernet = False
local    = False

if ethernet and not local:
    import ethernetolcblink
    network = ethernetolcblink.EthernetToOlcbLink()
    network.host = "10.00.01.98"
    network.port = 23
elif serial and not local : 
    import serialolcblink
    network = serialolcblink.SerialOlcbLink()
    network.port = "/dev/tty.usbserial-A7007AOC"
    network.speed = 230400
    network.startdelay = 13
elif local :
    import pipeolcblink
    network = pipeolcblink.PipeOlcbLink()


thisNodeID = [1,2,3,4,5,6]
thisNodeAlias = 0xAAA
testNodeID = [2,3,4,5,6,1]
testNodeAlias = 0xDDD

