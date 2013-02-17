#!/usr/bin/env python
'''
Utilities for communicating with CAN OpenLCB implementations

@author: Bob Jacobsen
'''

'''
Turn frame values into a string for sending to the interface.
header is the int value of the CAN frame header.
body is an array of 0 to 8 bytes of data for the frame body.
'''
def makeframestring(header, body) :
    retval = ":X"
    retval += hex(header).upper()[2:]
    retval += "N"
    if (body != None) :
        for a in body :
            retval += ("00"+(hex(a).upper()[2:]))[-2:]
    retval += ";"
    return retval

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
Pull body bytes from frame as array
'''
def bodyArray(frame) :
    string = frame[11:];
    result = []
    while (string[0] != ';') :
        result = result+[int(string[:2],16)]
        string = string[2:]
    return result
           
'''
Return (header, body) of a P/C Event Report frame
alias: the source alias of this node
id: array containing 8 bytes of event ID
'''
def eventframe(alias, event) :
    return (0x182DF000+alias, event)


def main():
    (header, body) = eventframe(0x123, [11,255,240,4,5,6,7,8]);
    print makeframestring(header, body)
    print splitSequence("1.2.3.a.0a.10.4")
    print bodyArray(":X1E000000F010203040506;")
    

if __name__ == '__main__':
    main()
    