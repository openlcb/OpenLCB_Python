#!/usr/bin/env python
## Input/Output stream helper for TCP sockets
#
# @author: Stuart Baker

## Raw input/output on a TCP socket

import time
import serial

class RawIoSerial :
    ## Constructor.
    # @param host host to connect to
    # @param port number to connect on
    # @param timeout receive timeout
    # @param verbose true to print verbose information
    def __init__(self, device, verbose=False) :
        self.device = device
        self.verbose = verbose
        return

    ## Create the serial connection.
    def connect(self) :
        if (self.verbose) :
            print "   connect to ", self.device
        self.ser = serial.Serial(self.device, timeout=0)
        return

    ## Close serial connection
    def close(self) :
        self.ser.close()

    ## Send data to the serial port.
    # @param string data to send
    def send(self, string) :
        # if verbose, print
        if (self.verbose and len(string) > 0) :
            print "  io send  ", string
    
        # send
        self.ser.write(string)
        return

    ## Receive data from the serial port.
    # @param size size of data in bytes to receive
    # @param timeout timout to wait for data to araive
    # @Return data received, else None if timeout and no data is available
    def recv(self, size, timeout=None) :
        self.ser.timeout = 0
        done = time.time() + timeout

        # get data
        data = ""
        while (size) :
            bytes = self.ser.read(size)
            if (len(bytes) == 0) :
                break
            data += bytes
            if (time.time > done) :
                break

            size -= len(bytes)
            sleep(0.1)

        if (len(data) == 0) :
            return None
        else :
            return data

