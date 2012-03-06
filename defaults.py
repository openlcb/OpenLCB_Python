
serial = True
ethernet = not serial

local = False

if ethernet :
    import ethernetolcblink
    network = ethernetolcblink.EthernetToOlcbLink()
    network.host = "10.00.01.98"
    #network.host = "99.32.118.100"
    network.port = 23
elif serial : 
    import serialolcblink
    network = serialolcblink.SerialOlcbLink()
    network.port = "/dev/tty.usbserial-A6008c44"
    network.speed = 230400
    network.startdelay = 1
elif local :
    import pipeolcblink
    network = pipeolcblink.PipeOlcbLink()


thisNodeID = [1,2,3,4,5,6]
thisNodeAlias = 0xAAA
testNodeID = [2,3,4,5,6,1]
testNodeAlias = 0xDDD

