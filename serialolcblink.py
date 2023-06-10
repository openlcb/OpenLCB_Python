#!/usr/bin/env python
'''
Drive an OpenLCB via USB serial

Note: At 230400, requires CAN2USBino version 2 or later.

@author: Bob Jacobsen
'''
import serial
import time

class SerialOlcbLink :
    def __init__(self) :

        # defaults (generally overridden by system-wide defaults elsewhere)
        self.port = "/dev/cu.usbmodemCC570001B1"
        self.speed = 115200
        self.timeout = 0.1     # try to keep operations fast
        self.verbose = False
        self.parallel = False
        self.startdelay = 0    # set to 12 if your hardware resets on connection
        self.ser = None
        return

    def connect(self) :
        # if verbose, print
        if (self.verbose) : print ("   connect to "+str(self.port)+" at "+str(self.speed))

        self.ser = serial.Serial(self.port, self.speed)
        self.ser.parity = serial.PARITY_NONE
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.stopbits = serial.STOPBITS_TWO
        #self.ser.setXonXoff(True)
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.setDTR(True)
        self.ser.setRTS(True)


        # from http://bytes.com/topic/python/answers/170478-uart-parity-setting-mark-space-using-pyserial
        if self.speed == 230400 and not self.parallel :
            self.ser.parity = serial.PARITY_EVEN
            self.ser.stopbits = serial.STOPBITS_TWO
            import termios
            iflag, oflag, cflag, lflag, ispeed, ospeed, cc = termios.tcgetattr(self.ser)
            cflag |= 0x40000000 # CMSPAR to select MARK parity
            termios.tcsetattr(self.ser, termios.TCSANOW, [iflag, oflag, cflag, lflag,ispeed, ospeed, cc])


        # wait default time for Arduino startup
        # after (possible) reset due to serial startup
        if self.startdelay > 0 :
            if self.verbose : print ("   waiting", self.startdelay, "seconds for adapter restart")
            time.sleep(self.startdelay)
            # dump all messages
            while self.ser.inWaiting() > 0 :
                self.ser.readline()
        return

    def send(self, frame) :
        if self.ser == None : self.connect()

        # if verbose, print
        if self.verbose : print ("   send    "+str(frame))

        # double-output format needed if operating at  230400
        tframe = frame+'\n'
        if self.speed == 230400 :
            tframe = "!!"
            for c in frame[1:len(frame)-1] :
                tframe = tframe+c+c
            tframe = tframe+";;"
        # send
        self.ser.write(tframe.encode())

        return

    def receive(self) : # returns frame
        if (self.ser == None) : self.connect()

        self.ser.timeout = self.timeout
        line = "";
        r = self.ser.readline()
        # remove Xoff/Xon characters if present
        r = r.decode('utf8').replace("\x11", "")
        r = r.replace("\x13", "")
        r = r.replace("\x0A", "")
        r = r.replace("\x0D", "")
        # timeout returns ""
        if r == "" :
            if (self.verbose) : print ("   receive <none>") # blank line to show delay?
            return None
        # if verbose, display what's received
        if (self.verbose) : print ("   receive "+r.replace("\x0A", "").replace("\x0D", ""))
        return r

    '''
    Continue receiving data until the we get the expected result or timeout.
    @param exact if != None, look for result with exact string
    @param startswith if != None, look for result starting with string
    @param data if != None, tuple of data bytes to match
    @param timeout timeout in seconds, if timeout != 0, return None on timeout
    @return resulting message on success, None on timeout
    '''
    def expect(self, exact=None, startswith=None, data=None, timeout=1) :
        start = time.time()
        while (True) : # loop to find, timeout or fali
            result = self.receive()

            if (result == None) :
                 if (timeout != 0) :
                    if (time.time() > (start + timeout)) :
                        if (self.verbose) :
                            print ("Timeout")
                        return None
                    else :
                        continue
                 else : return None

            # here, result was not None - do sequential checks
            if (exact == None and startswith == None and data == None) :
                return result   # no test, just get the data

            if (data != None) :
                if (len(data) == ((len(result) - 12) / 2)) :
                    i = 0
                    j = 11
                    while i != len(data)-1 :
                        if (data[i] != int('0x' + result[j] + result[j + 1], 16)) :
                            # fail on non equal
                            return None
                        i = i + 1
                        j = j + 2
                else :
                    # fail on length
                    return None

            if (exact != None) :
                print ("exact may not be working right?")
                print (result)
                print (exact)
                print (result == exact)
                if (result != exact) :
                    return None

            if (startswith != None) :
                if (not result.startswith(startswith)) :
                    return None

            # here, we passed all the available tests!
            return result

    def close(self) :
        return

import getopt, sys

def main():
    global frame

    # create connection object
    network = SerialOlcbLink()

    # get defaults
    port = network.port
    speed = network.speed
    verbose = network.verbose

    frame = ':X19490001N;'

    # process arguments
    (port, speed, frame, verbose) = args(port, speed, frame, verbose)

    # load new defaults
    network.port = port
    network.speed = speed
    network.verbose = verbose

    # send the frame
    network.send(frame)

    # then wait for and display responses until interrupted or nothing received
    while True :
        reply = network.receive()
        if reply == None : break
        print (reply)
    return

def usage() :
    print ("")
    print ("Python module for connecting to an OpenLCB via an serial connection.")
    print ("Called standalone, will send one CAN frame.")
    print ("")
    print ("valid options:")
    print ("  -v for verbose; also displays any responses")
    print ("  -p, --port for serial port to USB connection")
    print ("  -s, --speed for baud rate")
    print ("")
    print ("valid usages (default values):")
    print ("  python serialolcblink.py --port=/dev/tty.usbserial-A7007AOK")
    print ("  python serialolcblink.py --port=/dev/tty.usbserial-A7007AOK --speed=115200")
    print ("  python serialolcblink.py --port=/dev/tty.usbserial-A7007AOK --speed=115200 :X19490001N\;")
    print ("")
    print ("Note: Most shells require escaping the semicolon at the end of the frame.")

def args(port, speed, frame, verbose) :
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "s:p:v", ["speed=", "port="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print (str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-s", "--speed"):
            speed = int(arg)
        else:
            assert False, "unhandled option"
    if (len(remainder) > 0) :
        frame = remainder[0]
    return (port, speed, frame, verbose)

if __name__ == '__main__':
    main()

