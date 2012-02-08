import ethernetolcblink
network = ethernetolcblink.EthernetToOlcbLink()
network.host = "10.00.01.98"
network.port = 23
thisNodeID = [1,2,3,4,5,6]
thisNodeAlias = 0xAAA
testNodeID = [2,3,4,5,6,1]
testNodeAlias = 0xDDD
