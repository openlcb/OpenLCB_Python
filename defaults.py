import ethernetolcblink
network = ethernetolcblink.EthernetToOlcbLink()
network.host = "10.00.01.98"
#network.host = "99.32.118.100"
network.port = 23

# import serialolcblink
# network = serialolcblink.SerialOlcbLink()
# network.host = "/dev/tty.usbserial-A7007AOK"
# network.port = 115200
# network.startdelay = 4


thisNodeID = [1,2,3,4,5,6]
thisNodeAlias = 0xAAA
testNodeID = [2,3,4,5,6,1]
testNodeAlias = 0xDDD

