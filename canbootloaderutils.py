#!/usr/bin/env python
'''
Utilities for communicating with CAN FLIP ISP

@author: Bob Jacobsen
@author: D.E. Goodman-Wilson
'''


'''
Check that a frame is of a given type
'''
def isFrameType(frame, CMD, CRIS) :
  if not frame.startswith(":S"): return False

  if (int(frame.split('S')[-1].split('N')[0], 16) == (CRIS<<3) + CMD): return True
  return False

'''
Turn frame values into a string for sending to the interface.
header is the int value of the CAN frame header.
body is an array of 0 to 8 bytes of data for the frame body.
'''
def makeframestring(CRIS, command, body) :
    retval = ":S"
    retval += "%0.8X" % ((CRIS<<3)+command)
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
    string = frame.split('N')[-1]
    result = []
    while (string[0] != ';') :
        result = result+[int(string[:2],16)]
        string = string[2:]
    return result
           
def main():
    print makeframestring(0xFF, 0xFF, [0x00])
    print splitSequence("1.2.3.a.0a.10.4")
    print bodyArray(":X1E00000N0F010203040506;")
    

if __name__ == '__main__':
    main()
    
