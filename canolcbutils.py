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
    for a in body :
        retval += ("00"+(hex(a).upper()[2:]))[-2:]
    retval += ";"
    return retval

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

if __name__ == '__main__':
    main()
    