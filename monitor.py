#!/usr/bin/env python
'''
Simple monitor of CAN traffic on default connection
Kill to end

@author: Bob Jacobsen
'''

import connection as connection

def main():
    while (True) :
        frame = connection.network.receive()
        if (frame != None ) : print frame,
    return

if __name__ == '__main__':
    main()
