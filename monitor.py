#!/usr/bin/env python
'''
Created on March 18, 2011

@author: Bob Jacobsen
'''

import ethernetolcblink as link

def main():
    link.receive('10.0.1.98', 23, True)

if __name__ == '__main__':
    main()
