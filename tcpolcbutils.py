#!/usr/bin/env python
'''
Utilities for communicating with TCP OpenLCB implementations

@author: Bob Jacobsen
'''

'''
Turn frame values into a string for sending to the interface.
source is a 6-byte array for the source NodeID
capture (time) is not currently used, so pass None
body is an array of bytes for the message itself, starting with the MTI 
    and including the source ID and (optionally) the dest ID
'''
def makemessagestring(source, capture, body) :
    retval = "\x80\x00"
    retval += "\x00\x00"+chr(len(body)+6+6)
    retval += chr(source[0])+chr(source[1])+chr(source[2])+chr(source[3])+chr(source[4])+chr(source[5])
    # capture time defaults to 0 for now
    retval += chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)
    if (body != None) :
        for a in body :
            retval += chr(a)
    return retval

'''
Take a string of bytes and present as their hex values
'''
def format(bytes) :
    output = ""
    for a in bytes :
        output  += ("00"+(hex(ord(a)).upper()[2:]))[-2:]+" "
    return output

'''
Take a message (array of bytes) and present as their hex values
'''
def formatMessage(bytes) :
    output = ""
    for a in bytes :
        output  += ("00"+(hex(a).upper()[2:]))[-2:]+" "
    return output

'''
Take a hex-byte-sequence string like 1.2.3.a3.4 and return
an array of ints, used for e.g. input of node and event IDs
'''
def splitSequence(seq) :
    strings = seq.split('.')
    result = []
    for a in strings : 
        result = result+[int(a, 16)]
    return result
 
'''
Parse a message into MTI, sourceID, destID-or-None, body
NOT for parsing received TCP strings
'''
def parseMessage(message) :
    mti = message[0]*256+message[1]
    source = message[2:7]
    if (mti & 0x0008) != 0 :
        dest = message[8:13]
        body = message[14:]
    else :
        dest = None
        body = message[8:]
    return [mti, source, dest, body]

'''
Do a simple test if run from command line
'''

def main():
    print format(makemessagestring([0x12,0x34,0x56,0x78,0x9A,0xbc], None, [0x04,0x90,0x12,0x34,0x56,0x78,0x9A,0xbc]))
    print parseMessage([0x04,0x90,0x12,0x34,0x56,0x78,0x9A,0xbc,1,2])
    print parseMessage([0x04,0x98,0x12,0x34,0x56,0x78,0x9A,0xbc, 0x12,0x34,0x56,0x78,0x9A,0xbc,1,2])

if __name__ == '__main__' :
    main()
    