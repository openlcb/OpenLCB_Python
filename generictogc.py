#!/usr/bin/env python
## Drive an OpenLCB link via Grid Connect
#
# @author: Stuart Baker

import time
import array
import threading

import rawiotcp
import mtiDefs
#import defaults
import canolcbutils

import verifyNodeAddressed
import verifyNodeGlobal
import aliasMapEnquiry

## mapping for multi-frame addressed messages
class MultiFrameMap(dict) :
    ## Value of a "missing" key
    # @param key key that was asked for and found missing
    def __missing__(self, key) :
        return None

## Mapping between an alias an a Node ID.
class AliasMap :
    ## Constructor.
    def __init__(self) :
        self.alias = None
        self.nodeID = None
        self.timestamp = 0

    ## Setup an alias/Node ID map.
    # @param alias alias to set
    # @param nodeID Node ID to set
    def setup(self, alias, nodeID) :
        self.alias = alias
        self.nodeID = nodeID
        if (self.alias == None or self.nodeID == None) :
            self.timestamp = 0
        else :
            self.timestamp = time.time()

    ## Setup an alias/Node ID map.
    # @param alias alias to set
    def setup_alias(self, alias) :
        self.alias = alias
        if (self.alias == None) :
            self.timestamp = 0
        else :
            self.timestamp = time.time()

    ## Get the alias/Node ID map.
    # @return (alias, nodeID) alias that is mapped, Node ID that is mapped
    def get(self) :
        return self.alias, self.nodeID

    ## Get the alias of map.
    # @return alias that is mapped
    def get_alias(self) :
        return self.alias

    ## Get the Node ID of map.
    # @return Node ID that is mapped
    def get_node_id(self) :
        return self.nodeID

    ## Get the timestamp of last use.
    # @return timestamp of last use
    def get_timestamp(self) :
        return self.timestamp

    ## Update the timestamp.
    def touch(self) :
        self.timestamp = time.time()

## Small cache of alias mappings
class AliasCache :
    ## Constructor.
    def __init__(self) :
        self.lock = threading.RLock()
        self.cache = []
        for x in range(16) :
            self.cache.append(AliasMap())

    ## Get the alias from a Node ID.
    # @param nodeID Node ID to lookup
    def alias_lookup(self, nodeID) :
        self.lock.acquire()
        for x in self.cache :
            try_alias, try_node_id = x.get()
            if (try_node_id == nodeID) :
                self.lock.release()
                return try_alias
        self.lock.release()
        return 0

    ## Get the Node II from an alias.
    # @param alias alias to look up
    def node_id_lookup(self, alias) :
        self.lock.acquire()
        for x in self.cache :
            try_alias, try_node_id = x.get()
            if (try_alias == alias) :
                self.lock.release()
                return try_node_id
        self.lock.release()
        return 0

    ## purge alias from cache.
    # @param alias alias to purge
    # @param nodeID Node ID to purge
    def alias_purge(self, alias) :
        self.lock.acquire()
        for x in self.cache :
            try_alias, try_node_id = x.get()
            if (try_alias == alias) :
                x.setup(None, None)
                break
        self.lock.release()

    ## purge Node ID from cache.
    # @param alias alias to purge
    # @param nodeID Node ID to purge
    def node_id_purge(self, nodeID) :
        self.lock.acquire()
        for x in self.cache :
            try_alias, try_node_id = x.get()
            if (try_node_id == nodeID) :
                x.setup(None, None)
                break
        self.lock.release()

    ## cache an alias/Node ID mapping.
    # @param alias alias to cache
    # @param nodeID Node ID to cache
    def add_to_cache(self, alias, nodeID) :
        self.lock.acquire()
        cache_alias = self.alias_lookup(nodeID)
        if (cache_alias == alias) :
            self.lock.release()
            return
        elif (cache_alias != 0) :
            node_id_purge(nodeID)

        oldest = self.cache[0]
        oldest_time = time.time()
        for x in self.cache :
            x_timestamp = x.get_timestamp()
            if (x_timestamp < oldest_time) :
                oldest_time = x_timestamp
                oldest = x
        oldest.setup(alias, nodeID)
        self.lock.release()

## Generic MTI to GC helper
class GenericToGC :
    ## Constructor.
    # @param rawIO input/ouput stream
    # @param verbose true to print verbose information
    def __init__(self, nodeID, rawIO, verbose, veryVerbose=False) :
        self.aliasCache = AliasCache()
        self.aliasSource = AliasMap()
        self.aliasSource.setup(None, nodeID)
        self.aliasReserve = 0
        self.aliasInUse = False

        self.mfMap = MultiFrameMap()

        self.rcvData = ""
        self.rcvIndex = 0
        self.rawIO = rawIO
        self.verbose = verbose
        self.veryVerbose = veryVerbose
        self.sendString = ""
        self.recvString = ""

        self.sendThread = threading.Thread(target = self.send_thread)
        self.recvThread = threading.Thread(target = self.recv_thread)
        self.sendLock = threading.Lock()
        self.recvLock = threading.Lock()
        self.sendSem = threading.Semaphore(0)

        self.rawIO.connect()
        self.sendThread.setDaemon(True)
        self.recvThread.setDaemon(True)
        self.sendThread.start()
        self.recvThread.start()

        self.exit = False;
        return

    ## Convert a hex string to a Node ID tuple.
    # @param string hex string to convert
    # @return [x,x,x,x,x,x] tuple containing Node ID
    def hex_string_to_node_id(self, string) :
        return [int(string[0:2],  16),  int(string[2:4],   16),
                int(string[4:6],  16),  int(string[6:8],   16),
                int(string[8:10], 16),  int(string[10:12], 16)]

    ## Thread for sending data to the raw interface.
    def send_thread(self) :
        while (True) :
            self.sendSem.acquire()
            if (self.exit == True) :
                return
            self.sendLock.acquire()
            if (len(self.sendString) > 0) :
                self.rawIO.send(self.sendString)
                self.sendString = ""
            self.sendLock.release()

    ## Thread for receiving data from the raw interface.
    def recv_thread(self) :
        recvData = None
        recvIndex = 0
        parsed = ""

        while (True) :
            recvIndex = 0
            recvData = self.rawIO.recv(1024, 3)
            if (self.exit == True) :
                return

            if (recvData == None) :
                continue

            while (recvIndex < len(recvData)) :
                # parse the data received
                c = recvData[recvIndex]
                recvIndex += 1
                if (c == ':') :
                    parsed = ""
                parsed = parsed + c
                if (c == ';') :
                    source_alias = int(parsed[7:10], 16)
                    if (source_alias == self.aliasReserve) :
                        # trying to reserve an in use alias
                        self.aliasInUse = True

                    (self_alias, self_node_id) = self.aliasSource.get()
                    if (self_alias == source_alias) :
                        # alias conflict with self
                        self.raw_send(canolcbutils.makeframestring(0x10703000 +
                                                                  self_alias,
                                                                  self_node_id))
                        self.aliasSource.setup_alias(None)
                        # this might still be a valid message, don't reset parse

                    if (parsed[0:4] == ":X17" or parsed[0:4] == ":X16" or
                        parsed[0:4] == ":X15" or parsed[0:4] == ":X14") :
                        # Check ID
                        if (self.veryVerbose) :
                            print "  receive  CID,0x%03X"% \
                                  int(parsed[7:10], 16)

                    elif (parsed[0:7] == ":X10700") :
                        # Reserve ID
                        if (self.veryVerbose) :
                            print "  receive  RID,0x%03X"% \
                                  int(parsed[7:10], 16)

                    elif (parsed[0:7] == ":X10701") :
                        # Alias Map Definition
                        if (self.veryVerbose) :
                            print "  receive  AMD,0x%03X"% \
                                     int(parsed[7:10], 16)

                        node_id = self.hex_string_to_node_id(parsed[11:23])
                        self.aliasCache.add_to_cache(source_alias, node_id)
                    elif (parsed[0:7] == ":X10702") :
                        # Alias Map Enquiry
                        if (self.veryVerbose) :
                            print "  receive  AME,0x%03X"% \
                                  int(parsed[7:10], 16)

                        node_id = None
                        if (parsed.len() == 23) :
                            node_id = self.hex_string_to_node_id(parsed[11:23])

                        if (node_id == None or self_node_id == node_id) :
                            self.raw_send(canolcbutils.makeframestring(
                                                        0x10701000 + self_alias,
                                                        self_node_id))
                    elif (parsed[0:7] == ":X10703") :
                        # Alias Map Reset
                        if (self.veryVerbose) :
                            print "  receive  AMR,0x%03X"% \
                                  int(parsed[7:10], 16)

                        node_id = self.hex_string_to_node_id(parsed[11:23])
                        self.aliasCache.alias_purge(source_alias)
                        self.aliasCache.node_id_purge(node_id)
                    elif (int(parsed[3], 16) & 0x8) :
                        # Standard MTI frame
                        if (parsed[4:7] == "170") :
                            # Verified Node ID Number, cache
                            node_id = self.hex_string_to_node_id(parsed[11:23])
                            self.aliasCache.add_to_cache(source_alias, node_id)

                    self.recvLock.acquire()
                    self.recvString += parsed
                    self.recvLock.release()
                    if (self.veryVerbose) :
                        print "  receive ", parsed

    ## Request thread exit.
    def shutdown(self) :
        self.exit = True
        self.sendSem.release()

    ## Send data to the interface.
    # @param string data to send
    def raw_send(self, string, verbose=False) :
        self.sendLock.acquire()
        self.sendString += string
        self.sendSem.release()
        self.sendLock.release()
        if (self.veryVerbose or verbose) :
            print "  send raw", string

    ## Receive data from the interface.
    # @param size size of data in bytes to receive
    # @Return data received, else None if timeout and no data is available
    def raw_recv(self, size) :
        self.recvLock.acquire()
        if (size > len(self.recvString)) :
            size = len(self.recvString)
        result = self.recvString[:size]
        self.recvString = self.recvString[size:]
        self.recvLock.release()

        if (result == "") :
            return None
        else :
            return result

    ## Get the alias for the source Node ID, allocate it if necessary.
    def source_alias(self) :
        src_alias, src_nodeID = self.aliasSource.get()
        if (src_alias != None) :
            return src_alias

        # alias not found in any local storage
        for x in xrange(0x001, 0xFFE) :
            self.aliasReserve = x
            self.aliasInUse = False

            self.raw_send(canolcbutils.makeframestring(0x17000000 +
                                               ((src_nodeID[0] & 0xFF) << 16) +
                                               ((src_nodeID[1] & 0xF0) <<  8) +
                                               x, 
                                               None))
            self.raw_send(canolcbutils.makeframestring(0x16000000 +
                                               ((src_nodeID[1] & 0x0F) << 20) +
                                               ((src_nodeID[2] & 0xFF) << 12) +
                                               x, 
                                               None))
            self.raw_send(canolcbutils.makeframestring(0x15000000 +
                                               ((src_nodeID[3] & 0xFF) << 16) +
                                               ((src_nodeID[4] & 0xF0) <<  8) +
                                               x, 
                                               None))
            self.raw_send(canolcbutils.makeframestring(0x14000000 +
                                               ((src_nodeID[4] & 0x0F) << 20) +
                                               ((src_nodeID[5] & 0xFF) << 12) +
                                               x, 
                                               None))
            start = time.time()
            time.sleep(0.2)
            if (self.aliasInUse != False) :
                # conflict found, try again
                continue;

            self.raw_send(canolcbutils.makeframestring(0x10700000 + x, None))
            self.raw_send(canolcbutils.makeframestring(0x10701000 + x,
                                                       src_nodeID))
            self.aliasSource.setup_alias(x)
            return x
            
        assert False, "cannot allocate an alias"

    ## Get the alias for the destination Node ID.
    # @param dest destination Node ID we are looking up the alias for
    # @return destination alias, else 0 on error
    def dest_alias(self, dest) :
        for x in range(3) :
            alias = self.aliasCache.alias_lookup(dest)
            if (alias != 0) :
                return alias

            # try and find the node alias out on the bus
            src_alias = self.source_alias()
            self.raw_send(verifyNodeGlobal.makeframe(src_alias, None))
            time.sleep(.2)

        assert False, "cannot find alias for Node ID"

    ## Get the Node ID for the destination alias.
    # @param alias alias we are looking up the Node ID for
    # @return destination alias, else 0 on error
    def dest_node_id(self, alias) :
        for x in range(3) :
            node_id = self.aliasCache.node_id_lookup(alias)
            if (node_id != 0) :
                return node_id

            # try and find the node id out on the bus
            src_alias = self.source_alias()
            self.raw_send(verifyNodeAddressed.makeframe(src_alias, alias, None))
            time.sleep(.2)

        assert False, "cannot find Node ID for alias"

    ## Add payload bytes to the string.  Pop the added bytes off the payload.
    # @param string string to add payload bytes to
    # @param alias destination alias
    # @param payload list of payload data
    # @param size number of payload bytes to append
    # @return (string, payload) appended string, payload less appended items
    def append_payload(self, string, alias, flags, payload, size) :
        if (alias != None) :
            alias += flags << 12
            retval += hex(alias).upper()[2:]
        while (size) :
            string += ("00"+(hex(payload[0]).upper()[2:]))[-2:]
            payload.pop(0)
            size = size - 1;
        return string, payload

    ## Send message.
    # @param message OlcbMessage to send
    # @param mti generic message MTI
    # @param paylaod list of payload bytes
    # @param dest destination Node ID
    def send(self, message) :
        src_alias = self.source_alias()
        message.set_source(self.aliasSource.get_node_id())
        flags = 0

        payload = []
        # setup data list
        if (message.get_payload() != []) :
            payload = list(message.get_payload())
        elif (message.get_event() != []) :
            payload = list(message.get_event())

        while (True) :
            string = ":X"
            if (message.get_mti() <= 0x0FFF) :
                string += "19"
                string += ("000"+(hex(message.get_mti()).upper()[2:]))[-3:]
            #else if (mti == MTI_DATAGRAM) :
            #else if (mti == MTI_STREAM_DATA_SEND) :
            else :
                assert False, "unknown message type"

            string += ("000"+(hex(src_alias).upper()[2:]))[-3:]
            string += "N"
            if (message.get_dest() != None) :
                dst_alias = self.dest_alias(message.get_dest())
                size = 0
                if (flags == 0 and len(paylaod) > 6) :
                    # first
                    flags = 1
                    size = 6
                elif (flags == 1 or flags == 3) :
                    if (len(payload) > 6) :
                        # middle
                        flags = 3
                        size = 6
                    else :
                        # last
                        flags = 2
                        size = len(payload)
                else :
                    # only
                    size = len(payload)

                string, payload = self.append_payload(string, dst_alias, flags,
                                                   payload, size)
            else :
                if (payload != None) :
                    assert (len(payload) <= 8), "Broadcast payload to large"
                    string, payload = self.append_payload(string, None, 0,
                                                          payload, len(payload))

            string += ";"

            # send
            self.raw_send(string)
            if (self.verbose) :
                print "  send    ", mtiDefs.olcb_message_to_string(message)
            if (len(payload) == 0 or dest == None) :
                return;

    ## Receive a message already parsed into Grid Connect format
    # @param timeout timout to wait for a message to araive
    def recv_parsed(self, timeout=1, verbose=False) :
        start = time.time()
        if (self.rcvIndex >= len(self.rcvData)) :
            self.rcvIndex = 0
            self.rcvData = ""

        result = ""
        while (True) :
            if (len(self.rcvData) == 0) :
                # get more data
                self.rcvData = self.raw_recv(1024)
                if (self.rcvData == None) :
                    self.rcvData = ""
                    if ((start + timeout) <= time.time()) :
                        return None
                    else :
                        # no data received, try again later
                        time.sleep(0.1)
                        continue
                self.rcvIndex = 0
            else :
                # parse our data
                done = False
                while (done == False) :
                    if (self.rcvData[self.rcvIndex] == ':') :
                        result = ""
                    result = result + self.rcvData[self.rcvIndex]
                    if (self.rcvData[self.rcvIndex] == ';') :
                        done = True

                    self.rcvIndex = self.rcvIndex + 1
                    if (self.rcvIndex >= len(self.rcvData)) :
                        self.rcvIndex = 0
                        self.rcvData = ""
                        break

                if (done) :
                    if (verbose) :
                        print "  recv raw", result
                    return result


    ## Receive a message. 
    # @param timeout timout to wait for a message to araive
    # @return mtiDefs.OlcbMessage object, else None on timeout.
    def recv(self, timeout=1) :
        while (True) :
            result = self.recv_parsed(timeout)
            if (result == None) :
                return None

            message = mtiDefs.OlcbMessage()

            # we have a full message to report back
            if (result[0:2] != ":X" or result[10] != 'N') :
                # not an interesting CAN frame type for us
                continue

            if ((int(result[3:4], 16) & 0x8) == 0) :
                # low level alias message
                continue

            can_source = int(result[7:10], 16)
            message.set_source(self.dest_node_id(can_source))

            can_header = int(result[2:7], 16)
            can_mti = can_header & 0xFFF

            if ((can_header & 0x7000) == 0x1000) :
                # not stream or datagram
                message.set_mti(can_mti)
            elif ((can_header & 0x7000) >= 0x2000 and
                  (can_header & 0x7000) <= 0x5000) :
                # datagram
                result = ""
                break
            elif ((can_header & 0x7000) == 0x7000) :
                # stream
                result = ""
                break

            if (can_mti & 0x8) :
                # addressed message
                can_dest = int(result[11:15], 16) & 0xFFF
                if (self.aliasSource.get_alias() != can_dest)  :
                    # not addressed to us
                    continue

                message.set_mti(can_mti)
                message.set_dest(self.aliasSource.get_node_id())

                flags = int(result[11:12], 16) & 0x3
                if (flags == 0) :
                    # only frame
                    message.append_data(result[15:len(result)-1])
                else :
                    key = (can_dest << 24) + (can_source << 12) + can_mti
                    if (flags == 1) :
                        # first frame
                        assert self.mfMap[key] == None, \
                               "multi-frame map already has map"
                        message.append_data(result[15:len(result)-1])
                        self.mfMap[key] = message
                        # need more frames
                        continue
                    else :
                        assert self.mfMap[key] != None, \
                               "multi-frame map missing"
                        assert self.mfMap[key].get_mti() == can_mti, \
                               "multi-frame mti mismatch"
                        self.mfMap[key].append_data(result[15:len(result)-1])
                        if (flags == 2) :
                            # last frame
                            message = self.mfMap[key]
                            del self.mfMap[key]
                        else :
                            # middle frame, need more frames
                            continue
            elif (can_mti & 0x4) :
                message.set_event_from_hex_string(result[11:27])

            print "  receive ", mtiDefs.olcb_message_to_string(message)
            return message

    
    ## Continue receiving data until the we get the expected result or timeout.
    # @param exact if != None, look for result with exact string
    # @param startswith if != None, look for result starting with string
    # @param data if != None, tuple of data bytes to match
    # @param timeout timeout in seconds, if timeout != 0, return None on timeout
    # @return resulting message on success, None on timeout
    def raw_expect(self, exact=None, startswith=None, data=None, timeout=1) :
        start = time.time()
        while (True) :
            result = self.recv_parsed(verbose=True)
            if (data != None and result != None) :
                if (len(data) == ((len(result) - 12) / 2)) :
                    i = 0
                    j = 11
                    while (data[i] == int('0x' + result[j] + result[j + 1], 16)) :
                        i = i + 1
                        j = j + 2
                        if (i == len(data)) :
                            return result
            elif (exact != None) :
                if (result == exact) :
                    return result
            elif (startswith != None and result != None) :
                if (result.startswith(startswith)) :
                    return result
            elif (exact == None and startswith == None and data == None) :
                return result

            if (timeout != 0) :
                if (time.time() > (start + timeout)) :
                    if (self.verbose) :
                        print "Timeout"
                    return None

    ## Continue receiving data until the we get the expected result or timeout.
    # @param exact if != None, look for result with exact string
    # @param startswith if != None, look for result starting with string
    # @param data if != None, tuple of data bytes to match
    # @param timeout timeout in seconds, if timeout != 0, return None on timeout
    # @return resulting message on success, None on timeout
    def expect(self, exact=None, startswith=None, data=None, timeout=1) :
        start = time.time()
        while (True) :
            result = self.receive()
            if (data != None and result != None) :
                if (len(data) == ((len(result) - 12) / 2)) :
                    i = 0
                    j = 11
                    while (data[i] == int('0x' + result[j] + result[j + 1], 16)) :
                        i = i + 1
                        j = j + 2
                        if (i == len(data)) :
                            return result
            elif (exact != None) :
                if (result == exact) :
                    return result
            elif (startswith != None and result != None) :
                if (result.startswith(startswith)) :
                    return result
            elif (exact == None and startswith == None and data == None) :
                return result

            if (timeout != 0) :
                if (time.time() > (start + timeout)) :
                    if (self.verbose) :
                        print "Timeout"
                    return None

import sys
from optparse import OptionParser

## Entry point for an example
def main():
    result = 0

    raw_io = rawiotcp.RawIoTCP("localhost", 12021, 3, False)
    network = GenericToGC([01, 02, 03, 04, 05, 06], raw_io, True)

    # test generic interface
    network.send(mtiDefs.OlcbMessage(mtiDefs.INITIALIZATION_COMPLETE,
                                     payload = [01, 02, 03, 04, 05, 06]))
    network.send(mtiDefs.OlcbMessage(mtiDefs.IDENTIFY_EVENTS_GLOBAL))

    while (network.recv(1) != None) :
        continue
    # test raw interface
    alias = network.source_alias()
    network.raw_send(canolcbutils.makeframestring(0x10702000+alias,None), True)
    if (network.raw_expect(startswith=':X10701') == None) :
        print "Expected reply"
        result = 2

    network.shutdown()

    time.sleep(.5)
    return  result # done with example

def args(host, port, frame, verbose) :
    # argument processing
    usage = "usage: %prog [options] arg1\n\n" + \
            "Python module for connecting to an OpenLCB via a TCP native " + \
            "connection.\n" + \
            "Called standalone, will send one message frame.\n\n" + \
            "valid usages (default values):\n" + \
            "  ./tcpolcblink.py --ip=localhost\n" + \
            "  ./tcpolcblink.py --ip=localhost --port=12021\n" + \
            "  ./tcpolcblink.py --ip=localhost " + \
            "--port=12021 :X182DF123N0203040506080001\;" \

    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--ip", dest="host", metavar="IP",
                      default="localhost",
                      help="host name or ip address")
    parser.add_option("-p", "--port", dest="port", metavar="PORT",
                      default=12021,
                      help="port number")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="print verbose debug information")

    (options, args) = parser.parse_args()

    if (len(args) > 0) :
        frame = args[0]

    return (options.host, options.port, frame, options.verbose)
    
if __name__ == '__main__':
    main()
    
