#!/usr/bin/env python
'''
Load firmware to OpenLCB device using FLIP CAN ISP protocol. Requires IntelHex library, http://www.bialix.com/intelhex/

@author: D.E. Goodman-Wilson
@author: Bob Jacobsen
'''

import connection as connection
from canbootloaderutils import *
from intelhex import IntelHex

CAN_SELECT_NODE = 0x00
CAN_PROG_START = 0x01
CAN_PROG_DATA = 0x02
CAN_DISPLAY_DATA = 0x03
CAN_START_APPLICATION = 0x04
CAN_SELECT_MEM_PAGE = 0x06
CAN_ERROR = 0x06
#TODO
BOOTLOADER_VERSION = 0xA5

def selectNode(CRIS, NNB, connection, verbose) :
    print "In selectNode"
    frame = makeframestring(CRIS, CAN_SELECT_NODE, [NNB])
    response = False
    resp_frame = ''
    counter = 100
    while (not response) and counter:
      print "sending CAN_SELECT_NODE"
      connection.network.send(frame)
      resp_frame = connection.network.receive()
      if (resp_frame != None) and isFrameType(resp_frame, CAN_SELECT_NODE, CRIS):
        print "node selected!"
	response = True
      else:
	counter -= 1
    if(counter == 0): return False
    #now examine the response more carefully
    data = bodyArray(resp_frame)
    print "data contains ",
    print data
    if(data[0] >= BOOTLOADER_VERSION) and (data[1] == 1):
      print "selectNode success! Done"
      return True
    print "selectNode fail!"
    return False

def expect(good, bad, connection, verbose) :
  counter = 0
  while counter <= 1000:
    response = connection.network.receive()
    if response != None:
      response = response.strip()
    if response == good:
      return True
    elif bad != None and response == bad:
      return False
    else:
      counter += 1
  return False

FLASH_SPACE = 0
EEPROM_SPACE = 1
SIGNATURE_SPACE = 2
BOOTLOADER_INFORMATION_SPACE = 3
BOOTLOADER_CONFIGURATION_SPACE = 4
DEVICE_REGISTER_SPACE = 5

def selectMemorySpace(space, CRIS, connection, verbose):
    frame = makeframestring(CRIS, CAN_SELECT_MEM_PAGE, [0x03, space, 0x00])
    expected_response = makeframestring(CRIS, CAN_SELECT_MEM_PAGE, [0x00])
    error_response = makeframestring(CRIS, CAN_ERROR, [0x00])
    connection.network.send(frame)
    return expect(expected_response, error_response, connection, verbose)


def selectMemoryPage(page, CRIS, connection, verbose):
    frame = makeframestring(CRIS, CAN_SELECT_MEM_PAGE, [0x02, FLASH_SPACE, page])
    expected_response = makeframestring(CRIS, CAN_SELECT_MEM_PAGE, [0x00])
    error_response = makeframestring(CRIS, CAN_ERROR, [0x00])
    connection.network.send(frame)
    return expect(expected_response, error_response, connection, verbose)

def eraseMemory(CRIS, connection, verbose) :
    print "eraseMemory"
    frame = makeframestring(CRIS, CAN_PROG_START, [0x80, 0xFF, 0xFF])
    expected_response = makeframestring(CRIS, CAN_PROG_START, [0x00])
    print expected_response
    error_response = makeframestring(CRIS, CAN_ERROR, [0x00])
    connection.network.send(frame)
    return expect(expected_response, error_response, connection, verbose)

def startWrite(start, end, CRIS, connection, verbose) :
    frame = makeframestring(CRIS, CAN_PROG_START, [0x00, start>>8, start & 0xFF, end>>8, end & 0xFF])
    expected_response = makeframestring(CRIS, CAN_PROG_START, None)
    error_response = makeframestring(CRIS, CAN_ERROR, [0x00])
    connection.network.send(frame)
    return expect(expected_response, error_response, connection, verbose)

def writeMemory(ih, zero_index, start, end, CRIS, connection, verbose) :
    if verbose: print "WRITE"
    if not startWrite(start, end, CRIS, connection, verbose) :
      return False
    address = start
    while(address < end):
      incr = min(8, (end+1) - address)
      #copy data
      data = []
      for i in range(incr):
        data.append(ih[zero_index+i])
      frame = makeframestring(CRIS, CAN_PROG_DATA, data)
      connection.network.send(frame)
      done = False
      while not done:
        response = connection.network.receive()
        if(response != None) and isFrameType(response, CAN_PROG_DATA, CRIS):
          payload = bodyArray(response)
          if payload[0] != 0x00 and payload[0] != 0x02:
            print "ERROR WRITING"
            return False
          else:
            done = True
            address += incr
	    zero_index += incr
           
    return True

def verifyMemory(ih, CRIS, connection, verbose) :
    if verbose: print "VERIFY"
    address = ih.minaddr()
    while(address < ih.maxaddr()):
      incr = min(8, (ih.maxaddr()+1) - address)
      frame = makeframestring(CRIS, CAN_DISPLAY_DATA, [0x00, address>>8, address&0xFF, (address+incr-1)>>8, (address+incr-1)&0xFF])
      connection.network.send(frame)
      done = False
      while not done:
        response = connection.network.receive()
        if (response != None) and isFrameType(response, CAN_DISPLAY_DATA, CRIS):
          payload = bodyArray(response)
          for i in range(len(payload)):
            if payload[i] != ih[address + i]:
              print "ERROR IN VERIFY!"
              exit
          address += len(payload)
          done = True
    return True

def startApplication(CRIS, connection, verbose) :
    frame = makeframestring(CRIS, CAN_START_APPLICATION, [0x03, 0x00])
    connection.network.send(frame)
    
def usage() :
    print ""
    print "TODO Called standalone, will send one CAN datagram message"
    print " and display response."
    print ""
    print "Expect a single datagram reply in return"
    print "e.g. [1Esssddd] 4C"
    print "from destination alias to source alias"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-t find destination alias semi-automatically"
    print "-v verbose"
    print "-V Very verbose"


if __name__ == '__main__':
    import getopt, sys
    # argument processing
    dest = connection.testNodeAlias
   
    verbose = False
    identifynode = False 
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:vVt", ["dest=", "alias=", "content="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt == "-V" :
            connection.network.verbose = True
            verbose = True
        elif opt in ("-d", "--dest"):  # needs hex processing
            dest = int(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

#    if identifynode :
#        import getUnderTestAlias
#        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)

############ main code
    #fake an alias
    #dest = 0x703
    #CRIS = (dest>>4) & 0xFF
    #NNB = dest & 0x0F

    #use universal address, will program any node in bootloader mode on network. Will probably break if more than one :(
    CRIS = 0x00
    NNB = 0xFF
    if not selectNode(CRIS, NNB, connection, verbose): exit(1)

    #connected, now what?

    #first, verify that this is an AT90CAN128
#    selectMemorySpace(SIGNATURE_SPACE, CRIS, connection, verbose)



    #first, select the Flash memory space
#    selectMemorySpace(FLASH_SPACE, CRIS, connection, verbose)
#    selectMemoryPage(0, CRIS, connection, verbose)

    #now, read the HEX file, and start writing
    ih = IntelHex('Io_16P_16C_default.hex')
    address = ih.minaddr()
    max = ih.maxaddr()
    if(max > 0xFFFF): #have to do this in two pages
      max = 0xFFFF

    #now, start programming
    eraseMemory(CRIS, connection, verbose)
    writeMemory(ih, ih.minaddr(), ih.minaddr(), max, CRIS, connection, verbose)
    #and now, verify
    verifyMemory(ih, CRIS, connection, verbose)

    #finally, set bootloader flag, and start application
    selectMemorySpace(EEPROM_SPACE, CRIS, connection, verbose)
    writeMemory([0x00, 0x00], 0x00, 0x0FF8, 0x0FF9, CRIS, connection, verbose)
    frame = makeframestring(CRIS, CAN_DISPLAY_DATA, [0x00, 0x0F, 0xF7, 0x0F, 0xFF])
    connection.network.send(frame)
    resp_frame = connection.network.receive()
    resp_frame = connection.network.receive()


    startApplication(CRIS, connection, verbose)
